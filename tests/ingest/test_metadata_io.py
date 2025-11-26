"""
tests/ingest/test_metadata_io.py

Tests for converting CTMetadataRow collections to Parquet files.

We test three things:
1. rows_to_dataframe() produces a DataFrame with the expected columns.
2. write_dataset_metadata_parquet() writes a Parquet file that can be
   read back into an equivalent DataFrame.
3. write_per_dataset_parquet() writes one Parquet file per dataset_name.
"""

from typing import List

import pytest

# These will be skipped if pandas/pyarrow are not available
pd = pytest.importorskip("pandas")
pytest.importorskip("pyarrow")

from src.ingest.metadata_schema import (
    CTMetadataRow,
    ALL_COLUMNS,
    COL_DATASET_NAME,
    COL_PATIENT_ID,
    COL_SCAN_ID,
    COL_SERIES_UID,
    COL_RAW_IMAGE_PATH,
)
from src.ingest.metadata_io import (
    rows_to_dataframe,
    write_dataset_metadata_parquet,
    write_per_dataset_parquet,
)


def make_row(dataset_name: str, patient_suffix: str) -> CTMetadataRow:
    """
    Helper that returns a minimal but valid CTMetadataRow for tests.

    We reuse the same pattern as earlier tests: one row per CT series
    with all required fields populated and optional fields left as None.
    """
    patient_id = f"{dataset_name}_P{patient_suffix}"
    series_uid = f"1.2.3.4.{patient_suffix}"
    scan_id = f"{dataset_name}__{patient_id}__{series_uid}"

    return CTMetadataRow(
        dataset_name=dataset_name,
        patient_id=patient_id,
        scan_id=scan_id,
        study_uid="1.2.3.4",
        series_uid=series_uid,
        modality="CT",
        acquisition_date="2010-06-05",
        slice_thickness_mm=1.25,
        spacing_x_mm=0.7,
        spacing_y_mm=0.7,
        spacing_z_mm=1.25,
        image_size_x=512,
        image_size_y=512,
        image_size_z=350,
        label_primary_name="dummy_label",
        label_primary_value="0",
        raw_image_path=f"raw/{dataset_name}/{patient_id}/series_001/",
        preprocessed_image_path=None,
        label_mask_path=None,
    )


# ---------------------------------------------------------------------------
# rows_to_dataframe tests
# ---------------------------------------------------------------------------

def test_rows_to_dataframe_has_expected_columns() -> None:
    rows: List[CTMetadataRow] = [
        make_row("NLST", "0001"),
        make_row("COPDGene", "0002"),
    ]

    df = rows_to_dataframe(rows)

    # We expect exactly the canonical ALL_COLUMNS set (order not important).
    assert set(df.columns) == set(ALL_COLUMNS)

    # Row count should match
    assert len(df) == len(rows)

    # Spot-check a field or two
    assert df.iloc[0][COL_DATASET_NAME] == "NLST"
    assert df.iloc[1][COL_DATASET_NAME] == "COPDGene"


# ---------------------------------------------------------------------------
# Single Parquet output tests
# ---------------------------------------------------------------------------

def test_write_dataset_metadata_parquet_round_trip(tmp_path) -> None:
    rows: List[CTMetadataRow] = [
        make_row("NLST", "0001"),
        make_row("NLST", "0002"),
    ]

    out_path = tmp_path / "metadata_nlst.parquet"

    write_dataset_metadata_parquet(rows, out_path)

    assert out_path.exists(), "Expected Parquet file to be created."

    # Read back and compare
    df = pd.read_parquet(out_path)
    assert len(df) == len(rows)
    assert set(df.columns) == set(ALL_COLUMNS)

    # Spot-check that dataset_name and scan_id survived correctly
    assert set(df[COL_DATASET_NAME].unique()) == {"NLST"}
    assert sorted(df[COL_SCAN_ID].tolist()) == sorted([r.scan_id for r in rows])


# ---------------------------------------------------------------------------
# Per-dataset Parquet output tests
# ---------------------------------------------------------------------------

def test_write_per_dataset_parquet_creates_files_per_dataset(tmp_path) -> None:
    rows: List[CTMetadataRow] = [
        make_row("NLST", "0001"),
        make_row("NLST", "0002"),
        make_row("COPDGene", "0003"),
        make_row("LIDC-IDRI", "0004"),
    ]

    write_per_dataset_parquet(rows, tmp_path)

    # Expected files
    nlst_path = tmp_path / "metadata_NLST.parquet"
    copd_path = tmp_path / "metadata_COPDGene.parquet"
    lidc_path = tmp_path / "metadata_LIDC-IDRI.parquet"

    for p in (nlst_path, copd_path, lidc_path):
        assert p.exists(), f"Expected file {p} to be created."

    # NLST file should contain only NLST rows
    df_nlst = pd.read_parquet(nlst_path)
    assert set(df_nlst[COL_DATASET_NAME].unique()) == {"NLST"}

    # COPDGene file only COPDGene
    df_copd = pd.read_parquet(copd_path)
    assert set(df_copd[COL_DATASET_NAME].unique()) == {"COPDGene"}

    # LIDC-IDRI file only LIDC-IDRI
    df_lidc = pd.read_parquet(lidc_path)
    assert set(df_lidc[COL_DATASET_NAME].unique()) == {"LIDC-IDRI"}
