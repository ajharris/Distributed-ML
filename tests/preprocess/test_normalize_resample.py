import json
from pathlib import Path

import numpy as np
import pytest

from src.preprocess.normalize_resample import (
    CTVolume,
    normalize_and_resample,
    normalize_and_resample_with_cache,
    histogram_sanity_check,
    compute_zoom_factors,
    resample_to_spacing,
    save_cached_volume,
    load_cached_volume,
)


def test_compute_zoom_factors_positive_spacing():
    current = (2.5, 0.8, 0.8)
    target = (1.0, 1.0, 1.0)
    zoom = compute_zoom_factors(current, target)

    # current_spacing / target_spacing
    assert pytest.approx(zoom[0]) == 2.5
    assert pytest.approx(zoom[1]) == 0.8
    assert pytest.approx(zoom[2]) == 0.8


def test_compute_zoom_factors_raises_for_nonpositive_target():
    current = (1.0, 1.0, 1.0)
    with pytest.raises(ValueError):
        compute_zoom_factors(current, (0.0, 1.0, 1.0))


def test_resample_to_spacing_preserves_physical_extent_within_tolerance():
    # Synthetic volume with known spacing
    orig_spacing = (2.5, 0.8, 0.8)  # (sz, sy, sx)
    target_spacing = (1.0, 1.0, 1.0)
    orig_shape = (16, 128, 128)

    volume = np.random.normal(loc=-600, scale=200, size=orig_shape).astype(
        np.float32
    )

    resampled = resample_to_spacing(
        volume,
        current_spacing=orig_spacing,
        target_spacing=target_spacing,
        order=1,
    )

    # Derived spacing from physical extent
    physical_extent = np.array(orig_shape) * np.array(orig_spacing)
    derived_spacing = physical_extent / np.array(resampled.shape)

    # Allow a small tolerance because of rounding in zoom()
    assert np.allclose(derived_spacing, np.array(target_spacing), rtol=0.05)


def test_normalize_and_resample_basic_hu_clamping_and_spacing():
    # Include values outside the window to test clamping
    orig_shape = (8, 32, 32)
    volume = np.linspace(-1500, 800, num=np.prod(orig_shape), dtype=np.float32).reshape(
        orig_shape
    )
    orig_spacing = (2.0, 1.5, 1.5)
    target_spacing = (1.0, 1.0, 1.0)
    hu_window = (-1000, 400)

    meta_in = {"series_uid": "test-series"}

    ct = normalize_and_resample(
        volume=volume,
        spacing=orig_spacing,
        metadata=meta_in,
        target_spacing=target_spacing,
        hu_window=hu_window,
        apply_denoising=False,
    )

    # Spacing in metadata should match requested target spacing
    assert ct.spacing == target_spacing
    assert tuple(ct.metadata["spacing_mm"]) == target_spacing

    # HU values should be clamped to window
    assert ct.data.min() >= hu_window[0] - 1e-3
    assert ct.data.max() <= hu_window[1] + 1e-3

    # Original metadata preserved
    assert ct.metadata["series_uid"] == "test-series"
    # Preprocessing info added
    assert "normalize_resample" in ct.metadata["preprocessing"]


def test_normalize_and_resample_denoising_changes_values():
    orig_shape = (8, 32, 32)
    # Some structured signal instead of pure noise
    z = np.linspace(-1000, 400, orig_shape[0], dtype=np.float32)[:, None, None]
    volume = z + np.random.normal(scale=50.0, size=orig_shape).astype(np.float32)

    orig_spacing = (2.0, 1.0, 1.0)

    ct_no_denoise = normalize_and_resample(
        volume=volume,
        spacing=orig_spacing,
        target_spacing=(1.0, 1.0, 1.0),
        apply_denoising=False,
    )

    ct_denoise = normalize_and_resample(
        volume=volume,
        spacing=orig_spacing,
        target_spacing=(1.0, 1.0, 1.0),
        apply_denoising=True,
        denoise_sigma=0.75,
    )

    # Shapes should match
    assert ct_no_denoise.data.shape == ct_denoise.data.shape

    # Denoising should change the values at least somewhere
    assert not np.allclose(ct_no_denoise.data, ct_denoise.data)

    # Noise level should decrease a bit
    assert np.std(ct_denoise.data) < np.std(ct_no_denoise.data)


def test_histogram_sanity_check_keys_and_ranges():
    shape = (8, 32, 32)
    volume = np.random.uniform(-1000, 400, size=shape).astype(np.float32)

    stats = histogram_sanity_check(volume)

    # Expected keys present
    for key in ["min", "max", "mean", "std", "p01", "p99"]:
        assert key in stats

    # Values in reasonable ranges for synthetic windowed lung data
    assert -1100 <= stats["min"] <= 500
    assert -1100 <= stats["p01"] <= 500
    assert -1100 <= stats["p99"] <= 500
    assert stats["min"] <= stats["p01"] <= stats["p99"] <= stats["max"]


