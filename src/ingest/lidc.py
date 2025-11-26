# src/ingest/lidc.py

"""
High-level loader for the LIDC-IDRI dataset.

CSV-based loader that:
- reads a LIDC-IDRI metadata CSV
- maps each row into CTMetadataRow via lidc_ingest.lidc_row_to_ct_metadata
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import pandas as pd

from .metadata_schema import CTMetadataRow
from .lidc_ingest import lidc_row_to_ct_metadata


def load_lidc_metadata(csv_path: str | Path) -> List[CTMetadataRow]:
    """
    Load LIDC-IDRI metadata from a CSV file and return a list of CTMetadataRow.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"LIDC-IDRI metadata CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    rows: List[CTMetadataRow] = []
    for _, row in df.iterrows():
        lidc_dict = row.to_dict()
        rows.append(lidc_row_to_ct_metadata(lidc_dict))

    return rows


def iter_lidc_metadata(csv_path: str | Path) -> Iterable[CTMetadataRow]:
    """
    Generator version of load_lidc_metadata.
    """
    for row in load_lidc_metadata(csv_path):
        yield row
