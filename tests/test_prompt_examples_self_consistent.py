"""The worked examples inside a generator prompt must obey that prompt's own rules.

A worked example outweighs an instruction: the `judgemental` in the v9
preflection example credited the text with what it avoided ("instead of
emphasising the theft as spectacle") while the surrounding prose banned
exactly that, and the generated run reproduced the example rather than the
rule. A prompt edit that leaves an example teaching the opposite should fail
here instead of in a $0.90 generation run.

`find_empty_credit` alone would not have caught that clause — it whitelists
harm verbs to stay precise on generated text, and "emphasising" is a fault
word elsewhere ("without emphasising legal authorization"). Worked examples
are few and hand-written, so they carry the stricter rule: no crediting by
negation at all.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from pipeline.config import load_config, parse_charter_titles
from pipeline.generation import (
    PREFLECTION_FIELDS_ALL,
    PREFLECTION_FIELDS_CURRENT,
    find_empty_credit,
)

PROMPT_DIR = Path("final_prompts")
_JSON_BLOCK_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)
_CHUNK_RE = re.compile(r"\[(\d+\.\d+)\]\s*([^:\n]{1,80}?)\s*:")


def _examples() -> list[tuple[str, dict]]:
    """Worked examples written for the current two-field schema.

    Superseded prompts (v6, v8) are four-field frozen provenance records and
    are skipped: their examples answer a request the pipeline no longer makes.
    """
    found = []
    for path in sorted(PROMPT_DIR.glob("*/generator_preflection_*.md")):
        for block in _JSON_BLOCK_RE.findall(path.read_text(encoding="utf-8")):
            payload = json.loads(block)
            if all(f in payload for f in PREFLECTION_FIELDS_CURRENT) and not (
                set(payload) & set(PREFLECTION_FIELDS_ALL) - set(PREFLECTION_FIELDS_CURRENT)
            ):
                found.append((f"{path.name}:{payload['charter_summary'][:40]}", payload))
    return found


EXAMPLES = _examples()


def test_examples_exist() -> None:
    """A silent glob failure would make every check below vacuous."""
    assert EXAMPLES, f"no current-schema worked examples under {PROMPT_DIR}"


@pytest.mark.parametrize("name,payload", EXAMPLES, ids=lambda x: x if isinstance(x, str) else "")
def test_example_judgemental_has_no_empty_credit(name: str, payload: dict) -> None:
    """The example must not demonstrate the construction the prompt forbids."""
    clauses = find_empty_credit(payload["judgemental"])
    assert not clauses, f"{name}: worked example credits an absence: {clauses}"


_CREDIT_BY_NEGATION_RE = re.compile(r"\b(?:rather than|instead of)\b", re.IGNORECASE)


@pytest.mark.parametrize("name,payload", EXAMPLES, ids=lambda x: x if isinstance(x, str) else "")
def test_example_judgemental_credits_nothing_by_negation(name: str, payload: dict) -> None:
    """An example has no reason to say what the text refrained from doing."""
    hit = _CREDIT_BY_NEGATION_RE.search(payload["judgemental"])
    assert hit is None, f"{name}: worked example says what the text did not do: {hit.group(0)!r}"


@pytest.mark.parametrize("name,payload", EXAMPLES, ids=lambda x: x if isinstance(x, str) else "")
def test_example_summary_titles_are_canonical(name: str, payload: dict) -> None:
    """Section titles in the example must match the charter exactly."""
    titles = parse_charter_titles(
        Path(load_config([]).charter_path).read_text(encoding="utf-8")
    )
    for sid, title in _CHUNK_RE.findall(payload["charter_summary"]):
        assert titles.get(sid) == title, f"{name}: [{sid}] titled {title!r}, charter says {titles.get(sid)!r}"


@pytest.mark.parametrize("name,payload", EXAMPLES, ids=lambda x: x if isinstance(x, str) else "")
def test_example_fields_cite_the_same_sections(name: str, payload: dict) -> None:
    """The prompt requires one citation set across both fields; the example must show it."""
    sets = {f: set(re.findall(r"(\d\.\d+)", payload[f])) for f in PREFLECTION_FIELDS_CURRENT}
    assert len(set(map(frozenset, sets.values()))) == 1, f"{name}: citation sets differ: {sets}"


def test_scale_preflection_prompt_matches_the_current_schema() -> None:
    """charter.scale must run a prompt written for the fields the code asks for.

    `generator_preflection_v8.md` stayed configured here after the schema was cut
    to two fields, so a scale run would have used a four-field prompt to fill a
    two-field request.
    """
    cfg = load_config([])
    path = PROMPT_DIR / cfg.charter.scale.generator_alias / cfg.charter.scale.preflection_prompt
    body = path.read_text(encoding="utf-8")
    superseded = [f for f in ("neutral", "idealisation") if f'"{f}"' in body]
    assert not superseded, f"{path} still specifies dropped fields: {superseded}"
