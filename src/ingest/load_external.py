from __future__ import annotations

import argparse
import io
from pathlib import Path
from typing import Union

import pandas as pd
import requests


def load_and_convert_to_parquet(
    input_path: str,
    output_dir: Union[str, Path] = "data/metadata",
) -> Path:
    """
    Load a CSV from a local path or a URL and save it as a parquet file.

    Parameters
    ----------
    input_path : str
        Local file path or URL pointing to a CSV file.
    output_dir : str or Path
        Directory where the parquet file will be saved.

    Returns
    -------
    Path
        Path to the created parquet file.
    """
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    # Detect if input is a URL
    is_url = input_path.startswith("http://") or input_path.startswith("https://")

    if is_url:
        print(f"Downloading dataset from URL: {input_path}")
        response = requests.get(input_path)
        response.raise_for_status()

        # Read CSV directly from memory
        df = pd.read_csv(io.StringIO(response.text))

        # Use the last part of the URL as filename
        filename = input_path.rstrip("/").split("/")[-1].split("?")[0]
        stem = Path(filename).stem or "external_dataset"
    else:
        print(f"Loading local dataset from: {input_path}")
        input_path_path = Path(input_path)
        df = pd.read_csv(input_path_path)
        stem = input_path_path.stem

    parquet_path = output_dir_path / f"{stem}.parquet"
    df.to_parquet(parquet_path, index=False)

    print(f"Parquet file created at: {parquet_path}")
    return parquet_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load a CSV from a local path or URL and save it as a Parquet file."
    )
    parser.add_argument(
        "input_path",
        help="Local file path or URL pointing to a CSV file.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/metadata",
        help="Directory where the Parquet file will be saved (default: data/metadata).",
    )

    args = parser.parse_args()
    load_and_convert_to_parquet(args.input_path, args.output_dir)


if __name__ == "__main__":
    main()
