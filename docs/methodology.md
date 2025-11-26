# Methodology

This document describes the methodology used in developing a Machine Learning based medical image analysis pipeline, including dataset handling, metadata schema definitions, preprocessing strategy, modeling pipelines, and reproducibility practices.

The project is designed to support **multiple medical imaging datasets** (e.g., NLST, COPDGene, LIDC-IDRI) under a **unified pipeline**. The goal is to allow standardized ingestion, preprocessing, modeling, and evaluation while maintaining transparency and reproducibility.

---

# 1. Project Overview

This research project uses large CT imaging datasets to study clinical, morphological, and predictive biomarkers in lung disease and lung cancer. Because these datasets differ widely in structure, imaging conventions, and clinical metadata, we adopt a **dataset-agnostic schema** that allows all data to be harmonized into a single consistent structure.

This methodology document serves as the foundation for:

- dataset ingestion (`src/ingest/`)
- feature extraction (`src/features/`)
- modeling (`src/modeling/`)
- evaluation (`src/eval/`)
- scientific documentation (`docs/`)

---

# 2. Dataset-Agnostic CT Metadata Schema

## 2.1 Motivation

Each imaging dataset provides metadata in a different format (DICOM headers, XML, CSV, JSON). Without a unified schema, downstream code becomes brittle and filled with dataset-specific exceptions. Absent a database to manage, Excel files are often used to share information across teams, making it someone's responsibility to update and maintain these files.

To avoid this, we define a **canonical metadata schema** where each row corresponds to one **CT series** (a full 3D volume). All datasets must be transformed into this schema before being used by any preprocessing or modeling components.

---

## 2.2 Row Granularity

**One row = one CT series**, defined by a unique DICOM `SeriesInstanceUID`.

- Patient-level attributes are duplicated across series (if a patient has multiple scans).
- Study-level attributes (e.g., acquisition date) are included per series.
- Optional clinical fields are included as available.

This makes the table simple, flat, and Dask-friendly.

---

## 2.3 Required Fields

These **must** exist for all datasets, even if the value is `null` for some.

| Column | Type | Description |
|--------|------|-------------|
| `dataset_name` | string | Identifier for dataset (e.g., `"NLST"`, `"COPDGene"`). |
| `patient_id` | string | Project-level anonymized patient ID. |
| `scan_id` | string | Unique project identifier for a scan/series. Often `<dataset>__<patient_id>__<series_uid>`. |
| `study_uid` | string / null | DICOM StudyInstanceUID. |
| `series_uid` | string | DICOM SeriesInstanceUID (primary key for imaging volume). |
| `modality` | string | Usually `"CT"`. |
| `acquisition_date` | yyyy-mm-dd | Scan acquisition date. |
| `slice_thickness_mm` | float | From DICOM `SliceThickness`. |
| `spacing_x_mm` | float | In-plane pixel spacing (X). |
| `spacing_y_mm` | float | In-plane pixel spacing (Y). |
| `spacing_z_mm` | float | Slice spacing (Z). |
| `image_size_x` | int | Number of columns. |
| `image_size_y` | int | Number of rows. |
| `image_size_z` | int | Number of slices. |
| `label_primary_name` | string/null | Name of primary label (e.g., `"mortality_6yr"`). |
| `label_primary_value` | numeric/string/null | Value of primary label for this scan. |
| `raw_image_path` | string | **Relative** path to raw DICOM or dataset format. |
| `preprocessed_image_path` | string/null | **Relative** path to normalized preprocessed image (e.g., .nii.gz, Zarr). |
| `label_mask_path` | string/null | Relative path to segmentation mask (if available). |

---

## 2.4 Optional Clinical & Demographic Fields

These may be present in some datasets and missing in others. When present, they follow these names and types:

| Field | Type | Description |
|-------|-------|-------------|
| `age_at_scan_years` | float | Age in years at time of scan. |
| `sex` | string | `"M"`, `"F"`, or `"Other"`. |
| `bmi_kg_m2` | float | Body mass index. |
| `smoking_status` | string | `"Never"`, `"Former"`, `"Current"`. |
| `pack_years` | float | Cumulative smoking exposure. |
| `fev1_l` | float | Forced expiratory volume (absolute liters). |
| `fev1_percent_pred` | float | FEV1 % predicted. |
| `fvc_l` | float | Forced vital capacity. |
| `fev1_fvc_ratio` | float | Ratio FEV1/FVC. |
| `gold_stage` | int | COPD severity stage 1–4. |
| `copd_status` | string | `"COPD"`, `"Control"`, `"At-risk"`. |
| `emphysema_percent` | float | Percent emphysema or LAA%. |
| `mortality_5yr` | int/bool | 5-year mortality outcome. |
| `mortality_6yr` | int/bool | 6-year mortality outcome (NLST). |
| `lung_cancer_diagnosis` | int/bool | Cancer diagnosis indicator. |
| `other_clinical_json` | string | JSON blob for dataset-specific extra fields. |

