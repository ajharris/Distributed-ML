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

```text
.
├── README.md
│   Main project overview, installation instructions, and navigation links
│
├── config/
│   README.md              Explains configuration files and how pipelines use YAML configs
│
├── data/
│   README.md              Instructions for dataset placement, structure, and storage rules
│
│   metadata/              Canonical metadata outputs (not tracked in git)
│   ├── metadata_COPDGene.parquet   Canonical metadata from COPDGene
│   ├── metadata_LIDC-IDRI.parquet  Canonical metadata from LIDC-IDRI
│   └── metadata_NLST.parquet       Canonical metadata from NLST
│
│   raw_metadata/          Small CSV fixtures used for demos/tests (not tracked in git)
│   ├── copdgene_demo.csv          COPDGene demo subset for ingestion tests
│   ├── lidc_demo.csv              LIDC-IDRI demo subset for ingestion tests
│   └── nlst_demo.csv              NLST demo subset for ingestion tests
│
├── docs/
│   methodology/           Subdivided methodology documentation
│   ├── README.md                  Index of methodology subsections
│   ├── overview.md                Purpose of methodology & structure
│   ├── project_overview.md        Scientific/clinical background
│   ├── metadata_schema.md         Canonical dataset metadata schema
│   ├── dataset_access.md          Dataset download, folder layout, REB/licensing
│   └── next_steps.md              Development/TDD roadmap
│
│   methodology.md         Legacy unified methodology file
│   references.md          References and citations
│   results.md             Experiment/benchmark summaries
│
├── environment.yml        Conda environment definition
│
├── notebooks/
│   README.md              Notebook organization overview
│
│   exploration/           Exploratory data analysis notebooks
│   ├── README.md
│   └── parquet_exploration.ipynb  Inspect Parquet metadata files
│
│   modeling/
│   └── README.md          Modeling notebook notes
│
│   pipeline-demos/
│   └── README.md          End-to-end pipeline demo notebooks
│
├── requirements-colab.txt Lightweight pip environment for Colab
│
├── scripts/
│   bootstrap_local.sh     Initialize local development environment
│   build_metadata.py      CLI to generate Parquet metadata from CSV input
│
├── src/
│   README.md              High-level explanation of src/ modules
│
│   eval/                  Evaluation metrics & utilities
│   ├── README.md
│   └── __init__.py
│
│   features/              Radiomics + deep feature extraction
│   ├── README.md
│   └── __init__.py
│
│   ingest/                Dataset ingestion + metadata standardization
│   ├── README.md
│   ├── __init__.py
│   ├── copdgene.py        Field extraction utilities for COPDGene
│   ├── copdgene_ingest.py Full COPDGene ingestion pipeline
│   ├── dataset_validators.py  Field-level validators & schema checks
│   ├── lidc.py            Field extraction for LIDC-IDRI
│   ├── lidc_ingest.py     Full LIDC-IDRI ingestion pipeline
│   ├── metadata_io.py     Reading/writing Parquet and CSV metadata
│   ├── metadata_schema.py Canonical metadata schema constants
│   ├── nlst.py            Field extraction for NLST
│   ├── nlst_ingest.py     Full NLST ingestion pipeline
│   ├── registry.py        DatasetRegistry abstraction layer
│   └── row_builder.py     Constructs canonical metadata rows
│
│   preprocess/            CT preprocessing pipeline
│   ├── README.md
│   └── __init__.py
│
│   train/                 Training module entry points
│   ├── README.md
│   └── __init__.py
│
│   utils/                 Shared utilities (logging, IO, cluster)
│   ├── README.md
│   ├── __init__.py
│   ├── dask_cluster.py    Launch & configure Dask clusters
│   ├── io.py              I/O helpers for NIfTI, Zarr, DICOM
│   └── logger.py          Unified logging interface
│
└── tests/                 Test suite (pytest)
    README.md              How tests are organized + how to run them
    conftest.py            Shared pytest fixtures
    ingest/                Tests for ingestion modules
    utils/                 Tests for utils (I/O, logging, Dask)
```
