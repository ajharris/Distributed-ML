"""
src/ingest/row_builder.py

Dataset-agnostic helpers for building CT metadata rows.

Design:
- Dataset-specific loaders (e.g., nlst_loader.py, copdgene_loader.py)
  will gather raw values (sometimes messy or dataset-specific).
- This module provides small, focused normalization helpers and a
  high-level build_ct_metadata_row() function that:

    * normalizes sex and smoking status
    * normalizes acquisition dates
    * ensures raw/preprocessed paths are relative
    * constructs a scan_id if missing
    * returns a validated CTMetadataRow instance

The goal is to keep all "generic" logic here so each dataset loader
can stay simple and focused on parsing its own files.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from .metadata_schema import (
    CTMetadataRow,
    Sex,
    SmokingStatus,
    # Column names
    COL_DATASET_NAME,
    COL_PATIENT_ID,
    COL_SCAN_ID,
    COL_STUDY_UID,
    COL_SERIES_UID,
    COL_ACQUISITION_DATE,
    COL_RAW_IMAGE_PATH,
    COL_PREPROCESSED_IMAGE_PATH,
    COL_LABEL_MASK_PATH,
    COL_SEX,
    COL_SMOKING_STATUS,
    REQUIRED_COLUMNS,
)


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

def normalize_sex(value: Optional[str]) -> str:
    """
    Normalize various sex encodings into canonical values defined in Sex enum.

    Examples:
    - 'M', 'm', 'Male'       -> 'M'
    - 'F', 'female', 'FEMALE'-> 'F'
    - 'other'                -> 'Other'
    - None, '', unknown text -> 'Unknown'
    """
    if value is None:
        return Sex.UNKNOWN.value

    v = value.strip().lower()
    if v in {"m", "male"}:
        return Sex.MALE.value
    if v in {"f", "female"}:
        return Sex.FEMALE.value
    if v in {"other", "nonbinary", "non-binary"}:
        return Sex.OTHER.value

    return Sex.UNKNOWN.value


def normalize_smoking_status(value: Optional[str]) -> str:
    """
    Normalize various smoking status encodings into canonical values
    defined in SmokingStatus enum.

    Examples:
    - 'never', 'never smoker'    -> 'Never'
    - 'former', 'ex-smoker'      -> 'Former'
    - 'current', 'current smoker'-> 'Current'
    - None, '', unknown text     -> 'Unknown'
    """
    if value is None:
        return SmokingStatus.UNKNOWN.value

    v = value.strip().lower()

    # Never smoker
    if v in {"never", "never smoker", "non-smoker", "nonsmoker"}:
        return SmokingStatus.NEVER.value

    # Former smoker
    if v in {"former", "ex-smoker", "ex smoker", "former smoker"}:
        return SmokingStatus.FORMER.value

    # Current smoker
    if v in {"current", "current smoker", "smoker"}:
        return SmokingStatus.CURRENT.value

    return SmokingStatus.UNKNOWN.value


def normalize_acquisition_date(value: Optional[str]) -> Optional[str]:
    """
    Normalize acquisition date to 'YYYY-MM-DD' (ISO date) or None.

    Supported input formats:
    - None or empty string -> None
    - 'YYYY-MM-DD'         -> unchanged
    - 'YYYYMMDD'           -> converted to 'YYYY-MM-DD'

    This function is intentionally conservative; if a format is not
    recognized, it raises a ValueError so that dataset loaders must
    explicitly handle unusual date formats.
    """
    if value is None:
        return None

    v = value.strip()
    if not v:
        return None

    # Already in ISO form
    if len(v) == 10 and v[4] == "-" and v[7] == "-":
        # quick sanity check this is actually a date
        datetime.strptime(v, "%Y-%m-%d")
        return v

    # Compact yyyymmdd form
    if len(v) == 8 and v.isdigit():
        dt = datetime.strptime(v, "%Y%m%d")
        return dt.strftime("%Y-%m-%d")

    raise ValueError(f"Unsupported acquisition_date format: {value!r}")


def build_scan_id(dataset_name: str, patient_id: str, series_uid: str) -> str:
    """
    Construct a canonical scan_id string using the pattern:

        <dataset_name>__<patient_id>__<series_uid>

    This pattern is documented in docs/methodology.md and is used
    consistently across the project.
    """
    return f"{dataset_name}__{patient_id}__{series_uid}"


def ensure_relative_path(path: Optional[str]) -> Optional[str]:
    """
    Ensure that a filesystem path is relative (no leading '/').

    Rationale:
    - All paths stored in metadata should be relative to the project-wide
      data_root defined in config/paths.yml.
    - This makes the metadata portable across machines.

    Behavior:
    - If path is None -> return None
    - If path starts with '/' -> strip the leading '/'
    - Otherwise -> return path unchanged
    """
    if path is None:
        return None

    if path.startswith("/"):
        return path.lstrip("/")

    return path


# ---------------------------------------------------------------------------
# High-level builder
# ---------------------------------------------------------------------------

def build_ct_metadata_row(raw: Dict[str, Any]) -> CTMetadataRow:
    """
    Build a CTMetadataRow from a "raw" metadata dict.

    Responsibilities:
    - Ensure all REQUIRED_COLUMNS (except scan_id, and study_uid which may be None) are present in `raw`.
    - If scan_id is missing, construct it via build_scan_id().
    - Normalize acquisition_date, sex, and smoking_status.
    - Ensure raw/preprocessed/label paths are relative.
    - Delegate final validation & field filling to CTMetadataRow.from_dict().
    """
    # 1) Make a shallow copy so we don't mutate caller's dict
    data = dict(raw)

    # 1a) Some required-but-nullable fields can be defaulted to None if missing
    #     (the column must exist, but the value is allowed to be null).
    if COL_STUDY_UID not in data:
        data[COL_STUDY_UID] = None

    # 2) Check for required columns (except scan_id and study_uid, which we handle specially)
    missing_required = [
        col
        for col in REQUIRED_COLUMNS
        if col not in data and col not in (COL_SCAN_ID, COL_STUDY_UID)
    ]
    if missing_required:
        raise ValueError(
            "Missing required columns in raw metadata before building row: "
            f"{missing_required}"
        )

    # 3) Construct scan_id if missing
    if COL_SCAN_ID not in data:
        dataset_name = data[COL_DATASET_NAME]
        patient_id = data[COL_PATIENT_ID]
        series_uid = data[COL_SERIES_UID]
        data[COL_SCAN_ID] = build_scan_id(dataset_name, patient_id, series_uid)

    # 4) Normalize acquisition date
    if COL_ACQUISITION_DATE in data:
        data[COL_ACQUISITION_DATE] = normalize_acquisition_date(
            data[COL_ACQUISITION_DATE]
        )

    # 5) Normalize sex and smoking status
    data[COL_SEX] = normalize_sex(data.get(COL_SEX))
    data[COL_SMOKING_STATUS] = normalize_smoking_status(
        data.get(COL_SMOKING_STATUS)
    )

    # 6) Ensure paths are relative (if present)
    if COL_RAW_IMAGE_PATH in data:
        data[COL_RAW_IMAGE_PATH] = ensure_relative_path(data[COL_RAW_IMAGE_PATH])

    if COL_PREPROCESSED_IMAGE_PATH in data:
        data[COL_PREPROCESSED_IMAGE_PATH] = ensure_relative_path(
            data[COL_PREPROCESSED_IMAGE_PATH]
        )

    if COL_LABEL_MASK_PATH in data:
        data[COL_LABEL_MASK_PATH] = ensure_relative_path(
            data[COL_LABEL_MASK_PATH]
        )

    # 7) Delegate to CTMetadataRow.from_dict for final construction
    return CTMetadataRow.from_dict(data)

    """
    Build a CTMetadataRow from a "raw" metadata dict.

    Responsibilities:
    - Ensure all REQUIRED_COLUMNS (except scan_id) are present in `raw`.
    - If scan_id is missing, construct it via build_scan_id().
    - Normalize acquisition_date, sex, and smoking_status.
    - Ensure raw/preprocessed/label paths are relative.
    - Delegate final validation & field filling to CTMetadataRow.from_dict().

    NOTE:
    - This function assumes that dataset-specific loaders have already
      mapped their original field names into our canonical column names.
    - It focuses on *generic* normalization that applies to all datasets.
    """
    # 1) Make a shallow copy so we don't mutate caller's dict
    data = dict(raw)

    # 2) Check for required columns (except scan_id which we can construct)
    missing_required = [
        col
        for col in REQUIRED_COLUMNS
        if col not in data and col != COL_SCAN_ID
    ]
    if missing_required:
        raise ValueError(
            f"Missing required columns in raw metadata before building row: "
            f"{missing_required}"
        )

    # 3) Construct scan_id if missing
    if COL_SCAN_ID not in data:
        dataset_name = data[COL_DATASET_NAME]
        patient_id = data[COL_PATIENT_ID]
        series_uid = data[COL_SERIES_UID]
        data[COL_SCAN_ID] = build_scan_id(dataset_name, patient_id, series_uid)

    # 4) Normalize acquisition date
    if COL_ACQUISITION_DATE in data:
        data[COL_ACQUISITION_DATE] = normalize_acquisition_date(
            data[COL_ACQUISITION_DATE]
        )

    # 5) Normalize sex and smoking status
    data[COL_SEX] = normalize_sex(data.get(COL_SEX))
    data[COL_SMOKING_STATUS] = normalize_smoking_status(
        data.get(COL_SMOKING_STATUS)
    )

    # 6) Ensure paths are relative (if present)
    if COL_RAW_IMAGE_PATH in data:
        data[COL_RAW_IMAGE_PATH] = ensure_relative_path(data[COL_RAW_IMAGE_PATH])

    if COL_PREPROCESSED_IMAGE_PATH in data:
        data[COL_PREPROCESSED_IMAGE_PATH] = ensure_relative_path(
            data[COL_PREPROCESSED_IMAGE_PATH]
        )

    if COL_LABEL_MASK_PATH in data:
        data[COL_LABEL_MASK_PATH] = ensure_relative_path(
            data[COL_LABEL_MASK_PATH]
        )

    # 7) Delegate to CTMetadataRow.from_dict for final construction
    return CTMetadataRow.from_dict(data)
