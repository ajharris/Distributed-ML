"""
CT normalization and resampling utilities.

This module implements:

- HU clamping to a standard lung window
- Optional denoising
- Resampling to a target voxel spacing (default 1x1x1 mm)
- Simple, explicit metadata updates
- Optional on-disk caching of intermediate outputs

The core entry point is `normalize_and_resample` for array-based
processing, and `normalize_and_resample_with_cache` for pipeline
usage with caching.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple, Union

import json
import numpy as np
from scipy.ndimage import gaussian_filter, zoom


Array3D = np.ndarray
Spacing3D = Tuple[float, float, float]  # (z, y, x) in mm


@dataclass
class CTVolume:
    """Container for a preprocessed CT volume and associated metadata.

    Attributes
    ----------
    data:
        3D numpy array in (z, y, x) order, dtype float32.
    spacing:
        Voxel spacing in mm as (sz, sy, sx).
    metadata:
        Opaque metadata dictionary. This module only *adds* keys and does
        not remove or rename any existing fields.
    """

    data: Array3D
    spacing: Spacing3D
    metadata: Dict[str, Any]


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------


def clamp_hu(
    volume: Array3D,
    hu_min: int = -1000,
    hu_max: int = 400,
) -> Array3D:
    """Clamp HU values to a lung window.

    Parameters
    ----------
    volume:
        3D array of HU values.
    hu_min, hu_max:
        Lower and upper HU bounds. Default approximates a standard lung window.

    Returns
    -------
    Array3D
        Clamped volume (float32).
    """
    v = volume.astype(np.float32, copy=False)
    return np.clip(v, hu_min, hu_max, out=v)


def maybe_denoise(
    volume: Array3D,
    enabled: bool = False,
    sigma: float = 0.75,
) -> Array3D:
    """Optionally apply a light Gaussian denoising filter.

    Parameters
    ----------
    volume:
        3D array (float32).
    enabled:
        If True, apply Gaussian denoising.
    sigma:
        Standard deviation for the Gaussian kernel, in voxels.

    Returns
    -------
    Array3D
        Possibly denoised volume.
    """
    if not enabled:
        return volume

    # gaussian_filter preserves dtype by default; ensure float32
    out = gaussian_filter(volume.astype(np.float32, copy=False), sigma=sigma)
    return out.astype(np.float32, copy=False)


def compute_zoom_factors(
    current_spacing: Spacing3D,
    target_spacing: Spacing3D,
) -> Tuple[float, float, float]:
    """Compute zoom factors for resampling.

    zoom_factor = current_spacing / target_spacing

    Parameters
    ----------
    current_spacing:
        Original spacing (sz, sy, sx) in mm.
    target_spacing:
        Desired spacing (sz, sy, sx) in mm.

    Returns
    -------
    (float, float, float)
        Zoom factors for (z, y, x) axes.
    """
    sz, sy, sx = current_spacing
    tz, ty, tx = target_spacing

    if tz <= 0 or ty <= 0 or tx <= 0:
        raise ValueError(f"Target spacing must be positive, got {target_spacing}")

    return (sz / tz, sy / ty, sx / tx)


def resample_to_spacing(
    volume: Array3D,
    current_spacing: Spacing3D,
    target_spacing: Spacing3D = (1.0, 1.0, 1.0),
    order: int = 1,
) -> Array3D:
    """Resample a 3D volume to the desired spacing.

    Parameters
    ----------
    volume:
        3D array in (z, y, x) order.
    current_spacing:
        Original spacing (sz, sy, sx) in mm.
    target_spacing:
        Desired spacing (sz, sy, sx) in mm. Defaults to 1x1x1 mm.
    order:
        Spline interpolation order for `scipy.ndimage.zoom`.
        1 = linear (recommended for CT).

    Returns
    -------
    Array3D
        Resampled volume (float32) with new spacing `target_spacing`.
    """
    zoom_factors = compute_zoom_factors(current_spacing, target_spacing)
    resampled = zoom(
        volume.astype(np.float32, copy=False),
        zoom=zoom_factors,
        order=order,
    )
    return resampled.astype(np.float32, copy=False)


def histogram_sanity_check(volume: Array3D) -> Dict[str, float]:
    """Compute simple histogram stats for downstream sanity checks.

    This function does *not* raise by default; tests or callers can
    inspect the returned statistics and decide on thresholds.

    Parameters
    ----------
    volume:
        3D float32 array.

    Returns
    -------
    dict
        Dictionary with basic statistics.
    """
    v = volume.astype(np.float32, copy=False)
    stats = {
        "min": float(np.min(v)),
        "max": float(np.max(v)),
        "mean": float(np.mean(v)),
        "std": float(np.std(v)),
        "p01": float(np.percentile(v, 1)),
        "p99": float(np.percentile(v, 99)),
    }
    return stats


# ---------------------------------------------------------------------------
# Public pipeline API
# ---------------------------------------------------------------------------


def normalize_and_resample(
    volume: Array3D,
    spacing: Spacing3D,
    metadata: Optional[Dict[str, Any]] = None,
    target_spacing: Spacing3D = (1.0, 1.0, 1.0),
    hu_window: Tuple[int, int] = (-1000, 400),
    apply_denoising: bool = False,
    denoise_sigma: float = 0.75,
    interpolation_order: int = 1,
) -> CTVolume:
    """Full normalization + resampling pipeline for a single CT volume.

    Steps:
    1. HU clamp to `hu_window`.
    2. Optional Gaussian denoising.
    3. Resample to `target_spacing` using `scipy.ndimage.zoom`.
    4. Update metadata with new spacing and preprocessing parameters.

    Parameters
    ----------
    volume:
        Input 3D HU volume (z, y, x).
    spacing:
        Original voxel spacing (sz, sy, sx) in mm.
    metadata:
        Optional metadata dict to copy and update.
    target_spacing:
        Desired spacing (sz, sy, sx) in mm. Default: (1, 1, 1).
    hu_window:
        (hu_min, hu_max) for clamping.
    apply_denoising:
        Whether to apply Gaussian denoising.
    denoise_sigma:
        Gaussian sigma (in voxels) if denoising is enabled.
    interpolation_order:
        Spline interpolation order for resampling (1 = linear).

    Returns
    -------
    CTVolume
        Normalized and resampled volume plus updated metadata.
    """
    hu_min, hu_max = hu_window

    # 1. Clamp HU
    v = clamp_hu(volume, hu_min=hu_min, hu_max=hu_max)

    # 2. Optional denoising
    v = maybe_denoise(v, enabled=apply_denoising, sigma=denoise_sigma)

    # 3. Resample to target spacing
    v = resample_to_spacing(
        v,
        current_spacing=spacing,
        target_spacing=target_spacing,
        order=interpolation_order,
    )

    # 4. Metadata update (non-destructive)
    meta: Dict[str, Any] = dict(metadata) if metadata is not None else {}
    meta["spacing_mm"] = tuple(float(s) for s in target_spacing)

    preprocessing_info = meta.get("preprocessing", {})
    preprocessing_info["normalize_resample"] = {
        "hu_window": (float(hu_min), float(hu_max)),
        "apply_denoising": bool(apply_denoising),
        "denoise_sigma": float(denoise_sigma),
        "target_spacing_mm": tuple(float(s) for s in target_spacing),
        "interpolation_order": int(interpolation_order),
    }
    meta["preprocessing"] = preprocessing_info

    return CTVolume(
        data=v.astype(np.float32, copy=False),
        spacing=target_spacing,
        metadata=meta,
    )


# ---------------------------------------------------------------------------
# Simple caching helpers
# ---------------------------------------------------------------------------


def _cache_path_for_key(
    cache_dir: Union[str, Path],
    cache_key: str,
) -> Path:
    """Construct a cache path for a given key."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    safe_key = cache_key.replace("/", "_")
    return cache_dir / f"{safe_key}_normalized_resampled.npz"


