import numpy as np
from src.utils import io


def test_nifti_roundtrip(tmp_path):
    vol = np.random.rand(8, 8, 8)
    fp = tmp_path / "test.nii.gz"
    io.save_nifti(vol, fp)
    out = io.load_nifti(fp)
    assert np.allclose(vol, out)


def test_zarr_roundtrip(tmp_path):
    vol = np.random.rand(4, 4)
    fp = tmp_path / "test.zarr"
    io.save_zarr(vol, fp)
    out = io.load_zarr(fp)
    assert np.allclose(vol, out)


def test_hdf5_roundtrip(tmp_path):
    vol = np.random.rand(5, 5)
    fp = tmp_path / "test.h5"
    io.save_hdf5(vol, fp)
    out = io.load_hdf5(fp)
    assert np.allclose(vol, out)
