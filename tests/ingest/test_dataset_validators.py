"""
tests/ingest/test_dataset_validators.py

Tests for dataset-level metadata validation.

These validators operate on a collection of CTMetadataRow objects and
check "bigger picture" issues such as:

- non-positive spacing or image sizes
- missing or empty raw_image_path
- malformed acquisition_date strings
"""

from typing import Any, Dict, List

import re
import pytest

from src.ingest.metadata_schema import (
    CTMetadataRow,
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
)
from src.ingest.dataset_validators import (
    validate_dataset_metadata,
    assert_valid_dataset_metadata,
)


def make_valid_row_dict(dataset_name: str = "NLST") -> Dict[str, Any]:
    """
    Construct a dict representing a single valid CT series row using
    canonical column names.

    This helper lets us easily tweak fields to test specific validation
    failure cases.
    """
    return {
        COL_DATASET_NAME: dataset_name,
        COL_PATIENT_ID: f"{dataset_name}_P0001",
        COL_SCAN_ID: f"{dataset_name}__{dataset_name}_P0001__1.2.3",
        COL_STUDY_UID: "1.2.3.4.5",
        COL_SERIES_UID: "1.2.3.4.5.6",
        COL_MODALITY: "CT",
        COL_ACQUISITION_DATE: "2010-06-05",
        COL_SLICE_THICKNESS_MM: 1.25,
        COL_SPACING_X_MM: 0.7,
        COL_SPACING_Y_MM: 0.7,
        COL_SPACING_Z_MM: 1.25,
        COL_IMAGE_SIZE_X: 512,
        COL_IMAGE_SIZE_Y: 512,
        COL_IMAGE_SIZE_Z: 350,
        COL_LABEL_PRIMARY_NAME: "dummy_label",
        COL_LABEL_PRIMARY_VALUE: "0",
        COL_RAW_IMAGE_PATH: "raw/NLST/NLST_P0001/series_001/",
        COL_PREPROCESSED_IMAGE_PATH: "preprocessed/NLST/NLST_P0001/series_001.nii.gz",
        COL_LABEL_MASK_PATH: None,
    }


def make_valid_row(dataset_name: str = "NLST") -> CTMetadataRow:
    """Return a CTMetadataRow instance that should pass all validations."""
    return CTMetadataRow.from_dict(make_valid_row_dict(dataset_name))


# ---------------------------------------------------------------------------
# Basic "happy path" test
# ---------------------------------------------------------------------------

def test_validate_dataset_metadata_accepts_valid_rows() -> None:
    rows: List[CTMetadataRow] = [
        make_valid_row("NLST"),
        make_valid_row("COPDGene"),
        make_valid_row("LIDC-IDRI"),
    ]

    errors = validate_dataset_metadata(rows)

    assert errors == [], f"Expected no validation errors, got: {errors}"


# ---------------------------------------------------------------------------
# Tests for specific failure modes
# ---------------------------------------------------------------------------

def test_validator_flags_non_positive_spacing_and_sizes() -> None:
    """
    If spacing or image sizes are 0 or negative (when not None),
    the validator should report an error.
    """
    row_dict = make_valid_row_dict("NLST")
    row_dict[COL_SPACING_Z_MM] = 0.0   # invalid
    row_dict[COL_IMAGE_SIZE_X] = -1    # invalid

    row = CTMetadataRow.from_dict(row_dict)

    errors = validate_dataset_metadata([row])

    # Expect at least one error mentioning dataset and scan_id
    assert errors, "Expected validation errors for invalid spacing/size."
    msg = "\n".join(errors)
    assert "NLST" in msg
    assert row.scan_id in msg
    assert "non-positive" in msg.lower()


def test_validator_flags_missing_raw_image_path() -> None:
    """
    raw_image_path is critical for reproducibility; if it is None or empty,
    the validator should report an error.
    """
    row_dict = make_valid_row_dict("COPDGene")
    row_dict[COL_RAW_IMAGE_PATH] = None

    row = CTMetadataRow.from_dict(row_dict)
    errors = validate_dataset_metadata([row])

    assert errors, "Expected validation errors for missing raw_image_path."
    msg = errors[0].lower()
    assert "raw_image_path" in msg
    assert "missing or empty" in msg


def test_validator_flags_bad_acquisition_date_format() -> None:
    """
    acquisition_date should either be None or in ISO 'YYYY-MM-DD' form.
    Any other non-empty string should be flagged.
    """
    row_dict = make_valid_row_dict("LIDC-IDRI")
    row_dict[COL_ACQUISITION_DATE] = "06/05/2010"  # invalid format

    row = CTMetadataRow.from_dict(row_dict)
    errors = validate_dataset_metadata([row])

    assert errors, "Expected validation errors for bad acquisition_date format."
    msg = "\n".join(errors).lower()
    assert "acquisition_date" in msg
    assert "iso" in msg or "yyyy-mm-dd" in msg


def test_assert_valid_dataset_metadata_raises_on_errors() -> None:
    """
    assert_valid_dataset_metadata should raise a ValueError if validation
    finds any errors, and include those error messages in the exception text.
    """
    row_dict = make_valid_row_dict("NLST")
    row_dict[COL_RAW_IMAGE_PATH] = ""  # invalid: empty string
    row = CTMetadataRow.from_dict(row_dict)

    with pytest.raises(ValueError) as excinfo:
        assert_valid_dataset_metadata([row])

    msg = str(excinfo.value).lower()
    assert "validation errors" in msg
    assert "raw_image_path" in msg
    assert "missing or empty" in msg
