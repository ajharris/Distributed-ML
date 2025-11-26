# Scalable Machine Learning for Large-Scale CT Phenotyping of COPD

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&repo=Distributed-ML)

[![Open in Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/<your-username>/Distributed-ML/blob/main/notebooks/pipeline-demos/README.ipynb)

This repository contains the code, pipeline components, and documentation for a research project exploring scalable machine learning approaches for **large-scale lung CT phenotyping**, with a focus on **chronic obstructive pulmonary disease (COPD)**.  
The project integrates medical imaging, distributed computing, metadata standardization, and reproducible research practices designed to scale across large public datasets such as **NLST**, **COPDGene**, and **LIDC-IDRI**.

---

## Project Goals

### 1. Develop a reproducible, distributed CT processing pipeline

- Lung segmentation, voxel spacing normalization, and HU normalization  
- Radiomics and 3D deep-learning feature extraction  
- Distributed execution with Dask, cloud-compatible

### 2. Build phenotyping and predictive models

- Unsupervised clustering of structural lung patterns  
- Supervised prediction of COPD severity, progression, and risk factors  
- Benchmark classical radiomics vs deep embedding methods

### 3. Evaluate scalability and performance

- End-to-end throughput for thousands of scans  
- Distributed preprocessing benchmarks  
- Memory usage, parallel efficiency, and cluster tuning

### 4. Enable transparent, reproducible medical imaging research

- Unified ingestion schema across heterogeneous datasets  
- Well-documented pipeline with tests at every layer  
- Clear I/O formats (e.g., Parquet metadata, NIfTI/Zarr volumes)

---

## Current Status

- **Ingestion & metadata pipeline implemented** for NLST, COPDGene, LIDC-IDRI demo subsets.
- **Dataset-agnostic metadata schema** (`metadata_schema.py`).
- **Dataset-specific ingestion modules** (`*_ingest.py`).
- **Registry interface** (`DatasetRegistry`).
- **Demo raw metadata CSVs** in `data/raw_metadata/`.
- **Parquet outputs** in `data/metadata/`.
- **All tests currently passing.**

Run:

```
pytest
```

---

## CLI for Full Ingestion

```
python scripts/build_metadata.py   --nlst-csv data/raw_metadata/nlst_demo.csv   --copdgene-csv data/raw_metadata/copdgene_demo.csv   --lidc-csv data/raw_metadata/lidc_demo.csv   --output-dir data/metadata
```

---

## Repository Structure

(Full structure as in your provided tree.)

---

## Getting Started

```
conda env create -f environment.yml
conda activate scalable-ct
pytest
```

---

## License

MIT License.
