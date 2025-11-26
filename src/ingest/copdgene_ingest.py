"""
src/ingest/copdgene_ingest.py

COPDGene-specific ingestion helpers.

We assume a "raw COPDGene row" dict with COPDGene-style field names,
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
    COL_COPD_STATUS,
    COL_FEV1_L,
    COL_FEV1_PERCENT_PRED,
)
from .row_builder import build_ct_metadata_row


# Project-local COPDGene input column name conventions
COPD_COL_PATIENT_ID = "copdgene_patient_id"
COPD_COL_STUDY_INSTANCE_UID = "study_instance_uid"
COPD_COL_SERIES_INSTANCE_UID = "series_instance_uid"
COPD_COL_ACQUISITION_DATE = "acquisition_date"
COPD_COL_SLICE_THICKNESS_MM = "slice_thickness_mm"
COPD_COL_PIXEL_SPACING_X_MM = "pixel_spacing_x_mm"
COPD_COL_PIXEL_SPACING_Y_MM = "pixel_spacing_y_mm"
COPD_COL_SPACING_BETWEEN_SLICES_MM = "spacing_between_slices_mm"
COPD_COL_NUM_COLUMNS = "num_columns"
COPD_COL_NUM_ROWS = "num_rows"
COPD_COL_NUM_SLICES = "num_slices"
COPD_COL_DICOM_REL_PATH = "dicom_rel_path"
COPD_COL_COPD_STATUS = "copd_status"
COPD_COL_FEV1_L = "fev1_l"
COPD_COL_FEV1_PERCENT_PRED = "fev1_percent_pred"


def copdgene_row_to_ct_metadata(copd_row: Dict[str, Any]) -> CTMetadataRow:
    """
    Map a single "raw COPDGene row" dict into a CTMetadataRow.
    """
    canonical: Dict[str, Any] = {
        # Identity
        COL_DATASET_NAME: "COPDGene",
        COL_PATIENT_ID: copd_row[COPD_COL_PATIENT_ID],
        COL_STUDY_UID: copd_row[COPD_COL_STUDY_INSTANCE_UID],
        COL_SERIES_UID: copd_row[COPD_COL_SERIES_INSTANCE_UID],
        COL_MODALITY: "CT",

        # Acquisition date (to be normalized by build_ct_metadata_row)
        COL_ACQUISITION_DATE: copd_row.get(COPD_COL_ACQUISITION_DATE),

        # Geometry
        COL_SLICE_THICKNESS_MM: copd_row.get(COPD_COL_SLICE_THICKNESS_MM),
        COL_SPACING_X_MM: copd_row.get(COPD_COL_PIXEL_SPACING_X_MM),
        COL_SPACING_Y_MM: copd_row.get(COPD_COL_PIXEL_SPACING_Y_MM),
        COL_SPACING_Z_MM: copd_row.get(COPD_COL_SPACING_BETWEEN_SLICES_MM),
        COL_IMAGE_SIZE_X: copd_row.get(COPD_COL_NUM_COLUMNS),
        COL_IMAGE_SIZE_Y: copd_row.get(COPD_COL_NUM_ROWS),
        COL_IMAGE_SIZE_Z: copd_row.get(COPD_COL_NUM_SLICES),

        # Label: primary label is COPD status
        COL_LABEL_PRIMARY_NAME: "copd_status",
        COL_LABEL_PRIMARY_VALUE: (
            None
            if copd_row.get(COPD_COL_COPD_STATUS) is None
            else str(copd_row[COPD_COL_COPD_STATUS])
        ),

        # Paths
        COL_RAW_IMAGE_PATH: copd_row.get(COPD_COL_DICOM_REL_PATH),
        COL_PREPROCESSED_IMAGE_PATH: None,
        COL_LABEL_MASK_PATH: None,

        # Clinical extras
        COL_COPD_STATUS: copd_row.get(COPD_COL_COPD_STATUS),
        COL_FEV1_L: copd_row.get(COPD_COL_FEV1_L),
        COL_FEV1_PERCENT_PRED: copd_row.get(COPD_COL_FEV1_PERCENT_PRED),
    }

    return build_ct_metadata_row(canonical)
