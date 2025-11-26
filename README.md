# Scalable Machine Learning for Large-Scale CT Phenotyping of COPD

This repository implements a **scalable, reproducible pipeline** for CT-based phenotyping of **Chronic Obstructive Pulmonary Disease (COPD)**.  
It unifies ingestion, metadata standardization, validation, and Parquet export for major public datasets (COPDGene, NLST, LIDC-IDRI), while laying the foundation for fully distributed CT preprocessing and machine‑learning workflows.

---

# Project Overview

CT imaging contains rich structural information relevant to COPD severity, progression, and phenotypic subtypes. This project provides:

- A **dataset‑agnostic ingestion system**  
- A **canonical metadata schema** for heterogeneous datasets  
- A **validated Parquet output layer** designed for large-scale ML workflows  
- A structure intended for future **feature extraction**, **distributed preprocessing**, and **predictive modeling**

The system is fully test‑driven, ensuring reproducibility and long‑term maintainability.

---

# Current Functionality

## Dataset Ingestion (COPDGene, NLST, LIDC-IDRI)
Each dataset has:
- A field extraction script (`copdgene.py`, `nlst.py`, `lidc.py`)
- A complete ingestion pipeline (`*_ingest.py`)
- Schema enforcement through `dataset_validators.py`
- Canonical row construction via `row_builder.py`
- Validated Parquet output via `metadata_io.py`

All ingestion modules support:
- Consistent field mapping
- Per-dataset normalization
- Type & range validation
- Canonical Parquet export

## Dataset Registry Working
The unified registry interface provides:

```python
DatasetRegistry.get("copdgene")
DatasetRegistry.get("nlst")
DatasetRegistry.get("lidc")
```

## Canonical Metadata Schema
Defined in `metadata_schema.py` with:
- Required fields  
- Standardized naming  
- COPD-focused metadata structure  

Validators ensure:
- Complete & correct fields  
- Type safety  
- Value sanity checks  

## Metadata I/O Layer
`metadata_io.py` provides:
- Parquet load/save
- Schema checking
- CSV-to-Parquet transformations

## External Dataset Loading
`load_external.py` is implemented for future import of new COPD datasets.

## All Tests Passing
Test coverage includes:
- Ingestion modules  
- Validators  
- Metadata I/O  
- Row builder  
- Logger, IO utilities  
- Dask cluster utilities  

## CLI: Build Metadata

```bash
python scripts/build_metadata.py \
--nlst-csv data/raw_metadata/nlst_demo.csv \
--copdgene-csv data/raw_metadata/copdgene_demo.csv \
--lidc-csv data/raw_metadata/lidc_demo.csv \
--output-dir data/metadata
```

Output includes:
- `metadata.parquet` (merged canonical metadata)
- Per‑dataset Parquet files

---

# Repository Structure (with notes)

```
.
├── README.md                       # Main project overview
│
├── config/
│   └── README.md                   # Pipeline configuration documentation
│
├── data/
│   ├── README.md                   # Data management rules & info
│   ├── metadata/                   # Canonical Parquet metadata outputs
│   │   ├── copdgene_demo.parquet   # Demo COPDGene subset
│   │   ├── metadata.parquet        # Unified merged metadata
│   │   ├── metadata_COPDGene.parquet
│   │   ├── metadata_LIDC-IDRI.parquet
│   │   └── metadata_NLST.parquet
│   └── raw_metadata/               # Input CSVs for ingestion
│       ├── copdgene_demo.csv
│       ├── lidc_demo.csv
│       └── nlst_demo.csv
│
├── docs/
│   ├── methodology/                # Detailed documentation for the pipeline
│   │   ├── README.md
│   │   ├── dataset_access.md       # Access instructions for NLST/COPDGene/LIDC
│   │   ├── metadata_schema.md      # Canonical metadata schema description
│   │   ├── next_steps.md           # Planned development roadmap
│   │   ├── overview.md
│   │   └── project_overview.md     # Clinical + technical background
│   ├── references.md
│   └── results.md                  # Generated experiment summaries (future)
│
├── environment.yml                 # Conda environment definition
│
├── notebooks/
│   ├── README.md
│   ├── exploration/
│   │   ├── README.md
│   │   └── parquet_exploration.ipynb  # Inspecting Parquet metadata
│   ├── modeling/
│   │   └── README.md
│   └── pipeline-demos/
│       └── README.md
│
├── requirements-colab.txt          # Lightweight Colab environment
│
├── scripts/
│   ├── bootstrap_local.sh          # Local dev environment setup
│   └── build_metadata.py           # CLI to run ingestion and build Parquet
│
├── src/
│   ├── README.md                   # High-level explanation of src structure
│   ├── __init__.py
│   │
│   ├── eval/
│   │   ├── README.md               # Evaluation utilities
│   │   └── __init__.py
│   │
│   ├── features/
│   │   ├── README.md               # Feature extraction (placeholder)
│   │   └── __init__.py
│   │
│   ├── ingest/                     # Dataset ingestion + normalization
│   │   ├── README.md
│   │   ├── copdgene.py             # COPDGene field extraction
│   │   ├── copdgene_ingest.py      # Full COPDGene ingestion pipeline
│   │   ├── dataset_validators.py   # Field-level validation rules
│   │   ├── lidc.py                 # LIDC-IDRI field extraction
│   │   ├── lidc_ingest.py          # LIDC-IDRI ingestion pipeline
│   │   ├── load_external.py        # External dataset loader
│   │   ├── metadata_io.py          # Parquet/CSV IO
│   │   ├── metadata_schema.py      # Canonical metadata schema
│   │   ├── nlst.py                 # NLST field extraction
│   │   ├── nlst_ingest.py          # Full NLST ingestion pipeline
│   │   ├── registry.py             # DatasetRegistry abstraction
│   │   └── row_builder.py          # Canonical metadata row builder
│   │
│   ├── preprocess/
│   │   ├── README.md               # CT preprocessing (future work)
│   │   └── __init__.py
│   │
│   ├── train/
│   │   ├── README.md               # Model training entry points (planned)
│   │   └── __init__.py
│   │
│   └── utils/
│       ├── README.md               # Logging, IO, distributed utilities
│       ├── dask_cluster.py         # Dask cluster helper for scaling
│       ├── io.py                   # IO helpers for NIfTI/DICOM/Zarr
│       └── logger.py               # Unified logging interface
│
└── tests/
    ├── README.md                   # Test documentation
    ├── ingest/                     # Ingestion + schema test suite
    └── utils/                      # Utility test suite
```

---

# Next Steps

Future work planned in `docs/methodology/next_steps.md` includes:

- Full CT preprocessing pipeline (segmentation, spacing normalization)
- 3D CNN and radiomics feature extraction
- Large-scale distributed processing
- Exploratory ML + predictive modeling
- Automated benchmarking tools
- Ingestion for additional COPD imaging datasets

---

# Getting Started

### 1. Create the environment:

```bash
conda env create -f environment.yml
conda activate scalable-ct
```

### 2. Run all ingestion tests:

```bash
pytest -q
```

### 3. Build canonical metadata:

```bash
python scripts/build_metadata.py     --nlst-csv data/raw_metadata/nlst_demo.csv     --copdgene-csv data/raw_metadata/copdgene_demo.csv     --lidc-csv data/raw_metadata/lidc_demo.csv     --output-dir data/metadata
```

---

# License

MIT License (recommended; add LICENSE file if desired)

---

