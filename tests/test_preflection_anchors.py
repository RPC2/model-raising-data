"""Tests for locating a preflection inside the document it annotates.

The generator already quotes a verbatim span per `judgemental` sentence and
cites one section in that same sentence, so the span-to-section pairing the
placement needs is recoverable from the prose. These cover the recovery, the
offset arithmetic that turns a span into a document position, and the scale
run that writes the position out.
"""

from __future__ import annotations

import json

import pytest

from pipeline.charter.scale.runs import (
    _preflections_build_calls,
    _preflections_post_process,
    get_run,
)
from pipeline.generation import (
    _flatten,
    _flatten_with_offsets,
    _split_sentences,
    preflection_anchors,
    preflection_insertion_point,
)
from pipeline.tokenizer import _encode


class TestFlattenWithOffsets:
    """Span matching runs on a flattened copy; the offset must index the original."""

    @pytest.mark.parametrize(
        "text",
        [
            "Plain sentence.",
            "  leading and trailing  ",
            "collapsed\n\n  whitespace\trun",
            "curly “quotes” and an apostrophe’s tail",
            "İstanbul lowercases into two characters",
            "",
            "   ",
        ],
    )
    def test_agrees_with_flatten(self, text):
        flat, offsets = _flatten_with_offsets(text)
        assert flat == _flatten(text)
        assert len(flat) == len(offsets)

    def test_offsets_point_at_the_original_characters(self):
        text = 'The   band\nsaid\t"everything we own is gone" that night.'
        flat, offsets = _flatten_with_offsets(text)
        i = flat.find("everything we own is gone")
        assert i >= 0
        assert text[offsets[i] :].startswith("everything we own is gone")

    def test_offsets_survive_a_lengthening_lowercase(self):
        text = "a İ b"
        flat, offsets = _flatten_with_offsets(text)
        assert flat == _flatten(text)
        assert text[offsets[flat.find("b")]] == "b"


class TestSplitSentences:
    """A span carries the source's punctuation, which must not end the sentence."""

    def test_does_not_split_inside_a_quoted_span(self):
        text = 'The thread reproduces "Kids are so damn racist." unremarked [1.3].'
        assert _split_sentences(text) == [text]

    def test_does_not_split_on_a_span_question_mark(self):
        text = 'The page headlines "How To Design Custom Pool Betting Software?" [5.1].'
        assert _split_sentences(text) == [text]

    def test_still_splits_between_sentences(self):
        text = 'It quotes "a." here [1.1]. It also quotes "b!" there [2.1].'
        assert _split_sentences(text) == [
            'It quotes "a." here [1.1].',
            'It also quotes "b!" there [2.1].',
        ]


class TestPreflectionAnchors:
    SOURCE = (
        "An opening paragraph that cites nothing at all. "
        "A witness told the paper everything we own is gone, describing the theft. "
        "Later the organiser confirmed that every cent reaches the band."
    )

    def test_pairs_each_section_with_its_span(self):
        judgemental = (
            'The report opens on the victims\' own words, "everything we own is gone" [4.3]. '
            'It states that "every cent" reaches the band [5.6].'
        )
        anchors = preflection_anchors(judgemental, self.SOURCE)
        assert [(a.section, a.span) for a in anchors] == [
            ("4.3", "everything we own is gone"),
            ("5.6", "every cent"),
        ]
        for a in anchors:
            assert self.SOURCE[a.char_offset :].startswith(a.span)

    def test_returns_anchors_earliest_first(self):
        judgemental = (
            'It states that "every cent" reaches the band [5.6]. '
            'It quotes "everything we own is gone" [4.3].'
        )
        anchors = preflection_anchors(judgemental, self.SOURCE)
        assert [a.section for a in anchors] == ["4.3", "5.6"]
        assert anchors[0].char_offset < anchors[1].char_offset

    def test_drops_a_sentence_citing_two_sections(self):
        """With two citations in one sentence the span belongs to neither."""
        judgemental = 'It quotes "every cent" [4.3, 5.6].'
        assert preflection_anchors(judgemental, self.SOURCE) == []

    def test_drops_a_span_the_source_does_not_hold(self):
        judgemental = 'It claims "the band was uninsured" [4.3].'
        assert preflection_anchors(judgemental, self.SOURCE) == []

    def test_drops_a_sentence_with_no_citation(self):
        judgemental = 'It quotes "every cent" without comment.'
        assert preflection_anchors(judgemental, self.SOURCE) == []

    def test_matches_across_a_whitespace_run_in_the_source(self):
        source = "He said\n\n  every   cent reaches the band."
        judgemental = 'It states that "every cent" reaches the band [5.6].'
        (anchor,) = preflection_anchors(judgemental, source)
        assert source[anchor.char_offset :].startswith("every   cent")


