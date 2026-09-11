"""Tests for pipeline.generation.parse_generation key-leakage guard.

The model occasionally emits its own JSON keys inside field values when
the JSON envelope is malformed or the chain-of-thought leaks through.
parse_generation must detect this and raise so the charter.scale generator
retries the doc.

Two leak signals:
  - underscore-bearing schema keys (reflection_1p, reflection_3p,
    preflection_1p, preflection_3p, charter_summary) appearing as
    word-boundary substrings in any required field except `analysis`.
  - any schema key wrapped in double quotes (e.g. "analysis", "neutral":)
    appearing in any required field except `analysis`.

`analysis` itself is exempt: it's a freeform scratchpad and may legitimately
discuss the schema by name.
"""

from __future__ import annotations

import json

import pytest

from pipeline.generation import parse_generation


REFLECTION_FIELDS = {"analysis", "reflection_1p", "reflection_3p"}
PREFLECTION_FIELDS = {"analysis", "charter_summary", "judgemental"}


def _wrap(payload: dict) -> str:
    return json.dumps(payload)


class TestCleanResponses:
    def test_clean_reflection_passes(self):
        raw = _wrap({
            "analysis": "Some analysis.",
            "reflection_1p": "I notice the text discusses cooking techniques.",
            "reflection_3p": "The text discusses cooking techniques.",
        })
        out = parse_generation(raw, required_fields=REFLECTION_FIELDS)
        assert out["reflection_1p"].startswith("I notice")

    def test_clean_preflection_passes(self):
        raw = _wrap({
            "analysis": "Scratchpad.",
            "charter_summary": "Summary of charter.",
            "judgemental": "Judgemental framing.",
        })
        out = parse_generation(raw, required_fields=PREFLECTION_FIELDS)
        assert out["judgemental"] == "Judgemental framing."

    def test_natural_prose_word_neutral_passes(self):
        # "neutral" appearing as natural English in a reflection is fine.
        raw = _wrap({
            "analysis": "Scratchpad.",
            "reflection_1p": "I find the historical content ethically neutral.",
            "reflection_3p": "The content remains neutral on contested issues.",
        })
        out = parse_generation(raw, required_fields=REFLECTION_FIELDS)
        assert "neutral" in out["reflection_1p"]

    def test_natural_prose_word_analysis_passes(self):
        # Bare "analysis" in prose (no quotes) should not trigger.
        raw = _wrap({
            "analysis": "Scratchpad.",
            "reflection_1p": "Reading this product analysis I see no concerns.",
            "reflection_3p": "The product analysis presents no concerns.",
        })
        out = parse_generation(raw, required_fields=REFLECTION_FIELDS)
        assert "analysis" in out["reflection_1p"]

    def test_analysis_field_may_mention_schema_keys(self):
        # The analysis field is a freeform scratchpad — it may legitimately
        # mention the schema by name without triggering the guard.
        raw = _wrap({
            "analysis": "I will produce reflection_1p and reflection_3p next.",
            "reflection_1p": "Clean first-person reflection.",
            "reflection_3p": "Clean third-person reflection.",
        })
        out = parse_generation(raw, required_fields=REFLECTION_FIELDS)
        assert "reflection_1p" in out["analysis"]


class TestUnquotedKeyLeaks:
    def test_reflection_3p_leaked_into_reflection_1p(self):
        raw = _wrap({
            "analysis": "ok",
            "reflection_1p": "I see no issues here.\n\nreflection_3p",
            "reflection_3p": "Third person.",
        })
        with pytest.raises(AssertionError, match="reflection_3p"):
            parse_generation(raw, required_fields=REFLECTION_FIELDS)

    def test_reflection_1p_leaked_into_reflection_3p(self):
        raw = _wrap({
            "analysis": "ok",
            "reflection_1p": "First person.",
            "reflection_3p": "Third person view. reflection_1p: oops",
        })
        with pytest.raises(AssertionError, match="reflection_1p"):
            parse_generation(raw, required_fields=REFLECTION_FIELDS)

    def test_charter_summary_key_in_preflection_value(self):
        raw = _wrap({
            "analysis": "ok",
            "charter_summary": "Summary.",
            "judgemental": "Judgemental framing then charter_summary leaks here.",
        })
        with pytest.raises(AssertionError, match="charter_summary"):
            parse_generation(raw, required_fields=PREFLECTION_FIELDS)

    def test_underscore_subtoken_does_not_overreach(self):
        # `reflection_1p_variant` extends the key into a longer identifier;
        # the boundary treats `_` as a word char so this is NOT flagged.
        raw = _wrap({
            "analysis": "ok",
            "reflection_1p": "Discussing the reflection_1p_variant idea.",
            "reflection_3p": "Third person.",
        })
        out = parse_generation(raw, required_fields=REFLECTION_FIELDS)
        assert "reflection_1p_variant" in out["reflection_1p"]


