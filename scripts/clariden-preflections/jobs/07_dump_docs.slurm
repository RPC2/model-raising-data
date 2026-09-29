#!/bin/bash
#SBATCH --job-name=mrd-dump-docs
#SBATCH -A ab023
#SBATCH -p debug
#SBATCH --time=00:10:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH -o /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/logs/%x-%j.out
#SBATCH -e /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/logs/%x-%j.out
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
export HF_HOME=/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/hf_cache UV_CACHE_DIR=/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/cache/uv
cd /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data
uv run python - <<'PY'
import json, random
import pyarrow.parquet as pq
from pipeline.tokenizer import compute_reflection_point_end
t = pq.read_table("/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/mini_sidecar.parquet").to_pylist()
with open("/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/docs_clipped.jsonl", "w") as f:
    for i, r in enumerate(t):
        end, _ = compute_reflection_point_end(r["text"], random.Random(), max_tokens=r["token_length"])
        f.write(json.dumps({"global_row_idx": i, "doc_id": r["doc_id"], "safety_score": r["safety_score"], "token_length": r["token_length"], "clipped_text": r["text"][:end]}) + "\n")
print("DUMP_DONE")
PY
