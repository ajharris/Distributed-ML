"""
tests/ingest/test_metadata_schema_constants.py

Tests for the canonical CT metadata schema constants.

GOALS OF THESE TESTS
--------------------
1. Make sure the required column lists are correct and stable.
2. Ensure there are no duplicate column names.
3. Ensure every column in REQUIRED_COLUMNS and OPTIONAL_CLINICAL_COLUMNS
   has an entry in METADATA_COLUMN_DTYPES.
4. Sanity-check the expected dtype mapping (e.g., IDs are strings,
   image sizes are ints, etc.).
5. Check that the enums for Sex, SmokingStatus, and COPDStatus
   expose the expected values.

These tests are intentionally "low-level" but they give us:
- a safety net against accidental renaming/typos
- clear documentation of what the schema is supposed to look like
"""

from typing import Set, Type

import pytest

from src.ingest.metadata_schema import (
    # Column name constants (just a few key ones for sanity checks)
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
    COL_AGE_AT_SCAN_YEARS,
    COL_SEX,
    COL_SMOKING_STATUS,
    COL_PACK_YEARS,
    COL_MORTALITY_6YR,

    # Grouped column sets
    REQUIRED_COLUMNS,
    OPTIONAL_CLINICAL_COLUMNS,
    ALL_COLUMNS,

    # Dtype mapping
    METADATA_COLUMN_DTYPES,

    # Enums
    Sex,
    SmokingStatus,
    COPDStatus,
)


# ---------------------------------------------------------------------------
# Helper utilities for tests
# ---------------------------------------------------------------------------

def assert_no_duplicates(values: list[str]) -> None:
    """
    Helper to assert that a list of strings has no duplicates.

    This is important for schema column names because:
    - duplicates can silently shadow each other
    - Parquet / DataFrame code can behave strangely
    """
    as_set: Set[str] = set(values)
    assert len(as_set) == len(values), f"Found duplicate values in list: {values}"


# ---------------------------------------------------------------------------
# Tests for basic column list structure
# ---------------------------------------------------------------------------

def test_required_columns_not_empty() -> None:
    """REQUIRED_COLUMNS should not be empty and should contain key identity fields."""
    assert len(REQUIRED_COLUMNS) > 0, "REQUIRED_COLUMNS should not be empty."

    # Spot-check a few core columns that MUST be required.
    assert COL_DATASET_NAME in REQUIRED_COLUMNS
    assert COL_PATIENT_ID in REQUIRED_COLUMNS
    assert COL_SCAN_ID in REQUIRED_COLUMNS
    assert COL_SERIES_UID in REQUIRED_COLUMNS
    assert COL_MODALITY in REQUIRED_COLUMNS
    assert COL_ACQUISITION_DATE in REQUIRED_COLUMNS


def test_optional_columns_not_empty() -> None:
    """OPTIONAL_CLINICAL_COLUMNS should not be empty and should contain some core clinical fields."""
    assert len(OPTIONAL_CLINICAL_COLUMNS) > 0, "OPTIONAL_CLINICAL_COLUMNS should not be empty."

    # Spot-check a few expected optional clinical columns.
    assert COL_AGE_AT_SCAN_YEARS in OPTIONAL_CLINICAL_COLUMNS
    assert COL_SEX in OPTIONAL_CLINICAL_COLUMNS
    assert COL_SMOKING_STATUS in OPTIONAL_CLINICAL_COLUMNS
    assert COL_PACK_YEARS in OPTIONAL_CLINICAL_COLUMNS
    assert COL_MORTALITY_6YR in OPTIONAL_CLINICAL_COLUMNS


def test_all_columns_is_union_of_required_and_optional() -> None:
    """
    ALL_COLUMNS should be exactly the union of REQUIRED_COLUMNS and OPTIONAL_CLINICAL_COLUMNS.

    This test catches:
    - columns present in ALL_COLUMNS but not in required/optional lists
    - columns missing from ALL_COLUMNS
    """
    required_set = set(REQUIRED_COLUMNS)
    optional_set = set(OPTIONAL_CLINICAL_COLUMNS)
    all_set = set(ALL_COLUMNS)

    assert all_set == required_set.union(optional_set), (
        "ALL_COLUMNS must be exactly the union of REQUIRED_COLUMNS "
        "and OPTIONAL_CLINICAL_COLUMNS."
    )


def test_no_duplicate_columns_anywhere() -> None:
    """
    There should be no duplicate column names in:
    - REQUIRED_COLUMNS
    - OPTIONAL_CLINICAL_COLUMNS
    - ALL_COLUMNS
    """
    assert_no_duplicates(REQUIRED_COLUMNS)
    assert_no_duplicates(OPTIONAL_CLINICAL_COLUMNS)
    assert_no_duplicates(ALL_COLUMNS)


def test_required_and_optional_do_not_overlap() -> None:
    """Required columns and optional clinical columns should be disjoint sets."""
    overlap = set(REQUIRED_COLUMNS) & set(OPTIONAL_CLINICAL_COLUMNS)
    assert (
        not overlap
    ), f"Required and optional columns should not overlap, but found: {overlap}"


# ---------------------------------------------------------------------------
# Tests for METADATA_COLUMN_DTYPES mapping
# ---------------------------------------------------------------------------

