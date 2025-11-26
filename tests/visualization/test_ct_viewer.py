# tests/visualization/test_ct_viewer.py

import numpy as np
import pytest

from src.visualization.ct_viewer import (
    CTVolume,
    get_slice,
    apply_window,
    extract_display_metadata,
)


def _make_dummy_ct(shape=(8, 16, 32)) -> CTVolume:
    z, y, x = shape
    volume = np.arange(z * y * x, dtype=np.float32).reshape(z, y, x)
    spacing = (1.5, 0.8, 0.8)
    metadata = {
        "source_type": "test",
        "SeriesInstanceUID": "1.2.3.4",
        "PatientID": "TEST001",
        "Modality": "CT",
        "Manufacturer": "ChatGPTScanner",
    }
    return CTVolume(volume=volume, spacing=spacing, metadata=metadata, source="dummy")


def test_ctvolume_summary_structure():
    ct = _make_dummy_ct()
    summary = ct.summary()

    assert "volume" in summary
    assert "shape" in summary["volume"]
    assert summary["volume"]["shape"] == ct.shape
    assert "source" in summary
    assert summary["source"] == "dummy"


@pytest.mark.parametrize("plane", ["axial", "coronal", "sagittal"])
def test_get_slice_valid_indices(plane):
    ct = _make_dummy_ct(shape=(8, 16, 32))
    z, y, x = ct.shape

    if plane == "axial":
        idx = z // 2
    elif plane == "coronal":
        idx = y // 2
    else:
        idx = x // 2

    slice_2d = get_slice(ct, idx, plane=plane)
    assert slice_2d.ndim == 2
    assert slice_2d.dtype == np.float32


@pytest.mark.parametrize("plane", ["axial", "coronal", "sagittal"])
def test_get_slice_out_of_range_raises(plane):
    ct = _make_dummy_ct(shape=(4, 4, 4))

    if plane == "axial":
        idx = 10
    elif plane == "coronal":
        idx = 10
    else:
        idx = 10

    with pytest.raises(IndexError):
        get_slice(ct, idx, plane=plane)


def test_apply_window_basic_properties():
    # Hard-code HU-like values
    slice_2d = np.array(
        [
            [-1000.0, -800.0, -600.0],
            [-400.0, -200.0, 0.0],
            [200.0, 400.0, 600.0],
        ],
        dtype=np.float32,
    )

    center = -500.0
    width = 1500.0
    windowed = apply_window(slice_2d, center=center, width=width)

    assert windowed.dtype == np.uint8
    assert windowed.min() >= 0
    assert windowed.max() <= 255
    # Check that ordering is preserved (monotonic)
    flat = windowed.flatten()
    assert np.all(flat[:-1] <= flat[1:])


def test_apply_window_invalid_width_raises():
    slice_2d = np.zeros((4, 4), dtype=np.float32)
    with pytest.raises(ValueError):
        _ = apply_window(slice_2d, center=0.0, width=0.0)


def test_extract_display_metadata_has_core_fields():
    ct = _make_dummy_ct()
    display = extract_display_metadata(ct)

    assert display["source"] == "dummy"
    assert display["source_type"] == "test"
    assert display["series_uid"] == "1.2.3.4"
    assert display["patient_id"] == "TEST001"
    assert display["modality"] == "CT"
    assert display["manufacturer"] == "ChatGPTScanner"

    shape = display["shape"]
    assert shape["z"] == ct.shape[0]
    assert shape["y"] == ct.shape[1]
    assert shape["x"] == ct.shape[2]

    spacing = display["spacing_mm"]
    assert spacing["z"] == ct.spacing[0]
    assert spacing["y"] == ct.spacing[1]
    assert spacing["x"] == ct.spacing[2]
