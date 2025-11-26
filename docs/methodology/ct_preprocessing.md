
# 4. CT Preprocessing Pipeline Roadmap

This section outlines the planned components of the CT preprocessing workflow now that baseline lung segmentation has been implemented.

## 4.1 Lung Segmentation (Completed)

- Classical HU-threshold + connected-component segmentation implemented in  
  `src/preprocess/segment_lung.py`
- Full deterministic test suite in  
  `tests/preprocess/test_segment_lung.py`
- Produces binary lung masks aligned with original voxel spacing
- Forms the foundation for downstream preprocessing and feature extraction

## 4.2 Spacing Normalization (Upcoming)

- Resample CT volumes to a unified voxel spacing  
  (e.g., 1.0 × 1.0 × 1.0 mm isotropic)
- Resample lung masks using nearest-neighbor interpolation
- Add regression tests verifying:
  - Shape changes
  - Preservation of object boundaries
  - Deterministic outputs

## 4.3 HU Normalization and Clipping

- Define standardized HU window for thoracic CT (e.g., [-1024, 200])
- Normalize intensity ranges across heterogeneous datasets
- Add tests verifying idempotency and consistent clipping behavior

## 4.4 Preprocessed Volume / Mask Registration

- Write `preprocessed_image_path` and `lung_mask_path` to metadata
- Ensure compatibility with ingestion schema
- Maintain deterministic and reproducible file naming across datasets

## 4.5 Preprocessing Orchestration

- Implement dataset-level preprocessing scripts
- Batch processing of entire datasets via Dask
- Ensure reproducibility for cluster-based or local execution
