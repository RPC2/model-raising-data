#!/bin/bash
#SBATCH --job-name=mrd-snap-positions
#SBATCH -A ab023
#SBATCH -p debug
#SBATCH --time=00:20:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH -o /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/logs/%x-%j.out
#SBATCH -e /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/logs/%x-%j.out
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
export HF_HOME=/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/hf_cache UV_CACHE_DIR=/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/cache/uv
cd /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data
uv run pytest tests/test_preflection_anchors.py tests/test_charter_scale_runs.py tests/test_charter_scale_merge.py -q
uv run python /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/recompute_positions.py
