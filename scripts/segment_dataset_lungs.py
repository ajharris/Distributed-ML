#!/usr/bin/env python

"""
Run classical lung segmentation across an entire dataset
based on the metadata parquet file.

This script:
  - Loads dataset metadata (Parquet)
  - Reads the CT path for each scan
  - Loads each CT volume ON DEMAND (lazy loading)
  - Runs segmentation via segment_lung_and_save
  - Writes a lung_mask_path column back into the metadata

Usage:

python scripts/segment_dataset_lungs.py \
    --metadata data/metadata/metadata_COPDGene.parquet \
    --cache-dir data/cache/lung_masks
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.preprocess.segment_lung import (
    segment_lung_and_save,
    LungSegmentationConfig,
)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run lung segmentation across a dataset using metadata."
    )
    parser.add_argument(
        "--metadata",
        type=Path,
        required=True,
        help="Path to metadata Parquet file.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        required=True,
        help="Directory to store lung mask .npy files.",
    )
    parser.add_argument(
        "--ct-path-col",
        type=str,
        default="ct_volume_path",
        help="Column in the metadata containing the CT file path.",
    )
    parser.add_argument(
        "--scan-id-col",
        type=str,
        default="scan_id",
        help="Column containing unique scan identifiers.",
    )
    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    metadata_path = args.metadata
    cache_dir = args.cache_dir
    ct_col = args.ct_path_col
    scan_id_col = args.scan_id_col

    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_path}")

    df = pd.read_parquet(metadata_path)

    if ct_col not in df.columns:
        raise ValueError(
            f"Metadata must contain column '{ct_col}'. "
            f"Columns available: {list(df.columns)}"
        )

    if scan_id_col not in df.columns:
        raise ValueError(
            f"Metadata must contain unique scan id column '{scan_id_col}'."
        )

    cache_dir.mkdir(parents=True, exist_ok=True)

    lung_mask_paths = []

    for idx, row in df.iterrows():
        ct_path = Path(row[ct_col])
        scan_id = str(row[scan_id_col])

        if not ct_path.exists():
            raise FileNotFoundError(f"CT file not found: {ct_path}")

        # Load CT volume lazily
        volume_hu = np.load(ct_path) if ct_path.suffix == ".npy" else None
        # (Extend here if you introduce io.load_ct_volume)

        out_path = cache_dir / f"{scan_id}_lung_mask.npy"

        mask = segment_lung_and_save(
            volume_hu=volume_hu,
            spacing_mm=None,   # If you store spacing in metadata, pass it here
            cache_path=out_path,
            config=LungSegmentationConfig(),
        )

        lung_mask_paths.append(str(out_path))

        print(f"[{idx+1}/{len(df)}] Segmented {scan_id} → {out_path}")

    df["lung_mask_path"] = lung_mask_paths

    # Write metadata back in place
    df.to_parquet(metadata_path, index=False)

    print("\nDataset segmentation complete.")
    print(f"Updated metadata written to: {metadata_path}")


if __name__ == "__main__":
    main()
