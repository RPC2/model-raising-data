"""Rebuild the comparison page dataset with the thinking-off run as a third backend."""

import json
from pathlib import Path

from pipeline.generation import preflection_insertion_point

BASE = Path("/iopsstor/scratch/cscs/xccyn/mrd-local-qwen")
RUNS = ("openrouter", "local", "local_nothink")
KEEP = ("charter_summary", "judgemental", "charter_preflection", "preflection_position",
        "old_preflection_position", "input_tokens", "output_tokens", "reasoning_tokens")


def load(path):
    """Read a JSONL file into a dict keyed by global_row_idx."""
    return {json.loads(l)["global_row_idx"]: json.loads(l) for l in path.open() if l.strip()}


def main():
    """Write data.json holding the document plus one entry per backend."""
    docs = load(BASE / "docs_clipped.jsonl")
    runs = {n: load(BASE / n / "preflections/00000/results.jsonl") for n in RUNS}
    rows = []
    for idx in sorted(docs):
        doc = docs[idx]
        entry = {"idx": idx, "text": doc["clipped_text"],
                 **{k: doc[k] for k in ("doc_id", "safety_score", "token_length")}}
        for name, run in runs.items():
            r = dict(run[idx])
            r["old_preflection_position"] = r["preflection_position"]
            r["preflection_position"] = preflection_insertion_point(r["judgemental"], doc["clipped_text"])
            entry[name] = {k: r[k] for k in KEEP}
        rows.append(entry)
    Path("/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/data_3runs.json").write_text(json.dumps(rows))
    print("rows", len(rows))


if __name__ == "__main__":
    main()
