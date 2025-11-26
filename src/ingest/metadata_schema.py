"""
src/ingest/metadata_schema.py

Central definition of the dataset-agnostic CT metadata schema.

This module is intentionally "constants-first":

- It defines the canonical column names and groupings.
- It defines small enums / allowed values for certain fields.
- It does NOT yet depend on any external libraries or IO.
- It is safe to import from tests and other modules.

Later, we will add:
- A CTMetadataRow dataclass / Pydantic model
- Validation and normalization utilities
- Dataset-specific mapping helpers (e.g., for NLST, COPDGene, LIDC-IDRI)

The goal is that every ingestion task in this project
uses these constants rather than hardcoding strings.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Type


# ---------------------------------------------------------------------------
# Column name constants (strings only)
# ---------------------------------------------------------------------------
# NOTE:
# - These names are the *canonical* schema column names used across ALL datasets.
# - If you need to know "what is the correct spelling?", import from here.
# - Do NOT hardcode these strings throughout the codebase.
#   Instead, do: from src.ingest.metadata_schema import COL_DATASET_NAME, REQUIRED_COLUMNS, ...
# ---------------------------------------------------------------------------


# --- Identity / dataset info ------------------------------------------------

COL_DATASET_NAME = "dataset_name"
"""Short identifier for the dataset (e.g., 'NLST', 'COPDGene', 'LIDC-IDRI')."""

COL_PATIENT_ID = "patient_id"
"""Project-level anonymized patient identifier."""

COL_SCAN_ID = "scan_id"
"""
Unique project identifier for a scan/series.

Common pattern:
    '<dataset_name>__<patient_id>__<series_uid>'
"""

COL_STUDY_UID = "study_uid"
"""DICOM StudyInstanceUID (may be null)."""

COL_SERIES_UID = "series_uid"
"""DICOM SeriesInstanceUID (primary imaging series identifier)."""

COL_MODALITY = "modality"
"""Imaging modality (typically 'CT' in this project)."""

COL_ACQUISITION_DATE = "acquisition_date"
"""
Scan acquisition date, stored as ISO-8601 string: 'YYYY-MM-DD'.

We intentionally store as text in Parquet to avoid timezone subtleties.
"""


# --- Geometry / voxel spacing ----------------------------------------------

COL_SLICE_THICKNESS_MM = "slice_thickness_mm"
"""Nominal slice thickness in millimetres (DICOM: SliceThickness)."""

COL_SPACING_X_MM = "spacing_x_mm"
"""Pixel spacing in X (mm) (DICOM: PixelSpacing[0])."""

COL_SPACING_Y_MM = "spacing_y_mm"
"""Pixel spacing in Y (mm) (DICOM: PixelSpacing[1])."""

COL_SPACING_Z_MM = "spacing_z_mm"
"""Distance between consecutive slices in mm (may differ from slice_thickness_mm)."""

COL_IMAGE_SIZE_X = "image_size_x"
"""Number of columns (width) in pixels."""

COL_IMAGE_SIZE_Y = "image_size_y"
"""Number of rows (height) in pixels."""

COL_IMAGE_SIZE_Z = "image_size_z"
"""Number of slices (depth) in the series."""


# --- Labels and masks ------------------------------------------------------

COL_LABEL_PRIMARY_NAME = "label_primary_name"
"""
Name of the primary label associated with this scan.

Example values:
- 'mortality_6yr'
- 'copd_status'
- 'nodule_malignancy'
"""

COL_LABEL_PRIMARY_VALUE = "label_primary_value"
"""
Value of the primary label (string or numeric).

Examples:
- '1' / '0' for binary outcomes
- 'COPD' / 'Control'
- A numeric risk score

Exact type may vary by dataset; we normalize to string or numeric per use-case.
"""

COL_RAW_IMAGE_PATH = "raw_image_path"
"""
Relative path to raw image data (DICOM directory or dataset-native format),
relative to the project-wide data_root (see config/paths.yml).
"""

COL_PREPROCESSED_IMAGE_PATH = "preprocessed_image_path"
"""
Relative path to the preprocessed imaging volume used by the pipeline
(e.g., NIfTI or Zarr), relative to data_root.

