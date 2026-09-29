"""Assemble the preflected-document corpus for the viewer artifact.

One record per document: the text the generator saw, the preflection it wrote,
and the character offset the annotation is inserted at.
"""

import argparse
import json
import random
from pathlib import Path

import pyarrow.parquet as pq

from pipeline.generation import preflection_insertion_point
from pipeline.tokenizer import char_offset_to_token_index, compute_reflection_point_end

BASE = Path("/iopsstor/scratch/cscs/xccyn/mrd-local-qwen")


def main():
    """Write corpus.json for the first *n* rows of the thinking-on bench run."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--run-dir", default="bench")
    args = ap.parse_args()

    table = pq.read_table(BASE / "bench_sidecar.parquet").slice(0, args.n).to_pylist()
    results = {}
    for line in (BASE / args.run_dir / "preflections/00000/results.jsonl").open():
        if line.strip():
            r = json.loads(line)
            results[r["global_row_idx"]] = r

    out = []
    for idx, row in enumerate(table):
        end, _ = compute_reflection_point_end(row["text"], random.Random(), max_tokens=row["token_length"])
        text = row["text"][:end]
        r = results[idx]
        position = preflection_insertion_point(r["judgemental"], text)
        out.append({
            "i": idx,
            "id": row["doc_id"],
            "safety": row["safety_score"],
            "tok": row["token_length"],
            "text": text,
            "summary": r["charter_summary"],
            "judgemental": r["judgemental"],
            "cites": json.loads(r["charter_preflection"]),
            "pos": position,
            "tokidx": None if position is None else char_offset_to_token_index(text, position),
            "out_tok": r["output_tokens"],
        })

    path = BASE / "corpus.json"
    path.write_text(json.dumps(out, separators=(",", ":")))
    cited = sum(1 for r in out if r["cites"])
    placed = sum(1 for r in out if r["pos"] is not None)
    chars = sum(len(r["text"]) for r in out)
    print(f"docs {len(out)}  cited {cited}  placed {placed}  text {chars/1e6:.2f} MB  file {path.stat().st_size/1e6:.2f} MB")


if __name__ == "__main__":
    main()