---

## 2.5 File Path Conventions

Paths in the metadata table are always **relative** to a
project-level `data_root` defined in `config/paths.yml`.

Example `paths.yml`:

```yaml
data_root: "/path/to/project/data"

datasets:
  NLST:
    raw_root: "raw/NLST"
    preprocessed_root: "preprocessed/NLST"
  COPDGene:
    raw_root: "raw/COPDGene"
    preprocessed_root: "preprocessed/COPDGene"
  LIDC-IDRI:
    raw_root: "raw/LIDC-IDRI"
    preprocessed_root: "preprocessed/LIDC-IDRI"
```

---

## 2.6 Output Format

Standard outputs:

- **Parquet** (primary)
- **Master table** (optional)
- **Optional CSVs** for debugging.

---

## 2.7 Example Metadata Table

The table below shows a **toy example** of the canonical metadata schema for
three scans (one per dataset). Values are illustrative only.

| dataset_name | patient_id      | scan_id                                         | series_uid          | modality | acquisition_date | slice_thickness_mm | spacing_x_mm | spacing_y_mm | spacing_z_mm | image_size_x | image_size_y | image_size_z | label_primary_name | label_primary_value | raw_image_path                                         | preprocessed_image_path                                              | label_mask_path                                                                 | age_at_scan_years | sex | smoking_status | pack_years |
|-------------:|-----------------|------------------------------------------------|---------------------|----------|------------------|--------------------|--------------|--------------|--------------|--------------|--------------|--------------|--------------------|---------------------|--------------------------------------------------------|------------------------------------------------------------------------|---------------------------------------------------------------------------------|-------------------|-----|----------------|-----------|
| NLST         | NLST_P0001      | NLST__NLST_P0001__1.2.3                        | 1.2.3               | CT       | 2005-03-12       | 1.25               | 0.70         | 0.70         | 1.25         | 512          | 512          | 350          | mortality_6yr      | 1                   | raw/NLST/NLST_P0001/series_001/                       | preprocessed/NLST/NLST_P0001/series_001.nii.gz                         | *(none)*                                                                        | 63                | F   | Former         | 25        |
| COPDGene     | COPD-0123       | COPDGene__COPD-0123__2.25.1234567890.1.1       | 2.25.1234567890.1.1 | CT       | 2010-06-05       | 0.75               | 0.68         | 0.68         | 0.75         | 512          | 512          | 450          | copd_status        | COPD                | raw/COPDGene/COPD-0123/CT_baseline/                   | preprocessed/COPDGene/COPD-0123/CT_baseline.nii.gz                     | *(none)*                                                                        | 58                | M   | Current        | 40        |
| LIDC-IDRI    | LIDC-IDRI-0005  | LIDC-IDRI__LIDC-IDRI-0005__1.3.6.1.4.1.14519…  | 1.3.6.1.4.1.14519…  | CT       | 2004-11-10       | 1.25               | 0.70         | 0.70         | 1.25         | 512          | 512          | 150          | nodule_malignancy  | 4                   | raw/LIDC-IDRI/LIDC-IDRI-0005/CT/                      | preprocessed/LIDC-IDRI/LIDC-IDRI-0005/series_001.nii.gz               | preprocessed/LIDC-IDRI/LIDC-IDRI-0005/series_001_nodule_mask.nii.gz  | *(unknown)*        | F   | Never          | 0         |

This example demonstrates:

- One row per **CT series**
- Consistent naming across NLST, COPDGene, and LIDC-IDRI
- Relative file paths (no leading `/`)
- Optional clinical fields present for some scans and missing for others


---

## 2.8 Implementation Notes

(Description of dataclass and ingestion implementation.)

---

# 3. Next Steps

A TDD workflow will be applied to:

- [x] Define schema constants.
- [x] Write schema validation tests.
- [x] Implement dataset-agnostic constructor.
- [x] Build NLST ingestion.
- [x] Add ingestion for COPDGene and LIDC-IDRI.
- [x] Write dataset-level validators.
- [x] Produce dataset Parquet outputs.