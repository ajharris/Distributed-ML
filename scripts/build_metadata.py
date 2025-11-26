#!/usr/bin/env python

"""
scripts/build_metadata.py

Command-line entry point to:

1. Load preprocessed tabular metadata for one or more datasets
   (e.g., NLST, COPDGene, LIDC-IDRI) from CSV files.
2. Map each dataset's rows into the canonical CTMetadataRow schema.
3. Run dataset-level validators.
4. Write one Parquet file per dataset into an output directory
   (default: data/metadata/).

This script assumes you have already created small "metadata CSVs"
for each dataset whose column names match the project-local
NLST/COPDGene/LIDC column constants defined in:

- src/ingest/nlst_ingest.py
- src/ingest/copdgene_ingest.py
- src/ingest/lidc_ingest.py
"""

from __future__ import annotations

# --- ensure project root is on sys.path ---
import sys
from pathlib import Path

# This file lives in <repo_root>/scripts/build_metadata.py
# So the repo root is one level up.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import argparse
from typing import List

from src.ingest.metadata_schema import CTMetadataRow
from src.ingest.dataset_validators import assert_valid_dataset_metadata
from src.ingest.metadata_io import write_per_dataset_parquet
from src.ingest.registry import DatasetRegistry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build canonical CT metadata Parquet files for NLST, "
                    "COPDGene, and LIDC-IDRI."
    )

    parser.add_argument(
        "--nlst-csv",
        type=Path,
        default=None,
        help="Path to NLST metadata CSV (columns must match nlst_ingest.NLST_COL_*).",
    )
    parser.add_argument(
        "--copdgene-csv",
        type=Path,
        default=None,
        help="Path to COPDGene metadata CSV (columns must match copdgene_ingest.COPD_COL_*).",
    )
    parser.add_argument(
        "--lidc-csv",
        type=Path,
        default=None,
        help="Path to LIDC-IDRI metadata CSV (columns must match lidc_ingest.LIDC_COL_*).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/metadata"),
        help="Directory where per-dataset Parquet files will be written "
             "(default: data/metadata).",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    all_rows: List[CTMetadataRow] = []

    # NLST
    if args.nlst_csv is not None:
        if not args.nlst_csv.exists():
            raise FileNotFoundError(f"NLST CSV not found: {args.nlst_csv}")
        nlst_loader = DatasetRegistry.get("nlst")
        all_rows.extend(nlst_loader(args.nlst_csv))

    # COPDGene
    if args.copdgene_csv is not None:
        if not args.copdgene_csv.exists():
            raise FileNotFoundError(f"COPDGene CSV not found: {args.copdgene_csv}")
        copd_loader = DatasetRegistry.get("copdgene")
        all_rows.extend(copd_loader(args.copdgene_csv))

    # LIDC-IDRI
    if args.lidc_csv is not None:
        if not args.lidc_csv.exists():
            raise FileNotFoundError(f"LIDC-IDRI CSV not found: {args.lidc_csv}")
        lidc_loader = DatasetRegistry.get("lidc")
        all_rows.extend(lidc_loader(args.lidc_csv))

    if not all_rows:
        raise SystemExit(
            "No datasets provided. Use --nlst-csv, --copdgene-csv, and/or --lidc-csv."
        )

    # Validate the combined dataset before writing
    assert_valid_dataset_metadata(all_rows)

    # Write one Parquet per dataset_name
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_per_dataset_parquet(all_rows, args.output_dir)

    print(f"Wrote per-dataset metadata Parquet files to: {args.output_dir}")


if __name__ == "__main__":
    main()
