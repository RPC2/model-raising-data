"""Compare the thinking and no-thinking preflection runs over the same documents.

Reports citation behaviour, span locatability (a quote the source does not hold),
and insertion coverage, then dumps paired outputs for reading.
"""

import argparse
import json
import random
from pathlib import Path

import pyarrow.parquet as pq

from pipeline.generation import _flatten, _quoted_spans, _section_refs, _split_sentences, _SPAN_TRIM
from pipeline.tokenizer import compute_reflection_point_end

BASE = Path("/iopsstor/scratch/cscs/xccyn/mrd-local-qwen")
MODES = {"thinking": "bench", "no_thinking": "bench_nothink"}


def clipped(text, token_length):
    """The exact span the generator saw."""
    end, _ = compute_reflection_point_end(text, random.Random(), max_tokens=token_length)
    return text[:end]


def unlocatable_spans(judgemental, source):
    """Quoted spans the source does not contain, by the same matching the anchors use."""
    flat = _flatten(source)
    missing = []
    for sentence in _split_sentences(judgemental):
        for span in _quoted_spans(sentence):
            probe = _flatten(span).strip(_SPAN_TRIM)
            if probe and flat.find(probe) < 0:
                missing.append(span)
    return missing


def main():
    """Print per-mode stats over the first *n* rows and dump paired samples."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100)
    args = ap.parse_args()

    table = pq.read_table(BASE / "bench_sidecar.parquet").slice(0, args.n).to_pylist()
    runs = {}
    for mode, d in MODES.items():
        rows = [json.loads(l) for l in (BASE / d / "preflections/00000/results.jsonl").open() if l.strip()]
        runs[mode] = {r["global_row_idx"]: r for r in rows}

    stats = {m: {"cited": 0, "sections": 0, "chars": 0, "missing": 0, "rows_missing": 0, "positioned": 0} for m in MODES}
    both_cite = agree = 0
    same_sections = 0
    dump = []
    for idx, row in enumerate(table):
        source = clipped(row["text"], row["token_length"])
        cites = {}
        for mode in MODES:
            r = runs[mode][idx]
            sections = sorted(set(json.loads(r["charter_preflection"])))
            cites[mode] = sections
            s = stats[mode]
            s["cited"] += bool(sections)
            s["sections"] += len(sections)
            s["chars"] += len(r["judgemental"])
            s["positioned"] += r["preflection_position"] is not None
            missing = unlocatable_spans(r["judgemental"], source)
            s["missing"] += len(missing)
            s["rows_missing"] += bool(missing)
            if missing:
                print(f"  UNLOCATABLE row {idx} [{mode}]: {missing}")
        agree += bool(cites["thinking"]) == bool(cites["no_thinking"])
        if cites["thinking"] and cites["no_thinking"]:
            both_cite += 1
            same_sections += cites["thinking"] == cites["no_thinking"]
        dump.append({"idx": idx, "doc_id": row["doc_id"], "safety_score": row["safety_score"],
                     "source": source, **{m: runs[m][idx] for m in MODES}})

    print(f"\n=== {args.n} documents, same text in both runs ===")
    for mode, s in stats.items():
        n = args.n
        print(f"{mode:<12} cited {s['cited']:>3}/{n}  sections/citing-doc {s['sections'] / max(s['cited'], 1):.2f}  "
              f"judgemental {s['chars'] / n:.0f} chars  position set {s['positioned']:>3}/{n}  "
              f"unlocatable quotes {s['missing']} in {s['rows_missing']} rows")
    print(f"cite/no-cite agreement {agree}/{args.n}; identical section sets {same_sections}/{both_cite} of the both-cite rows")
    (BASE / "thinking_pairs.json").write_text(json.dumps(dump))


if __name__ == "__main__":
    main()
