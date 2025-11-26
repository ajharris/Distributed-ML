# src/ingest/nlst.py

"""
High-level loader for the NLST dataset.

CSV-based loader that:
- reads an NLST metadata CSV
- maps each row into CTMetadataRow via nlst_ingest.nlst_row_to_ct_metadata
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import pandas as pd

from .metadata_schema import CTMetadataRow
from .nlst_ingest import nlst_row_to_ct_metadata


def load_nlst_metadata(csv_path: str | Path) -> List[CTMetadataRow]:
    """
    Load NLST metadata from a CSV file and return a list of CTMetadataRow.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"NLST metadata CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    rows: List[CTMetadataRow] = []
    for _, row in df.iterrows():
        nlst_dict = row.to_dict()
        rows.append(nlst_row_to_ct_metadata(nlst_dict))

    return rows


def iter_nlst_metadata(csv_path: str | Path) -> Iterable[CTMetadataRow]:
    """
    Generator version of load_nlst_metadata for streaming scenarios.
    """
    for row in load_nlst_metadata(csv_path):
        yield row
