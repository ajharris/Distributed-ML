# src/utils/io.py
from pathlib import Path
import nibabel as nib
import zarr
import h5py
import numpy as np


def load_nifti(path: str) -> np.ndarray:
    img = nib.load(path)
    return img.get_fdata()


def save_nifti(data: np.ndarray, path: str, affine=None):
    affine = affine if affine is not None else np.eye(4)
    img = nib.Nifti1Image(data, affine)
    nib.save(img, path)


def save_zarr(data: np.ndarray, path: str):
    z = zarr.open(path, mode="w")
    z[:] = data


def load_zarr(path: str) -> np.ndarray:
    return zarr.open(path, mode="r")[:]


def save_hdf5(data: np.ndarray, path: str, dataset_name="volume"):
    with h5py.File(path, "w") as f:
        f.create_dataset(dataset_name, data=data)


def load_hdf5(path: str, dataset_name="volume") -> np.ndarray:
    with h5py.File(path, "r") as f:
        return f[dataset_name][:]
