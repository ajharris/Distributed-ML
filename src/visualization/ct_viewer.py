# src/visualization/ct_viewer.py

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Tuple, Union

import numpy as np

# Optional dependencies: we guard imports so the rest of the module still works
try:  # NIfTI
    import nibabel as nib  # type: ignore
except ImportError:  # pragma: no cover - exercised only if nibabel missing at runtime
    nib = None  # type: ignore

try:  # DICOM
    import pydicom  # type: ignore
except ImportError:  # pragma: no cover
    pydicom = None  # type: ignore

try:  # Zarr
    import zarr as zarr_lib  # type: ignore
except ImportError:  # pragma: no cover
    zarr_lib = None  # type: ignore


Plane = Literal["axial", "coronal", "sagittal"]


@dataclass
class CTVolume:
    """
    In-memory representation of a 3D CT volume and associated metadata.

    Attributes
    ----------
    volume:
        3D numpy array with shape (z, y, x). Values are typically Hounsfield units.
    spacing:
        Tuple of (z_spacing, y_spacing, x_spacing) in mm.
    metadata:
        Arbitrary dictionary of metadata fields. Should be compatible with the
        canonical metadata schema where possible.
    source:
        Path to the original on-disk source (file or directory).
    """

    volume: np.ndarray
    spacing: Tuple[float, float, float]
    metadata: Dict[str, Any]
    source: Path

    @property
    def shape(self) -> Tuple[int, int, int]:
        return tuple(self.volume.shape)  # type: ignore[return-value]

    def summary(self) -> Dict[str, Any]:
        """
        Lightweight summary dictionary suitable for printing/logging.
        The volume itself is not returned to avoid huge dumps.
        """
        d = asdict(self)
        d["volume"] = {
            "shape": self.volume.shape,
            "dtype": str(self.volume.dtype),
            "min": float(np.nanmin(self.volume)),
            "max": float(np.nanmax(self.volume)),
        }
        d["source"] = str(self.source)
        return d


def load_ct_series(path: Union[str, Path]) -> CTVolume:
    """
    Load a CT series from a NIfTI file, Zarr store, or DICOM directory.

    Parameters
    ----------
    path:
        Path to a single file (.nii/.nii.gz), a Zarr store (.zarr), or a directory
        containing DICOM slices.

    Returns
    -------
    CTVolume
        Loaded CT volume, spacing, and basic metadata.

    Raises
    ------
    FileNotFoundError
        If the path does not exist.
    ValueError
        If the path type is unsupported.
    ImportError
        If a required optional dependency (nibabel, pydicom, zarr) is missing.
    """
    path = Path(path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"CT source not found: {path}")

    if path.is_file():
        suffix = "".join(path.suffixes).lower()
        if suffix in {".nii", ".nii.gz"}:
            return _load_nifti(path)
        else:
            raise ValueError(
                f"Unsupported file type for CT series: {suffix} (path={path})"
            )

    # Directory-like
    if path.is_dir():
        # Zarr stores are usually directories ending with .zarr and containing .zarray
        if path.suffix == ".zarr" or (path / ".zarray").exists():
            return _load_zarr(path)
        return _load_dicom_dir(path)

    raise ValueError(f"Unsupported CT source: {path}")


def _load_nifti(path: Path) -> CTVolume:
    if nib is None:
        raise ImportError(
            "nibabel is required to load NIfTI files. "
            "Install with `pip install nibabel` or add to environment.yml."
        )

    img = nib.load(str(path))
    data = img.get_fdata().astype(np.float32)

    if data.ndim != 3:
        raise ValueError(f"Expected 3D NIfTI, got shape {data.shape} for {path}")

    # NIfTI zooms are typically (x, y, z) or (x, y, z, t). We standardize as (z, y, x).
    zooms = img.header.get_zooms()[:3]
    x_spacing, y_spacing, z_spacing = zooms
    spacing = (float(z_spacing), float(y_spacing), float(x_spacing))

    metadata: Dict[str, Any] = {
        "source_type": "nifti",
        "nifti_affine": img.affine.tolist(),
        "zooms": tuple(float(z) for z in zooms),
    }

    # Reorder axes if needed so volume is (z, y, x).
    # Many NIfTI images are (x, y, z). We transpose to (z, y, x).
    volume = np.transpose(data, (2, 1, 0))

    return CTVolume(volume=volume, spacing=spacing, metadata=metadata, source=path)


