#!/bin/bash
#SBATCH --job-name=mrd-nothink-submit
#SBATCH -A ab023
#SBATCH -p normal
#SBATCH --time=00:20:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH -o /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/logs/%x-%j.out
#SBATCH -e /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/logs/%x-%j.out
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
export HF_HOME=/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/hf_cache UV_CACHE_DIR=/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/cache/uv
cd /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data
uv run python -m pipeline.charter.scale submit --run preflections \
  $(cat /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/overrides.txt) \
  charter.scale.output_dir=/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/local_nothink \
  charter.scale.thinking=false \
  "charter.scale.sglang.extra_args=--context-length 24576 --kv-cache-dtype bf16 --max-running-requests 512 --schedule-conservativeness 0.3 --cuda-graph-max-bs 1024 --mamba-ssm-dtype bfloat16 --mem-fraction-static 0.88 --mamba-full-memory-ratio 2.0 --attention-backend flashinfer --mm-attention-backend sdpa"
echo SUBMIT_DONE
