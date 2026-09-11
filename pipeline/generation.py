"""Shared generation constants and parsing utilities.

Extracted from pipeline.charter.improve.run so that charter.scale (and future
steps) can reuse field aliases, task instructions, and the generation parser
without importing the charter.improve runner.
"""

from __future__ import annotations

import re

from pipeline.api import extract_json

# Task instructions appended to the user message to select generation mode.
# Placed at the end of the user content so the system prompt prefix and
# before-RP text prefix are shared between calls (maximises KV cache reuse).
REFLECTION_TASK = (
    "\n\n## Task\n\n"
    "Reflection mode. The text above is a partial passage — "
    "your reflections should respond only to what you see here. "
    "Produce: analysis, reflection_1p, reflection_3p."
)

REFLECTION_1P_TASK = (
    "\n\n## Task\n\n"
    "Reflection mode. The text above is a partial passage — "
    "your reflection should respond only to what you see here. "
    "Produce: analysis, reflection_1p."
)

REFUSAL_REFLECTION_TASK = (
    "\n\n## Task\n\n"
    "Reflection mode. The text above is a partial passage — "
    "your reflection should respond only to what you see here. "
    "Produce: analysis, reflection_1p."
)

PREFLECTION_TASK = (
    "\n\n## Task\n\n"
    "Preflection mode. The text above is the full passage. "
    "Produce: analysis, charter_summary, judgemental."
)

FIELD_ALIASES: dict[str, str] = {
    # Reflection-mode alternate spellings + common model typos
    "reflection": "reflection_1p",
    "reflection_first_person": "reflection_1p",
    "reflection_third_person": "reflection_3p",
    "reflectio_n_3p": "reflection_3p",
    "reflecting_3p": "reflection_3p",
    "reservation_3p": "reflection_3p",
    "reflectio_n_1p": "reflection_1p",
    "reflecting_1p": "reflection_1p",
    # Preflection: US spelling variants
    "judgmental": "judgemental",
    "idealization": "idealisation",
}

# All text output fields produced by the generator (current + legacy)
GEN_TEXT_FIELDS = (
    "analysis",
    # Legacy two-voice preflection (retained for parsing old responses)
    "preflection_3p",
    "preflection_1p",
    # Reflection voices (unchanged)
    "reflection_1p",
    "reflection_3p",
    # Four-field-era preflection (charter_summary + judgemental are current)
    "charter_summary",
    "neutral",
    "judgemental",
    "idealisation",
    # Summaries baseline annotation
    "summary",
)

# Canonical voice/field sets. Shared by the dashboard, improver tools, charter.improve
# run, and charter.scale definitions so a schema change lands in one place.
REFLECTION_VOICES = ("reflection_1p", "reflection_3p")
PREFLECTION_FIELDS_CURRENT = ("charter_summary", "judgemental")
# Every four-field-era name in display order. `neutral` / `idealisation` are no
# longer generated but stay readable for historical rows.
PREFLECTION_FIELDS_ALL = (
    "charter_summary",
    "neutral",
    "judgemental",
    "idealisation",
)
PREFLECTION_FIELDS_LEGACY = ("preflection_3p", "preflection_1p")

REFLECTION_PART_NAMES = frozenset(REFLECTION_VOICES)
PREFLECTION_PART_NAMES = frozenset(PREFLECTION_FIELDS_ALL + PREFLECTION_FIELDS_LEGACY)
MODE_PART_NAMES = {
    "reflection": REFLECTION_PART_NAMES,
    "preflection": PREFLECTION_PART_NAMES,
}


_VIRTUE_VERB = (
    r"glorif|endors|sensationalis|sensationaliz|normalis|normaliz|promot|celebrat|exploit|"
    r"justif|encourag|trivialis|trivializ|condon|present|sanitis|sanitiz|instruct"
)
_EMPTY_CREDIT_RES = (
    # virtue by negation: "without glorifying the act", "rather than sensationalising it"
    re.compile(
        r"\b(?:without|avoids?|avoiding|rather than|instead of|free from|refrains? from)"
        r"\s+(?:\w+\s+){0,3}?(?:" + _VIRTUE_VERB + r")",
        re.IGNORECASE,
    ),
    # virtue by adverb: "effectively critiques", "responsibly clarifies"
    re.compile(
        r"\b(?:effectively|critically|actively|appropriately|responsibly|carefully|"
        r"successfully|properly)\s+\w+",
        re.IGNORECASE,
    ),
    # virtue by equilibrium: "balances reporting interest with caution"
    re.compile(
        r"(?<!fails to )(?<!requires )(?<!should )(?<!must )"
        r"\b(?:balanc\w+|maintain\w+)\s+(?:\w+\s+){0,3}?"
        r"(?:with|between|distance|interest|restraint|caution|neutrality)\b",
        re.IGNORECASE,
    ),
)


def find_empty_credit(text: str) -> list[str]:
    """Return clauses that credit a general virtue instead of naming a specific choice.

    "Without glorifying the act" is true of nearly any passage, so it asserts almost
    nothing. Three prompt revisions failed to stop the model writing these; detecting
    them and quoting them back is what works, because a quoted clause is specific in
    the way a standing rule is not.
    """
    out: list[str] = []
    for pattern in _EMPTY_CREDIT_RES:
        for m in pattern.finditer(text):
            start = text.rfind(".", 0, m.start()) + 1
            end = text.find(".", m.end())
            clause = text[start : end if end != -1 else len(text)].strip()
            if clause and clause not in out:
                out.append(clause)
    return out


_SUMMARY_CHUNK_RE = re.compile(r"\[(\d+\.\d+)\]\s*([^:\n]{1,80}?)\s*:")


