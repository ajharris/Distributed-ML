# CT Visualization Tool Documentation

## Overview

The CT Visualization Tool provides a lightweight and extensible way to inspect CT volumes and associated metadata. It is designed for:

- Verification of ingestion outputs
- Quality control during preprocessing
- Understanding CT geometry
- Debugging transformations
- Building intuition before large-scale runs

---

## Features

### Supported Input Formats

- NIfTI (.nii, .nii.gz)
- DICOM directories
- Zarr stores

### Visualization Features

- Axial, coronal, sagittal slicing
- Window/level adjustment
- HU clipping and normalization
- Optional interactive widgets

### Metadata Panel

Displays:

- Series UID
- Spacing
- Dimensions
- Patient ID
- Manufacturer
- Modality
- Slice thickness
- Pixel spacing

---

## Module Structure

```
src/visualization/
    ct_viewer.py
    __init__.py
```

---

## Usage Examples

### Load CT + Metadata

```python
from src.visualization.ct_viewer import load_ct_series, extract_display_metadata

ct = load_ct_series("Lung_001.nii.gz")
meta = extract_display_metadata(ct)

for k, v in meta.items():
    print(k, ":", v)
```

### Visualize a Slice

```python
import matplotlib.pyplot as plt
from src.visualization.ct_viewer import get_slice, apply_window

slice_2d = get_slice(ct, index=80, plane="axial")
windowed = apply_window(slice_2d, center=-600, width=1500)

plt.imshow(windowed, cmap="gray")
plt.axis("off")
plt.show()
```

### Interactive Viewer

```python
import ipywidgets as widgets
import matplotlib.pyplot as plt

def display_slice(idx):
    s = get_slice(ct, idx, plane="axial")
    w = apply_window(s, center=-600, width=1500)
    plt.figure(figsize=(5,5))
    plt.imshow(w, cmap="gray")
    plt.axis("off")
    plt.show()

widgets.interact(display_slice, idx=(0, ct.shape[0]-1))
```

---

## Testing

```
tests/visualization/test_ct_viewer.py
```

---

## Future Extensions

- Mask overlays
- 3D rendering
- Integration with segmentation modules
