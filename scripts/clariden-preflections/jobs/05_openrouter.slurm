#!/bin/bash
#SBATCH --job-name=mrd-openrouter
#SBATCH -A ab023
#SBATCH -p debug
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH -o /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/logs/%x-%j.out
#SBATCH -e /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/logs/%x-%j.out

set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
export HF_HOME=/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/hf_cache
export UV_CACHE_DIR=/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/cache/uv
export SGLANG_ENDPOINT=https://openrouter.ai/api/v1
export SGLANG_API_KEY=$(cat ~/.sdsp_openrouter_api_key)
cd /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data
uv run python /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/run_openrouter.py \
  $(cat /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/overrides.txt) \
  charter.scale.output_dir=/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/openrouter
echo OPENROUTER_DONE
