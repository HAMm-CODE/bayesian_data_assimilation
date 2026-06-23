"""Evaluation metrics for carbon flux baseline model outputs."""

import numpy as np
import pandas as pd
from scipy.stats import pearsonr


def _paired_values(data: pd.DataFrame, observed_column: str, modelled_column: str) -> pd.DataFrame:
    """Return paired observed/modelled values after dropping missing values."""
    paired = data[[observed_column, modelled_column]].copy()

    # Metric calculations need numeric arrays, especially for Pearson correlation.
    paired[observed_column] = pd.to_numeric(paired[observed_column], errors="coerce")
    paired[modelled_column] = pd.to_numeric(paired[modelled_column], errors="coerce")

    return paired.dropna()


def calculate_rmse(observed: pd.Series, modelled: pd.Series) -> float:
    """Calculate root mean squared error."""
    return float(np.sqrt(np.mean((modelled - observed) ** 2)))


def calculate_mae(observed: pd.Series, modelled: pd.Series) -> float:
    """Calculate mean absolute error."""
    return float(np.mean(np.abs(modelled - observed)))


def calculate_bias(observed: pd.Series, modelled: pd.Series) -> float:
    """Calculate mean model bias as modelled minus observed."""
    return float(np.mean(modelled - observed))


def calculate_pearson_correlation(observed: pd.Series, modelled: pd.Series) -> float:
    """Calculate Pearson correlation, returning NaN if too few values exist."""
    if len(observed) < 2:
        return float("nan")

    return float(pearsonr(observed, modelled).statistic)


def calculate_metrics(
    data: pd.DataFrame,
    observed_column: str,
    modelled_column: str,
) -> dict[str, float]:
    """Calculate all baseline metrics for one observed/modelled comparison."""
    paired = _paired_values(data, observed_column, modelled_column)

    if paired.empty:
        return {
            "n": 0,
            "rmse": float("nan"),
            "mae": float("nan"),
            "bias": float("nan"),
            "pearson_r": float("nan"),
        }

    observed = paired[observed_column]
    modelled = paired[modelled_column]

    return {
        "n": int(len(paired)),
        "rmse": calculate_rmse(observed, modelled),
        "mae": calculate_mae(observed, modelled),
        "bias": calculate_bias(observed, modelled),
        "pearson_r": calculate_pearson_correlation(observed, modelled),
    }


def evaluate_model_output(data: pd.DataFrame) -> pd.DataFrame:
    """Evaluate NEE and optional secondary GPP/RECO comparisons."""
    comparisons = [
        {
            "comparison": "NEE_model vs NEE_VUT_REF",
            "observed_column": "NEE_VUT_REF",
            "modelled_column": "NEE_model",
            "comparison_type": "main",
            "note": "Primary comparison against processed FLUXNET NEE.",
        }
    ]

    if "GPP_NT_VUT_REF" in data.columns:
        comparisons.append(
            {
                "comparison": "GPP_model vs GPP_NT_VUT_REF",
                "observed_column": "GPP_NT_VUT_REF",
                "modelled_column": "GPP_model",
                "comparison_type": "secondary",
                "note": "FLUXNET GPP is a partitioned model-derived estimate.",
            }
        )

    if "RECO_NT_VUT_REF" in data.columns:
        comparisons.append(
            {
                "comparison": "RECO_model vs RECO_NT_VUT_REF",
                "observed_column": "RECO_NT_VUT_REF",
                "modelled_column": "RECO_model",
                "comparison_type": "secondary",
                "note": "FLUXNET RECO is a partitioned model-derived estimate.",
            }
        )

    rows = []
    for comparison in comparisons:
        metrics = calculate_metrics(
            data,
            observed_column=comparison["observed_column"],
            modelled_column=comparison["modelled_column"],
        )
        rows.append({**comparison, **metrics})

    return pd.DataFrame(rows)
