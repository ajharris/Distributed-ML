# Scalable Machine Learning for Large-Scale CT Phenotyping of COPD

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&repo=Distributed-ML)

[![Open in Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/<your-username>/Distributed-ML/blob/main/notebooks/pipeline-demos/README.ipynb)

This repository contains the code, experiments, and documentation for a research project exploring scalable machine learning methods for large-scale lung CT analysis, with a focus on chronic obstructive pulmonary disease (COPD). The project integrates medical imaging, radiomics, deep learning, distributed computing, and reproducible research practices.

The central objective is to build a fully scalable, cloud-compatible pipeline for CT preprocessing, feature extraction, and phenotypic modeling using large public datasets such as NLST, COPDGene (subset), and LIDC-IDRI. The project leverages Dask for distributed computation across thousands of CT volumes to enable production-scale processing and analysis.

---

## Project Goals

1. **Develop a reproducible, distributed CT processing pipeline**
   - Lung segmentation, resampling, HU normalization  
   - Computation of radiomic features and 3D deep-learning embeddings  
   - Distributed execution using Dask (CPU clusters or cloud)

2. **Build phenotyping and predictive models**
   - Unsupervised clustering of lung disease patterns  
   - Supervised prediction of disease severity and progression  
   - Comparative analysis of radiomics vs. learned embeddings

3. **Evaluate scalability and performance**
   - Benchmarks of Dask-based preprocessing and inference  
   - Throughput, memory, and efficiency analyses  
   - Pipeline design suitable for research or production deployment

4. **Enable transparent, reproducible medical imaging research**
   - Modular, configuration-driven experiment design  
   - Clear I/O schemas and diagnostics  
   - Extensible framework for additional imaging datasets

---

## Repository Structure

```
.
├── README.md                → Project overview (this file)
├── environment.yml          → Conda environment for reproducibility
├── requirements-colab.txt   → Colab-compatible dependencies
│
├── config/                  → Experiment and pipeline configuration files
│   └── README.md
│
├── data/                    → Local data caching (ignored in .gitignore)
│   └── README.md
│
├── docs/
│   ├── methodology.md       → Methods and preprocessing details
│   ├── references.md        → Literature and dataset references
│   └── results.md           → Experiments and benchmark results
│
├── notebooks/
│   ├── README.md
│   ├── exploration/         → Exploratory analysis notebooks
│   ├── modeling/            → Model development notebooks
│   └── pipeline-demos/      → End-to-end pipeline demonstrations
│
├── scripts/
│   └── bootstrap_local.sh   → Local setup helper
│
├── src/
│   ├── README.md
│   ├── ingest/              → Dataset loaders and metadata utilities
│   ├── preprocess/          → Preprocessing (segmentation, resampling, norms)
│   ├── features/            → Radiomics and deep embedding extraction
│   ├── train/               → Training loops and model orchestration
│   ├── eval/                → Metrics, validation, visualization tools
│   └── utils/               → Shared utilities
│       ├── logger.py        → Unified logging utilities
│       ├── io.py            → NIfTI/Zarr/HDF5 read/write helpers
│       └── dask_cluster.py  → Local cluster utilities for Dask
│
└── tests/
    ├── README.md
    ├── conftest.py          → Ensures consistent import path resolution
    └── utils/               → Unit tests for utility modules
```

---

## Utilities (New)

The utilities module (`src/utils/`) was added to support all parts of the pipeline with consistent and reusable infrastructure.

### `logger.py`
- Console + rotating file logging  
- Optional JSON structured logs  
- Centralized formatting

### `io.py`
- Unified helpers for NIfTI, Zarr, and HDF5  
- Symmetrical load/save APIs  
- Designed for 3D CT data

### `dask_cluster.py`
- Helper for starting a local Dask cluster during development  
- Placeholder for future cloud cluster implementations

---

## Work Completed in `add-shared-utilities-and-logging-setup` Branch

### ✔ Added core utilities  
### ✔ Implemented corresponding unit tests  
### ✔ Added README files across utilities/tests  
### ✔ Added `conftest.py` to ensure import stability  
### ✔ Updated root documentation

---

## Getting Started

### Create the Conda environment
```
conda env create -f environment.yml
conda activate scalable-ct
```

### Configure dataset paths
Edit `config/paths.yml`.

### Run tests
```
pytest
```

---

## License
This project is released under MIT License.
