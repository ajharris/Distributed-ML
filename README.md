# Distributed-ML: CT Preprocessing Pipeline with Dask

This repository implements a distributed, dataset-agnostic CT preprocessing pipeline designed for large clinical imaging datasets such as NLST, COPDGene, LIDC-IDRI, and research benchmarking datasets.

The pipeline supports:

- **CT loading** (DICOM/NIfTI/Zarr)
- **Classical lung segmentation**
- **Normalization and 3D resampling**
- **On-disk caching for full dataset sweeps**
- **Distributed, out-of-core preprocessing using Dask**
- **Dataset-agnostic metadata schema**
- **Extensive unit tests**
- **Config-driven execution via YAML**
- **Benchmarking mode for evaluating parallel scaling**

---

## 🚀 Running the Distributed Preprocessing Pipeline

Entry point:

```bash
python -m src.preprocess.run --config <your_config.yml>
```

Example:

```bash
python -m src.preprocess.run --config config/preprocess_task06_benchmark.yml
```

---

## 🔧 Benchmarking (10–20 scans)

A working benchmark is provided under:

```
config/preprocess_task06_benchmark.yml
```

This runs preprocessing on **Task06 Lung (10 CT volumes)** and demonstrates:

- Distributed parallel execution
- Out-of-core caching
- Full segmentation + normalization pipeline
- Successful end-to-end completion

To run the benchmark:

```bash
rm -rf data/cache/preprocess/task06_demo
time python -m src.preprocess.run --config config/preprocess_task06_benchmark.yml
```

---

## 📂 Project Structure

```
src/
  ingest/                  # dataset loaders, registry
  preprocess/              # segmentation, normalization, distributed run
  visualization/           # CT loading and metadata viewer
  utils/                   # logging + Dask cluster manager

docs/
  methodology/             # technical documentation

config/
  *.yml                    # preprocessing configs

data/
  metadata/
  raw/
  raw_test/                # Task06_Lung benchmark volumes
  cache/                   # output cache
```

---

## 🧪 Tests

Run all unit tests with:

```bash
pytest -q
```

Tests cover:

- metadata ingestion  
- CT loading  
- segmentation  
- normalization + caching  
- Dask graph creation  
- preprocessing orchestration  

---

## 📘 Documentation

Technical documentation lives in:

```
docs/methodology/
```

Contains metadata schema, pipeline overview, segmentation, normalization, and benchmarking docs.