def test_all_known_columns_have_dtypes() -> None:
    """
    Every column in REQUIRED_COLUMNS and OPTIONAL_CLINICAL_COLUMNS
    must have an entry in METADATA_COLUMN_DTYPES.

    If this test fails, someone added a new column name but forgot
    to specify its expected dtype.
    """
    for col in ALL_COLUMNS:
        assert col in METADATA_COLUMN_DTYPES, (
            f"Column '{col}' is missing from METADATA_COLUMN_DTYPES."
        )


def test_no_extra_dtypes_for_unknown_columns() -> None:
    """
    Conversely, METADATA_COLUMN_DTYPES should not contain keys that
    are not present in ALL_COLUMNS. This helps catch typos in the
    dtype mapping itself.
    """
    extra_cols = set(METADATA_COLUMN_DTYPES.keys()) - set(ALL_COLUMNS)
    assert (
        not extra_cols
    ), f"METADATA_COLUMN_DTYPES contains unknown columns: {extra_cols}"


@pytest.mark.parametrize(
    "col,expected_type",
    [
        (COL_DATASET_NAME, str),
        (COL_PATIENT_ID, str),
        (COL_SCAN_ID, str),
        (COL_SERIES_UID, str),
        (COL_MODALITY, str),
        (COL_ACQUISITION_DATE, str),
        (COL_RAW_IMAGE_PATH, str),
        (COL_PREPROCESSED_IMAGE_PATH, str),
        (COL_LABEL_MASK_PATH, str),
        (COL_SLICE_THICKNESS_MM, float),
        (COL_SPACING_X_MM, float),
        (COL_SPACING_Y_MM, float),
        (COL_SPACING_Z_MM, float),
        (COL_IMAGE_SIZE_X, int),
        (COL_IMAGE_SIZE_Y, int),
        (COL_IMAGE_SIZE_Z, int),
    ],
)
def test_selected_column_dtypes(col: str, expected_type: Type) -> None:
    """
    Spot-check that selected key columns have the expected logical dtypes.

    NOTE: This test is not exhaustive, but it's a useful sanity check.
    """
    assert METADATA_COLUMN_DTYPES[col] is expected_type, (
        f"Column '{col}' expected type {expected_type}, "
        f"found {METADATA_COLUMN_DTYPES[col]}."
    )


def test_label_primary_columns_have_dtypes() -> None:
    """
    Check that label name and value columns have dtypes defined.

    We expect:
    - label_primary_name: str
    - label_primary_value: str (even if underlying data may be numeric)
    """
    assert METADATA_COLUMN_DTYPES[COL_LABEL_PRIMARY_NAME] is str
    assert METADATA_COLUMN_DTYPES[COL_LABEL_PRIMARY_VALUE] is str


def test_boolean_like_columns_are_int_or_bool() -> None:
    """
    Some columns represent boolean / 0-1 indicators.
    We store them as int in the dtype mapping, but in general
    we will accept either int or bool at the DataFrame level.

    This test checks that the dtype mapping uses 'int' for these fields.
    """
    boolean_like_cols = [
        COL_MORTALITY_6YR,
        # If you add more boolean-like fields (mortality_5yr, lung_cancer_diagnosis, etc.),
        # you can include them here as well.
    ]

    for col in boolean_like_cols:
        dtype = METADATA_COLUMN_DTYPES[col]
        assert dtype is int, (
            f"Boolean-like column '{col}' should be mapped to int in "
            f"METADATA_COLUMN_DTYPES, got {dtype} instead."
        )


# ---------------------------------------------------------------------------
# Tests for Enums (Sex, SmokingStatus, COPDStatus)
# ---------------------------------------------------------------------------

def test_sex_enum_values() -> None:
    """
    The Sex enum should expose the expected normalized string values.

    This test serves as both documentation and a correctness check.
    """
    assert Sex.MALE.value == "M"
    assert Sex.FEMALE.value == "F"
    assert Sex.OTHER.value == "Other"
    assert Sex.UNKNOWN.value == "Unknown"

    # Ensure all values are unique
    values = {member.value for member in Sex}
    assert len(values) == len(list(Sex)), "Sex enum has duplicate values."


def test_smoking_status_enum_values() -> None:
    """
    The SmokingStatus enum should expose the expected normalized labels.
    """
    assert SmokingStatus.NEVER.value == "Never"
    assert SmokingStatus.FORMER.value == "Former"
    assert SmokingStatus.CURRENT.value == "Current"
    assert SmokingStatus.UNKNOWN.value == "Unknown"

    values = {member.value for member in SmokingStatus}
    assert len(values) == len(list(SmokingStatus)), "SmokingStatus enum has duplicate values."


def test_copd_status_enum_values() -> None:
    """
    The COPDStatus enum should expose the expected high-level COPD labels.
    """
    assert COPDStatus.COPD.value == "COPD"
    assert COPDStatus.CONTROL.value == "Control"
    assert COPDStatus.AT_RISK.value == "At-risk"
    assert COPDStatus.UNKNOWN.value == "Unknown"

    values = {member.value for member in COPDStatus}
    assert len(values) == len(list(COPDStatus)), "COPDStatus enum has duplicate values."