def _load_dicom_dir(path: Path) -> CTVolume:
    if pydicom is None:
        raise ImportError(
            "pydicom is required to load DICOM directories. "
            "Install with `pip install pydicom` or add to environment.yml."
        )

    dcm_files = sorted(
        [p for p in path.iterdir() if p.is_file()],
        key=lambda p: p.name,
    )
    if not dcm_files:
        raise ValueError(f"No DICOM files found in directory: {path}")

    datasets = []
    for f in dcm_files:
        try:
            ds = pydicom.dcmread(str(f), stop_before_pixels=False)
            datasets.append(ds)
        except Exception:
            # Skip files that are not valid DICOM
            continue

    if not datasets:
        raise ValueError(f"No readable DICOM datasets in directory: {path}")

    # Try to filter to CT images only
    ct_datasets = [ds for ds in datasets if getattr(ds, "Modality", None) == "CT"]
    if ct_datasets:
        datasets = ct_datasets

    # Sort slices by ImagePositionPatient (z coordinate) or InstanceNumber
    def _slice_sort_key(ds: Any) -> Tuple[float, int]:
        ipp = getattr(ds, "ImagePositionPatient", None)
        z = float(ipp[2]) if ipp is not None and len(ipp) >= 3 else 0.0
        instance = int(getattr(ds, "InstanceNumber", 0))
        return (z, instance)

    datasets.sort(key=_slice_sort_key)

    # Stack pixel arrays into a volume (z, y, x)
    first = datasets[0]
    rows = int(first.Rows)
    cols = int(first.Columns)
    num_slices = len(datasets)

    volume = np.empty((num_slices, rows, cols), dtype=np.float32)
    for i, ds in enumerate(datasets):
        arr = ds.pixel_array.astype(np.float32)
        if arr.shape != (rows, cols):
            raise ValueError(
                f"Inconsistent DICOM slice shape: expected {(rows, cols)}, got {arr.shape}"
            )
        volume[i] = arr

    # Spacing
    pixel_spacing = getattr(first, "PixelSpacing", [1.0, 1.0])
    slice_thickness = float(getattr(first, "SliceThickness", 1.0))
    y_spacing, x_spacing = map(float, pixel_spacing)
    spacing = (slice_thickness, y_spacing, x_spacing)

    metadata: Dict[str, Any] = {
        "source_type": "dicom",
        "SeriesInstanceUID": getattr(first, "SeriesInstanceUID", None),
        "StudyInstanceUID": getattr(first, "StudyInstanceUID", None),
        "PatientID": getattr(first, "PatientID", None),
        "Modality": getattr(first, "Modality", None),
        "Manufacturer": getattr(first, "Manufacturer", None),
        "SliceThickness": slice_thickness,
        "PixelSpacing": (y_spacing, x_spacing),
        "NumSlices": num_slices,
        "Rows": rows,
        "Cols": cols,
    }

    return CTVolume(volume=volume, spacing=spacing, metadata=metadata, source=path)


