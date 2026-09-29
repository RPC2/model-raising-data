#!/bin/bash
#SBATCH --job-name=mrd-inputs-openrouter-submit
#SBATCH -A ab023
#SBATCH -p normal
#SBATCH --time=00:45:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH -o /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/logs/%x-%j.out
#SBATCH -e /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/logs/%x-%j.out

set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
export HF_TOKEN=$(cat ~/.hf_token)
export HF_HOME=/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/hf_cache
export UV_CACHE_DIR=/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/cache/uv
cd /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data

uv run python /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/make_mini_sidecar.py --n 20 --out /iopsstor/scratch/cscs/xccyn/mrd-local-qwen/mini_sidecar.parquet
uv run python -c "import pyarrow.parquet as pq; t = pq.read_table('/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/mini_sidecar.parquet'); assert t.num_rows == 20; assert max(t['token_length'].to_pylist()) <= 1920; print('SIDECAR_OK')"

SGLANG_ENDPOINT=https://openrouter.ai/api/v1 SGLANG_API_KEY=$(cat ~/.sdsp_openrouter_api_key) \
  uv run python /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/run_openrouter.py $(cat /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/overrides.txt) charter.scale.output_dir=/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/openrouter
echo OPENROUTER_DONE

uv run python -m pipeline.charter.scale submit --run preflections $(cat /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/overrides.txt) charter.scale.output_dir=/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/local
echo SUBMIT_DONE
