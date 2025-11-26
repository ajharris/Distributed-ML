#!/usr/bin/env python
"""
CLI entrypoint for classical lung segmentation.

Usage examples
--------------

# Segment a CT volume stored as a NumPy array (HU values)
python scripts/run_lung_segmentation.py \
    --input data/cache/example_ct.npy \
    --output data/cache/example_lung_mask.npy

# Segment a NIfTI volume (requires nibabel)
python scripts/run_lung_segmentation.py \
    --input data/ct/example_ct.nii.gz \
    --output data/cache/example_lung_mask.npy
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional, Sequence

import numpy as np

from src.preprocess.segment_lung import (
    LungSegmentationConfig,
    segment_lung_and_save,
)


def _load_volume(input_path: Path) -> np.ndarray:
    """
    Load a 3D CT volume from disk.

    Supported formats:
      - .npy: NumPy array saved with np.save, containing a 3D array in HU.
      - .nii / .nii.gz: NIfTI file (requires nibabel).

    Returns
    -------
    volume_hu : np.ndarray, shape (Z, Y, X), dtype float32/float64
    """
    suffix = "".join(input_path.suffixes)  # handles .nii.gz

    if suffix == ".npy":
        arr = np.load(input_path)
        if arr.ndim != 3:
            raise ValueError(f"Expected 3D array in {input_path}, got shape {arr.shape}")
        return arr.astype(np.float32)

    if suffix in {".nii", ".nii.gz"}:
        try:
            import nibabel as nib  # type: ignore
        except ImportError as e:
            raise ImportError(
                "nibabel is required to load NIfTI files. "
                "Install it or convert your volume to .npy."
            ) from e

        img = nib.load(str(input_path))
        data = img.get_fdata()
        if data.ndim != 3:
            raise ValueError(
                f"Expected 3D NIfTI volume in {input_path}, got shape {data.shape}"
            )
        return data.astype(np.float32)

    raise ValueError(
        f"Unsupported input format '{suffix}'. "
        "Use .npy or NIfTI (.nii / .nii.gz)."
    )


def _parse_spacing(spacing_str: Optional[str]) -> Optional[Sequence[float]]:
    """
    Parse spacing string of the form 'dz,dy,dx' into a tuple of floats.
    If spacing_str is None, returns None.
    """
    if spacing_str is None:
        return None

    parts = spacing_str.split(",")
    if len(parts) != 3:
        raise ValueError(
            f"Invalid spacing format '{spacing_str}'. "
            "Expected 'dz,dy,dx' (e.g. '1.0,0.7,0.7')."
        )
    return tuple(float(p) for p in parts)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run classical lung segmentation on a CT volume."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to input CT volume (.npy or NIfTI .nii/.nii.gz) in HU.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to output lung mask cache (.npy). "
             "Parent directories will be created if needed.",
    )
    parser.add_argument(
        "--spacing",
        type=str,
        default=None,
        help=(
            "Optional voxel spacing as 'dz,dy,dx' in millimetres "
            "(e.g. '1.0,0.7,0.7'). If omitted, spacing is not used."
        ),
    )
    parser.add_argument(
        "--hu-threshold",
        type=float,
        default=-320.0,
        help="HU threshold to separate lung parenchyma + air from soft tissue "
             "(default: -320.0).",
    )
    parser.add_argument(
        "--min-lung-component-size",
        type=int,
        default=10_000,
        help="Minimum connected component size in voxels to keep as lung "
             "(default: 10000).",
    )
    parser.add_argument(
        "--num-components-to-keep",
        type=int,
        default=2,
        help="How many largest connected components to keep (default: 2, for left + right lung).",
    )
    parser.add_argument(
        "--closing-iterations",
        type=int,
        default=2,
        help="Number of binary closing iterations for mask smoothing (default: 2).",
    )
    parser.add_argument(
        "--no-fill-holes",
        action="store_true",
        help="Disable slice-wise binary hole filling inside the lungs.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    input_path: Path = args.input
    output_path: Path = args.output
    spacing = _parse_spacing(args.spacing)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Load CT volume
    volume_hu = _load_volume(input_path)

    # Build deterministic config
    config = LungSegmentationConfig(
        hu_threshold=args.hu_threshold,
        min_lung_component_size=args.min_lung_component_size,
        num_components_to_keep=args.num_components_to_keep,
        closing_iterations=args.closing_iterations,
        fill_holes=not args.no_fill_holes,
    )

    # Run segmentation and save mask to cache
    lung_mask = segment_lung_and_save(
        volume_hu=volume_hu,
        spacing_mm=spacing,
        cache_path=output_path,
        config=config,
    )

    # Print a small summary for the user
    total_voxels = lung_mask.size
    lung_voxels = int(lung_mask.sum())
    frac = lung_voxels / float(total_voxels) if total_voxels > 0 else 0.0

    print(f"Segmentation complete.")
    print(f"  Input volume: {input_path} (shape={volume_hu.shape})")
    print(f"  Output mask:  {output_path}")
    print(f"  Lung voxels:  {lung_voxels} / {total_voxels} ({frac:.3%})")


if __name__ == "__main__":
    main()
