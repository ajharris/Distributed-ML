#!/usr/bin/env bash
set -e

ENV_NAME=scalable-ct

micromamba env create -f environment.yml -n "$ENV_NAME" || true
eval "$(micromamba shell hook -s bash)"
micromamba activate "$ENV_NAME"

uv pip install "monai>=1.3,<1.5" "torchmetrics>=1.3,<1.6" "einops>=0.7,<0.9"
pip install --no-build-isolation "pyradiomics==3.0.1"
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