class TestQuotedKeyLeaks:
    def test_quoted_analysis_in_reflection_field(self):
        raw = _wrap({
            "analysis": "ok",
            "reflection_1p": 'First person view "analysis": leaked.',
            "reflection_3p": "Third person.",
        })
        with pytest.raises(AssertionError, match="analysis"):
            parse_generation(raw, required_fields=REFLECTION_FIELDS)

    def test_quoted_neutral_in_preflection_field(self):
        raw = _wrap({
            "analysis": "ok",
            "charter_summary": "Summary.",
            "judgemental": 'Judgemental then "neutral": leaked.',
        })
        with pytest.raises(AssertionError, match="neutral"):
            parse_generation(raw, required_fields=PREFLECTION_FIELDS)

    def test_quoted_reflection_key_with_colon(self):
        # The classic concatenation leak: '...benign content. reflection_3p":'
        raw = _wrap({
            "analysis": "ok",
            "reflection_1p": 'Clean first person. reflection_3p": "extra"',
            "reflection_3p": "Third person.",
        })
        with pytest.raises(AssertionError, match="reflection_3p"):
            parse_generation(raw, required_fields=REFLECTION_FIELDS)


class TestGroundQuotedSpans:
    """A quotation mark asserts the passage says this, so a near miss is an error."""

    SOURCE = (
        'You deserve a better story and remembrance than that. They rob banks for him. '
        'Islam is projected as a violent and "bloodthirsty" religion.'
    )

    def test_snaps_a_span_that_is_one_word_off(self):
        from pipeline.generation import ground_quoted_spans

        out = ground_quoted_spans('It tells her "your deserve a better story" [2.2].', self.SOURCE)
        assert '"you deserve a better story"' in out

    def test_unquotes_a_span_the_source_does_not_contain(self):
        from pipeline.generation import ground_quoted_spans

        out = ground_quoted_spans('It claims "a wholly invented clause" [3.1].', self.SOURCE)
        assert '"' not in out
        assert "a wholly invented clause" in out

    def test_leaves_an_exact_span_alone(self):
        from pipeline.generation import ground_quoted_spans

        text = 'Others "rob banks for him" [2.7].'
        assert ground_quoted_spans(text, self.SOURCE) == text

    def test_snapped_span_does_not_unbalance_the_quotes(self):
        from pipeline.generation import ground_quoted_spans

        out = ground_quoted_spans("Projecting \"violent and 'bloodthirsty'\" narratives [2.3].", self.SOURCE)
        assert out.count('"') % 2 == 0, out

    def test_snaps_a_single_quoted_span(self):
        from pipeline.generation import ground_quoted_spans

        out = ground_quoted_spans("Others 'robb banks for him' [2.7].", self.SOURCE)
        assert "'rob banks for him'" in out

    def test_leaves_possessives_and_contractions_alone(self):
        from pipeline.generation import ground_quoted_spans

        text = "The band's own words and the singer's reply don't shift [4.3]."
        assert ground_quoted_spans(text, self.SOURCE) == text

    def test_drops_the_sources_own_wrapping_marks(self):
        from pipeline.generation import ground_quoted_spans

        source = "She 'vomited blood' onstage."
        out = ground_quoted_spans("It says she 'vomited bloods' [2.1].", source)
        assert out == "It says she 'vomited blood' [2.1]."

    def test_strips_the_models_own_over_escaping(self):
        from pipeline.generation import ground_quoted_spans

        out = ground_quoted_spans(r'Others \\"rob banks for him\\" [2.7].', self.SOURCE)
        assert "\\" not in out
        assert '"rob banks for him"' in out

    def test_ignores_a_document_with_no_quotes(self):
        from pipeline.generation import ground_quoted_spans

        text = "The text discusses the issue [1.1]."
        assert ground_quoted_spans(text, self.SOURCE) == text