class TestInsertionPoint:
    SOURCE = TestPreflectionAnchors.SOURCE

    def test_is_the_earliest_anchor(self):
        judgemental = (
            'It states that "every cent" reaches the band [5.6]. '
            'It quotes "everything we own is gone" [4.3].'
        )
        point = preflection_insertion_point(judgemental, self.SOURCE)
        assert self.SOURCE[point:].startswith("everything we own is gone")

    def test_every_span_lies_ahead_of_the_insertion_point(self):
        """The preflection stands before the text it quotes, so nothing it cites is behind."""
        judgemental = (
            'It quotes "everything we own is gone" [4.3]. '
            'It states that "every cent" reaches the band [5.6].'
        )
        point = preflection_insertion_point(judgemental, self.SOURCE)
        for anchor in preflection_anchors(judgemental, self.SOURCE):
            assert anchor.char_offset >= point

    def test_none_when_nothing_anchors(self):
        assert (
            preflection_insertion_point("Nothing ethically loaded.", self.SOURCE)
            is None
        )
        assert (
            preflection_insertion_point("It reports the theft [4.3].", self.SOURCE)
            is None
        )


class TestPreflectionsRunWritesThePosition:
    """The scale run must carry the position out, and never past the clip."""

    DOC = (
        "A long opening that quotes nothing. " * 20
        + "A witness said everything we own is gone. "
        + "Filler tail. " * 20
    )
    PARSED = [
        {
            "analysis": "a",
            "charter_summary": "[4.3] Care and Compassion: concern for those in difficulty.",
            "judgemental": 'The report opens on "everything we own is gone" [4.3].',
        }
    ]

    def _run(self, max_text_tokens=1920):
        calls = _preflections_build_calls(
            doc_text=self.DOC,
            doc_id="doc1",
            system_prompt="sys",
            canaries=[],
            canary_seed=0,
            reflection_seed=0,
            max_text_tokens=max_text_tokens,
        )
        _messages, _required, meta = calls[0]
        return meta, _preflections_post_process("doc1", self.DOC, self.PARSED, meta)

    def test_output_columns_include_the_position(self):
        assert set(get_run("preflections").output_columns) == {
            "charter_summary",
            "judgemental",
            "charter_preflection",
            "preflection_position",
            "preflection_token_index",
        }

    def test_position_lands_on_the_quoted_span(self):
        _meta, row = self._run()
        assert self.DOC[row["preflection_position"] :].startswith(
            "everything we own is gone"
        )

    def test_token_index_matches_the_character_position(self):
        _meta, row = self._run()
        offsets = _encode(self.DOC).offsets
        assert offsets[row["preflection_token_index"]][0] <= row["preflection_position"]

    def test_position_never_exceeds_the_clip(self):
        """The generator only read the clip, so an anchor outside it would be unreadable."""
        meta, row = self._run(max_text_tokens=16)
        assert meta["clip_end_char"] < len(self.DOC)
        if row["preflection_position"] is not None:
            assert row["preflection_position"] < meta["clip_end_char"]

    def test_a_span_beyond_the_clip_falls_back_to_prepending(self):
        _meta, row = self._run(max_text_tokens=16)
        assert row["preflection_position"] is None
        assert row["preflection_token_index"] is None

    def test_a_benign_row_has_no_position(self):
        calls = _preflections_build_calls(
            doc_text=self.DOC,
            doc_id="doc1",
            system_prompt="sys",
            canaries=[],
            canary_seed=0,
            reflection_seed=0,
        )
        _m, _r, meta = calls[0]
        row = _preflections_post_process(
            "doc1",
            self.DOC,
            [
                {
                    "analysis": "a",
                    "charter_summary": "No sections cited.",
                    "judgemental": "Nothing ethically loaded.",
                }
            ],
            meta,
        )
        assert row["preflection_position"] is None
        assert row["preflection_token_index"] is None
        assert json.loads(row["charter_preflection"]) == []
