# Scalable Machine Learning for Large-Scale CT Phenotyping of COPD

This site documents the codebase, methodology, and experiments for a project on **large-scale lung CT phenotyping**, with a focus on **COPD**. It is intended to be a reproducible reference for data ingestion, CT preprocessing, feature extraction, modeling, and evaluation.

The documentation is organized so that high-level scientific context and detailed implementation notes live together, while the repository’s root `README.md` stays focused on quick start and orientation.

---

## What this project provides

- **Dataset-agnostic metadata schema** for CT series across multiple cohorts (NLST, COPDGene, LIDC-IDRI, etc.).
- **Ingestion utilities** to harmonize raw metadata into a common format.
- **CT preprocessing pipeline**, including normalization, resampling, and volume handling.
- Hooks for **feature extraction** (radiomics and deep-learning-based).
- A growing set of **modeling and evaluation utilities**.
- **Tests and environment definitions** to support reproducible research.

---

## Getting started

### Environment

Create and activate the Conda environment:

```bash
conda env create -f environment.yml
conda activate scalable-ct
