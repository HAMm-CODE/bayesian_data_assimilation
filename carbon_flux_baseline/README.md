# Carbon Flux Baseline

This project is a beginner-friendly baseline for a Master's thesis experiment using FLUXNET2015/ONEFlux-style eddy covariance data from the FI-Hyy site.

The first workflow uses half-hourly data from:

```text
ICOS_FI-Hyy_FLUXNET_FLUXMET_HH_1997-2024_v1.3_r1.csv
```

Place this file in:

```text
carbon_flux_baseline/data/raw/
```

## Baseline Model

The main target variable is `NEE_VUT_REF`, the processed FLUXNET net ecosystem exchange estimate. Missing values are represented by `-9999` in FLUXNET2015-style files and are converted to `NaN` during cleaning.

The baseline model estimates GPP and RECO internally using simple process equations:

```text
GPP_model = alpha * SW_IN_F
RECO_model = R0 * exp(k * TA_F)
NEE_model = RECO_model - GPP_model
```

The default parameters are:

```text
alpha = 0.02
R0 = 2.0
k = 0.05
```

FLUXNET sign convention is important: negative NEE usually means ecosystem carbon uptake, while positive NEE means ecosystem carbon release. For that reason, the model calculates:

```text
NEE_model = RECO_model - GPP_model
```

The first test year is `2018`. Daytime data are selected using:

```text
SW_IN_F > 20
```

## FLUXNET GPP and RECO Columns

The workflow keeps optional FLUXNET partitioned variables if they exist:

```text
GPP_NT_VUT_REF
RECO_NT_VUT_REF
GPP_DT_VUT_REF
RECO_DT_VUT_REF
```

These variables are used only for optional secondary comparison plots and metrics. They are partitioned estimates produced by FLUXNET/ONEFlux processing, not direct measurements, so they are not used to fit the first baseline model.

## Project Structure

```text
carbon_flux_baseline/
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── data_cleaning.py
│   ├── process_model.py
│   ├── evaluation.py
│   └── main.py
├── results/
│   ├── figures/
│   ├── metrics/
│   └── outputs/
├── requirements.txt
└── README.md
```

## How to Run

From the terminal, move into the project folder:

```bash
cd carbon_flux_baseline
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the full workflow:

```bash
python src/main.py
```

The workflow saves:

```text
data/processed/FI_Hyy_2018_daytime_clean.csv
results/outputs/model_output_2018.csv
results/metrics/model_metrics_2018.csv
results/figures/nee_observed_vs_modelled_2018.png
```

If `GPP_NT_VUT_REF` and `RECO_NT_VUT_REF` exist, the workflow also saves optional secondary comparison plots in `results/figures/`.
