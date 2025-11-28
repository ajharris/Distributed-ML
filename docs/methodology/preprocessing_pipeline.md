# CT Preprocessing Pipeline

This document describes the complete preprocessing workflow used in the Distributed-ML project.

---

## Overview

The pipeline transforms raw CT volumes into standardized, reproducible 3D arrays suitable for ML and downstream analysis.

Steps:

1. **Load CT series** (DICOM / NIfTI / Zarr)
2. **Perform classical lung segmentation**
3. **Mask non-lung voxels**
4. **Apply HU normalization**
5. **Resample to isotropic spacing**
6. **Cache results to disk (NPZ + mask)**
7. **Run distributed processing with Dask**

The workflow is fully configurable via YAML.

---

## Distributed Execution

Main orchestrator:

```
src/preprocess/run.py
```

It performs:

- Metadata loading (`metadata_parquet` / registry)
- Dask cluster creation (`start_local_cluster`)
- Per-series DAG construction (Dask `delayed`)
- Lazy parallel execution
- Disk caching of volumes + masks
- Logging and progress reporting

Each series is independent → highly parallelizable.

---

## Benchmarking

A functional benchmark is provided:

```
config/preprocess_task06_benchmark.yml
```

This benchmark processes **10 CT volumes** from the *Task06 Lung* dataset located at:

```
data/raw_test/Task06_Lung/imagesTr/*.nii.gz
```

Outputs stored in:

```
data/cache/preprocess/task06_demo/
```

To run:

```bash
rm -rf data/cache/preprocess/task06_demo
time python -m src.preprocess.run --config config/preprocess_task06_benchmark.yml
```

Benchmark demonstrates:

- End-to-end distributed execution
- Out-of-core performance
- Realistic runtime (~1–2 minutes on laptop)
- Correct caching of results

---

## Output Structure

For each series:

- **Normalized volume (.npz)**  
  ```
  data/cache/preprocess/<dataset>/volumes/<key>.npz
  ```

- **Lung mask (.npy)**  
  ```
  data/cache/preprocess/<dataset>/lung_masks/<key>_lungmask.npy
  ```

NPZ metadata includes:

- spacing  
- series_uid  
- dataset name  
- source location  

---

