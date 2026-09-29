"""Write a small sidecar-schema parquet from the Dolma3 annotation sample for local generation tests."""

import argparse
import itertools
import os
import sys

import pyarrow as pa
import pyarrow.parquet as pq
from datasets import load_dataset

from pipeline.data import DATASET
from pipeline.storage import compute_item_id
from pipeline.tokenizer import _encode

MAX_CONTENT_TOKENS = 1920  # annotated.bin content cap; sidecar token_length never exceeds it


def main():
    """Stream *n* shuffled rows and write doc_id/text/token_length/safety_score/is_bad."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    ds = load_dataset(DATASET, split="train", streaming=True).shuffle(seed=args.seed, buffer_size=10_000)
    rows = list(itertools.islice(ds, args.n))
    assert len(rows) == args.n
    table = pa.table({
        "doc_id": [compute_item_id(r["text"]) for r in rows],
        "text": pa.array([r["text"] for r in rows], type=pa.large_string()),
        "token_length": pa.array([min(len(_encode(r["text"]).ids), MAX_CONTENT_TOKENS) for r in rows], type=pa.int32()),
        "safety_score": pa.array([float(r["safety_score"]) for r in rows], type=pa.float32()),
        "is_bad": [int(r["safety_score"]) >= 3 for r in rows],
    })
    pq.write_table(table, args.out)
    print(table.select(["doc_id", "token_length", "safety_score"]).to_pandas().to_string())


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    # datasets' streaming worker threads hang interpreter shutdown after the parquet is written.
    os._exit(0)
