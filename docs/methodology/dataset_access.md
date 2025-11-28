# 3. Dataset Access & Directory Layout

This section integrates the complete dataset-access instructions and directory layout expectations for NLST, COPDGene (TCIA subset), and LIDC-IDRI. These instructions ensure any new user can correctly acquire, place, and stage datasets for ingestion.

## 3.1 Prerequisites & Compliance

- **Institutional approval**: NLST and COPDGene are controlled-access datasets. REB/IRB approval may be required depending on your institution.
- **Data Use Agreements (DUAs)**: Each dataset has its own DUA. Store copies in `docs/compliance/` (not tracked).
- **Accounts required**:
  - NLST: NIH Cancer Data Access System (CDAS)
  - COPDGene & LIDC-IDRI: The Cancer Imaging Archive (TCIA)
- **PHI handling**: Keep all raw datasets inside an encrypted `data/` volume.

---

## 3.2 Canonical Directory Layout

All ingestion modules rely on the following layout under `data_root` (defined in `config/paths.yml`):

```
data/
  raw/
    NLST/
      manifest/
      dicom/
        NLST_PXXXX/<series_uid>/*.dcm
    COPDGene/
      manifest/
      dicom/
        COPD-XXXX/baseline/*.dcm
    LIDC-IDRI/
      manifest/
      dicom/
        LIDC-IDRI-XXXX/<series_uid>/*.dcm

  metadata/
    NLST/nlst_raw_metadata.csv
    COPDGene/copdgene_raw_metadata.csv
    LIDC-IDRI/lidc_raw_metadata.csv

  preprocessed/
    NLST/
    COPDGene/
    LIDC-IDRI/
```

Segmentation masks should be placed at:

```
preprocessed/<DATASET>/masks/
```

---

## 3.3 NLST (National Lung Screening Trial)

### Access
- Apply through CDAS: https://biometry.nci.nih.gov/cdas/learn/nlst/
- Submit project request linked to REB/IRB protocol.

### Download
- Use CDAS Download Manager.
- Save manifests in: `data/raw/NLST/manifest/`
- Extract DICOMs to:
```
data/raw/NLST/dicom/<ParticipantID>/<SeriesInstanceUID>/*.dcm
```

### Metadata
- Convert CDAS clinical tables → `data/metadata/NLST/nlst_raw_metadata.csv`
- Ensure `dicom_rel_path` matches the above structure.

---

## 3.4 COPDGene (TCIA Subset)

### Access
- TCIA collection page: https://www.cancerimagingarchive.net/collection/copdgene/
- Requires TCIA account + COPDGene license acceptance.

### Download
- Use NBIA Data Retriever.
- Expected layout:
```
data/raw/COPDGene/dicom/<SubjectID>/<VisitName>/*.dcm
```

### Metadata
- Consolidate clinical spreadsheets → `data/metadata/COPDGene/copdgene_raw_metadata.csv`
- Include spirometry, COPD status, smoking info when present.

---

## 3.5 LIDC-IDRI

### Access
- TCIA collection page (CC-BY 3.0): https://www.cancerimagingarchive.net/collection/lidc-idri/

### Download
- Use NBIA Data Retriever.
- Layout:
```
data/raw/LIDC-IDRI/dicom/LIDC-IDRI-XXXX/<SeriesInstanceUID>/*.dcm
```

### Metadata
- Write:
```
data/metadata/LIDC-IDRI/lidc_raw_metadata.csv
```
- Include optional nodule malignancy labels.
- Place masks in `preprocessed/LIDC-IDRI/masks/`.

---

## 3.6 Verifying Placement

Run:
```
pytest tests/ingest/test_dataset_registry.py
```

Any missing paths or schema mismatches will be caught before further processing.

---

---

## Related Methodology Sections

- [Methodology Overview](overview.md)
- [1. Project Overview](project_overview.md)
- [2. Dataset-Agnostic CT Metadata Schema](metadata_schema.md)
- [3. Dataset Access & Directory Layout](dataset_access.md)
- [4. Next Steps](next_steps.md)

## Test Data (Task06 Lung)

For development and benchmarking purposes, the repository includes a subset of the **Medical Segmentation Decathlon Task06_Lung** dataset under:

```
data/raw_test/Task06_Lung/
```

These files are used exclusively for internal benchmarks and demos and are **not** part of the DatasetRegistry.

The benchmark configuration:

```
config/preprocess_task06_benchmark.yml
```

uses a metadata parquet (`metadata_task06_demo.parquet`) that maps 10 Task06 volumes to the preprocessing pipeline.

This allows validation of the distributed Dask pipeline without requiring access to NLST, COPDGene, or LIDC-IDRI datasets.
