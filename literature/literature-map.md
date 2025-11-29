# Literature Map for CT Phenotyping PhD

This document is a living overview of the field. Update it weekly.

## 1. COPD Clinical Background

- Key papers:
  - [Hogg 2004] – small airway obstruction.
  - [GOLD report] – definitions and staging.
- Main ideas:
- Open questions:

## 2. CT-Derived Imaging Biomarkers (Kirby Cluster)

- Key papers:
  - [Kirby 2015, 2016, 2017, 2018, 2020, ...]
- Biomarkers:
  - PRM
  - Airway wall thickness
  - Emphysema burden
  - Small airway disease metrics
- How these are computed:
- Clinical relevance:
- Gaps / limitations:

## 3. Radiomics and Shape/Texture (Ward Cluster)

- Key papers:
  - [Ward 2015, 2017, Paris/Ward 2020, Goddard/Ward 2021, Sorensen/Ward 2019]
- Feature families (texture, shape, intensity distributions):
- Reproducibility lessons:
- How they compare with deep features:

## 4. Phenotyping and Clustering

- COPD subtypes (Castaldi, Estepar, Kirby, Ward, others):
- Cluster definitions and what they represent biologically:
- Methods used (k-means, mixture models, hierarchical, etc.):
- How your project could extend or refine this work:

## 5. CT Preprocessing, Segmentation, and Harmonization

- What steps your pipeline performs (link to code in `src/preprocess/`):
- Mapping papers to steps:
  - Segmentation:
  - HU normalization:
  - Resampling and voxel spacing:
  - Scanner harmonization:
- Risks and common failure modes:

## 6. Deep Learning for 3D CT and COPD

- 3D CNN architectures:
- Self-supervised and contrastive learning approaches:
- COPD-specific deep learning studies:
- How these can plug into your distributed preprocessing pipeline:

## 7. Distributed Computing and Large-Scale Pipelines

- How Dask/Spark/Monai/others handle large CT datasets:
- What your project currently does:
- What would be needed to scale to:
  - multi-site cohorts,
  - cloud environments,
  - mixed datasets (COPDGene, NLST, LIDC-IDRI).

## 8. Reproducibility, Bias, and Evaluation

- Sources of non-reproducibility in imaging studies:
- Dataset bias and cohort differences:
- Evaluation metrics and uncertainty:
- How you will design experiments to be reproducible.

## 9. Research Gaps and Potential Dissertation Aims

Update this section every 1–3 months.

- Gap 1:
- Gap 2:
- Gap 3:

Possible aims:

1. Aim 1:
2. Aim 2:
3. Aim 3:
