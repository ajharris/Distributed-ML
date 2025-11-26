"""
tests/ingest/test_dataset_registry.py

Tests for DatasetRegistry and the high-level dataset loaders.

We use small, in-memory CSV fixtures written to tmp_path to avoid any
dependency on external files.
"""

from pathlib import Path
from typing import List

import pandas as pd

from src.ingest.metadata_schema import CTMetadataRow
from src.ingest.registry import DatasetRegistry


def _write_csv(tmp_path: Path, filename: str, content: str) -> Path:
    """
    Helper to write a small CSV string to disk under tmp_path.
    """
    path = tmp_path / filename
    path.write_text(content.strip() + "\n")
    return path


def test_dataset_registry_get_lidc(tmp_path) -> None:
    """
    DatasetRegistry.get('lidc') should return a callable that loads
    CTMetadataRow objects from a LIDC-style CSV.
    """
    csv_content = """
lidc_patient_id,study_instance_uid,series_instance_uid,acquisition_date,slice_thickness_mm,pixel_spacing_x_mm,pixel_spacing_y_mm,spacing_between_slices_mm,num_columns,num_rows,num_slices,dicom_rel_path,nodule_malignancy,nodule_mask_rel_path
LIDC-IDRI-0005,1.3.6.1.4.1.1,1.3.6.1.4.1.1.1,20041110,1.25,0.7,0.7,1.25,512,512,150,/raw/LIDC-IDRI/0005/CT/,4,preprocessed/LIDC-IDRI/0005/series_001_mask.nii.gz
"""
    csv_path = _write_csv(tmp_path, "lidc_demo.csv", csv_content)

    loader = DatasetRegistry.get("lidc")
    rows = list(loader(csv_path))

    assert len(rows) == 1
    row = rows[0]
    assert isinstance(row, CTMetadataRow)
    assert row.dataset_name == "LIDC-IDRI"
    assert row.patient_id == "LIDC-IDRI-0005"
    assert row.label_primary_name == "nodule_malignancy"
    assert row.label_primary_value == "4"


def test_dataset_registry_get_nlst(tmp_path) -> None:
    """
    DatasetRegistry.get('nlst') should work for NLST-style CSV.
    """
    csv_content = """
nlst_patient_id,study_instance_uid,series_instance_uid,mortality_6yr,acquisition_date,slice_thickness_mm,pixel_spacing_x_mm,pixel_spacing_y_mm,spacing_between_slices_mm,num_columns,num_rows,num_slices,dicom_rel_path
NLST-0001,1.2.3.4.100,1.2.3.4.100.1,1,20050312,1.25,0.7,0.7,1.25,512,512,350,/raw/NLST/0001/series_1/
"""
    csv_path = _write_csv(tmp_path, "nlst_demo.csv", csv_content)

    loader = DatasetRegistry.get("nlst")
    rows = list(loader(csv_path))

    assert len(rows) == 1
    row = rows[0]
    assert row.dataset_name == "NLST"
    assert row.label_primary_name == "mortality_6yr"
    assert row.label_primary_value == "1"


def test_dataset_registry_unknown_key() -> None:
    """
    Requesting an unknown dataset key should raise a helpful KeyError.
    """
    try:
        DatasetRegistry.get("nonexistent-dataset")
    except KeyError as e:
        msg = str(e).lower()
        assert "unknown dataset key" in msg
        assert "known datasets" in msg
    else:
        assert False, "Expected KeyError for unknown dataset key"
