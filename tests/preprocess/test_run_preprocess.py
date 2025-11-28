# tests/preprocess/test_run_preprocess.py

from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import pytest

import dask

from src.preprocess import run as preprocess_run


# ---------------------------------------------------------------------------
# load_metadata_table
# ---------------------------------------------------------------------------


def test_load_metadata_table_reads_parquet_and_preserves_dataset_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """load_metadata_table should:
    - Use pandas.read_parquet when metadata_parquet is provided
    - Ensure COL_DATASET_NAME exists and is filled with dataset.name
    """

    meta_path = tmp_path / "metadata.parquet"
    meta_path.write_text("dummy")  # just to satisfy Path.exists()

    # Fake DataFrame returned by pd.read_parquet
    df_in = pd.DataFrame(
        {
            preprocess_run.COL_DATASET_NAME: ["nlst"],
            "series_uid": ["series-001"],
        }
    )

    def fake_read_parquet(path: Path):
        assert path == meta_path
        return df_in

    monkeypatch.setattr(preprocess_run.pd, "read_parquet", fake_read_parquet)

    config = {
        "dataset": {
            "name": "nlst",
            "metadata_parquet": str(meta_path),
            "limit": 10,
        }
    }

    df = preprocess_run.load_metadata_table(config)

    assert df.shape[0] == 1
    assert preprocess_run.COL_DATASET_NAME in df.columns
    assert set(df[preprocess_run.COL_DATASET_NAME].unique()) == {"nlst"}


def test_load_metadata_table_uses_dataset_registry_for_csv_and_applies_limit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """When metadata_csv is provided, load_metadata_table should:
    - Look up a loader via DatasetRegistry.get(dataset_name)
    - Call rows_to_dataframe on the returned rows
    - Apply dataset.limit if provided
    """
    csv_path = tmp_path / "metadata.csv"
    csv_path.write_text("dummy\n")

    rows_seen: List[str] = []

    def fake_loader(path: Path):
        # Called with the CSV path
        assert Path(path) == csv_path
        return ["ROW1", "ROW2"]

    def fake_rows_to_dataframe(rows):
        rows_seen.extend(list(rows))
        return pd.DataFrame(
            {
                preprocess_run.COL_DATASET_NAME: ["nlst", "nlst"],
                "series_uid": ["s1", "s2"],
            }
        )

    # Override DatasetRegistry.get to return our loader
    monkeypatch.setattr(
        preprocess_run.DatasetRegistry,
        "get",
        lambda key: fake_loader,
    )
    monkeypatch.setattr(preprocess_run, "rows_to_dataframe", fake_rows_to_dataframe)

    config = {
        "dataset": {
            "name": "nlst",
            "metadata_csv": str(csv_path),
            "limit": 1,
        }
    }

    df = preprocess_run.load_metadata_table(config)

    # Loader was used, and rows_to_dataframe saw the rows
    assert rows_seen == ["ROW1", "ROW2"]

    # Limit applied → only first row kept
    assert df.shape[0] == 1
    assert list(df["series_uid"]) == ["s1"]
    assert set(df[preprocess_run.COL_DATASET_NAME].unique()) == {"nlst"}


# ---------------------------------------------------------------------------
# preprocess_single_series
# ---------------------------------------------------------------------------