def test_save_and_load_cached_volume_roundtrip(tmp_path: Path):
    shape = (4, 16, 16)
    data = np.random.uniform(-1000, 400, size=shape).astype(np.float32)
    spacing = (1.0, 1.0, 1.0)
    metadata = {
        "series_uid": "abc",
        "spacing_mm": spacing,
        "preprocessing": {
            "normalize_resample": {
                "hu_window": [-1000.0, 400.0],
                "apply_denoising": False,
                "denoise_sigma": 0.75,
                "target_spacing_mm": spacing,
                "interpolation_order": 1,
            }
        },
    }

    ct = CTVolume(data=data, spacing=spacing, metadata=metadata)
    cache_path = tmp_path / "ct_volume.npz"

    save_cached_volume(ct, cache_path)
    assert cache_path.exists()

    loaded = load_cached_volume(cache_path)

    assert loaded.data.shape == data.shape
    assert np.allclose(loaded.data, data)
    assert loaded.spacing == spacing
    assert loaded.metadata["series_uid"] == "abc"
    # Preprocessing block preserved
    assert loaded.metadata["preprocessing"]["normalize_resample"]["hu_window"] == [
        -1000.0,
        400.0,
    ]


def test_normalize_and_resample_with_cache_loads_from_cache(tmp_path: Path):
    # Use a counter to verify that the loader is only called once
    call_count = {"n": 0}

    def load_raw_fn():
        call_count["n"] += 1
        shape = (4, 16, 16)
        volume = np.zeros(shape, dtype=np.float32)
        spacing = (2.0, 1.5, 1.5)
        metadata = {"series_uid": "cache-test"}
        return volume, spacing, metadata

    cache_dir = tmp_path / "cache"
    cache_key = "series-001"

    # First call: should invoke load_raw_fn and write cache
    ct1, cache_path1 = normalize_and_resample_with_cache(
        cache_key=cache_key,
        load_raw_fn=load_raw_fn,
        cache_dir=cache_dir,
        target_spacing=(1.0, 1.0, 1.0),
    )

    assert call_count["n"] == 1
    assert cache_path1.exists()
    assert isinstance(ct1, CTVolume)

    # Second call: should load from cache and *not* call loader again
    ct2, cache_path2 = normalize_and_resample_with_cache(
        cache_key=cache_key,
        load_raw_fn=load_raw_fn,
        cache_dir=cache_dir,
        target_spacing=(1.0, 1.0, 1.0),
    )

    assert call_count["n"] == 1  # no additional calls
    assert cache_path2 == cache_path1
    # Data should be identical for both loads
    assert np.allclose(ct1.data, ct2.data)
    assert ct1.spacing == ct2.spacing

    # Metadata should be semantically equivalent
    assert ct1.metadata["series_uid"] == ct2.metadata["series_uid"]
    # spacing_mm may be tuple vs list after JSON round-trip
    assert np.allclose(ct1.metadata["spacing_mm"], ct2.metadata["spacing_mm"])

    nr1 = ct1.metadata["preprocessing"]["normalize_resample"]
    nr2 = ct2.metadata["preprocessing"]["normalize_resample"]

    # Check core fields; allow list/tuple differences
    assert nr1["apply_denoising"] == nr2["apply_denoising"]
    assert nr1["denoise_sigma"] == nr2["denoise_sigma"]
    assert nr1["interpolation_order"] == nr2["interpolation_order"]
    assert np.allclose(nr1["hu_window"], nr2["hu_window"])
    assert np.allclose(nr1["target_spacing_mm"], nr2["target_spacing_mm"])



def test_normalize_and_resample_with_cache_force_recompute(tmp_path: Path):
    call_count = {"n": 0}

    def load_raw_fn():
        call_count["n"] += 1
        shape = (4, 8, 8)
        volume = np.full(shape, fill_value=-800.0, dtype=np.float32)
        spacing = (2.0, 2.0, 2.0)
        metadata = {"series_uid": "force-recompute"}
        return volume, spacing, metadata

    cache_dir = tmp_path / "cache"
    cache_key = "series-002"

    # First call populates cache
    ct1, cache_path1 = normalize_and_resample_with_cache(
        cache_key=cache_key,
        load_raw_fn=load_raw_fn,
        cache_dir=cache_dir,
    )

    assert call_count["n"] == 1
    assert cache_path1.exists()

    # Second call with force_recompute=True should *re*-invoke loader
    ct2, cache_path2 = normalize_and_resample_with_cache(
        cache_key=cache_key,
        load_raw_fn=load_raw_fn,
        cache_dir=cache_dir,
        force_recompute=True,
    )

    assert call_count["n"] == 2
    assert cache_path2 == cache_path1
    assert np.allclose(ct1.data, ct2.data)
