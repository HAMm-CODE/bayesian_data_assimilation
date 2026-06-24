# Carbon Flux Baseline

This project is a beginner-friendly baseline for a Master's thesis experiment using FLUXNET2015/ONEFlux-style eddy covariance data from the FI-Hyy site.

The first workflow uses half-hourly data from:

```text
FLX_FI-Hyy_FLUXNET2015_FULLSET_HH_1996-2014_1-4.csv
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

The first test year is `2012`. Daytime data are selected using:

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
data/processed/FI_Hyy_2012_daytime_clean.csv
results/outputs/model_output_2012.csv
results/metrics/model_metrics_2012.csv
results/figures/nee_observed_vs_modelled_2012.png
```

If `GPP_NT_VUT_REF` and `RECO_NT_VUT_REF` exist, the workflow also saves optional secondary comparison plots in `results/figures/`.

## Note on Bayesian Data Assimilation

Note: This project does not implement any Bayesian data assimilation techniques. It uses a simple baseline process model and associated equations to explore the larger workflow and build familiarity. In this project I ingest data -> clean it -> evaluate it using metrics -> run the `process_model` with the observed NEE sensor data. I plan to continue these investigations in future projects and will add a short conclusion to this README later.
