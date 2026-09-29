#!/bin/bash
#SBATCH --job-name=mrd-verify-sglang
#SBATCH -A ab023
#SBATCH -p debug
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --exclusive
#SBATCH -o /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/logs/%x-%j.out
#SBATCH -e /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/logs/%x-%j.out

set -euo pipefail
export HF_TOKEN=$(cat ~/.hf_token)

srun --environment=/capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/mrd-sglang.toml bash -c '
set -e
nvidia-smi --query-gpu=name,memory.total --format=csv
python3 -c "import sglang, torch; print(\"sglang\", sglang.__version__, \"torch\", torch.__version__, \"cuda\", torch.version.cuda, \"gpus\", torch.cuda.device_count())"
python3 -c "from huggingface_hub import snapshot_download; print(snapshot_download(\"Qwen/Qwen3.5-35B-A3B-FP8\", local_dir=\"/iopsstor/scratch/cscs/xccyn/mrd-local-qwen/hf_models/Qwen3.5-35B-A3B-FP8\"))"
du -sh /iopsstor/scratch/cscs/xccyn/mrd-local-qwen/hf_models/Qwen3.5-35B-A3B-FP8
'
echo VERIFY_DONE
