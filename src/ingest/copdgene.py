# src/ingest/copdgene.py

"""
High-level loader for the COPDGene dataset.

CSV-based loader that:
- reads a COPDGene metadata CSV
- maps each row into CTMetadataRow via copdgene_ingest.copdgene_row_to_ct_metadata
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import pandas as pd

from .metadata_schema import CTMetadataRow
from .copdgene_ingest import copdgene_row_to_ct_metadata


def load_copdgene_metadata(csv_path: str | Path) -> List[CTMetadataRow]:
    """
    Load COPDGene metadata from a CSV file and return a list of CTMetadataRow.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"COPDGene metadata CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    rows: List[CTMetadataRow] = []
    for _, row in df.iterrows():
        copd_dict = row.to_dict()
        rows.append(copdgene_row_to_ct_metadata(copd_dict))

    return rows


def iter_copdgene_metadata(csv_path: str | Path) -> Iterable[CTMetadataRow]:
    """
    Generator version of load_copdgene_metadata.
    """
    for row in load_copdgene_metadata(csv_path):
        yield row
