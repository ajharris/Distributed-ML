
# Lung Segmentation Module (`segment_lung.py`)

This module provides the baseline lung segmentation implementation for the project.  
It is fully deterministic, fast, and does not require a GPU or deep-learning model.

## Method

The algorithm uses a classical pipeline:

1. **HU Thresholding**  
   Voxels below a configurable HU threshold (default: −320 HU) are considered potential lung/air.

2. **3D Connected Components**  
   The algorithm retains the largest connected components, typically corresponding to the left and right lungs.

3. **Morphological Closing**  
   Binary closing smooths boundaries and seals small gaps.

4. **Slice-Wise Hole Filling**  
   Ensures anatomically consistent masks by removing internal cavities within the lung regions.

## Functions

### `segment_lung(volume_hu, spacing_mm=None, config=None)`
Returns a boolean lung mask with the **same shape** as the input CT volume.

### `segment_lung_and_save(volume_hu, spacing_mm=None, cache_path=None, config=None)`
Runs segmentation and optionally saves the resulting binary mask to a `.npy` cache file.

If `cache_path` is provided, the directory is created automatically.

## Example

```python
from src.preprocess.segment_lung import segment_lung

mask = segment_lung(volume_hu, spacing_mm=(1.0, 1.0, 1.0))
```

Saving the mask:

```python
from src.preprocess.segment_lung import segment_lung_and_save

mask = segment_lung_and_save(volume_hu, cache_path="masks/scan123_lung_mask.npy")
```

## Tests

Unit tests are located at:

```
tests/preprocess/test_segment_lung.py
```

These tests ensure:

- correct mask shape and type  
- plausible segmentation of synthetic lung volumes  
- deterministic outputs  
- cache saving correctness  
- stable behavior when no voxels meet threshold criteria  

This documentation corresponds to the lung segmentation module implemented in the branch `implement-lung-segmentation-pipeline`.
