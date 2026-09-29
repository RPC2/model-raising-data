"""Recompute preflection_position for both backends' results under the sentence-snapping rule.

Reports how far each position moves and whether the old one split a sentence, then
writes the page dataset with both the old and the new offsets.
"""

import json
from pathlib import Path

from pipeline.generation import preflection_insertion_point
from pipeline.tokenizer import char_offset_to_token_index

BASE = Path("/iopsstor/scratch/cscs/xccyn/mrd-local-qwen")


def load(path):
    """Read a JSONL file into a dict keyed by global_row_idx."""
    return {json.loads(l)["global_row_idx"]: json.loads(l) for l in path.open() if l.strip()}


def main():
    """Rewrite data.json with snapped positions and print a per-row report."""
    docs = load(BASE / "docs_clipped.jsonl")
    runs = {name: load(BASE / name / "preflections/00000/results.jsonl") for name in ("openrouter", "local")}
    rows = []
    for idx in sorted(docs):
        doc = docs[idx]
        text = doc["clipped_text"]
        entry = {k: doc[k] for k in ("doc_id", "safety_score", "token_length")}
        entry["idx"] = idx
        entry["text"] = text
        for name, run in runs.items():
            r = dict(run[idx])
            old = r["preflection_position"]
            new = preflection_insertion_point(r["judgemental"], text)
            r["old_preflection_position"] = old
            r["preflection_position"] = new
            r["preflection_token_index"] = None if new is None else char_offset_to_token_index(text, new)
            r["split_a_sentence"] = old is not None and new is not None and old != new
            entry[name] = {k: r[k] for k in (
                "charter_summary", "judgemental", "charter_preflection", "preflection_position",
                "old_preflection_position", "split_a_sentence", "input_tokens", "output_tokens", "reasoning_tokens")}
            if old is not None:
                print(f"row {idx:>2} {name:<10} {old:>5} -> {new:<5} moved {old - new:>4}  |{text[new:new + 60]!r}")
        rows.append(entry)
    (BASE / "data_snapped.json").write_text(json.dumps(rows))
    moved = sum(1 for e in rows for n in runs if e[n]["split_a_sentence"])
    total = sum(1 for e in rows for n in runs if e[n]["old_preflection_position"] is not None)
    print(f"SNAP_DONE moved {moved} of {total} positioned rows")


if __name__ == "__main__":
    main()
