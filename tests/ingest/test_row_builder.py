"""
tests/ingest/test_row_builder.py

Tests for the dataset-agnostic metadata row builder.

The idea:
- Dataset-specific loaders (NLST, COPDGene, LIDC-IDRI) will produce
  a "raw" dict of values (maybe slightly messy).
- The row_builder module normalizes those values into canonical form
  and constructs a CTMetadataRow instance.

These tests cover:
- normalization of sex labels
- normalization of smoking status labels
- normalization of acquisition dates
- construction of scan_id when missing
- forcing raw_image_path to be relative
- an end-to-end build_ct_metadata_row() call
"""

from typing import Any, Dict

import pytest

from src.ingest.metadata_schema import (
    CTMetadataRow,
    Sex,
    SmokingStatus,
    COL_DATASET_NAME,
    COL_PATIENT_ID,
    COL_SCAN_ID,
    COL_SERIES_UID,
    COL_MODALITY,
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
    COL_PREPROCESSED_IMAGE_PATH,
    COL_LABEL_MASK_PATH,
    COL_SEX,
    COL_SMOKING_STATUS,
)

from src.ingest.row_builder import (
    normalize_sex,
    normalize_smoking_status,
    normalize_acquisition_date,
    build_scan_id,
    ensure_relative_path,
    build_ct_metadata_row,
)


# ---------------------------------------------------------------------------
# Helper for end-to-end tests
# ---------------------------------------------------------------------------

def make_raw_row_minimal() -> Dict[str, Any]:
    """
    Return a "raw" metadata dict that resembles what a dataset-specific
    loader might produce BEFORE normalization.

    Notes:
    - We intentionally use slightly messy values (e.g., 'Female', 'current smoker')
      that the row_builder is expected to normalize.
    - We omit scan_id to test automatic construction.
    """
    return {
        COL_DATASET_NAME: "NLST",
        COL_PATIENT_ID: "NLST_P0001",
        # COL_SCAN_ID is deliberately omitted to test build_scan_id
        COL_SERIES_UID: "1.2.3.4.5.6",
        COL_MODALITY: "ct",  # lower-case; row_builder should not rely on case
        COL_ACQUISITION_DATE: "20050312",  # yyyymmdd format

        COL_SLICE_THICKNESS_MM: 1.25,
        COL_SPACING_X_MM: 0.7,
        COL_SPACING_Y_MM: 0.7,
        COL_SPACING_Z_MM: 1.25,
        COL_IMAGE_SIZE_X: 512,
        COL_IMAGE_SIZE_Y: 512,
        COL_IMAGE_SIZE_Z: 350,

        COL_LABEL_PRIMARY_NAME: "mortality_6yr",
        COL_LABEL_PRIMARY_VALUE: "1",

        COL_RAW_IMAGE_PATH: "/raw/NLST/NLST_P0001/series_001/",
        COL_PREPROCESSED_IMAGE_PATH: "preprocessed/NLST/NLST_P0001/series_001.nii.gz",
        COL_LABEL_MASK_PATH: None,

        # Slightly messy clinical fields to test normalization
        COL_SEX: "Female",
        COL_SMOKING_STATUS: "current smoker",
    }


# ---------------------------------------------------------------------------
# Unit tests for individual normalization helpers
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "input_value, expected",
    [
        ("M", Sex.MALE.value),
        ("m", Sex.MALE.value),
        ("Male", Sex.MALE.value),
        ("F", Sex.FEMALE.value),
        ("female", Sex.FEMALE.value),
        ("FEMALE", Sex.FEMALE.value),
        ("other", Sex.OTHER.value),
        (None, Sex.UNKNOWN.value),
        ("", Sex.UNKNOWN.value),
        ("nonsense", Sex.UNKNOWN.value),
    ],
)
def test_normalize_sex(input_value: str, expected: str) -> None:
    assert normalize_sex(input_value) == expected


@pytest.mark.parametrize(
    "input_value, expected",
    [
        ("Never", SmokingStatus.NEVER.value),
        ("never smoker", SmokingStatus.NEVER.value),
        ("NEVER", SmokingStatus.NEVER.value),
        ("Former", SmokingStatus.FORMER.value),
        ("ex-smoker", SmokingStatus.FORMER.value),
        ("Current", SmokingStatus.CURRENT.value),
        ("current smoker", SmokingStatus.CURRENT.value),
        (None, SmokingStatus.UNKNOWN.value),
        ("", SmokingStatus.UNKNOWN.value),
        ("weird_value", SmokingStatus.UNKNOWN.value),
    ],
)
def test_normalize_smoking_status(input_value: str, expected: str) -> None:
    assert normalize_smoking_status(input_value) == expected


@pytest.mark.parametrize(
    "input_value, expected",
    [
        ("20050312", "2005-03-12"),      # yyyymmdd
        ("2005-03-12", "2005-03-12"),    # already iso
        (None, None),
        ("", None),
    ],
)
def test_normalize_acquisition_date(input_value: str, expected: str) -> None:
    assert normalize_acquisition_date(input_value) == expected


def test_build_scan_id_uses_expected_pattern() -> None:
    """
    build_scan_id should construct scan_id using the pattern:
        <dataset_name>__<patient_id>__<series_uid>
    """
    scan_id = build_scan_id("NLST", "NLST_P0001", "1.2.3.4")
    assert scan_id == "NLST__NLST_P0001__1.2.3.4"


@pytest.mark.parametrize(
    "input_path, expected",
    [
        ("raw/NLST/NLST_P0001/series_001/", "raw/NLST/NLST_P0001/series_001/"),
        ("/raw/NLST/NLST_P0001/series_001/", "raw/NLST/NLST_P0001/series_001/"),
        ("", ""),
        (None, None),
    ],
)
def test_ensure_relative_path(input_path: str, expected: str) -> None:
    """
    ensure_relative_path should:
    - strip a leading '/' if present (so paths are relative to data_root)
    - otherwise leave the string unchanged
    - propagate None unchanged
    """
    assert ensure_relative_path(input_path) == expected


# ---------------------------------------------------------------------------
# End-to-end test for build_ct_metadata_row
# ---------------------------------------------------------------------------

def test_build_ct_metadata_row_end_to_end() -> None:
    """
    build_ct_metadata_row should:
    - normalize sex and smoking status
    - normalize acquisition date
    - construct scan_id if missing
    - ensure raw_image_path is relative
    - return a CTMetadataRow instance
    """
    raw = make_raw_row_minimal()

    row = build_ct_metadata_row(raw)

    assert isinstance(row, CTMetadataRow)

    # Scan ID should have been constructed
    assert row.scan_id == "NLST__NLST_P0001__1.2.3.4.5.6"

    # Acquisition date should be normalized to YYYY-MM-DD
    assert row.acquisition_date == "2005-03-12"

    # Sex and smoking status should be normalized to enum values
    assert row.sex == Sex.FEMALE.value
    assert row.smoking_status == SmokingStatus.CURRENT.value

    # Raw image path should be relative (no leading slash)
    assert not row.raw_image_path.startswith("/")
    assert row.raw_image_path == "raw/NLST/NLST_P0001/series_001/"