def test_preprocess_single_series_writes_outputs_and_uses_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """preprocess_single_series should:
    - load CT via load_ct_series
    - run segmentation (masking the volume)
    - call normalize_and_resample_with_cache with a loader
    - write a .npy output under data/cache/preprocess/<dataset> by default
    """
    # Minimal config
    config: Dict[str, Any] = {
        "paths": {
            "data_root": str(tmp_path / "data"),
            "output_root": str(tmp_path / "cache"),
        },
        "preprocess": {
            "input_path_field": "filepath",
            "series_uid_field": "series_uid",
            "segmentation": {"hu_threshold": -600.0},
            "normalization": {
                "target_spacing": [1.0, 1.0, 1.0],
                "hu_window": [-1000.0, 400.0],
            },
            "cache": {
                "force_recompute": True,
            },
        },
        "dataset": {"name": "nlst"},
    }

    row = {
        preprocess_run.COL_DATASET_NAME: "nlst",
        "series_uid": "series-001",
        "filepath": "ct/series-001",
    }

    # Fake CT object returned by load_ct_series
    class FakeCT:
        def __init__(self, volume, spacing):
            self.volume = volume
            self.spacing = spacing

    volume = np.zeros((4, 8, 8), dtype=np.float32)
    spacing = (2.0, 1.5, 1.5)

    def fake_load_ct_series(path: Path):
        # Path should be under data_root / filepath
        expected = Path(config["paths"]["data_root"]) / row["filepath"]
        assert Path(path) == expected.resolve()
        return FakeCT(volume=volume.copy(), spacing=spacing)

    mask_cache_paths: List[Path] = []

    def fake_segment_lung_and_save(
        volume_hu,
        spacing_mm,
        cache_path,
        config=None,
        **kwargs,
    ):
        # Called with CT volume and spacing from loader
        assert volume_hu.shape == volume.shape
        assert spacing_mm == spacing
        mask_cache_paths.append(Path(cache_path))
        # Simple mask: keep everything
        return np.ones_like(volume_hu, dtype=bool)

    from src.preprocess.normalize_resample import CTVolume

    called_norm: Dict[str, Any] = {}

    def fake_normalize_and_resample_with_cache(
        cache_key,
        load_raw_fn,
        cache_dir,
        force_recompute,
        **norm_kwargs,
    ):
        # Called with the expected key and cache dir
        called_norm["cache_key"] = cache_key
        called_norm["cache_dir"] = Path(cache_dir)
        called_norm["force_recompute"] = force_recompute
        called_norm["norm_kwargs"] = norm_kwargs

        vol, sp, meta = load_raw_fn()

        called_norm["volume_shape"] = vol.shape
        called_norm["spacing"] = sp
        called_norm["metadata"] = meta

        out_path = Path(cache_dir) / f"{cache_key}.npz"
        out_path.parent.mkdir(parents=True, exist_ok=True)

        ct = CTVolume(data=vol, spacing=sp, metadata=meta)
        return ct, out_path

    monkeypatch.setattr(preprocess_run, "load_ct_series", fake_load_ct_series)
    monkeypatch.setattr(
        preprocess_run, "segment_lung_and_save", fake_segment_lung_and_save
    )
    monkeypatch.setattr(
        preprocess_run,
        "normalize_and_resample_with_cache",
        fake_normalize_and_resample_with_cache,
    )

    # Run
    cache_path_str = preprocess_run.preprocess_single_series(row=row, config=config)
    cache_path = Path(cache_path_str)

    dataset_name = row[preprocess_run.COL_DATASET_NAME]
    series_uid = row["series_uid"]
    expected_cache_key = f"{dataset_name}__{series_uid}"

    # Mask cache path: data/cache/preprocess/<dataset>/lung_masks/<key>_lungmask.npy
    expected_mask_cache = (
        Path(config["paths"]["output_root"])
        / dataset_name
        / "lung_masks"
        / f"{expected_cache_key}_lungmask.npy"
    ).resolve()

    assert mask_cache_paths, "segment_lung_and_save was never called"
    assert mask_cache_paths[0].resolve() == expected_mask_cache

    # Volume cache path: data/cache/preprocess/<dataset>/volumes/<key>.npz
    expected_volume_cache_dir = (
        Path(config["paths"]["output_root"]) / dataset_name / "volumes"
    )
    assert cache_path.parent.resolve() == expected_volume_cache_dir.resolve()
    assert cache_path.name == f"{expected_cache_key}.npz"

    # normalize_and_resample_with_cache received correct args
    assert called_norm["cache_key"] == expected_cache_key
    assert called_norm["cache_dir"].resolve() == expected_volume_cache_dir.resolve()
    assert called_norm["force_recompute"] is True

    meta = called_norm["metadata"]
    # Metadata should include useful fields
    assert meta["dataset_name"] == dataset_name
    assert meta["series_uid"] == series_uid
    assert "source_path" in meta
    assert meta["source_path"].endswith(row["filepath"])


