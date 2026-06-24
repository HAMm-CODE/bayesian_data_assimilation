"""Run the full FI-Hyy carbon flux baseline workflow."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from data_cleaning import clean_fluxnet_file
from evaluation import evaluate_model_output
from process_model import run_process_model


PROJECT_ROOT = Path(__file__).resolve().parents[1]
YEAR = 2012
RAW_FILE_NAME = "FLX_FI-Hyy_FLUXNET2015_FULLSET_HH_1996-2014_1-4.csv"

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / RAW_FILE_NAME
CLEANED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "FI_Hyy_2012_daytime_clean.csv"
MODEL_OUTPUT_PATH = PROJECT_ROOT / "results" / "outputs" / "model_output_2012.csv"
METRICS_OUTPUT_PATH = PROJECT_ROOT / "results" / "metrics" / "model_metrics_2012.csv"
FIGURES_DIR = PROJECT_ROOT / "results" / "figures"


def save_time_series_plot(model_output: pd.DataFrame, output_path: Path) -> None:
    """Plot observed and modelled NEE through time."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(14, 6))
    plt.plot(
        model_output["TIMESTAMP_START"],
        model_output["NEE_VUT_REF"],
        label="Observed NEE_VUT_REF",
        linewidth=1,
    )
    plt.plot(
        model_output["TIMESTAMP_START"],
        model_output["NEE_model"],
        label="Modelled NEE_model",
        linewidth=1,
    )
    plt.xlabel("Time")
    plt.ylabel("NEE")
    plt.title("FI-Hyy 2018 daytime NEE: observed vs modelled")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def save_scatter_plot(
    model_output: pd.DataFrame,
    x_column: str,
    y_column: str,
    output_path: Path,
    title: str,
) -> None:
    """Plot a modelled value against an optional FLUXNET partitioned estimate."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plot_data = model_output[[x_column, y_column]].dropna()

    plt.figure(figsize=(7, 7))
    plt.scatter(plot_data[x_column], plot_data[y_column], s=12, alpha=0.5)
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def save_optional_partitioned_plots(model_output: pd.DataFrame) -> None:
    """Create secondary comparison plots when FLUXNET partitioned columns exist."""
    if "GPP_NT_VUT_REF" in model_output.columns:
        save_scatter_plot(
            model_output,
            x_column="GPP_NT_VUT_REF",
            y_column="GPP_model",
            output_path=FIGURES_DIR / "gpp_model_vs_gpp_nt_vut_ref_2018.png",
            title="Secondary comparison: GPP_model vs GPP_NT_VUT_REF",
        )

    if "RECO_NT_VUT_REF" in model_output.columns:
        save_scatter_plot(
            model_output,
            x_column="RECO_NT_VUT_REF",
            y_column="RECO_model",
            output_path=FIGURES_DIR / "reco_model_vs_reco_nt_vut_ref_2018.png",
            title="Secondary comparison: RECO_model vs RECO_NT_VUT_REF",
        )


def run_workflow() -> None:
    """Run cleaning, modelling, evaluation, and plotting."""
    cleaned_data = clean_fluxnet_file(
        input_path=RAW_DATA_PATH,
        output_path=CLEANED_DATA_PATH,
        year=YEAR,
    )

    model_output = run_process_model(cleaned_data)
    MODEL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    model_output.to_csv(MODEL_OUTPUT_PATH, index=False)

    metrics = evaluate_model_output(model_output)
    METRICS_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(METRICS_OUTPUT_PATH, index=False)

    save_time_series_plot(
        model_output,
        output_path=FIGURES_DIR / "nee_observed_vs_modelled_2018.png",
    )
    save_optional_partitioned_plots(model_output)

    print("Workflow complete.")
    print(f"Cleaned data saved to: {CLEANED_DATA_PATH}")
    print(f"Model output saved to: {MODEL_OUTPUT_PATH}")
    print(f"Metrics saved to: {METRICS_OUTPUT_PATH}")
    print(f"Figures saved to: {FIGURES_DIR}")


if __name__ == "__main__":
    run_workflow()
