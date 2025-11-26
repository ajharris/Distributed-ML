# tests/preprocess/test_segment_lung.py

from pathlib import Path

import numpy as np

from src.preprocess.segment_lung import (
    LungSegmentationConfig,
    segment_lung,
    segment_lung_and_save,
)


def _synthetic_lung_volume(
    shape=(32, 32, 32),
    lung_hu: float = -800.0,
    body_hu: float = 40.0,
) -> np.ndarray:
    """
    Tiny synthetic CT-like volume:
    - background/body at body_hu
    - two spherical 'lungs' at lung_hu
    """
    z, y, x = np.indices(shape)
    center_left = np.array([shape[0] // 2, shape[1] // 3, shape[2] // 2])
    center_right = np.array([shape[0] // 2, 2 * shape[1] // 3, shape[2] // 2])
    radius = min(shape) // 4

    dist_left = ((z - center_left[0]) ** 2 +
                 (y - center_left[1]) ** 2 +
                 (x - center_left[2]) ** 2)
    dist_right = ((z - center_right[0]) ** 2 +
                  (y - center_right[1]) ** 2 +
                  (x - center_right[2]) ** 2)

    vol = np.full(shape, body_hu, dtype=np.float32)
    vol[dist_left <= radius ** 2] = lung_hu
    vol[dist_right <= radius ** 2] = lung_hu
    return vol


def test_segment_lung_produces_plausible_mask():
    volume = _synthetic_lung_volume()
    config = LungSegmentationConfig(
        hu_threshold=-320.0,
        min_component_size=100,  # smaller for synthetic data
        num_components_to_keep=2,
        closing_iterations=1,
        fill_holes=True,
    )

    mask = segment_lung(volume, spacing_mm=(1.0, 1.0, 1.0), config=config)

    # Shape & dtype
    assert mask.shape == volume.shape
    assert mask.dtype == bool

    # Non-trivial lung region
    lung_voxels = int(mask.sum())
    assert lung_voxels > 0

    # Center of left 'lung' should be inside the mask
    zc, yc, xc = volume.shape[0] // 2, volume.shape[1] // 3, volume.shape[2] // 2
    assert mask[zc, yc, xc]


def test_segment_lung_is_deterministic():
    volume = _synthetic_lung_volume()
    config = LungSegmentationConfig(
        hu_threshold=-320.0,
        min_component_size=100,
        num_components_to_keep=2,
        closing_iterations=2,
        fill_holes=True,
    )

    mask1 = segment_lung(volume, spacing_mm=(1.0, 1.0, 1.0), config=config)
    mask2 = segment_lung(volume, spacing_mm=(1.0, 1.0, 1.0), config=config)

    # Exact equality for fixed inputs and config
    assert np.array_equal(mask1, mask2)


def test_segment_lung_and_save_writes_cache(tmp_path: Path):
    volume = _synthetic_lung_volume()
    out_path = tmp_path / "lung_masks" / "synthetic_mask.npy"

    mask = segment_lung_and_save(
        volume_hu=volume,
        spacing_mm=(1.0, 1.0, 1.0),
        cache_path=out_path,
    )

    # Sanity checks
    assert mask.shape == volume.shape
    assert mask.dtype == bool

    assert out_path.exists()
    loaded = np.load(out_path)
    assert loaded.shape == volume.shape
    assert np.array_equal(mask, loaded.astype(bool))


def test_segment_lung_handles_no_below_threshold():
    """
    If all voxels are above threshold, we should get an all-false mask
    without crashing.
    """
    volume = np.full((16, 16, 16), 100.0, dtype=np.float32)
    mask = segment_lung(volume)

    assert mask.shape == volume.shape
    assert not mask.any()