def canonicalise_summary_titles(text: str, titles: dict[str, str]) -> str:
    """Replace each ``[X.Y] Title:`` in a charter_summary with the charter's own title.

    The generator abbreviates section names — "Mental Health" for "Mental Health
    and Self-Harm" — dropping the clause the citation was made for. There is
    exactly one correct title per section, so this is a repair, not a check.
    """

    def _fix(m: re.Match) -> str:
        want = titles.get(m.group(1))
        return m.group(0) if want is None else f"[{m.group(1)}] {want}:"

    return _SUMMARY_CHUNK_RE.sub(_fix, text)


def detect_mode_voices(payload: dict, mode: str) -> tuple[str, ...]:
    """Return voice/field keys in *payload* that belong to *mode*, sorted.

    *payload* can be a judgment dict or a review `scores` dict. The preflection
    mode spans three schema generations (legacy 2-voice, 4-field, current
    2-field), so old and new payloads both resolve to their natural key set.
    """
    part_names = MODE_PART_NAMES.get(mode, frozenset())
    return tuple(sorted(k for k in payload.keys() if k in part_names))


# Reflection-mode guard: model produced preflection_* keys when we asked for
# reflection_*. No inverse entry for the new preflection schema — its field
# names (charter_summary / judgemental) can't collide with reflection voices,
# so no remap is needed.
_MODE_REMAP = {
    ("reflection_1p", "reflection_3p"): {
        "preflection_1p": "reflection_1p",
        "preflection_3p": "reflection_3p",
    },
    ("reflection_1p",): {
        "preflection_1p": "reflection_1p",
    },
}


def _fix_wrong_mode_keys(parsed: dict, required_fields: set[str]) -> None:
    """Remap keys when the model used the wrong mode's field names."""
    for expected_pair, remap in _MODE_REMAP.items():
        if all(f in required_fields for f in expected_pair):
            # This is the expected mode — check if wrong keys are present
            for wrong_key, right_key in remap.items():
                if wrong_key in parsed and right_key not in parsed:
                    parsed[right_key] = parsed.pop(wrong_key)


# Schema keys that almost never appear as natural English — if one of these
# turns up inside a field value, it's a JSON-key leak, not legitimate prose.
# Caught with a word-boundary match (treating `_` as a word char).
_LEAK_UNQUOTED_KEYS = (
    "reflection_1p",
    "reflection_3p",
    "preflection_1p",
    "preflection_3p",
    "charter_summary",
)
_LEAK_UNQUOTED_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:"
    + "|".join(re.escape(k) for k in _LEAK_UNQUOTED_KEYS)
    + r")(?![A-Za-z0-9_])"
)

# Any schema key wrapped in double quotes, e.g. `"analysis"` or `"neutral":`.
# Catches concatenated-JSON leaks for the prose-friendly keys (analysis,
# neutral, judgemental, idealisation) without false-positiving on bare words.
_LEAK_QUOTED_RE = re.compile(
    r'"(?:' + "|".join(re.escape(k) for k in GEN_TEXT_FIELDS) + r')"'
)


def _assert_no_key_leakage(parsed: dict, required_fields: set[str]) -> None:
    """Raise if a field value contains an emitted JSON key string.

    The charter.scale generator catches the AssertionError and retries the doc
    (see ``pipeline/charter/scale/generate.py``).  ``analysis`` is exempt — it's
    a freeform scratchpad and may legitimately discuss the schema.
    """
    fields_to_check = (required_fields - {"analysis"}) & set(GEN_TEXT_FIELDS)
    for field in fields_to_check:
        val = parsed.get(field)
        if not isinstance(val, str) or not val:
            continue
        m = _LEAK_UNQUOTED_RE.search(val) or _LEAK_QUOTED_RE.search(val)
        assert m is None, (
            f"JSON key leakage in field '{field}': matched '{m.group(0)}'. "
            f"Value preview: {val[:200]!r}"
        )


def parse_generation(
    raw: str,
    required_fields: set[str] | None = None,
) -> dict:
    """Parse generator JSON output into structured fields.

    Extracts JSON from response, handling prose before/after JSON and code fences.
    Normalises known alias variants to the canonical schema. The default
    *required_fields* covers the current preflection (2 fields) +
    reflection (2 voices) schema; pass a subset to parse a single-mode response.
    """
    parsed = extract_json(raw)
    # Unwrap single-key wrappers (e.g. {"key": {...actual...}})
    if len(parsed) == 1:
        sole_value = next(iter(parsed.values()))
        if isinstance(sole_value, dict):
            parsed = sole_value
    # Apply aliases iteratively until stable (some aliases chain)
    changed = True
    while changed:
        changed = False
        for variant, canonical in FIELD_ALIASES.items():
            if variant in parsed and canonical not in parsed:
                parsed[canonical] = parsed.pop(variant)
                changed = True
    if required_fields is None:
        required_fields = {
            "analysis",
            *PREFLECTION_FIELDS_CURRENT,
            "reflection_1p",
            "reflection_3p",
        }
    # Handle wrong-mode keys: model produced reflection_* when asked for
    # preflection_* (or vice versa). Remap if the required fields tell us
    # the expected mode and the wrong-mode keys are present.
    if required_fields:
        _fix_wrong_mode_keys(parsed, required_fields)

    missing = required_fields - set(parsed.keys())
    assert not missing, (
        f"Missing fields in generation: {missing}. "
        f"Got keys: {list(parsed.keys())}. Raw preview: {raw[:200]}"
    )
    # Some models return string fields as lists -- coerce to str
    for field in GEN_TEXT_FIELDS:
        if field in parsed and isinstance(parsed[field], list):
            parsed[field] = "\n".join(str(x) for x in parsed[field])
    _assert_no_key_leakage(parsed, required_fields)
    return parsed