May be null if preprocessing not yet run.
"""

COL_LABEL_MASK_PATH = "label_mask_path"
"""
Relative path to any associated voxel-wise label/segmentation mask
(e.g., nodule mask for LIDC-IDRI), relative to data_root.

May be null if no mask exists.
"""


# --- Optional clinical & demographic fields --------------------------------

COL_AGE_AT_SCAN_YEARS = "age_at_scan_years"
"""Age in years at time of scan."""

COL_SEX = "sex"
"""Sex as recorded ('M', 'F', or 'Other')."""

COL_BMI_KG_M2 = "bmi_kg_m2"
"""Body Mass Index (kg/m^2)."""

COL_SMOKING_STATUS = "smoking_status"
"""Categorical smoking status (e.g., 'Never', 'Former', 'Current')."""

COL_PACK_YEARS = "pack_years"
"""Cumulative smoking exposure in pack-years."""

COL_FEV1_L = "fev1_l"
"""Forced Expiratory Volume in 1 second (absolute value, litres)."""

COL_FEV1_PERCENT_PRED = "fev1_percent_pred"
"""FEV1 expressed as percent predicted."""

COL_FVC_L = "fvc_l"
"""Forced Vital Capacity (litres)."""

COL_FEV1_FVC_RATIO = "fev1_fvc_ratio"
"""FEV1 / FVC ratio."""

COL_GOLD_STAGE = "gold_stage"
"""GOLD COPD severity stage (integer, typically 1–4)."""

COL_COPD_STATUS = "copd_status"
"""High-level COPD status label (e.g., 'COPD', 'Control', 'At-risk')."""

COL_EMPHYSEMA_PERCENT = "emphysema_percent"
"""Percent emphysema (e.g., lung volume fraction below -950 HU)."""

COL_MORTALITY_5YR = "mortality_5yr"
"""Indicator for 5-year mortality (0/1 or boolean)."""

COL_MORTALITY_6YR = "mortality_6yr"
"""Indicator for 6-year mortality (0/1 or boolean, e.g., in NLST)."""

COL_LUNG_CANCER_DIAGNOSIS = "lung_cancer_diagnosis"
"""Indicator for lung cancer diagnosis associated with this scan (0/1 or boolean)."""

COL_OTHER_CLINICAL_JSON = "other_clinical_json"
"""
Catch-all JSON string for extra clinical fields that do not yet warrant
dedicated top-level columns.

This allows us to store exploratory or dataset-specific fields without
constantly changing the Parquet schema.
"""


# ---------------------------------------------------------------------------
# Column groupings
# ---------------------------------------------------------------------------
# These lists are useful for:
# - Asserting presence of required columns in tests
# - Selecting subsets of columns for particular analysis tasks
# - Documenting the logical grouping of the schema
# ---------------------------------------------------------------------------

REQUIRED_IDENTITY_COLUMNS: List[str] = [
    COL_DATASET_NAME,
    COL_PATIENT_ID,
    COL_SCAN_ID,
    COL_STUDY_UID,
    COL_SERIES_UID,
    COL_MODALITY,
    COL_ACQUISITION_DATE,
]

REQUIRED_GEOMETRY_COLUMNS: List[str] = [
    COL_SLICE_THICKNESS_MM,
    COL_SPACING_X_MM,
    COL_SPACING_Y_MM,
    COL_SPACING_Z_MM,
    COL_IMAGE_SIZE_X,
    COL_IMAGE_SIZE_Y,
    COL_IMAGE_SIZE_Z,
]

REQUIRED_LABEL_AND_PATH_COLUMNS: List[str] = [
    COL_LABEL_PRIMARY_NAME,
    COL_LABEL_PRIMARY_VALUE,
    COL_RAW_IMAGE_PATH,
    COL_PREPROCESSED_IMAGE_PATH,
    COL_LABEL_MASK_PATH,
]

REQUIRED_COLUMNS: List[str] = (
    REQUIRED_IDENTITY_COLUMNS
    + REQUIRED_GEOMETRY_COLUMNS
    + REQUIRED_LABEL_AND_PATH_COLUMNS
)
"""
The full set of required columns that must be present in every metadata table.

