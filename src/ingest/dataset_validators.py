"""
src/ingest/dataset_validators.py

Dataset-level validators for CT metadata.

These functions operate on collections of CTMetadataRow objects and
look for "bigger picture" issues that go beyond simple schema checks.

Examples of what we validate here:
- Non-positive spacing or image dimensions (when values are present).
- Missing or empty raw_image_path.
- acquisition_date not in ISO 'YYYY-MM-DD' format (when non-empty).

They are deliberately conservative and return human-readable error
messages rather than silently fixing problems. Callers can either:

- inspect the list of errors, or
- use assert_valid_dataset_metadata() to raise if any errors exist.
"""

from __future__ import annotations

import re
from typing import Iterable, List

from .metadata_schema import (
    CTMetadataRow,
    COL_DATASET_NAME,
    COL_SCAN_ID,
    COL_SLICE_THICKNESS_MM,
    COL_SPACING_X_MM,
    COL_SPACING_Y_MM,
    COL_SPACING_Z_MM,
    COL_IMAGE_SIZE_X,
    COL_IMAGE_SIZE_Y,
    COL_IMAGE_SIZE_Z,
    COL_RAW_IMAGE_PATH,
    COL_ACQUISITION_DATE,
)


# Precompiled regex for ISO date validation (YYYY-MM-DD)
ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _row_prefix(row: CTMetadataRow) -> str:
    """
    Short prefix to identify a row in error messages.

    Example: "[NLST scan NLST__NLST_P0001__1.2.3]"
    """
    dataset = getattr(row, "dataset_name", "UNKNOWN_DATASET")
    scan_id = getattr(row, "scan_id", "UNKNOWN_SCAN")
    return f"[{dataset} scan {scan_id}]"


def validate_dataset_metadata(rows: Iterable[CTMetadataRow]) -> List[str]:
    """
    Validate a collection of CTMetadataRow objects and return a list
    of human-readable error messages.

    No exception is raised here; callers can inspect the returned list.
    For a stricter behavior, see assert_valid_dataset_metadata().
    """
    errors: List[str] = []

    for row in rows:
        prefix = _row_prefix(row)

        # --- Spacing and slice thickness ---
        for col_name in (
            COL_SLICE_THICKNESS_MM,
            COL_SPACING_X_MM,
            COL_SPACING_Y_MM,
            COL_SPACING_Z_MM,
        ):
            value = getattr(row, col_name)
            if value is not None and value <= 0:
                errors.append(
                    f"{prefix} has non-positive {col_name}={value!r}; "
                    "expected a positive value."
                )

        # --- Image dimensions ---
        for col_name in (COL_IMAGE_SIZE_X, COL_IMAGE_SIZE_Y, COL_IMAGE_SIZE_Z):
            value = getattr(row, col_name)
            if value is not None and value <= 0:
                errors.append(
                    f"{prefix} has non-positive {col_name}={value!r}; "
                    "expected a positive integer."
                )

        # --- raw_image_path presence ---
        raw_path = getattr(row, "raw_image_path", None)
        if raw_path is None or (isinstance(raw_path, str) and raw_path.strip() == ""):
            errors.append(
                f"{prefix} has raw_image_path missing or empty; this field is "
                "required for reproducible data loading."
            )

        # --- acquisition_date ISO format ---
        acq_date = getattr(row, "acquisition_date", None)
        if acq_date:
            # Only check non-empty strings
            if not ISO_DATE_PATTERN.match(acq_date):
                errors.append(
                    f"{prefix} has acquisition_date={acq_date!r} which is not in "
                    "ISO 'YYYY-MM-DD' format."
                )

    return errors


def assert_valid_dataset_metadata(rows: Iterable[CTMetadataRow]) -> None:
    """
    Validate the given rows and raise ValueError if any validation errors
    are found. The exception message contains a concatenated summary of
    all error messages.
    """
    errors = validate_dataset_metadata(rows)

    if errors:
        joined = "\n".join(errors)
        raise ValueError(
            f"Dataset metadata validation errors detected:\n{joined}"
        )
