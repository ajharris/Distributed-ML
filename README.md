# Scalable Machine Learning for Large-Scale CT Phenotyping of COPD

This repository contains code and documentation for a research project on **scalable CT phenotyping** for **COPD** and lung disease. It focuses on:

- Dataset-agnostic metadata and ingestion for large chest CT cohorts.
- CT preprocessing (normalization, resampling, segmentation).
- Feature extraction (radiomics and deep learning–based).
- Modeling and evaluation utilities.
- Reproducible workflows driven by tests and environment management.

Full, detailed documentation is provided via the MkDocs-powered documentation site.

---

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/ajharris/Distributed-ML.git
cd Distributed-ML
```

### 2. Create and activate the environment

```bash
conda env create -f environment.yml
conda activate scalable-ct
```

### 3. Run tests

```bash
pytest
```

If tests pass, your environment is correctly configured and the core pipeline imports should be working.

---

## Documentation

All detailed documentation (methodology, metadata schema, dataset access, results) lives in the `docs/` directory.

To preview documentation locally:

```bash
mkdocs serve
```

Then navigate to the served URL (typically `http://127.0.0.1:8000/`).

Key sections:

- **Methodology overview** — `docs/methodology/overview.md`
- **Dataset-agnostic metadata schema** — `docs/methodology/metadata_schema.md`
- **Dataset access and directory layout** — `docs/methodology/dataset_access.md`
- **Next steps / roadmap** — `docs/methodology/next_steps.md`
- **Results summary** — `docs/results.md`
- **References** — `docs/references.md`

If GitHub Pages is configured:

```
https://<your-username>.github.io/<your-repo-name>/
```

---

## Repository structure (high level)

```text
.
├── README.md                 # Concise repo overview and quickstart
├── environment.yml           # Conda environment definition
├── docs/                     # MkDocs documentation (canonical docs)
│   ├── index.md              # Documentation landing page
│   ├── methodology/
│   │   ├── README.md         # Methodology index (can be auto-generated)
│   │   ├── overview.md
│   │   ├── project_overview.md
│   │   ├── metadata_schema.md
│   │   ├── dataset_access.md
│   │   └── next_steps.md
│   ├── results.md
│   └── references.md
├── src/                      # Ingestion, preprocessing, modeling code
├── tests/                    # Test suite
└── data/                     # Metadata and demo raw metadata files
```

---

## Contributing

- Run tests frequently:

```bash
pytest
```

- Preview documentation before committing changes:

```bash
mkdocs serve
```
