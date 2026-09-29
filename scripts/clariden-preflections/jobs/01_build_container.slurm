#!/bin/bash
#SBATCH --job-name=mrd-build-sglang
#SBATCH -A ab023
#SBATCH -p debug
#SBATCH --time=01:30:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=256G
#SBATCH -o /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/logs/%x-%j.out
#SBATCH -e /capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/logs/%x-%j.out

set -euo pipefail

RECIPE_DIR="/capstor/store/cscs/swissai/ab023/xccyn/spsd/model-raising-data/scripts/clariden-preflections/sglang-container"
IMAGE_TAG="mrd-sglang-v0.5.19-cu129"
SQSH_IMAGE="/iopsstor/scratch/cscs/xccyn/containers/${IMAGE_TAG}.sqsh"

srun bash -lc "
  set -e
  cd \"$RECIPE_DIR\"
  podman build -t \"$IMAGE_TAG\" .
  enroot import -x mount -o \"$SQSH_IMAGE\" podman://\"$IMAGE_TAG\"
" || echo "srun exited non-zero (enroot often does after writing the image); checking artifact"

ls -la "$SQSH_IMAGE"
echo "BUILD_DONE $(du -h "$SQSH_IMAGE" | cut -f1)"
