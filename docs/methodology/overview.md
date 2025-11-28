# Methodology

This document describes the methodology used in developing a Machine Learning based medical image analysis pipeline, including dataset handling, metadata schema definitions, preprocessing strategy, modeling pipelines, and reproducibility practices.

The project is designed to support **multiple medical imaging datasets** (e.g., NLST, COPDGene, LIDC-IDRI) under a **unified pipeline**. The goal is to allow standardized ingestion, preprocessing, modeling, and evaluation while maintaining transparency and reproducibility.

---

---

## Related Methodology Sections

- [Methodology Overview](overview.md)
- [1. Project Overview](project_overview.md)
- [2. Dataset-Agnostic CT Metadata Schema](metadata_schema.md)
- [3. Dataset Access & Directory Layout](dataset_access.md)
- [4. Next Steps](next_steps.md)

## Benchmarking

A working benchmark configuration (`config/preprocess_task06_benchmark.yml`) is provided for validating distributed preprocessing.

It processes 10 CT volumes from the *Task06 Lung* dataset and verifies:

- End-to-end preprocessing
- Segmentation + normalization correctness
- Dask scaling on multi-process execution
- Reproducible output caching

See `docs/methodology/preprocessing_pipeline.md` for full details.


