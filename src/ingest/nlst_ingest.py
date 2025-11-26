"""
src/ingest/nlst_ingest.py

NLST-specific ingestion helpers.

This module is intentionally narrow in scope:

- It does NOT parse raw NLST DICOM or CSV files yet.
- Instead, it assumes we already have a "raw NLST row" dict with
  NLST-specific field names (e.g., from a preprocessed CSV or DB).
- It maps that dict into the *canonical* CTMetadataRow via:

    NLST row dict  --->  canonical dict  --->  build_ct_metadata_row()

When you later inspect real NLST metadata layouts, you can update the
NLST_* column name constants and the mapping logic here.
"""

from __future__ import annotations

from typing import Any, Dict

from .metadata_schema import (
    CTMetadataRow,
    # canonical column names
    COL_DATASET_NAME,
    COL_PATIENT_ID,
    COL_STUDY_UID,
    COL_SERIES_UID,
    COL_ACQUISITION_DATE,
    COL_SLICE_THICKNESS_MM,
    COL_SPACING_X_MM,
    COL_SPACING_Y_MM,
    COL_SPACING_Z_MM,
    COL_IMAGE_SIZE_X,
    COL_IMAGE_SIZE_Y,
    COL_IMAGE_SIZE_Z,
    COL_LABEL_PRIMARY_NAME,
    COL_LABEL_PRIMARY_VALUE,
    COL_RAW_IMAGE_PATH,
    COL_MODALITY,
    COL_PREPROCESSED_IMAGE_PATH,
    COL_LABEL_MASK_PATH,
)
from .row_builder import build_ct_metadata_row


# ---------------------------------------------------------------------------
# NLST "input" column name conventions
# ---------------------------------------------------------------------------
# These constants represent the *input* field names we expect to see for NLST.
# They are PROJECT-LOCAL placeholders; when you explore real NLST tables,
# adjust these strings to match actual column names.
# ---------------------------------------------------------------------------

NLST_COL_PATIENT_ID = "nlst_patient_id"
NLST_COL_STUDY_INSTANCE_UID = "study_instance_uid"
NLST_COL_SERIES_INSTANCE_UID = "series_instance_uid"
NLST_COL_MORTALITY_6YR = "mortality_6yr"
NLST_COL_ACQUISITION_DATE = "acquisition_date"  # e.g., '20050312' (yyyymmdd format)
NLST_COL_SLICE_THICKNESS_MM = "slice_thickness_mm"
NLST_COL_PIXEL_SPACING_X_MM = "pixel_spacing_x_mm"
NLST_COL_PIXEL_SPACING_Y_MM = "pixel_spacing_y_mm"
NLST_COL_SPACING_BETWEEN_SLICES_MM = "spacing_between_slices_mm"
NLST_COL_NUM_COLUMNS = "num_columns"
NLST_COL_NUM_ROWS = "num_rows"
NLST_COL_NUM_SLICES = "num_slices"
NLST_COL_DICOM_REL_PATH = "dicom_rel_path"  # relative path to DICOM folder


# ---------------------------------------------------------------------------
# Row-level mapping
# ---------------------------------------------------------------------------

def nlst_row_to_ct_metadata(nlst_row: Dict[str, Any]) -> CTMetadataRow:
    """
    Map a single "raw NLST row" dict into a CTMetadataRow.

    Parameters
    ----------
    nlst_row:
        Dict with NLST-specific column names as keys. This is a logical
        representation, NOT a raw DICOM header. For example:

            {
                'nlst_patient_id': 'NLST-0001',
                'study_instance_uid': '1.2.840...',
                'series_instance_uid': '1.2.840...1',
                'mortality_6yr': 1,
                'acquisition_date': '20050312',
                'slice_thickness_mm': 1.25,
                ...
            }

    Returns
    -------
    CTMetadataRow
        Canonical metadata row that fits the dataset-agnostic schema.
    """
    # 1) Build a canonical dict keyed by canonical column names.
    canonical: Dict[str, Any] = {
        # Identity
        COL_DATASET_NAME: "NLST",
        COL_PATIENT_ID: nlst_row[NLST_COL_PATIENT_ID],
        COL_STUDY_UID: nlst_row[NLST_COL_STUDY_INSTANCE_UID],
        COL_SERIES_UID: nlst_row[NLST_COL_SERIES_INSTANCE_UID],

        # Modality: NLST is CT
        COL_MODALITY: "CT",

        # Acquisition date (format will be normalized by build_ct_metadata_row)
        COL_ACQUISITION_DATE: nlst_row.get(NLST_COL_ACQUISITION_DATE),

        # Geometry
        COL_SLICE_THICKNESS_MM: nlst_row.get(NLST_COL_SLICE_THICKNESS_MM),
        COL_SPACING_X_MM: nlst_row.get(NLST_COL_PIXEL_SPACING_X_MM),
        COL_SPACING_Y_MM: nlst_row.get(NLST_COL_PIXEL_SPACING_Y_MM),
        COL_SPACING_Z_MM: nlst_row.get(NLST_COL_SPACING_BETWEEN_SLICES_MM),
        COL_IMAGE_SIZE_X: nlst_row.get(NLST_COL_NUM_COLUMNS),
        COL_IMAGE_SIZE_Y: nlst_row.get(NLST_COL_NUM_ROWS),
        COL_IMAGE_SIZE_Z: nlst_row.get(NLST_COL_NUM_SLICES),

        # Label: for NLST we treat 6-year mortality as the primary label
        COL_LABEL_PRIMARY_NAME: "mortality_6yr",
        COL_LABEL_PRIMARY_VALUE: (
            None
            if nlst_row.get(NLST_COL_MORTALITY_6YR) is None
            else str(nlst_row[NLST_COL_MORTALITY_6YR])
        ),

        # Paths
        COL_RAW_IMAGE_PATH: nlst_row.get(NLST_COL_DICOM_REL_PATH),
        COL_PREPROCESSED_IMAGE_PATH: None,
        COL_LABEL_MASK_PATH: None,
    }

    # 2) Delegate to the generic builder for normalization & CTMetadataRow creation
    return build_ct_metadata_row(canonical)
