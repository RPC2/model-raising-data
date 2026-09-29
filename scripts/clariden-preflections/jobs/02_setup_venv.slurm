#!/bin/bash
#SBATCH --job-name=mrd-setup-venv
#SBATCH -A ab023
#SBATCH -p debug
#SBATCH --time=00:45:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH -o /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/logs/%x-%j.out
#SBATCH -e /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/logs/%x-%j.out

set -euo pipefail
export HF_TOKEN=$(cat ~/.hf_token)
export HF_HOME=/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/hf_cache
export UV_CACHE_DIR=/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/cache/uv

command -v uv || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv --version

cd /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data
uv sync
uv run python -c "import pipeline.charter.scale.generate, pipeline.charter.scale.__main__, datatrove, openai; print('IMPORT_OK')"
uv run pytest tests/test_charter_scale_runs.py tests/test_charter_scale_reader.py -q
uv run python /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/make_mini_sidecar.py --n 20 --out /iopsstor/scratch/cscs/xccyn/mrd-local-qwen/mini_sidecar.parquet
echo SETUP_DONE