def _load_zarr(path: Path) -> CTVolume:
    if zarr_lib is None:
        raise ImportError(
            "zarr is required to load Zarr stores. "
            "Install with `pip install zarr` or add to environment.yml."
        )

    store = zarr_lib.open(str(path), mode="r")
    data = np.asarray(store, dtype=np.float32)

    if data.ndim != 3:
        raise ValueError(f"Expected 3D Zarr array, got shape {data.shape} for {path}")

    # Assume store is already (z, y, x)
    volume = data

    # Attempt to read spacing from attributes; fall back to (1,1,1)
    attrs = getattr(store, "attrs", {})
    spacing_attr = attrs.get("spacing") or attrs.get("voxel_spacing")
    if spacing_attr is not None and len(spacing_attr) == 3:
        spacing = tuple(float(s) for s in spacing_attr)  # type: ignore[assignment]
    else:
        spacing = (1.0, 1.0, 1.0)

    metadata: Dict[str, Any] = {
        "source_type": "zarr",
        "zarr_path": str(path),
        "attrs": dict(attrs),
    }

    return CTVolume(volume=volume, spacing=spacing, metadata=metadata, source=path)


def get_slice(
    ct: CTVolume,
    index: int,
    plane: Plane = "axial",
) -> np.ndarray:
    """
    Extract a single 2D slice from a CTVolume in the given plane.

    Parameters
    ----------
    ct:
        CTVolume instance.
    index:
        Slice index along the chosen plane.
    plane:
        "axial" (z), "coronal" (y), or "sagittal" (x).

    Returns
    -------
    np.ndarray
        2D slice as a float32 array.
    """
    z, y, x = ct.shape

    if plane == "axial":
        if not 0 <= index < z:
            raise IndexError(f"Axial index {index} out of range [0, {z})")
        slice_2d = ct.volume[index, :, :]
    elif plane == "coronal":
        if not 0 <= index < y:
            raise IndexError(f"Coronal index {index} out of range [0, {y})")
        slice_2d = ct.volume[:, index, :]
    elif plane == "sagittal":
        if not 0 <= index < x:
            raise IndexError(f"Sagittal index {index} out of range [0, {x})")
        slice_2d = ct.volume[:, :, index]
    else:
        raise ValueError(f"Unknown plane: {plane}")

    return slice_2d.astype(np.float32)


def apply_window(
    slice_2d: np.ndarray,
    center: float,
    width: float,
    out_dtype: type = np.uint8,
) -> np.ndarray:
    """
    Apply a simple linear window/level to a 2D HU slice.

    Parameters
    ----------
    slice_2d:
        2D array of CT values (typically HU).
    center:
        Window center (level).
    width:
        Window width.
    out_dtype:
        Output dtype, usually uint8 for display.

    Returns
    -------
    np.ndarray
        Windowed image scaled to [0, 255] and cast to out_dtype.
    """
    if width <= 0:
        raise ValueError(f"Window width must be positive, got {width}")

    low = center - width / 2.0
    high = center + width / 2.0

    windowed = np.clip(slice_2d, low, high)
    # Normalize to [0, 1]
    windowed = (windowed - low) / (high - low)
    windowed = np.clip(windowed, 0.0, 1.0)

    # Scale to [0, 255] for typical 8-bit display
    scaled = (windowed * 255.0).round().astype(out_dtype)
    return scaled


def extract_display_metadata(
    ct: CTVolume,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Extract a compact set of metadata fields suitable for side-panel display
    in a viewer UI.

    Parameters
    ----------
    ct:
        CTVolume instance.
    extra:
        Optional additional fields to merge in.

    Returns
    -------
    Dict[str, Any]
        Dictionary with keys like series_uid, spacing, dims, etc.
    """
    z, y, x = ct.shape
    spacing = ct.spacing
    meta = ct.metadata

    # Try to map common schema fields; fall back if absent.
    display = {
        "source": str(ct.source),
        "source_type": meta.get("source_type"),
        "series_uid": meta.get("series_uid") or meta.get("SeriesInstanceUID"),
        "patient_id": meta.get("patient_id") or meta.get("PatientID"),
        "modality": meta.get("modality") or meta.get("Modality"),
        "manufacturer": meta.get("manufacturer") or meta.get("Manufacturer"),
        "shape": {"z": z, "y": y, "x": x},
        "spacing_mm": {"z": spacing[0], "y": spacing[1], "x": spacing[2]},
    }

    if extra:
        display.update(extra)

    return display