def save_cached_volume(
    ct_volume: CTVolume,
    cache_path: Union[str, Path],
) -> None:
    """Save a CTVolume to disk as a compressed NumPy archive.

    The archive stores:
      - data: float32 volume
      - spacing: float32 array of length 3
      - metadata_json: JSON-encoded metadata dictionary
    """
    cache_path = Path(cache_path)
    metadata_json = json.dumps(ct_volume.metadata or {})
    np.savez_compressed(
        cache_path,
        data=ct_volume.data.astype(np.float32, copy=False),
        spacing=np.asarray(ct_volume.spacing, dtype=np.float32),
        metadata_json=np.asarray(metadata_json, dtype=np.unicode_),
    )


def load_cached_volume(cache_path: Union[str, Path]) -> CTVolume:
    """Load a CTVolume from a compressed NumPy archive."""
    cache_path = Path(cache_path)
    if not cache_path.exists():
        raise FileNotFoundError(f"No cached volume at {cache_path}")

    with np.load(cache_path, allow_pickle=False) as npz:
        data = npz["data"].astype(np.float32, copy=False)
        spacing_arr = npz["spacing"].astype(np.float32, copy=False)
        metadata_json = str(npz["metadata_json"])
        metadata = json.loads(metadata_json)

    spacing = tuple(float(x) for x in spacing_arr.tolist())  # type: ignore[assignment]
    return CTVolume(data=data, spacing=spacing, metadata=metadata)


def normalize_and_resample_with_cache(
    cache_key: str,
    load_raw_fn: Callable[[], Tuple[Array3D, Spacing3D, Dict[str, Any]]],
    cache_dir: Union[str, Path],
    force_recompute: bool = False,
    **normalize_kwargs: Any,
) -> Tuple[CTVolume, Path]:
    """Normalize + resample a volume with optional on-disk caching.

    Parameters
    ----------
    cache_key:
        Unique identifier for this volume (e.g., series UID or filename stem).
    load_raw_fn:
        Zero-argument callable that returns (volume, spacing, metadata).
        This is only called if the cache is missing or `force_recompute=True`.
    cache_dir:
        Directory in which to store cache files.
    force_recompute:
        If True, ignore any existing cache and recompute.
    **normalize_kwargs:
        Additional keyword arguments forwarded to `normalize_and_resample`.

    Returns
    -------
    (CTVolume, Path)
        The processed CTVolume and the path to its cache file.
    """
    cache_path = _cache_path_for_key(cache_dir, cache_key)

    if cache_path.exists() and not force_recompute:
        ct = load_cached_volume(cache_path)
        return ct, cache_path

    # Load raw data on demand to avoid unnecessary I/O
    volume, spacing, metadata = load_raw_fn()

    ct = normalize_and_resample(
        volume=volume,
        spacing=spacing,
        metadata=metadata,
        **normalize_kwargs,
    )
    save_cached_volume(ct, cache_path)
    return ct, cache_path
