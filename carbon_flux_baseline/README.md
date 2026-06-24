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

### Model Equations

The baseline model estimates GPP and RECO internally using simple process equations:

```text
GPP_model = alpha * SW_IN_F
RECO_model = R0 * exp(k * TA_F)
NEE_model = RECO_model - GPP_model
```

### Model Inputs

The model takes the following FLUXNET variables as inputs:

- **`TA_F`**: Air temperature (°C)
- **`SW_IN_F`**: Incoming shortwave radiation (W/m²)

### Model Parameters

**Note:** In this baseline project, parameters are kept constant. In the data assimilation workflow, these parameters will be assigned probability distributions rather than fixed values.

The baseline parameters are:

```text
alpha: float = 0.02      # GPP light-use efficiency coefficient
r0: float = 2.0          # RECO reference rate at 0°C
k: float = 0.05          # RECO temperature sensitivity
```

### Model Outputs

The model produces the following outputs:

- **`output["GPP_model"]`**: Gross Primary Productivity (µmol CO₂/m²/s)
- **`output["RECO_model"]`**: Ecosystem Respiration (µmol CO₂/m²/s)
- **`output["NEE_model"]`**: Net Ecosystem Exchange (µmol CO₂/m²/s)

NEE is calculated as the difference between respiration and photosynthesis:

```text
NEE_model = RECO_model - GPP_model
```

FLUXNET sign convention is important: negative NEE usually means ecosystem carbon uptake, while positive NEE means ecosystem carbon release.

### Data Selection

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

## Conclusion

The baseline model was evaluated using 7,332 daytime observations. For the main comparison against FLUXNET `NEE_VUT_REF`, the model produced an RMSE of 5.15, MAE of 3.99, bias of 3.01, and Pearson correlation of 0.62. This shows moderate agreement between the observed and modelled NEE. The positive bias means the model tended to predict NEE values that were too high, which may indicate that daytime carbon uptake was underestimated under the usual NEE sign convention.

## Metrics Table

| Comparison | Observed Column | Modelled Column | Type | n | RMSE | MAE | Bias | Pearson r | Note |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| NEE_model vs NEE_VUT_REF | NEE_VUT_REF | NEE_model | main | 7332 | 5.153 | 3.985 | 3.006 | 0.623 | Primary comparison against processed FLUXNET NEE. |
| GPP_model vs GPP_NT_VUT_REF | GPP_NT_VUT_REF | GPP_model | secondary | 7332 | 5.973 | 4.561 | -3.167 | 0.695 | FLUXNET GPP is a partitioned model-derived estimate. |
| RECO_model vs RECO_NT_VUT_REF | RECO_NT_VUT_REF | RECO_model | secondary | 7332 | 1.293 | 1.062 | -0.160 | 0.908 | FLUXNET RECO is a partitioned model-derived estimate. |

The secondary comparison against FLUXNET partitioned GPP showed a Pearson correlation of 0.69, suggesting that the model captured some of the temporal variation in GPP. However, the RMSE of 5.97, MAE of 4.56, and negative bias of -3.17 show that the model underestimated GPP relative to the FLUXNET partitioned estimate. Because FLUXNET GPP is itself model-derived, this comparison should be treated as a consistency check rather than direct validation.

The RECO comparison showed the strongest performance, with a Pearson correlation of 0.91, RMSE of 1.29, MAE of 1.06, and bias of -0.16. This suggests that the respiration component of the model matched the reference RECO pattern well and had little systematic error. Overall, the results suggest that the baseline model represents respiration better than photosynthesis, while the weaker NEE performance likely reflects difficulty in balancing GPP and RECO during daytime conditions.

## Summary in Simple Terms

RMSE and MAE tell you how large the errors are. Bias tells you whether the model is generally too high or too low. Pearson correlation tells you whether the model follows the observed pattern.

For these results, RECO performed best. GPP was moderately correlated but underestimated. NEE was only moderate because errors in GPP and RECO combine when calculating net exchange.
