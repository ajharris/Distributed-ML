#!/usr/bin/env python
"""
src/preprocess/run.py

Distributed CT preprocessing entry point using Dask.

Responsibilities
----------------
- Load dataset records via DatasetRegistry (CSV) or canonical Parquet.
- Build a lazy Dask graph for:
    * loading raw CT volumes
    * lung segmentation (masking the volume)
    * normalization + resampling with on-disk caching
- Execute in parallel on a local multi-process Dask cluster with progress reporting.
- Write preprocessed outputs under data/cache/preprocess/<dataset>/…

Typical usage
-------------
    python -m src.preprocess.run --config config/preprocess_nlst.yml

Expected YAML config (example)
------------------------------
dataset:
  name: nlst
  # One of these:
  metadata_parquet: data/metadata/metadata_NLST.parquet
  # or:
  # metadata_csv: data/raw_metadata/nlst_demo.csv
  limit: 20        # optional: max number of scans to process

paths:
  data_root: data                      # base directory for raw_image_path
  output_root: data/cache/preprocess   # base directory for cache outputs

preprocess:
  input_path_field: raw_image_path     # usually metadata_schema.COL_RAW_IMAGE_PATH
  series_uid_field: series_uid         # usually metadata_schema.COL_SERIES_UID
  segmentation:
    hu_threshold: -320.0
    min_component_size: 10000
    num_components_to_keep: 2
    closing_iterations: 2
    fill_holes: true
  normalization:
    target_spacing: [1.0, 1.0, 1.0]
    hu_window: [-1000, 400]
    apply_denoising: false
    denoise_sigma: 0.75
    interpolation_order: 1
  cache:
    force_recompute: false

dask:
  n_workers: 4
  threads_per_worker: 1

Notes
-----
- This script is intentionally conservative: it only assumes a single dataset
  at a time, but uses the canonical metadata schema and DatasetRegistry.
- Out-of-core behavior comes from the Dask task graph: each worker processes
  one series at a time and writes results to disk, so memory usage scales
  with the number of workers, not the total number of scans.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import dask
from dask import delayed
from dask.diagnostics import ProgressBar
import pandas as pd
import yaml

from src.utils.logger import get_logger
from src.utils.dask_cluster import start_local_cluster
from src.ingest.registry import DatasetRegistry
from src.ingest.metadata_schema import (
    COL_DATASET_NAME,
    COL_SERIES_UID,
    COL_RAW_IMAGE_PATH,
)
from src.ingest.metadata_io import rows_to_dataframe
from src.visualization.ct_viewer import load_ct_series
from src.preprocess.segment_lung import (
    LungSegmentationConfig,
    segment_lung_and_save,
)
from src.preprocess.normalize_resample import (
    CTVolume,
    normalize_and_resample_with_cache,
)

# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Distributed CT preprocessing pipeline (segmentation + normalization) with Dask."
    )
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to YAML config file describing dataset and preprocessing options.",
    )
    return parser.parse_args()


def load_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r") as f:
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict):
        raise ValueError(f"Config at {path} must be a YAML mapping.")
    return cfg


# ---------------------------------------------------------------------------
# Metadata loading via registry or Parquet
# ---------------------------------------------------------------------------


def load_metadata_table(config: Dict[str, Any]) -> pd.DataFrame:
    """
    Load a canonical metadata table for a single dataset.

    Preference:
    1. If `dataset.metadata_parquet` is provided, read it directly.
    2. Else, if `dataset.metadata_csv` is provided, use DatasetRegistry loader
       and convert rows to a DataFrame.
    """
    dataset_cfg = config.get("dataset", {})
    dataset_name = dataset_cfg.get("name")
    if not dataset_name:
        raise ValueError("Config must define dataset.name")

    parquet_path = dataset_cfg.get("metadata_parquet")
    csv_path = dataset_cfg.get("metadata_csv")

    if parquet_path:
        parquet_path = Path(parquet_path)
        if not parquet_path.exists():
            raise FileNotFoundError(f"Metadata Parquet not found: {parquet_path}")
        df = pd.read_parquet(parquet_path)
    elif csv_path:
        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"Metadata CSV not found: {csv_path}")
        loader = DatasetRegistry.get(dataset_name)
        rows = loader(csv_path)
        df = rows_to_dataframe(rows)
    else:
        raise ValueError(
            "Config must define either dataset.metadata_parquet or dataset.metadata_csv"
        )

    # Ensure dataset_name column is present & consistent
    if COL_DATASET_NAME not in df.columns:
        df[COL_DATASET_NAME] = dataset_name
    else:
        df[COL_DATASET_NAME] = df[COL_DATASET_NAME].fillna(dataset_name)

    # Optional limit for quick benchmarking
    limit = dataset_cfg.get("limit")
    if isinstance(limit, int) and limit > 0:
        df = df.head(limit)

    return df


# ---------------------------------------------------------------------------
# Segmentation + normalization per-series
# ---------------------------------------------------------------------------


def build_segmentation_config(seg_cfg: Dict[str, Any] | None) -> LungSegmentationConfig:
    if not seg_cfg:
        return LungSegmentationConfig()
    # Only override known fields; everything else uses dataclass defaults
    kwargs: Dict[str, Any] = {}
    for field in (
        "hu_threshold",
        "min_component_size",
        "num_components_to_keep",
        "closing_iterations",
        "fill_holes",
    ):
        if field in seg_cfg:
            kwargs[field] = seg_cfg[field]
    return LungSegmentationConfig(**kwargs)


def extract_normalization_kwargs(norm_cfg: Dict[str, Any] | None) -> Dict[str, Any]:
    if not norm_cfg:
        return {}
    out: Dict[str, Any] = {}
    for key in (
        "target_spacing",
        "hu_window",
        "apply_denoising",
        "denoise_sigma",
        "interpolation_order",
    ):
        if key in norm_cfg:
            out[key] = norm_cfg[key]
    return out


def _build_cache_key(dataset_name: str, series_uid: str) -> str:
    # Safe, human-readable key; _cache_path_for_key in normalize_resample
    # will sanitize slashes and append suffix.
    return f"{dataset_name}__{series_uid}"


def _build_paths_for_series(
    data_root: Path,
    output_root: Path,
    row: Dict[str, Any],
    input_path_field: str,
    series_uid_field: str,
) -> Tuple[Path, Path, Path, str, str]:
    """
    Construct raw input path and cache directories for a single series.
    """
    dataset_name = str(row.get(COL_DATASET_NAME, "UNKNOWN"))
    series_uid = str(row[series_uid_field])

    raw_rel = row.get(input_path_field)
    if raw_rel is None:
        raise ValueError(
            f"Row for series_uid={series_uid!r} has no {input_path_field!r} field"
        )

    raw_path = (data_root / str(raw_rel)).expanduser().resolve()

    # Normalized volume cache and lung mask cache live under:
    #   output_root / <dataset_name> / volumes
    #   output_root / <dataset_name> / lung_masks
    dataset_root = output_root / dataset_name
    vol_cache_dir = dataset_root / "volumes"
    mask_cache_dir = dataset_root / "lung_masks"

    cache_key = _build_cache_key(dataset_name, series_uid)

    return raw_path, vol_cache_dir, mask_cache_dir, dataset_name, cache_key


def preprocess_single_series(
    row: Dict[str, Any],
    config: Dict[str, Any],
    logger_name: str = "src.preprocess.run",
) -> str:
    """
    Preprocess a single CT series:

    1. Load raw volume from disk (NIfTI / Zarr / DICOM directory) via `load_ct_series`.
    2. Run classical lung segmentation and save the lung mask to cache.
    3. Apply the lung mask to the volume (non-lung voxels set to air HU).
    4. Normalize & resample with `normalize_and_resample_with_cache`.
    5. Return the path to the cached normalized volume.

    This function is designed to be Dask-delayed.
    """
    logger = get_logger(logger_name)

    paths_cfg = config.get("paths", {})
    preprocess_cfg = config.get("preprocess", {})

    data_root = Path(paths_cfg.get("data_root", "data"))
    output_root = Path(paths_cfg.get("output_root", "data/cache/preprocess"))

    input_path_field = preprocess_cfg.get("input_path_field", COL_RAW_IMAGE_PATH)
    series_uid_field = preprocess_cfg.get("series_uid_field", COL_SERIES_UID)

    seg_cfg_dict = preprocess_cfg.get("segmentation", {}) or {}
    seg_config = build_segmentation_config(seg_cfg_dict)

    norm_cfg_dict = preprocess_cfg.get("normalization", {}) or {}
    norm_kwargs = extract_normalization_kwargs(norm_cfg_dict)

    cache_cfg = preprocess_cfg.get("cache", {}) or {}
    force_recompute = bool(cache_cfg.get("force_recompute", False))

    raw_path, vol_cache_dir, mask_cache_dir, dataset_name, cache_key = (
        _build_paths_for_series(
            data_root=data_root,
            output_root=output_root,
            row=row,
            input_path_field=input_path_field,
            series_uid_field=series_uid_field,
        )
    )

    logger.info(
        "Preprocessing series",
        extra={"dataset": dataset_name, "series_uid": row.get(series_uid_field)},
    )

    # Inner loader; this is only called by normalize_and_resample_with_cache
    # if the cache is missing or force_recompute=True.
    def load_raw_fn() -> Tuple[Any, Tuple[float, float, float], Dict[str, Any]]:
        # 1) Load raw CT series
        ct = load_ct_series(raw_path)

        # 2) Segment lungs and save mask
        mask_cache_path = mask_cache_dir / f"{cache_key}_lungmask.npy"
        lung_mask = segment_lung_and_save(
            volume_hu=ct.volume,
            spacing_mm=ct.spacing,
            cache_path=mask_cache_path,
            config=seg_config,
        )

        # 3) Apply mask (non-lung voxels set to -1024 HU / air)
        masked_volume = ct.volume.copy()
        masked_volume[~lung_mask] = -1024.0

        # 4) Build metadata, merging canonical row info with on-disk info
        metadata = dict(row)
        metadata.setdefault("source_path", str(raw_path))
        metadata.setdefault("dataset_name", dataset_name)

        return masked_volume, ct.spacing, metadata

    # Normalize + resample with on-disk caching
    ct_volume, cache_path = normalize_and_resample_with_cache(
        cache_key=cache_key,
        load_raw_fn=load_raw_fn,
        cache_dir=vol_cache_dir,
        force_recompute=force_recompute,
        **norm_kwargs,
    )

    logger.info(
        "Finished preprocessing series",
        extra={
            "dataset": dataset_name,
            "series_uid": row.get(series_uid_field),
            "cache_path": str(cache_path),
            "shape": tuple(ct_volume.data.shape),
        },
    )

    return str(cache_path)


# ---------------------------------------------------------------------------
# Dask graph construction and execution
# ---------------------------------------------------------------------------


def build_dask_graph(
    df: pd.DataFrame,
    config: Dict[str, Any],
    logger_name: str,
) -> List[dask.delayed]:
    tasks: List[dask.delayed] = []
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        task = delayed(preprocess_single_series)(
            row=row_dict,
            config=config,
            logger_name=logger_name,
        )
        tasks.append(task)
    return tasks


def run_pipeline(config: Dict[str, Any]) -> None:
    logger = get_logger("src.preprocess.run")

    logger.info("Loading metadata table for preprocessing")
    df = load_metadata_table(config)

    logger.info(
        "Loaded metadata table",
        extra={
            "n_rows": int(df.shape[0]),
            "columns": list(df.columns),
        },
    )

    dask_cfg = config.get("dask", {}) or {}
    n_workers = int(dask_cfg.get("n_workers", 4))
    threads_per_worker = int(dask_cfg.get("threads_per_worker", 1))

    logger.info(
        "Starting local Dask cluster",
        extra={
            "n_workers": n_workers,
            "threads_per_worker": threads_per_worker,
        },
    )

    client = start_local_cluster(
        n_workers=n_workers,
        threads_per_worker=threads_per_worker,
    )
    logger.info("Dask cluster started", extra={"scheduler_info": client.scheduler_info()})

    logger.info("Building Dask task graph for preprocessing")
    tasks = build_dask_graph(df=df, config=config, logger_name=logger.name)
    logger.info("Task graph built", extra={"n_tasks": len(tasks)})

    # Execute with progress reporting
    logger.info("Starting Dask computation")
    with ProgressBar():
        results = dask.compute(*tasks)

    logger.info(
        "Completed preprocessing",
        extra={
            "n_series": len(results),
            "outputs": results,
        },
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    args = parse_args()
    cfg_path = Path(args.config)
    config = load_config(cfg_path)
    run_pipeline(config)


if __name__ == "__main__":
    main()