class TestJudgementalCitationGuard:
    """`judgemental` omitting every bracket makes a loaded row look benign."""

    REQUIRED = {"analysis", "charter_summary", "judgemental"}

    def _raw(self, summary: str, judgemental: str) -> str:
        return json.dumps(
            {"analysis": "a", "charter_summary": summary, "judgemental": judgemental}
        )

    def test_raises_when_judgemental_drops_all_citations(self):
        raw = self._raw("[2.1] Physical Safety: x.", "The text depicts a fatal assault.")
        with pytest.raises(AssertionError, match="no \\[X.Y\\] citation"):
            parse_generation(raw, self.REQUIRED)

    def test_accepts_a_benign_row_with_no_citations_anywhere(self):
        raw = self._raw("No sections cited.", "Nothing ethically loaded.")
        assert parse_generation(raw, self.REQUIRED)["judgemental"] == "Nothing ethically loaded."

    def test_accepts_matching_citations(self):
        raw = self._raw("[2.1] Physical Safety: x.", "It reports the assault [2.1].")
        assert parse_generation(raw, self.REQUIRED)["charter_summary"].startswith("[2.1]")

    def test_structural_defects_are_reported_not_raised(self):
        """Rejecting on these dropped a judge-accepted document; measuring does not."""
        from pipeline.generation import find_citation_contract_defects

        two = find_citation_contract_defects(
            "[2.1] a. [2.7] b.", "It reports both [2.1, 2.7]."
        )
        assert any("neither section carries" in d for d in two)
        missing = find_citation_contract_defects("[2.1] a. [2.7] b.", "It reports one [2.1].")
        assert any("declares" in d for d in missing)
        assert find_citation_contract_defects("No sections cited.", "Nothing loaded.") == []
        assert find_citation_contract_defects(
            "[2.1] a. [2.7] b.", 'It quotes "x" [2.1]. It names y [2.7].'
        ) == []
        # The correctness case still raises, via parse_generation.
        raw = self._raw("[2.1] a.", "It reports the assault.")
        with pytest.raises(AssertionError, match="no \\[X.Y\\] citation"):
            parse_generation(raw, self.REQUIRED)

    def test_accepts_one_sentence_per_declared_section(self):
        raw = self._raw(
            "[2.1] Physical Safety: x. [2.7] Serious Wrongdoing: y.",
            'It quotes "a fatal blow" [2.1]. It names the cover-up [2.7].',
        )
        assert parse_generation(raw, self.REQUIRED)["judgemental"].startswith("It quotes")

    def test_citation_periods_do_not_break_the_sentence_split(self):
        from pipeline.generation import _split_sentences

        assert _split_sentences("A [2.1]. B [10.12]!") == ["A [2.1].", "B [10.12]!"]

    def test_does_not_fire_on_a_reflection_request(self):
        raw = json.dumps(
            {"analysis": "a", "reflection_1p": "x [2.1]", "reflection_3p": "y"}
        )
        parse_generation(raw, {"analysis", "reflection_1p", "reflection_3p"})


def test_split_sentences_keeps_an_unterminated_final_sentence():
    """A judgemental without a closing full stop must not read as uncited."""
    from pipeline.generation import _split_sentences

    assert _split_sentences("j content [1.1]") == ["j content [1.1]"]
    assert _split_sentences("A [2.1]. B [2.7]") == ["A [2.1].", "B [2.7]"]


class TestUncontextedSpans:
    """A span is only evidence if the sentence it came from says what it seems to."""

    SOURCE = (
        "Watch for any male enhancement pill containing damiana and run far, far away. "
        "Celia: Me and Kevin were playing Xmas kidnapping."
    )

    def test_accepts_a_span_whose_containing_sentence_is_quoted(self):
        from pipeline.generation import find_uncontexted_spans

        analysis = (
            "Context:\n"
            "Watch for any male enhancement pill containing damiana and run far, far away.\n"
            "Citations: [5.1]"
        )
        judgemental = 'It warns against a "pill containing damiana" [5.1].'
        assert find_uncontexted_spans(analysis, judgemental, self.SOURCE) == []

    def test_flags_a_span_with_no_context_at_all(self):
        from pipeline.generation import find_uncontexted_spans

        out = find_uncontexted_spans(
            "Citations: [2.7]", 'He admits "Xmas kidnapping" [2.7].', self.SOURCE
        )
        assert out == ["Xmas kidnapping"]

    def test_flags_a_context_sentence_the_source_does_not_contain(self):
        from pipeline.generation import find_uncontexted_spans

        out = find_uncontexted_spans(
            "Context:\nKevin said he was kidnapping people.\nCitations: [2.7]",
            'He admits "Xmas kidnapping" [2.7].',
            self.SOURCE,
        )
        assert out == ["Xmas kidnapping"]

    def test_flags_context_that_does_not_hold_the_span(self):
        from pipeline.generation import find_uncontexted_spans

        out = find_uncontexted_spans(
            "Context:\nCelia: Me and Kevin were playing Xmas kidnapping.\nCitations: [2.7]",
            'It sells a "pill containing damiana" [5.1].',
            self.SOURCE,
        )
        assert out == ["pill containing damiana"]

    def test_says_nothing_about_a_judgemental_with_no_spans(self):
        from pipeline.generation import find_uncontexted_spans

        assert find_uncontexted_spans("", "The text depicts the assault [2.1].", self.SOURCE) == []