# ---------------------------------------------------------------------------
# build_dask_graph
# ---------------------------------------------------------------------------


def test_build_dask_graph_creates_one_task_per_row(monkeypatch: pytest.MonkeyPatch):
    """build_dask_graph should create a delayed task for each metadata row."""

    df = pd.DataFrame(
        {
            "dataset_name": ["nlst", "nlst", "nlst"],
            "series_uid": ["s1", "s2", "s3"],
        }
    )

    calls: List[Dict[str, Any]] = []

    def fake_preprocess_single_series(row, config, logger_name):
        calls.append({"row": row, "config": config, "logger_name": logger_name})
        # Return a simple identifier
        return f"processed-{row['series_uid']}"

    monkeypatch.setattr(
        preprocess_run, "preprocess_single_series", fake_preprocess_single_series
    )

    config = {"dummy": "value"}
    tasks = preprocess_run.build_dask_graph(df=df, config=config, logger_name="tester")

    assert len(tasks) == len(df)

    # Execute synchronously via Dask to ensure tasks are runnable
    results = dask.compute(*tasks, scheduler="single-threaded")
    assert results == ("processed-s1", "processed-s2", "processed-s3")

    # And we saw all rows in preprocess_single_series
    assert {c["row"]["series_uid"] for c in calls} == {"s1", "s2", "s3"}


# ---------------------------------------------------------------------------
# run_pipeline wiring
# ---------------------------------------------------------------------------


def test_run_pipeline_uses_cluster_and_dask_compute(monkeypatch: pytest.MonkeyPatch):
    """run_pipeline should:
    - call load_metadata_table(config)
    - start a local cluster with config.dask params
    - build a Dask graph
    - call dask.compute on the tasks
    without requiring the real heavy CT stack.
    """

    observed: Dict[str, Any] = {}

    # 1) load_metadata_table stub
    def fake_load_metadata_table(config):
        observed["config"] = config
        return pd.DataFrame({"series_uid": ["s1", "s2"]})

    monkeypatch.setattr(
        preprocess_run, "load_metadata_table", fake_load_metadata_table
    )

    # 2) Fake client/cluster
    class FakeClient:
        def __init__(self, **info):
            self.info = info

        def scheduler_info(self):
            return {"workers": {}}

    def fake_start_local_cluster(n_workers: int, threads_per_worker: int):
        observed["cluster_args"] = (n_workers, threads_per_worker)
        return FakeClient(n_workers=n_workers, threads_per_worker=threads_per_worker)

    monkeypatch.setattr(
        preprocess_run, "start_local_cluster", fake_start_local_cluster
    )

    # 3) build_dask_graph stub
    tasks = ["task-1", "task-2"]

    def fake_build_dask_graph(df, config, logger_name):
        observed["build_df_len"] = len(df)
        observed["build_logger_name"] = logger_name
        return tasks

    monkeypatch.setattr(preprocess_run, "build_dask_graph", fake_build_dask_graph)

    # 4) dask.compute stub
    computed: Dict[str, Any] = {}

    def fake_compute(*args, **kwargs):
        computed["tasks"] = args
        computed["kwargs"] = kwargs
        # Return one result per task
        return tuple(f"result-{t}" for t in args)

    monkeypatch.setattr(preprocess_run.dask, "compute", fake_compute)

    # Run
    config = {
        "dataset": {"name": "nlst"},
        "dask": {"n_workers": 2, "threads_per_worker": 1},
    }

    preprocess_run.run_pipeline(config)

    # load_metadata_table saw the config
    assert observed["config"] is config

    # Cluster started with requested worker args
    assert observed["cluster_args"] == (2, 1)

    # build_dask_graph saw the right df and logger name
    assert observed["build_df_len"] == 2
    assert isinstance(observed["build_logger_name"], str)

    # dask.compute called with our tasks
    assert "tasks" in computed
    assert computed["tasks"] == tuple(tasks)
