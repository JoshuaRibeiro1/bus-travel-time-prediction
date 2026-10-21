# NYC Bus Travel Time Prediction — Separate vs. Pooled Models

A reproducible **DS 340W research baseline** comparing whether training one model across three Manhattan MTA bus routes (M101, M102, M103) predicts monthly weekday/hour average segment travel times better than training a separate model for each route.

**Research question:** Does pooling observations across M101, M102, and M103 improve prediction accuracy relative to route-specific models?

> **Scope:** This is a retrospective, aggregate travel-time prediction experiment—not live bus arrival tracking, individual-bus delay forecasting, or evidence of causal delay propagation.

## Reported findings

The original notebook reports the following evaluation on the supplied filtered CSV, using June–August 2026 as the three-month holdout (25,534 eligible rows):

| Approach | Holdout MAE (minutes) |
| --- | ---: |
| Historical mean | 0.7114 |
| Historical lag | 0.8395 |
| Separate gradient boosting | **0.6860** |
| Pooled gradient boosting | 0.6903 |

The pooled model was about **0.62% worse** than separate boosting in this run. The difference was **not** tested for statistical significance. Separate boosting improved on the historical mean baseline by about 3.57%. These are findings documented in the supplied notebook, not independently rerun results in this repository.

## Project structure

```text
bus-travel-time-prediction/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── README.md                   # Data schema; dataset not included
├── src/
│   ├── data_processing.py          # Validation, deduplication and auditing
│   ├── feature_engineering.py      # Historical lags and temporal splits
│   ├── training.py                 # Model tuning and refitting
│   ├── evaluation.py               # Predictions, metrics and model export
│   ├── visualization.py            # Charts
│   └── reporting.py                # Metadata and output ZIP
├── main.py                         # Runnable pipeline
└── notebooks/
    └── bus_travel_time_baseline.ipynb
```

## Run the modular pipeline

The code in `src/` reproduces the original notebook stages without requiring Google Colab.
Supply the original source CSV locally (not committed to GitHub):

```bash
python -m pip install -r requirements.txt
python main.py --csv data/mta_segment_speeds.csv
```

The pipeline writes audit tables, predictions, fitted models, reports and figures into `bus_baseline_outputs/` and creates a results ZIP. The data file is not included; reported metrics have not been independently rerun against the dataset.

## Run locally

Python 3.11 is a suitable starting point. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate             # macOS / Linux
python -m pip install -r requirements.txt
export BUS_CSV="data/mta_segment_speeds.csv"
jupyter notebook notebooks/bus_travel_time_baseline.ipynb
```

On Windows PowerShell, use `.venv\Scripts\Activate.ps1` instead of `source ...`, and `$env:BUS_CSV = "data/mta_segment_speeds.csv"` instead of `export ...`.

Replace the example CSV name with the path to your actual dataset. Run all notebook cells in order. **The CSV must be supplied by you**; it is not part of this package. If `BUS_CSV` is unset, the notebook attempts to open a Google Colab file-upload dialog, which does not work in ordinary local Jupyter.

## Run in Google Colab

1. Open `notebooks/bus_travel_time_baseline.ipynb` in Colab (after uploading it to GitHub, Colab can open the notebook from GitHub).
2. Choose **Runtime → Run all**.
3. Upload your filtered segment-speed CSV when prompted.
4. Find `bus_baseline_results.zip` in the Files pane. Optionally set `DOWNLOAD_RESULTS = True` in the final cell.

A CPU runtime is sufficient according to the original notebook.

## Methodology

1. **Data quality:** Select three bus routes; remove exact duplicates and invalid rows. Quarantine repeated endpoint/time keys with conflicting values rather than averaging them. The original run retained **166,776** rows after quarantining **23,157** ambiguous rows from **189,933** source records.
2. **Historical features:** Build month-offset travel-time lags, expanding historical travel-time means, prior distance, history counts, and categorical segment/time descriptors. Same-period target, speed, distance, and trip count are not model inputs.
3. **Temporal evaluation:** Assume observations become usable only after **two calendar months** (`LAG_MONTHS = 2`). Tune two modest gradient-boosted-tree configurations on earlier validation months, refit before the test cutoff, then evaluate later months.
4. **Compare models:** Historical mean, historical lag, one `HistGradientBoostingRegressor` for each route, and a single pooled `HistGradientBoostingRegressor` (scikit-learn, **not XGBoost**).
5. **Export:** Audits, cleaned and modeling datasets, coverage summaries, validation scores, held-out predictions, aggregate/route/month metrics, plots, fitted models, and run metadata. Outputs go to `bus_baseline_outputs/` plus `bus_baseline_results.zip`.

## Important limitations

- Source publication dates were not provided. The two-month data-availability rule is a **retrospective assumption**, not verified production-time availability.
- Historical features in later test months may use earlier test-month observed outcomes once they become old enough under the assumed lag; model parameters remain frozen.
- Quarantining ambiguous groups is conservative but may exclude valid, undocumented variants.
- The three-month holdout supports descriptive comparisons only; there is no significance test or proof the result generalizes to other seasons or routes.
- Candidate shared segments are identified using stop endpoints and direction; physical road-path identity is not confirmed.
- Loading saved `joblib` models is only safe when they are from a trusted source.

## Next experiments

Investigate the source documentation for quarantined groups, verify data publication lag, compare route-level performance, and test whether pooling is more beneficial when target-route training data are scarce.

## Attribution / AI assistance

The original notebook includes a suggested AI-use disclosure. Adapt and disclose any assistance in accordance with your course requirements. Research conclusions and reported numbers should be checked against your own run before submission.
