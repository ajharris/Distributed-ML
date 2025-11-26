"""
tests/ingest/test_ct_metadata_row.py

Tests for CTMetadataRow, the canonical in-memory representation
of a single CT metadata row.

These tests focus on:
- enforcing presence of required columns
- defaulting optional clinical fields to None
- round-tripping between dict <-> CTMetadataRow
"""

from typing import Any, Dict

import pytest

from src.ingest.metadata_schema import (
    # Column names & groupings
    REQUIRED_COLUMNS,
    OPTIONAL_CLINICAL_COLUMNS,
    ALL_COLUMNS,

    COL_DATASET_NAME,
    COL_PATIENT_ID,
    COL_SCAN_ID,
    COL_STUDY_UID,
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

    COL_AGE_AT_SCAN_YEARS,
    COL_SEX,
    COL_SMOKING_STATUS,

    # The dataclass itself
    CTMetadataRow,
)


def make_minimal_valid_row_dict() -> Dict[str, Any]:
    """
    Helper that returns the smallest possible dict that still satisfies
    all REQUIRED_COLUMNS.

    NOTE:
    - Values are toy examples; the goal is *structure*, not realism.
    - Optional clinical fields are intentionally omitted here to verify
      that they default to None.
    """
    return {
        COL_DATASET_NAME: "NLST",
        COL_PATIENT_ID: "NLST_P0001",
        COL_SCAN_ID: "NLST__NLST_P0001__1.2.3",
        COL_STUDY_UID: "1.2.840.113619.2.55.3.283",
        COL_SERIES_UID: "1.2.840.113619.2.55.3.283.1",
        COL_MODALITY: "CT",
        COL_ACQUISITION_DATE: "2005-03-12",
        COL_SLICE_THICKNESS_MM: 1.25,
        COL_SPACING_X_MM: 0.7,
        COL_SPACING_Y_MM: 0.7,
        COL_SPACING_Z_MM: 1.25,
        COL_IMAGE_SIZE_X: 512,
        COL_IMAGE_SIZE_Y: 512,
        COL_IMAGE_SIZE_Z: 350,
        COL_LABEL_PRIMARY_NAME: "mortality_6yr",
        COL_LABEL_PRIMARY_VALUE: "1",
        COL_RAW_IMAGE_PATH: "raw/NLST/NLST_P0001/series_001/",
        COL_PREPROCESSED_IMAGE_PATH: "preprocessed/NLST/NLST_P0001/series_001.nii.gz",
        COL_LABEL_MASK_PATH: None,
    }


# ---------------------------------------------------------------------------
# Required column validation
# ---------------------------------------------------------------------------

def test_from_dict_raises_if_required_column_missing() -> None:
    """
    CTMetadataRow.from_dict should raise a ValueError if any required
    column is missing in the input dict.
    """
    row_dict = make_minimal_valid_row_dict()

    # Remove one required column
    row_dict.pop(COL_SERIES_UID)

    with pytest.raises(ValueError) as excinfo:
        CTMetadataRow.from_dict(row_dict)

    msg = str(excinfo.value)
    assert "Missing required metadata columns" in msg
    assert COL_SERIES_UID in msg


def test_from_dict_accepts_minimal_valid_row() -> None:
    """
    CTMetadataRow.from_dict should successfully construct an object from
    a dict that contains all REQUIRED_COLUMNS.
    """
    row_dict = make_minimal_valid_row_dict()

    row = CTMetadataRow.from_dict(row_dict)

    # Spot-check a few fields
    assert row.dataset_name == "NLST"
    assert row.patient_id == "NLST_P0001"
    assert row.series_uid == "1.2.840.113619.2.55.3.283.1"
    assert row.raw_image_path == "raw/NLST/NLST_P0001/series_001/"


# ---------------------------------------------------------------------------
# Optional fields defaulting
# ---------------------------------------------------------------------------

def test_optional_clinical_fields_default_to_none() -> None:
    """
    When optional clinical columns are not present in the input dict,
    CTMetadataRow.from_dict should default them to None.
    """
    row_dict = make_minimal_valid_row_dict()
    # Make sure none of the optional clinical columns are present
    for col in OPTIONAL_CLINICAL_COLUMNS:
        row_dict.pop(col, None)

    row = CTMetadataRow.from_dict(row_dict)

    for col in OPTIONAL_CLINICAL_COLUMNS:
        value = getattr(row, col)
        assert value is None, f"Expected {col} to default to None, got {value!r}"


def test_optional_fields_can_be_provided() -> None:
    """
    Optional clinical fields may be provided in the input dict;
    from_dict should preserve these values on the CTMetadataRow.
    """
    row_dict = make_minimal_valid_row_dict()
    row_dict[COL_AGE_AT_SCAN_YEARS] = 63.0
    row_dict[COL_SEX] = "F"
    row_dict[COL_SMOKING_STATUS] = "Former"

    row = CTMetadataRow.from_dict(row_dict)

    assert row.age_at_scan_years == 63.0
    assert row.sex == "F"
    assert row.smoking_status == "Former"


# ---------------------------------------------------------------------------
# Round-trip dict <-> CTMetadataRow
# ---------------------------------------------------------------------------

def test_to_dict_round_trip_preserves_values() -> None:
    """
    Converting from dict -> CTMetadataRow -> dict should preserve values
    for all known columns (allowing missing optional fields to become None).
    """
    row_dict = make_minimal_valid_row_dict()
    row_dict[COL_AGE_AT_SCAN_YEARS] = 63.0

    row = CTMetadataRow.from_dict(row_dict)
    round_tripped = row.to_dict()

    # 1) All known columns should be present in the output dict
    assert set(round_tripped.keys()) == set(ALL_COLUMNS)

    # 2) Values that we set explicitly should be preserved
    for key, value in row_dict.items():
        assert round_tripped[key] == value, (
            f"Value for {key} did not survive round-trip. "
            f"Expected {value!r}, got {round_tripped[key]!r}"
        )

    # 3) Optional columns that were not set should exist and be None
    for col in OPTIONAL_CLINICAL_COLUMNS:
        if col not in row_dict:
            assert col in round_tripped
            assert round_tripped[col] is None
