# src/utils/dask_cluster.py
from __future__ import annotations  # optional but makes 3.10+ syntax safe later

from typing import Any, Dict, Optional

from dask.distributed import Client, LocalCluster


def start_local_cluster(
    n_workers: int = 4,
    threads_per_worker: int = 1,
) -> Client:
    """Start a local Dask cluster for CPU-bound CT processing."""
    cluster = LocalCluster(
        n_workers=n_workers,
        threads_per_worker=threads_per_worker,
        memory_limit="4GB",
    )
    client = Client(cluster)
    return client


def start_cloud_cluster(config: Optional[Dict[str, Any]] = None):
    """Future: Start a cloud-backed cluster (Coiled / K8s / CloudProvider)."""
    # This is intentionally unimplemented for now; config placeholder
    raise NotImplementedError("Cloud cluster support coming in phase 2.")
