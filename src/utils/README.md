# Utilities Module

This directory contains shared utilities used throughout the scalable CT processing pipeline.  
These modules provide standardized logging, unified data I/O helpers for medical imaging formats,  
and cluster management utilities for distributed computation with Dask.

## Contents

### `logger.py`
Centralized logging helper providing consistent log formatting, console/file handlers, and optional JSON logs.

### `io.py`
I/O convenience functions for [NIfTI](https://nifti.nimh.nih.gov/), [Zarr](https://zarr.readthedocs.io/en/stable/), and [HDF5](https://www.hdfgroup.org/solutions/hdf5/) formats.

### `dask_cluster.py`
Helpers for launching local [Dask](https://dask.org/) clusters and a placeholder for cloud clusters.