"""Data loading and cleaning helpers for FLUXNET2015-style FI-Hyy data."""

from pathlib import Path

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = [
    "TIMESTAMP_START",
    "TIMESTAMP_END",
    "NEE_VUT_REF",
    "TA_F",
    "SW_IN_F",
]

OPTIONAL_COLUMNS = [
    "VPD_F",
    "GPP_NT_VUT_REF",
    "RECO_NT_VUT_REF",
    "GPP_DT_VUT_REF",
    "RECO_DT_VUT_REF",
]

MISSING_VALUE = -9999


def load_fluxnet_data(csv_path: Path) -> pd.DataFrame:
    """Load a FLUXNET-style CSV file and convert -9999 missing values to NaN."""
    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Could not find the raw data file at {csv_path}. "
            "Place the FI-Hyy CSV file in carbon_flux_baseline/data/raw/ "
            "or pass a different input path to the workflow."
        )

    data = pd.read_csv(csv_path)
    data = data.replace(MISSING_VALUE, np.nan)
    return data


def convert_fluxnet_timestamps(data: pd.DataFrame) -> pd.DataFrame:
    """Convert FLUXNET YYYYMMDDHHMM timestamps into pandas datetime values."""
    data = data.copy()

    for column in ["TIMESTAMP_START", "TIMESTAMP_END"]:
        data[column] = pd.to_datetime(
            data[column].astype(str),
            format="%Y%m%d%H%M",
            errors="coerce",
        )

    return data


def select_available_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Keep required columns plus any optional comparison columns that exist."""
    missing_required = [column for column in REQUIRED_COLUMNS if column not in data.columns]

    if missing_required:
        raise ValueError(
            "The raw data file is missing required columns: "
            + ", ".join(missing_required)
        )

    available_optional = [column for column in OPTIONAL_COLUMNS if column in data.columns]
    return data[REQUIRED_COLUMNS + available_optional].copy()


def clean_fluxnet_data(
    data: pd.DataFrame,
    year: int = 2012,
    daytime_sw_threshold: float = 20.0,
) -> pd.DataFrame:
    """Clean FI-Hyy data for the first daytime baseline modelling experiment."""
    data = select_available_columns(data)
    data = convert_fluxnet_timestamps(data)

    # Work with one test year first so the baseline workflow stays small.
    data = data[data["TIMESTAMP_START"].dt.year == year]

    # Daytime records are selected with incoming shortwave radiation.
    data = data[data["SW_IN_F"] > daytime_sw_threshold]

    # The baseline model needs observed NEE, air temperature, and radiation.
    modelling_columns = ["NEE_VUT_REF", "TA_F", "SW_IN_F"]
    data = data.dropna(subset=modelling_columns)

    return data.reset_index(drop=True)


def save_cleaned_data(data: pd.DataFrame, output_path: Path) -> None:
    """Save cleaned data to the processed data folder."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False)


def clean_fluxnet_file(
    input_path: Path,
    output_path: Path,
    year: int = 2012,
    daytime_sw_threshold: float = 20.0,
) -> pd.DataFrame:
    """Load, clean, save, and return the FI-Hyy daytime dataset."""
    raw_data = load_fluxnet_data(input_path)
    cleaned_data = clean_fluxnet_data(
        raw_data,
        year=year,
        daytime_sw_threshold=daytime_sw_threshold,
    )
    save_cleaned_data(cleaned_data, output_path)
    return cleaned_data
