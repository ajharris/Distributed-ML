# Methodology Documentation Index

This folder contains the subdivided methodology documentation for the project.  
Each file covers a specific part of the overall methods description.

## Sections

1. **[Methodology Overview](overview.md)**  
   High-level description of the project’s goals, scope, and the role of this methodology document.

2. **[1. Project Overview](project_overview.md)**  
   Describes the research context, clinical problems of interest, and how CT datasets are used to study lung disease and lung cancer.

3. **[2. Dataset-Agnostic CT Metadata Schema](metadata_schema.md)**  
   Defines the canonical metadata schema (one row per CT series), required/optional fields, path conventions, and example tables used by all downstream components.

4. **[3. Dataset Access & Directory Layout](dataset_access.md)**  
   Explains how to request/download NLST, COPDGene (TCIA subset), and LIDC-IDRI; where to place files in `data/`; compliance notes; and how ingestion modules expect the directory structure to look.

5. **[4. CT Preprocessing Pipeline Roadmap](ct_preprocessing.md)**  
   Describes the preprocessing stages for CT scans, including lung segmentation (completed), spacing normalization, HU normalization, mask/volume registration, and orchestration of deterministic preprocessing workflows.

6. **[5. Next Steps](next_steps.md)**  
   Outlines broader project directions beyond preprocessing, including radiomics and deep feature extraction, distributed ML, predictive modeling, benchmarking, and dataset expansion.

## Suggested Reading Order

1. Start with **Methodology Overview** for overall context.  
2. Read **Project Overview** to understand the scientific and clinical motivation.  
3. Study **Dataset-Agnostic CT Metadata Schema** before implementing or modifying ingestion code.  
4. Follow **Dataset Access & Directory Layout** when setting up datasets on a new machine or environment.  
5. Consult **CT Preprocessing Pipeline Roadmap** when working on segmentation, resampling, HU normalization, and other data preparation tasks.  
6. Finally, review **Next Steps** for current development status and long-term planning.

This structure is intended for use under `docs/methodology/` in the repository, but the files can also be rendered by any markdown viewer or documentation tool.
