# src/preprocess/segment_lung.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

import numpy as np
from numpy.typing import NDArray
from scipy import ndimage


Array3D = NDArray[np.floating]


@dataclass
class LungSegmentationConfig:
    """
    Configuration for classical lung segmentation.

    All parameters are deterministic; no randomness is used anywhere.
    """
    hu_threshold: float = -320.0          # lung/air vs soft tissue
    min_component_size: int = 10_000     # min connected-component size (voxels)
    num_components_to_keep: int = 2      # left + right lung
    closing_iterations: int = 2          # morphological smoothing
    fill_holes: bool = True              # fill internal holes slice-wise


def segment_lung(
    volume_hu: Array3D,
    spacing_mm: Optional[Sequence[float]] = None,
    config: Optional[LungSegmentationConfig] = None,
) -> NDArray[np.bool_]:
    """
    Classical lung segmentation using HU threshold + connected components + morphology.

    Parameters
    ----------
    volume_hu
        3D CT volume in Hounsfield Units, shape (Z, Y, X).
    spacing_mm
        Optional voxel spacing (dz, dy, dx). Currently unused, but kept so the API
        is compatible with future spacing-aware logic.
    config
        Optional LungSegmentationConfig. If None, defaults are used.

    Returns
    -------
    lung_mask
        Boolean array of shape (Z, Y, X). True = lung.
        The mask is perfectly aligned with the input (same shape, no resampling).
    """
    if config is None:
        config = LungSegmentationConfig()

    if volume_hu.ndim != 3:
        raise ValueError(f"Expected 3D volume, got shape {volume_hu.shape}")

    # 1. Threshold: everything below hu_threshold is candidate lung/air
    thresh = volume_hu < config.hu_threshold

    if not np.any(thresh):
        # No voxels below threshold → no lung
        return np.zeros_like(thresh, dtype=bool)

    # 2. 3D connected components on thresholded mask
    labeled, num_features = ndimage.label(thresh)
    if num_features == 0:
        return np.zeros_like(thresh, dtype=bool)

    component_sizes = np.bincount(labeled.ravel())
    component_sizes[0] = 0  # background

    # Remove tiny components
    if config.min_component_size > 0:
        too_small = np.where(component_sizes < config.min_component_size)[0]
        if too_small.size > 0:
            small_mask = np.isin(labeled, too_small)
            labeled[small_mask] = 0
            component_sizes[too_small] = 0

    if np.all(component_sizes == 0):
        return np.zeros_like(thresh, dtype=bool)

    # Keep N largest components (usually two lungs)
    keep_labels = np.argsort(component_sizes)[-config.num_components_to_keep :]
    lung_mask = np.isin(labeled, keep_labels)

    # 3. Morphological closing to smooth + seal gaps
    if config.closing_iterations > 0:
        structure = ndimage.generate_binary_structure(rank=3, connectivity=1)
        lung_mask = ndimage.binary_closing(
            lung_mask,
            structure=structure,
            iterations=config.closing_iterations,
        )

    # 4. Slice-wise hole filling (axial)
    if config.fill_holes:
        filled = np.zeros_like(lung_mask)
        for z in range(lung_mask.shape[0]):
            filled[z] = ndimage.binary_fill_holes(lung_mask[z])
        lung_mask = filled

    return lung_mask.astype(bool)


def segment_lung_and_save(
    volume_hu: Array3D,
    spacing_mm: Optional[Sequence[float]] = None,
    cache_path: Optional[Path] = None,
    config: Optional[LungSegmentationConfig] = None,
) -> NDArray[np.bool_]:
    """
    Run lung segmentation and (optionally) save mask to a cache file.

    This is the function that directly matches your branch requirements:
    - Takes CT volume input.
    - Outputs binary lung mask aligned with original spacing (same shape).
    - Saves mask to cache if `cache_path` is provided.
    - Fully deterministic for fixed inputs and config.
    """
    lung_mask = segment_lung(volume_hu, spacing_mm=spacing_mm, config=config)

    if cache_path is not None:
        cache_path = Path(cache_path)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        # Save as uint8 for compact storage (0 or 1).
        np.save(cache_path, lung_mask.astype(np.uint8))

    return lung_mask
