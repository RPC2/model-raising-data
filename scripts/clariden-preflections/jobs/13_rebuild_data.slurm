#!/bin/bash
#SBATCH --job-name=mrd-rebuild-data
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
uv run python /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/rebuild_data.py
