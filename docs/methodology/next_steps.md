
# 5. Next Steps

These items reflect the broader project roadmap beyond preprocessing.

## 5.1 Feature Extraction

- Classical radiomics features (PyRadiomics or custom implementation)
- 3D CNN deep feature extraction
- Lung-mask-aware feature pipelines

## 5.2 Large-Scale Distributed Processing

- Dask-enabled multi-scan batch preprocessing
- Distributed radiomics and deep embedding computation
- Scaling benchmarks and reproducibility tests

## 5.3 Exploratory ML + Predictive Modeling

- COPD severity prediction
- Emphysema quantification
- Lung cancer risk modeling (e.g., NLST outcomes)
- Model comparison:
  - radiomics vs embeddings  
  - classical vs learned segmentation  

## 5.4 Automated Benchmarking Framework

- Runtime, memory, reproducibility, scaling efficiency
- Standardized report generation
- Comparison across datasets & pipeline configurations

## 5.5 Dataset Expansion

- Complete ingestion for full NLST, COPDGene, LIDC-IDRI datasets  
- Add ingestion modules for new public thoracic CT datasets
- Extend schema + validator tests with real dataset quirks

# Related Methodology Sections

- [Methodology Overview](overview.md)  
- [1. Project Overview](project_overview.md)  
- [2. Dataset-Agnostic CT Metadata Schema](metadata_schema.md)  
- [3. Dataset Access & Directory Layout](dataset_access.md)  
- [4. CT Preprocessing Pipeline Roadmap](ct_preprocessing.md)  
- [5. Next Steps](next_steps.md)
