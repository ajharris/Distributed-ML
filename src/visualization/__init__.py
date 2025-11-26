# src/visualization/__init__.py
"""
Visualization utilities for CT volumes and associated metadata.

Currently includes:
- CTVolume dataclass
- File loaders for NIfTI, DICOM directories, and Zarr stores
- Slice extraction helpers for axial/coronal/sagittal views
- Window/level utilities for display in notebooks or dashboards
"""

from .ct_viewer import (
    CTVolume,
    load_ct_series,
    get_slice,
    apply_window,
    extract_display_metadata,
)
