"""
tests/ingest/test_lidc_ingest.py

Tests for LIDC-IDRI-specific ingestion helpers.

We treat:
- primary label: nodule_malignancy (scan-level or series-level label)
- label_mask_path: voxel-wise nodule mask path (if available)
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
    COL_LABEL_MASK_PATH,
    COL_SLICE_THICKNESS_MM,
    COL_SPACING_X_MM,
    COL_SPACING_Y_MM,
    COL_SPACING_Z_MM,
    COL_IMAGE_SIZE_X,
    COL_IMAGE_SIZE_Y,
    COL_IMAGE_SIZE_Z,
    COL_ACQUISITION_DATE,
)
from src.ingest.lidc_ingest import (
    LIDC_COL_PATIENT_ID,
    LIDC_COL_STUDY_INSTANCE_UID,
    LIDC_COL_SERIES_INSTANCE_UID,
    LIDC_COL_ACQUISITION_DATE,
    LIDC_COL_SLICE_THICKNESS_MM,
    LIDC_COL_PIXEL_SPACING_X_MM,
    LIDC_COL_PIXEL_SPACING_Y_MM,
    LIDC_COL_SPACING_BETWEEN_SLICES_MM,
    LIDC_COL_NUM_COLUMNS,
    LIDC_COL_NUM_ROWS,
    LIDC_COL_NUM_SLICES,
    LIDC_COL_DICOM_REL_PATH,
    LIDC_COL_NODULE_MALIGNANCY,
    LIDC_COL_NODULE_MASK_REL_PATH,
    lidc_row_to_ct_metadata,
)


def make_fake_lidc_row() -> Dict[str, Any]:
    """
    Fake LIDC-IDRI metadata row with project-local LIDC-style field names.
    """
    return {
        LIDC_COL_PATIENT_ID: "LIDC-IDRI-0005",
        LIDC_COL_STUDY_INSTANCE_UID: "1.3.6.1.4.1.14519.5.2.1.6279.6001.1000000005",
        LIDC_COL_SERIES_INSTANCE_UID: "1.3.6.1.4.1.14519.5.2.1.6279.6001.1000000005.1",
        LIDC_COL_ACQUISITION_DATE: "20041110",
        LIDC_COL_SLICE_THICKNESS_MM: 1.25,
        LIDC_COL_PIXEL_SPACING_X_MM: 0.7,
        LIDC_COL_PIXEL_SPACING_Y_MM: 0.7,
        LIDC_COL_SPACING_BETWEEN_SLICES_MM: 1.25,
        LIDC_COL_NUM_COLUMNS: 512,
        LIDC_COL_NUM_ROWS: 512,
        LIDC_COL_NUM_SLICES: 150,
        LIDC_COL_DICOM_REL_PATH: "/raw/LIDC-IDRI/LIDC-IDRI-0005/CT/",
        LIDC_COL_NODULE_MALIGNANCY: 4,  # arbitrary example score
        LIDC_COL_NODULE_MASK_REL_PATH: "preprocessed/LIDC-IDRI/LIDC-IDRI-0005/series_001_nodule_mask.nii.gz",
    }


def test_lidc_row_to_ct_metadata_basic_mapping() -> None:
    row = lidc_row_to_ct_metadata(make_fake_lidc_row())

    assert isinstance(row, CTMetadataRow)

    # Identity
    assert row.dataset_name == "LIDC-IDRI"
    assert row.patient_id == "LIDC-IDRI-0005"

    # Label mapping
    assert row.label_primary_name == "nodule_malignancy"
    assert row.label_primary_value == "4"

    # Geometry
    assert row.slice_thickness_mm == 1.25
    assert row.spacing_x_mm == 0.7
    assert row.spacing_y_mm == 0.7
    assert row.spacing_z_mm == 1.25
    assert row.image_size_x == 512
    assert row.image_size_y == 512
    assert row.image_size_z == 150

    # Acquisition date normalized
    assert row.acquisition_date == "2004-11-10"

    # Paths
    assert not row.raw_image_path.startswith("/")
    assert row.raw_image_path == "raw/LIDC-IDRI/LIDC-IDRI-0005/CT/"
    assert row.label_mask_path == "preprocessed/LIDC-IDRI/LIDC-IDRI-0005/series_001_nodule_mask.nii.gz"


def test_lidc_row_to_ct_metadata_dict_view() -> None:
    lidc_row = make_fake_lidc_row()
    row = lidc_row_to_ct_metadata(lidc_row)
    d = row.to_dict()

    assert d[COL_DATASET_NAME] == "LIDC-IDRI"
    assert d[COL_PATIENT_ID] == lidc_row[LIDC_COL_PATIENT_ID]
    assert d[COL_SERIES_UID] == lidc_row[LIDC_COL_SERIES_INSTANCE_UID]
    assert d[COL_LABEL_PRIMARY_NAME] == "nodule_malignancy"
    assert d[COL_LABEL_PRIMARY_VALUE] == "4"
    assert d[COL_RAW_IMAGE_PATH] == "raw/LIDC-IDRI/LIDC-IDRI-0005/CT/"
    assert d[COL_LABEL_MASK_PATH] == "preprocessed/LIDC-IDRI/LIDC-IDRI-0005/series_001_nodule_mask.nii.gz"
    assert d[COL_SLICE_THICKNESS_MM] == lidc_row[LIDC_COL_SLICE_THICKNESS_MM]
    assert d[COL_SPACING_X_MM] == lidc_row[LIDC_COL_PIXEL_SPACING_X_MM]
    assert d[COL_SPACING_Y_MM] == lidc_row[LIDC_COL_PIXEL_SPACING_Y_MM]
    assert d[COL_SPACING_Z_MM] == lidc_row[LIDC_COL_SPACING_BETWEEN_SLICES_MM]
    assert d[COL_IMAGE_SIZE_X] == lidc_row[LIDC_COL_NUM_COLUMNS]
    assert d[COL_IMAGE_SIZE_Y] == lidc_row[LIDC_COL_NUM_ROWS]
    assert d[COL_IMAGE_SIZE_Z] == lidc_row[LIDC_COL_NUM_SLICES]
    assert d[COL_ACQUISITION_DATE] == "2004-11-10"
