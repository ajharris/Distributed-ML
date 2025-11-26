"""
tests/ingest/test_copdgene_ingest.py

Tests for COPDGene-specific ingestion helpers.

We assume a "raw COPDGene row" dict with COPDGene-style column names,
and test mapping:

    COPDGene row dict --> copdgene_row_to_ct_metadata() --> CTMetadataRow
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
    COL_COPD_STATUS,
    COL_FEV1_L,
    COL_FEV1_PERCENT_PRED,
)
from src.ingest.copdgene_ingest import (
    COPD_COL_PATIENT_ID,
    COPD_COL_STUDY_INSTANCE_UID,
    COPD_COL_SERIES_INSTANCE_UID,
    COPD_COL_COPD_STATUS,
    COPD_COL_ACQUISITION_DATE,
    COPD_COL_SLICE_THICKNESS_MM,
    COPD_COL_PIXEL_SPACING_X_MM,
    COPD_COL_PIXEL_SPACING_Y_MM,
    COPD_COL_SPACING_BETWEEN_SLICES_MM,
    COPD_COL_NUM_COLUMNS,
    COPD_COL_NUM_ROWS,
    COPD_COL_NUM_SLICES,
    COPD_COL_DICOM_REL_PATH,
    COPD_COL_FEV1_L,
    COPD_COL_FEV1_PERCENT_PRED,
    copdgene_row_to_ct_metadata,
)


def make_fake_copdgene_row() -> Dict[str, Any]:
    """
    Fake COPDGene metadata row with COPDGene-style field names.
    """
    return {
        COPD_COL_PATIENT_ID: "COPD-0123",
        COPD_COL_STUDY_INSTANCE_UID: "2.25.1234567890.1",
        COPD_COL_SERIES_INSTANCE_UID: "2.25.1234567890.1.1",
        COPD_COL_ACQUISITION_DATE: "20100605",  # yyyymmdd
        COPD_COL_SLICE_THICKNESS_MM: 0.75,
        COPD_COL_PIXEL_SPACING_X_MM: 0.68,
        COPD_COL_PIXEL_SPACING_Y_MM: 0.68,
        COPD_COL_SPACING_BETWEEN_SLICES_MM: 0.75,
        COPD_COL_NUM_COLUMNS: 512,
        COPD_COL_NUM_ROWS: 512,
        COPD_COL_NUM_SLICES: 450,
        COPD_COL_DICOM_REL_PATH: "/raw/COPDGene/COPD-0123/CT_baseline/",
        COPD_COL_COPD_STATUS: "COPD",
        COPD_COL_FEV1_L: 1.2,
        COPD_COL_FEV1_PERCENT_PRED: 38.0,
    }


def test_copdgene_row_to_ct_metadata_basic_mapping() -> None:
    row = copdgene_row_to_ct_metadata(make_fake_copdgene_row())

    assert isinstance(row, CTMetadataRow)

    # Identity
    assert row.dataset_name == "COPDGene"
    assert row.patient_id == "COPD-0123"

    # Label: here primary label is copd_status
    assert row.label_primary_name == "copd_status"
    assert row.label_primary_value == "COPD"

    # Geometry
    assert row.slice_thickness_mm == 0.75
    assert row.spacing_x_mm == 0.68
    assert row.spacing_y_mm == 0.68
    assert row.spacing_z_mm == 0.75
    assert row.image_size_x == 512
    assert row.image_size_y == 512
    assert row.image_size_z == 450

    # Acquisition date normalized
    assert row.acquisition_date == "2010-06-05"

    # Paths: raw path relative, no leading slash
    assert not row.raw_image_path.startswith("/")
    assert row.raw_image_path == "raw/COPDGene/COPD-0123/CT_baseline/"

    # Clinical fields mapped
    assert row.copd_status == "COPD"
    assert row.fev1_l == 1.2
    assert row.fev1_percent_pred == 38.0


def test_copdgene_row_to_ct_metadata_dict_view() -> None:
    copd_row = make_fake_copdgene_row()
    row = copdgene_row_to_ct_metadata(copd_row)
    d = row.to_dict()

    assert d[COL_DATASET_NAME] == "COPDGene"
    assert d[COL_PATIENT_ID] == copd_row[COPD_COL_PATIENT_ID]
    assert d[COL_SERIES_UID] == copd_row[COPD_COL_SERIES_INSTANCE_UID]
    assert d[COL_LABEL_PRIMARY_NAME] == "copd_status"
    assert d[COL_LABEL_PRIMARY_VALUE] == "COPD"
    assert d[COL_RAW_IMAGE_PATH] == "raw/COPDGene/COPD-0123/CT_baseline/"
    assert d[COL_SLICE_THICKNESS_MM] == copd_row[COPD_COL_SLICE_THICKNESS_MM]
    assert d[COL_SPACING_X_MM] == copd_row[COPD_COL_PIXEL_SPACING_X_MM]
    assert d[COL_SPACING_Y_MM] == copd_row[COPD_COL_PIXEL_SPACING_Y_MM]
    assert d[COL_SPACING_Z_MM] == copd_row[COPD_COL_SPACING_BETWEEN_SLICES_MM]
    assert d[COL_IMAGE_SIZE_X] == copd_row[COPD_COL_NUM_COLUMNS]
    assert d[COL_IMAGE_SIZE_Y] == copd_row[COPD_COL_NUM_ROWS]
    assert d[COL_IMAGE_SIZE_Z] == copd_row[COPD_COL_NUM_SLICES]
    assert d[COL_ACQUISITION_DATE] == "2010-06-05"
    assert d[COL_COPD_STATUS] == "COPD"
    assert d[COL_FEV1_L] == 1.2
    assert d[COL_FEV1_PERCENT_PRED] == 38.0
