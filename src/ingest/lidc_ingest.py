"""
src/ingest/lidc_ingest.py

LIDC-IDRI-specific ingestion helpers.

We assume a "raw LIDC row" dict with project-local LIDC-style column names,
and map it into the canonical CTMetadataRow via build_ct_metadata_row().
"""

from __future__ import annotations

from typing import Any, Dict

from .metadata_schema import (
    CTMetadataRow,
    COL_DATASET_NAME,
    COL_PATIENT_ID,
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
from .row_builder import build_ct_metadata_row


# Project-local LIDC input column names
LIDC_COL_PATIENT_ID = "lidc_patient_id"
LIDC_COL_STUDY_INSTANCE_UID = "study_instance_uid"
LIDC_COL_SERIES_INSTANCE_UID = "series_instance_uid"
LIDC_COL_ACQUISITION_DATE = "acquisition_date"
LIDC_COL_SLICE_THICKNESS_MM = "slice_thickness_mm"
LIDC_COL_PIXEL_SPACING_X_MM = "pixel_spacing_x_mm"
LIDC_COL_PIXEL_SPACING_Y_MM = "pixel_spacing_y_mm"
LIDC_COL_SPACING_BETWEEN_SLICES_MM = "spacing_between_slices_mm"
LIDC_COL_NUM_COLUMNS = "num_columns"
LIDC_COL_NUM_ROWS = "num_rows"
LIDC_COL_NUM_SLICES = "num_slices"
LIDC_COL_DICOM_REL_PATH = "dicom_rel_path"
LIDC_COL_NODULE_MALIGNANCY = "nodule_malignancy"
LIDC_COL_NODULE_MASK_REL_PATH = "nodule_mask_rel_path"


def lidc_row_to_ct_metadata(lidc_row: Dict[str, Any]) -> CTMetadataRow:
    """
    Map a single "raw LIDC-IDRI row" dict into a CTMetadataRow.
    """
    canonical: Dict[str, Any] = {
        # Identity
        COL_DATASET_NAME: "LIDC-IDRI",
        COL_PATIENT_ID: lidc_row[LIDC_COL_PATIENT_ID],
        COL_STUDY_UID: lidc_row[LIDC_COL_STUDY_INSTANCE_UID],
        COL_SERIES_UID: lidc_row[LIDC_COL_SERIES_INSTANCE_UID],
        COL_MODALITY: "CT",

        # Acquisition date (to be normalized)
        COL_ACQUISITION_DATE: lidc_row.get(LIDC_COL_ACQUISITION_DATE),

        # Geometry
        COL_SLICE_THICKNESS_MM: lidc_row.get(LIDC_COL_SLICE_THICKNESS_MM),
        COL_SPACING_X_MM: lidc_row.get(LIDC_COL_PIXEL_SPACING_X_MM),
        COL_SPACING_Y_MM: lidc_row.get(LIDC_COL_PIXEL_SPACING_Y_MM),
        COL_SPACING_Z_MM: lidc_row.get(LIDC_COL_SPACING_BETWEEN_SLICES_MM),
        COL_IMAGE_SIZE_X: lidc_row.get(LIDC_COL_NUM_COLUMNS),
        COL_IMAGE_SIZE_Y: lidc_row.get(LIDC_COL_NUM_ROWS),
        COL_IMAGE_SIZE_Z: lidc_row.get(LIDC_COL_NUM_SLICES),

        # Label: nodule malignancy
        COL_LABEL_PRIMARY_NAME: "nodule_malignancy",
        COL_LABEL_PRIMARY_VALUE: (
            None
            if lidc_row.get(LIDC_COL_NODULE_MALIGNANCY) is None
            else str(lidc_row[LIDC_COL_NODULE_MALIGNANCY])
        ),

        # Paths
        COL_RAW_IMAGE_PATH: lidc_row.get(LIDC_COL_DICOM_REL_PATH),
        COL_PREPROCESSED_IMAGE_PATH: None,
        COL_LABEL_MASK_PATH: lidc_row.get(LIDC_COL_NODULE_MASK_REL_PATH),
    }

    return build_ct_metadata_row(canonical)
