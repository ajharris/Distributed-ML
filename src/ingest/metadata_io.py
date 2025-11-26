"""
src/ingest/metadata_io.py

Utilities for converting CTMetadataRow collections into tabular metadata
and writing them to Parquet files.

Key functions:
- rows_to_dataframe(rows) -> pandas.DataFrame
- write_dataset_metadata_parquet(rows, path)
- write_per_dataset_parquet(rows, output_dir)
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import pandas as pd

from .metadata_schema import (
    CTMetadataRow,
    ALL_COLUMNS,
    COL_DATASET_NAME,
)


def rows_to_dataframe(rows: Iterable[CTMetadataRow]) -> pd.DataFrame:
    """
    Convert an iterable of CTMetadataRow objects into a pandas DataFrame
    with canonical column names.

    Notes
    -----
    - The DataFrame will have exactly the columns in ALL_COLUMNS.
    - Row order is preserved.
    - This function does not write to disk; it is purely in-memory.
    """
    dicts: List[dict] = [row.to_dict() for row in rows]

    if not dicts:
        # Create an empty DataFrame with the right columns in case of no rows.
        return pd.DataFrame(columns=ALL_COLUMNS)

    df = pd.DataFrame(dicts)

    # Ensure columns are in canonical order (helpful for debugging & Parquet)
    df = df.reindex(columns=ALL_COLUMNS)

    return df


def write_dataset_metadata_parquet(
    rows: Iterable[CTMetadataRow],
    path: str | Path,
) -> None:
    """
    Write the given metadata rows to a single Parquet file.

    Parameters
    ----------
    rows:
        Iterable of CTMetadataRow objects (all from one dataset is recommended,
        but not strictly enforced here).
    path:
        Output file path. Parent directories will be created if necessary.
    """
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df = rows_to_dataframe(list(rows))
    # We rely on pandas.to_parquet, which will use pyarrow (or other engine)
    df.to_parquet(out_path, index=False)


def write_per_dataset_parquet(
    rows: Iterable[CTMetadataRow],
    output_dir: str | Path,
) -> None:
    """
    Group CTMetadataRow objects by dataset_name and write one Parquet file
    per dataset to the specified directory.

    Files are named:

        metadata_<DATASET_NAME>.parquet

    Example:
        metadata_NLST.parquet
        metadata_COPDGene.parquet
        metadata_LIDC-IDRI.parquet
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Group rows by dataset_name
    by_dataset: dict[str, List[CTMetadataRow]] = {}

    for row in rows:
        dataset = getattr(row, "dataset_name", "UNKNOWN_DATASET")
        by_dataset.setdefault(dataset, []).append(row)

    for dataset_name, ds_rows in by_dataset.items():
        filename = f"metadata_{dataset_name}.parquet"
        out_path = output_dir / filename
        write_dataset_metadata_parquet(ds_rows, out_path)
