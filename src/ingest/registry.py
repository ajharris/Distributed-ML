"""
src/ingest/registry.py

Registry for dataset-specific metadata loaders.

This provides a unified entry point so callers can say:

    from src.ingest.registry import DatasetRegistry

    loader = DatasetRegistry.get("nlst")
    rows = loader("data/raw_metadata/nlst_metadata.csv")

By default we register:
- "nlst"
- "copdgene"
- "lidc"

You can extend this registry as new datasets are added.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, Iterable, Union

from .metadata_schema import CTMetadataRow

try:  # Support running inside the package or via absolute imports
    from src.ingest.nlst import load_nlst_metadata
    from src.ingest.copdgene import load_copdgene_metadata
    from src.ingest.lidc import load_lidc_metadata
except ImportError:  # pragma: no cover
    from .nlst import load_nlst_metadata
    from .copdgene import load_copdgene_metadata
    from .lidc import load_lidc_metadata

# Type alias: a loader takes a CSV path and returns an iterable of CTMetadataRow
DatasetLoader = Callable[[Union[str, Path]], Iterable[CTMetadataRow]]


class DatasetRegistry:
    """
    Simple registry for dataset metadata loaders.

    Internally this is just a mapping from dataset key (str) to a
    callable that loads CTMetadataRow objects from a CSV path.
    """

    _registry: Dict[str, DatasetLoader] = {
        "nlst": load_nlst_metadata,
        "copdgene": load_copdgene_metadata,
        "lidc": load_lidc_metadata,
    }

    @classmethod
    def register(cls, key: str, loader: DatasetLoader) -> None:
        """
        Register a new dataset loader under the given key.
        """
        key_norm = key.lower()
        cls._registry[key_norm] = loader

    @classmethod
    def get(cls, key: str) -> DatasetLoader:
        """
        Retrieve a dataset loader by key.

        Example keys:
        - "nlst"
        - "copdgene"
        - "lidc"

        Raises KeyError if the key is not registered.
        """
        key_norm = key.lower()
        try:
            return cls._registry[key_norm]
        except KeyError as exc:
            raise KeyError(
                f"Unknown dataset key {key!r}. "
                f"Known datasets: {sorted(cls._registry.keys())}"
            ) from exc

    @classmethod
    def available_datasets(cls) -> Dict[str, DatasetLoader]:
        """
        Return a shallow copy of the registry mapping.
        """
        return dict(cls._registry)
