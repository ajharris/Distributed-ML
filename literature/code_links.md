# Code–Literature Cross-Links

This document connects the 12-month reading program to specific parts of
the `Distributed-ML` codebase and documentation. The goal is that every
major idea from the literature has a clear “home” in the code, and vice
versa.

## 1. COPD Clinical Background and Datasets

Literature themes:
- COPD pathophysiology (Hogg 2004, GOLD reports).
- Large cohort design: COPDGene (Regan 2010), NLST, LIDC-IDRI.
- Imaging-based phenotypes and subtypes (Castaldi, Estepar, Kirby, Ward).

Relevant code and docs:
- `docs/methodology/project_overview.md`  
  High-level clinical and research context.
- `docs/methodology/dataset_access.md`  
  How NLST, COPDGene, and LIDC-IDRI are obtained, organized, and accessed.
- `data/README.md`  
  Dataset placement and structure rules.
- `data/raw_metadata/*.csv` and `data/metadata/*.parquet`  
  Concrete instances of the canonical metadata representation.

Suggested TODOs:
- [ ] Add citations in `docs/methodology/project_overview.md` for COPDGene, NLST, LIDC-IDRI.
- [ ] Document how clinical labels (e.g., GOLD stage, spirometry) could be joined to metadata tables.

---

## 2. CT-Derived Imaging Biomarkers (Kirby Cluster)

Literature themes:
- PRM: Galbán 2012, Labaki 2018, Kirby PRM papers.
- CT-derived emphysema, air-trapping, airway wall measures.
- Scanner harmonization and standardized densitometry (Kirby 2017–2020).

Relevant code and docs:
- `src/ingest/metadata_schema.py`  
  Canonical fields for CT series and any planned phenotype fields.
- `src/ingest/dataset_validators.py`  
  Schema checks that enforce consistency across datasets.
- `docs/methodology/metadata_schema.md`  
  Describes which imaging-derived fields might exist (e.g. emphysema fraction).
- `docs/results.md` (future)  
  Natural home for PRM-based or emphysema-based results summaries.

Suggested TODOs:
- [ ] Add sections to `metadata_schema.md` describing where PRM and related biomarkers would be stored.
- [ ] Create a design note for how PRM maps could be generated and summarized within this pipeline.

---

## 3. Radiomics and Shape/Texture (Ward Cluster)

Literature themes:
- Radiomic features for parenchyma and airway tree (Ward 2015, 2017).
- Texture features for emphysema patterns.
- Reproducibility of radiomic features across scanners (Sorensen & Ward).

Relevant code and docs:
- `src/features/`  
  Future home for radiomics and deep feature extraction modules.
- `src/features/README.md`  
  Description of feature families (radiomics vs deep embeddings).
- `tests/` under `features/`  
  Where to validate feature stability and reproducibility.

Suggested TODOs:
- [ ] Add a “Radiomics” section to `src/features/README.md` that identifies the core feature sets to implement.
- [ ] Add tests capturing basic invariances (e.g., small HU offsets or resampling) informed by radiomics reproducibility papers.

---

## 4. CT Preprocessing, Segmentation, and Harmonization

Literature themes:
- Lung segmentation (Hofmanninger 2020; 3D U-Net variants).
- HU normalization and resampling.
- Scanner harmonization and calibration (Kirby, Maier-Hein).

Relevant code and docs:
- `src/preprocess/`  
  Main preprocessing pipeline (segmentation, normalization, resampling).
- `src/utils/io.py`  
  I/O helpers for NIfTI/Zarr/DICOM.
- `src/utils/logger.py`  
  Unified logging for preprocessing runs.
- `docs/methodology/overview.md` and `docs/methodology/next_steps.md`  
  High-level pipeline description and roadmap.

Suggested TODOs:
- [ ] Document each preprocess step in `src/preprocess/README.md` and reference key papers (e.g., segmentation, resampling strategy).
- [ ] Add configuration options (and docs) for alternative windowing / normalization strategies inspired by the literature.

---

## 5. Phenotyping and Clustering

Literature themes:
- COPD subtypes via clustering (Castaldi 2014).
- Structural patterns in airway and parenchyma (Estepar, Kirby, Ward).
- Mapping phenotypes to outcomes (exacerbations, decline).

Relevant code and docs:
- `src/train/`  
  Training entry points for classical ML and deep models.
- `src/eval/`  
  Evaluation and metrics.
- `docs/results.md`  
  Natural destination for phenotype clustering results and figures.
- `notebooks/modeling/`  
  Exploratory phenotyping notebooks.

Suggested TODOs:
- [ ] Create a `docs/methodology/phenotyping.md` file describing clustering goals and linking to key papers.
- [ ] Add experiments in `notebooks/modeling/` that replicate or extend at least one phenotype clustering approach from the literature.

---

## 6. Deep Learning for 3D CT and COPD

Literature themes:
- 3D U-Net, DeepMedic, and related architectures.
- Self-supervised 3D learning (Models Genesis, MoCo adaptations).
- Deep features vs classical radiomics for COPD.

Relevant code and docs:
- `src/train/`  
  Hooks for model training; future home for deep learning modules.
- `notebooks/pipeline-demos/`  
  End-to-end demos (can be extended to show deep learning integration).
- `docs/results.md`  
  For reporting deep vs radiomics comparisons.

Suggested TODOs:
- [ ] Plan a `src/features/deep/` submodule for 3D encoders.
- [ ] Add a short “Deep Learning Roadmap” section to `src/train/README.md` referencing key deep COPD papers.

---

## 7. Distributed Computing and Large-Scale Pipelines

Literature themes:
- Dask (Rocklin 2015) and distributed computation.
- Cloud-native imaging (Zarr, MONAI, related frameworks).
- Large cohort processing (COPDGene, NLST) at scale.

Relevant code and docs:
- `src/utils/dask_cluster.py`  
  Dask cluster launch and configuration.
- `config/` and `config/README.md`  
  YAML configs controlling distributed runs.
- `docs/methodology/dataset_access.md`  
  Explains where data lives and hints at scaling needs.
- `docs/results.md` and `docs/methodology/next_steps.md`  
  Good places to record benchmark experiments and scaling results.

Suggested TODOs:
- [ ] Add a “Distributed Preprocessing” subsection to `src/preprocess/README.md` that references Dask and relevant scaling papers.
- [ ] Define benchmark experiments (number of scans, time, memory) and log them in `docs/results.md`.

---

## 8. Reproducibility, Bias, and Evaluation

Literature themes:
- Reproducibility in medical imaging (Maier-Hein, Pineau, others).
- Dataset bias and fairness in healthcare AI.
- Uncertainty, calibration, and robust evaluation.

Relevant code and docs:
- `tests/`  
  Entire pytest suite; a key pillar of reproducibility.
- `docs/methodology/next_steps.md`  
  Roadmap items concerning tests, CI/CD, and reproducibility.
- `docs/references.md`  
  Bibliographic references (can be aligned with the Mendeley `.bib` file).
- `README.md`  
  High-level statement of reproducibility goals for the project.

Suggested TODOs:
- [ ] Add a “Reproducibility and Evaluation” section to `docs/methodology/overview.md` outlining principles and linking to key papers.
- [ ] Ensure CI runs tests that specifically target known reproducibility issues (e.g., dependence on environment variables, file layouts).

---

## 9. How to Use This File

- When you implement something inspired by a paper, add a bullet here that links:
  - from the paper (citation, short description),
  - to the relevant code and docs.
- When you write documentation or new methods, update this file to indicate which part of the literature it corresponds to.

Over time, this document becomes a bridge between your reading program
and the evolution of the codebase.
