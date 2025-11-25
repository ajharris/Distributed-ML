from src.utils.dask_cluster import start_local_cluster


def test_start_local_cluster():
    client = start_local_cluster(n_workers=1, threads_per_worker=1)
    info = client.scheduler_info()
    assert "workers" in info
    client.shutdown()