IMPORTANT:
- Individual values may be null (e.g., label_primary_name for unlabeled scans),
  but the *columns* must exist in the table.
"""

OPTIONAL_CLINICAL_COLUMNS: List[str] = [
    COL_AGE_AT_SCAN_YEARS,
    COL_SEX,
    COL_BMI_KG_M2,
    COL_SMOKING_STATUS,
    COL_PACK_YEARS,
    COL_FEV1_L,
    COL_FEV1_PERCENT_PRED,
    COL_FVC_L,
    COL_FEV1_FVC_RATIO,
    COL_GOLD_STAGE,
    COL_COPD_STATUS,
    COL_EMPHYSEMA_PERCENT,
    COL_MORTALITY_5YR,
    COL_MORTALITY_6YR,
    COL_LUNG_CANCER_DIAGNOSIS,
    COL_OTHER_CLINICAL_JSON,
]

ALL_COLUMNS: List[str] = REQUIRED_COLUMNS + OPTIONAL_CLINICAL_COLUMNS
"""Convenience list containing ALL known columns in the canonical schema."""


# ---------------------------------------------------------------------------
# Expected logical dtypes (not enforced yet, but used in tests & validation)
# ---------------------------------------------------------------------------
# We specify dtypes as Python types or descriptive strings.
# These can later inform validation logic or schema-checking utilities.
# ---------------------------------------------------------------------------

# Using Python's Type objects for a rough indication of expected types.
# For booleans and 0/1 columns, we accept int or bool at the storage level.

METADATA_COLUMN_DTYPES: Dict[str, Type] = {
    # Identity
    COL_DATASET_NAME: str,
    COL_PATIENT_ID: str,
    COL_SCAN_ID: str,
    COL_STUDY_UID: str,
    COL_SERIES_UID: str,
    COL_MODALITY: str,
    COL_ACQUISITION_DATE: str,  # ISO date string

    # Geometry
    COL_SLICE_THICKNESS_MM: float,
    COL_SPACING_X_MM: float,
    COL_SPACING_Y_MM: float,
    COL_SPACING_Z_MM: float,
    COL_IMAGE_SIZE_X: int,
    COL_IMAGE_SIZE_Y: int,
    COL_IMAGE_SIZE_Z: int,

    # Labels & paths
    COL_LABEL_PRIMARY_NAME: str,
    COL_LABEL_PRIMARY_VALUE: str,  # may be numeric-like but kept as string for flexibility
    COL_RAW_IMAGE_PATH: str,
    COL_PREPROCESSED_IMAGE_PATH: str,
    COL_LABEL_MASK_PATH: str,

    # Clinical
    COL_AGE_AT_SCAN_YEARS: float,
    COL_SEX: str,
    COL_BMI_KG_M2: float,
    COL_SMOKING_STATUS: str,
    COL_PACK_YEARS: float,
    COL_FEV1_L: float,
    COL_FEV1_PERCENT_PRED: float,
    COL_FVC_L: float,
    COL_FEV1_FVC_RATIO: float,
    COL_GOLD_STAGE: int,
    COL_COPD_STATUS: str,
    COL_EMPHYSEMA_PERCENT: float,
    COL_MORTALITY_5YR: int,       # 0/1 or bool
    COL_MORTALITY_6YR: int,       # 0/1 or bool
    COL_LUNG_CANCER_DIAGNOSIS: int,  # 0/1 or bool
    COL_OTHER_CLINICAL_JSON: str,
}


# ---------------------------------------------------------------------------
# Enums for normalized categorical fields
# ---------------------------------------------------------------------------

class Sex(str, Enum):
    """Normalized representation of sex."""

    MALE = "M"
    FEMALE = "F"
    OTHER = "Other"
    UNKNOWN = "Unknown"


class SmokingStatus(str, Enum):
    """Normalized representation of smoking status."""

    NEVER = "Never"
    FORMER = "Former"
    CURRENT = "Current"
    UNKNOWN = "Unknown"


class COPDStatus(str, Enum):
    """High-level COPD status labels."""

    COPD = "COPD"
    CONTROL = "Control"
    AT_RISK = "At-risk"
    UNKNOWN = "Unknown"

# ---------------------------------------------------------------------------
# CTMetadataRow dataclass
# ---------------------------------------------------------------------------
# This is the canonical in-memory representation of a single CT series row.
#
# Design choices:
# - Field names match the schema column names exactly.
# - Many fields are Optional[...] to allow missing values (even though
#   the *columns* themselves are always present in the Parquet table).
# - from_dict() enforces presence of REQUIRED_COLUMNS and supplies
#   defaults (None) for any missing OPTIONAL_CLINICAL_COLUMNS.
# ---------------------------------------------------------------------------

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class CTMetadataRow:
    """
    Canonical metadata representation for a single CT series in this project.

    IMPORTANT:
    - Field names correspond exactly to the column names defined above.
    - Required vs optional here is about *value* presence, not the
      existence of the column itself in a DataFrame or Parquet file.
    """

    # --- Identity / dataset fields ---
    dataset_name: str
    patient_id: str
    scan_id: str
    study_uid: Optional[str]
    series_uid: str
    modality: str
    acquisition_date: Optional[str]

    # --- Geometry / voxel spacing ---
    slice_thickness_mm: Optional[float]
    spacing_x_mm: Optional[float]
    spacing_y_mm: Optional[float]
    spacing_z_mm: Optional[float]
    image_size_x: Optional[int]
    image_size_y: Optional[int]
    image_size_z: Optional[int]

    # --- Labels & paths ---
    label_primary_name: Optional[str]
    label_primary_value: Optional[str]
    raw_image_path: str
    preprocessed_image_path: Optional[str]
    label_mask_path: Optional[str]

    # --- Optional clinical & demographic ---
    age_at_scan_years: Optional[float] = None
    sex: Optional[str] = None
    bmi_kg_m2: Optional[float] = None
    smoking_status: Optional[str] = None
    pack_years: Optional[float] = None
    fev1_l: Optional[float] = None
    fev1_percent_pred: Optional[float] = None
    fvc_l: Optional[float] = None
    fev1_fvc_ratio: Optional[float] = None
    gold_stage: Optional[int] = None
    copd_status: Optional[str] = None
    emphysema_percent: Optional[float] = None
    mortality_5yr: Optional[int] = None
    mortality_6yr: Optional[int] = None
    lung_cancer_diagnosis: Optional[int] = None
    other_clinical_json: Optional[str] = None

    # ------------------------------------------------------------------
    # Constructors & helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CTMetadataRow":
        """
        Construct a CTMetadataRow from a flat dict whose keys are
        canonical column names.

        Responsibilities:
        - Verify that ALL required columns are present in the dict.
        - For any OPTIONAL_CLINICAL_COLUMNS missing from the dict,
          set the corresponding dataclass field to None.
        - Ignore any keys that we do not recognize (future-proofing).

        NOTE: This method does NOT yet do strict dtype validation;
        that can be layered on later.
        """
        # 1) Check required columns
        missing = [col for col in REQUIRED_COLUMNS if col not in data]
        if missing:
            raise ValueError(
                f"Missing required metadata columns in CTMetadataRow.from_dict: {missing}"
            )

        # 2) Build kwargs for dataclass constructor
        kwargs: dict[str, Any] = {}

        # Known columns: we use ALL_COLUMNS as the canonical list of fields
        for col in ALL_COLUMNS:
            if col in data:
                kwargs[col] = data[col]
            else:
                # If it's an optional clinical column and not provided,
                # default to None.
                if col in OPTIONAL_CLINICAL_COLUMNS:
                    kwargs[col] = None

        # 3) Construct the dataclass instance
        return cls(**kwargs)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert this CTMetadataRow back to a flat dict with keys
        matching the canonical schema column names.

        This is useful for:
        - building DataFrames
        - writing Parquet
        - debugging / logging
        """
        out: dict[str, Any] = {}
        for col in ALL_COLUMNS:
            out[col] = getattr(self, col)
        return out
