"""
tests/ingest/test_nlst_ingest.py

Tests for NLST-specific ingestion helpers.

Scope of these tests
--------------------
We do NOT read real NLST files here.

Instead, we pretend we already have a single "raw NLST row" dict
with NLST-specific column names (as you might get from a CSV or a
pre-aggregated table), and we:

    NLST row dict  --->  nlst_row_to_ct_metadata()  --->  CTMetadataRow

The goal is to:
- document the mapping between NLST field names and canonical schema
- exercise build_ct_metadata_row() in a concrete dataset setting
- give you a safe place to update NLST mappings later
"""

from typing import Any, Dict

from src.ingest.metadata_schema import (
    CTMetadataRow,
    COL_DATASET_NAME,
    COL_PATIENT_ID,
    COL_SERIES_UID,
    COL_LABEL_PRIMARY_NAME,
    COL_LABEL_PRIMARY_VALUE,
    COL_RAW_IMAGE_PATH,
    COL_SLICE_THICKNESS_MM,
    COL_SPACING_X_MM,
    COL_SPACING_Y_MM,
    COL_SPACING_Z_MM,
    COL_IMAGE_SIZE_X,
    COL_IMAGE_SIZE_Y,
    COL_IMAGE_SIZE_Z,
    COL_ACQUISITION_DATE,
)
from src.ingest.nlst_ingest import (
    NLST_COL_PATIENT_ID,
    NLST_COL_STUDY_INSTANCE_UID,
    NLST_COL_SERIES_INSTANCE_UID,
    NLST_COL_MORTALITY_6YR,
    NLST_COL_ACQUISITION_DATE,
    NLST_COL_SLICE_THICKNESS_MM,
    NLST_COL_PIXEL_SPACING_X_MM,
    NLST_COL_PIXEL_SPACING_Y_MM,
    NLST_COL_SPACING_BETWEEN_SLICES_MM,
    NLST_COL_NUM_COLUMNS,
    NLST_COL_NUM_ROWS,
    NLST_COL_NUM_SLICES,
    NLST_COL_DICOM_REL_PATH,
    nlst_row_to_ct_metadata,
)


def make_fake_nlst_row() -> Dict[str, Any]:
    """
    Construct a fake NLST metadata row with NLST-style field names.

    NOTE:
    - These NLST_* column names are "project-local" conventions for now.
      When you inspect real NLST tables, you can update these constants
      and this helper without touching other code.
    """
    return {
        NLST_COL_PATIENT_ID: "NLST-0001",
        NLST_COL_STUDY_INSTANCE_UID: "1.2.840.113619.2.55.3.283",
        NLST_COL_SERIES_INSTANCE_UID: "1.2.840.113619.2.55.3.283.1",
        NLST_COL_MORTALITY_6YR: 1,
        NLST_COL_ACQUISITION_DATE: "20050312",  # compact yyyymmdd; will be normalized
        NLST_COL_SLICE_THICKNESS_MM: 1.25,
        NLST_COL_PIXEL_SPACING_X_MM: 0.7,
        NLST_COL_PIXEL_SPACING_Y_MM: 0.7,
        NLST_COL_SPACING_BETWEEN_SLICES_MM: 1.25,
        NLST_COL_NUM_COLUMNS: 512,
        NLST_COL_NUM_ROWS: 512,
        NLST_COL_NUM_SLICES: 350,
        NLST_COL_DICOM_REL_PATH: "/raw/NLST/NLST-0001/series_001/",  # leading '/' on purpose
    }


def test_nlst_row_to_ct_metadata_basic_mapping() -> None:
    """
    nlst_row_to_ct_metadata should correctly map NLST-specific field names
    into the canonical schema and return a CTMetadataRow.
    """
    nlst_row = make_fake_nlst_row()

    row: CTMetadataRow = nlst_row_to_ct_metadata(nlst_row)

    # Basic identity fields
    assert row.dataset_name == "NLST"
    assert row.patient_id == nlst_row[NLST_COL_PATIENT_ID]
    assert row.series_uid == nlst_row[NLST_COL_SERIES_INSTANCE_UID]

    # Label mapping
    assert row.label_primary_name == "mortality_6yr"
    # We store label values as strings in the canonical schema
    assert row.label_primary_value == "1"

    # Geometry mapping
    assert row.slice_thickness_mm == nlst_row[NLST_COL_SLICE_THICKNESS_MM]
    assert row.spacing_x_mm == nlst_row[NLST_COL_PIXEL_SPACING_X_MM]
    assert row.spacing_y_mm == nlst_row[NLST_COL_PIXEL_SPACING_Y_MM]
    assert row.spacing_z_mm == nlst_row[NLST_COL_SPACING_BETWEEN_SLICES_MM]
    assert row.image_size_x == nlst_row[NLST_COL_NUM_COLUMNS]
    assert row.image_size_y == nlst_row[NLST_COL_NUM_ROWS]
    assert row.image_size_z == nlst_row[NLST_COL_NUM_SLICES]

    # Acquisition date should be normalized to ISO
    assert row.acquisition_date == "2005-03-12"

    # Raw image path should be relative (no leading '/')
    assert not row.raw_image_path.startswith("/")
    assert row.raw_image_path == "raw/NLST/NLST-0001/series_001/"


def test_nlst_row_to_ct_metadata_produces_canonical_dict_keys() -> None:
    """
    As a sanity check, convert the CTMetadataRow back to a dict and make
    sure the expected canonical keys are present and aligned with NLST input.
    """
    nlst_row = make_fake_nlst_row()
    row = nlst_row_to_ct_metadata(nlst_row)
    d = row.to_dict()

    assert d[COL_DATASET_NAME] == "NLST"
    assert d[COL_PATIENT_ID] == nlst_row[NLST_COL_PATIENT_ID]
    assert d[COL_SERIES_UID] == nlst_row[NLST_COL_SERIES_INSTANCE_UID]
    assert d[COL_LABEL_PRIMARY_NAME] == "mortality_6yr"
    assert d[COL_LABEL_PRIMARY_VALUE] == "1"
    assert d[COL_RAW_IMAGE_PATH] == "raw/NLST/NLST-0001/series_001/"

    # geometry again, via canonical column names
    assert d[COL_SLICE_THICKNESS_MM] == nlst_row[NLST_COL_SLICE_THICKNESS_MM]
    assert d[COL_SPACING_X_MM] == nlst_row[NLST_COL_PIXEL_SPACING_X_MM]
    assert d[COL_SPACING_Y_MM] == nlst_row[NLST_COL_PIXEL_SPACING_Y_MM]
    assert d[COL_SPACING_Z_MM] == nlst_row[NLST_COL_SPACING_BETWEEN_SLICES_MM]
    assert d[COL_IMAGE_SIZE_X] == nlst_row[NLST_COL_NUM_COLUMNS]
    assert d[COL_IMAGE_SIZE_Y] == nlst_row[NLST_COL_NUM_ROWS]
    assert d[COL_IMAGE_SIZE_Z] == nlst_row[NLST_COL_NUM_SLICES]
    assert d[COL_ACQUISITION_DATE] == "2005-03-12"
