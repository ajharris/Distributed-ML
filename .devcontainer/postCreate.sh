#!/usr/bin/env bash
set -euo pipefail

ENV_NAME="scalable-ct"

echo "[postCreate] Initializing micromamba shell hook"
eval "$(micromamba shell hook -s bash)"

echo "[postCreate] Creating env '${ENV_NAME}' from environment.yml (idempotent)"
micromamba env create -n "${ENV_NAME}" -f environment.yml || true

echo "[postCreate] Activating env"
micromamba activate "${ENV_NAME}"

echo "[postCreate] Installing pip-based packages (monai, pyradiomics, torch, etc.)"
# pip install --no-build-isolation "pyradiomics==3.0.1"
pip install "monai>=1.3,<1.5" "torchmetrics>=1.3,<1.6" "einops>=0.7,<0.9"

# CPU PyTorch for Codespaces (Linux, no GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Optional: create a venv symlink so VS Code picks it up easily
python -m venv /workspace/.venv
source /workspace/.venv/bin/activate
pip install ipykernel
python -m ipykernel install --user --name "${ENV_NAME}" --display-name "Python (${ENV_NAME})"

echo "[postCreate] Done."
