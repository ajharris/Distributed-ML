# CT Normalization & Resampling (Overview)

Located at: `src/preprocess/normalize_resample.py`

Features:
- HU clamping
- Optional denoising
- Resampling to 1x1x1 mm
- Metadata updates
- Caching

APIs:
- normalize_and_resample
- normalize_and_resample_with_cache
- save_cached_volume / load_cached_volume
- histogram_sanity_check