# Scalable Machine Learning for Large-Scale CT Phenotyping of COPD

This repository contains the code, experiments, and documentation for a research project exploring scalable machine learning methods for large-scale lung CT analysis, with a focus on chronic obstructive pulmonary disease (COPD). The project integrates medical imaging, radiomics, deep learning, distributed computing, and reproducible research practices.

The central objective is to build a fully scalable, cloud-compatible pipeline for CT preprocessing, feature extraction, and phenotypic modeling using large public datasets such as NLST, COPDGene (subset), and LIDC-IDRI. The project leverages Dask for distributed computation across thousands of CT volumes to enable production-scale processing and analysis.

---

## Project Goals

1. **Develop a reproducible, distributed CT processing pipeline**

   * Lung segmentation, resampling, HU normalization
   * Computation of radiomic features and 3D deep-learning embeddings
   * Distributed execution using Dask (CPU clusters or cloud)

2. **Build phenotyping and predictive models**

   * Unsupervised clustering of lung disease patterns (e.g., emphysema subtypes)
   * Supervised modeling of disease severity and progression (e.g., FEV1, GOLD stage)
   * Comparative analysis of radiomics vs. learned embeddings

3. **Evaluate scalability and performance**

   * Benchmarks of Dask-based preprocessing and inference
   * Memory, throughput, and compute efficiency analyses
   * Pipeline design suitable for production or research deployment

4. **Enable transparent, reproducible medical imaging research**

   * Clear data schemas and modular pipeline design
   * Configuration-driven experimentation
   * Extensible framework for integration with additional imaging datasets

---

## Repository Structure

```text
root/
│
├── README.md                  → Project overview (this file)
├── environment.yml            → Conda/micromamba base environment (Python 3.9)
├── requirements-colab.txt     → Lightweight pip environment for Google Colab
├── config/                    → YAML configs for experiments and pipelines
├── data/                      → Local data caching (may be git-ignored)
│   └── README.md
├── docs/
│   ├── methodology.md         → Full methods description
│   ├── results.md             → Experimental results and benchmarks
│   └── references.md          → Cited papers, datasets, and tools
├── src/
│   ├── ingest/                → Dataset loaders and metadata utilities
│   ├── preprocess/            → Lung segmentation, normalization, resampling
│   ├── features/              → Radiomics and deep embedding extraction
│   ├── train/                 → Model training scripts (supervised/unsupervised)
│   ├── eval/                  → Metrics, visualization, explainability
│   └── utils/                 → Shared utilities (I/O, logging, Dask cluster mgmt)
├── notebooks/
│   ├── exploration/           → Preliminary analysis and EDA
│   ├── pipeline-demos/        → Demonstrations of Dask-scale workflows
│   └── modeling/              → Model development and evaluation notebooks
├── scripts/
│   └── bootstrap_local.sh     → Helper script for local environment setup
└── .devcontainer/
    ├── devcontainer.json      → GitHub Codespaces dev container config
    └── postCreate.sh          → Post-create hook to build the env in Codespaces
```

---

## Datasets

This project uses publicly available, large-scale CT datasets. Due to licensing restrictions, datasets are not stored in this repository. Instead, instructions for access and preprocessing are provided in `docs/methodology.md`.

Recommended datasets:

* **NLST (National Lung Screening Trial)**

  > > 20,000 lung CT scans with screening labels
  > > Available through NCI Imaging Data Commons.

* **COPDGene (subset via TCIA)**

  > CT scans of COPD patients with rich clinical metadata
  > Available on The Cancer Imaging Archive (TCIA).

* **LIDC-IDRI**

  > 1,018 CTs with lung nodule annotations; ideal for segmentation benchmarking
  > Available via TCIA.

Users must obtain necessary approvals for these datasets where required.

---

## Technical Highlights

* Distributed CT preprocessing using Dask
* Chunked and lazy-loading architectures for large 3D volumetric data
* Radiomics extraction via PyRadiomics
* 3D CNN embedding extraction (custom or pretrained)
* Reproducible experiment management with configuration files
* Cluster-ready design (local CPU clusters or cloud backends)

---

## Getting Started

### 1. Local development environment

You can work locally using either **micromamba** (recommended) or **conda**.

#### Option A: micromamba

```bash
micromamba create -n scalable-ct -f environment.yml
micromamba activate scalable-ct
```

#### Option B: conda

```bash
conda env create -f environment.yml
conda activate scalable-ct
```

After creating the base environment, install the deep-learning and radiomics extras via `pip`:

```bash
# Radiomics
pip install --no-build-isolation "pyradiomics==3.0.1"

# Deep learning stack (CPU by default; see notes below for GPU)
pip install "monai>=1.3,<1.5" "torchmetrics>=1.3,<1.6" "einops>=0.7,<0.9"

# PyTorch (CPU build)
pip install torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/cpu
```

> If you have a local GPU and a compatible CUDA toolkit, you can swap the `cpu` index URL above for an appropriate CUDA build from the PyTorch docs.

### 2. Configure dataset paths

Edit `config/paths.yml` to point to your local or cloud-based data storage.

### 3. Run the preprocessing pipeline

```bash
python -m src.preprocess.run --config config/preprocess/nlst.yaml
```

### 4. Extract features

```bash
python -m src.features.radiomics --config config/features/radiomics.yaml
python -m src.features.deep_embeddings --config config/features/embeddings.yaml
```

### 5. Train models

```bash
python -m src.train.cluster --config config/models/unsupervised.yaml
python -m src.train.supervised --config config/models/supervised.yaml
```

---

## Development environment (GitHub Codespaces)

This repository includes a preconfigured **dev container** for GitHub Codespaces.

To use it:

1. Open the **Distributed-ML** repository on GitHub.
2. Click **Code → Create codespace on main**.
3. Wait for the Codespace to build.

The devcontainer will:

* Use a `micromamba`-based image.
* Create the `scalable-ct` environment from `environment.yml`.
* Run `.devcontainer/postCreate.sh` to install PyRadiomics, MONAI, and PyTorch.

Once the Codespace is ready:

* Open a terminal; the environment should be activated or easily activatable.
* You can run tests and scripts directly, e.g.:

```bash
python -m pytest
```

or open the notebooks using the Jupyter integration in VS Code.

---

## Run on Google Colab (GPU)

For GPU-accelerated experiments, you can use **Google Colab** without installing conda/mamba.

1. Open a notebook from this repo in Colab (e.g., via the Colab badge in the README or by uploading the notebook).
2. At the top of the notebook, add and run the following cell:

```python
# Colab setup cell
!pip install -q -r "https://raw.githubusercontent.com/<your-username>/Distributed-ML/main/requirements-colab.txt"
```

3. In Colab, go to **Runtime → Change runtime type → GPU** to enable GPU acceleration.
4. Run the rest of the notebook as usual.

The `requirements-colab.txt` file is a lightweight pip environment that installs the core scientific, imaging, and deep-learning dependencies (PyTorch, MONAI, PyRadiomics, etc.) suitable for Colab.

---

## Intended Research Outcomes

* A scalable, open-source framework for CT-based COPD phenotyping
* Novel clusters or imaging-based phenotypes associated with clinical outcomes
* Comparative analysis of traditional radiomics and deep-learning features
* Performance benchmarks for distributed medical imaging pipelines

This project can serve as the foundation for a graduate research thesis, manuscript, or extended industrial R&D work.

---

## Citation

If you use material or code from this repository, please cite it appropriately (citation format will be added once publications are finalized).

---

## License

This project is released under the MIT License. See `LICENSE` for details.
