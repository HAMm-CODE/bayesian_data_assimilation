"""Simple process-based carbon flux model for a first baseline experiment."""

import numpy as np
import pandas as pd


OPTIONAL_PARTITIONED_COLUMNS = [
    "GPP_NT_VUT_REF",
    "RECO_NT_VUT_REF",
    "GPP_DT_VUT_REF",
    "RECO_DT_VUT_REF",
]


def run_process_model(
    data: pd.DataFrame,
    alpha: float = 0.02,
    r0: float = 2.0,
    k: float = 0.05,
) -> pd.DataFrame:
    """Estimate GPP, RECO, and NEE using simple baseline equations."""
    output = data.copy()

    # Gross primary production increases linearly with incoming radiation.
    output["GPP_model"] = alpha * output["SW_IN_F"]

    # Ecosystem respiration increases exponentially with air temperature.
    output["RECO_model"] = r0 * np.exp(k * output["TA_F"])

    # FLUXNET convention: negative NEE means uptake, positive NEE means release.
    output["NEE_model"] = output["RECO_model"] - output["GPP_model"]

    output_columns = [
        "TIMESTAMP_START",
        "TIMESTAMP_END",
        "NEE_VUT_REF",
        "GPP_model",
        "RECO_model",
        "NEE_model",
    ]

    available_partitioned_columns = [
        column for column in OPTIONAL_PARTITIONED_COLUMNS if column in output.columns
    ]

    return output[output_columns + available_partitioned_columns].copy()
