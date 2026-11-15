# Spatiotemporal PM2.5 Forecasting in the Mediterranean Basin

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Academic Year: 2026-2027](https://img.shields.io/badge/Academic%20Year-2026--2027-green.svg)]()
[![Milestone: Part 1 Complete](https://img.shields.io/badge/Milestone-Part%201%20Complete-brightgreen.svg)]()

> **Master 1 Mini Project — Machine Learning for Environmental Time-Series Forecasting**  
> **Group Identifier:** B18  
> **Deterministic Random Seed:** `SEED = 42`  
> **Primary Evaluation Metric:** Root Mean Squared Error (RMSE, $\mu g/m^3$)

---

## 📌 Project Overview

This repository delivers **Part 1 (Data Exploration, Preprocessing, and Validation Protocol)** of the PM2.5 forecasting mini-project. The project aims to forecast next-day daily average surface fine particulate matter ($\text{PM}_{2.5}$) across monitoring stations in the Mediterranean Basin by combining:
1. **In-situ Ground Observations:** Surface $\text{PM}_{2.5}$ measurements from 94 monitoring stations.
2. **Satellite Remote Sensing:** Sentinel-5P TROPOMI tropospheric columns ($\text{NO}_2$, $\text{CO}$, $\text{O}_3$) and MODIS Aerosol Optical Depth (AOD).
3. **Reanalysis Surface Meteorology:** ERA5 temperature, surface barometric pressure, and horizontal wind components ($u, v$).

Our pipeline enforces **strict leakage-free preprocessing**, develops station-isolated past-only feature engineering, and establishes three cross-validation regimes (Temporal CV with 1-day embargo gap, Spatial CV grouped by station, and diagnostic Random CV) to prevent optimistic bias.

---

## 📂 Repository Directory Structure

The project strictly follows the required academic organization:

```text
pm25-forecasting-project/
│
├── .gitignore                   # Excludes heavy CSV data, checkpoints, and binaries
├── README.md                    # Project landing page, documentation, and reproduction instructions
├── requirements.txt             # Exact library dependencies and environment specifications
│
├── data/                        # Data directory (managed locally, ignored by git)
│   ├── raw/                     # Original Kaggle/GEE download (combined_gee_pm25.csv)
│   │   └── .gitkeep
│   ├── processed/               # Cleaned & feature-engineered datasets
│   │   ├── data_cleaned.csv     # 40,983 valid records after sentinel removal
│   │   ├── data_features.csv    # 40 engineered spatiotemporal features
│   │   └── .gitkeep
│   └── .gitkeep
│
├── notebooks/                   # Jupyter exploration and testing notebooks
│   ├── 01_eda.ipynb             # Exploratory Data Analysis, audit, and correlation
│   ├── 02_timeseries.ipynb      # ACF/PACF, ADF/KPSS stationarity, and seasonal dynamics
│   └── 03_test_models.ipynb     # Interactive model prototyping on cross-validation folds
│
├── src/                         # Core Python modular library
│   ├── __init__.py
│   ├── config.py                # Paths, constants, column metadata, SEED = 42
│   ├── preprocessing.py         # Audit, sentinel removal, leakage-free scalers & imputation
│   ├── features.py              # Past-only lags, rolling aggregates, cyclical doy encodings
│   ├── splits.py                # Temporal (gap=1d), Spatial (GroupKFold), and Random folds
│   ├── models.py                # Model registry (G1-G26 starting configurations)
│   ├── test_evaluation.py       # RMSE, MAE, R2, paired Wilcoxon tests, Holm correction
│   ├── explainability.py        # Validation permutation importance & ranking stability
│   └── ablation.py              # Factor ablation (features, preprocessing, validation schemes)
│
├── scripts/                     # Short execution scripts
│   ├── run_eda.py               # Runs complete audit, cleaning, time series, & produces figures/CSVs
│   ├── run_training.py          # Trains baseline models across validation folds
│   ├── run_evaluation.py        # Computes comparisons.csv with paired Wilcoxon tests
│   ├── run_ablation.py          # Executes feature/preprocessing ablation -> ablation.csv
│   └── run_explicability.py     # Computes feature_importance.csv & ranking_stability.csv
│
├── folds/                       # Serialized Cross-Validation partitions
│   ├── folds_temporal.json      # 5 temporal expanding folds (TimeSeriesSplit, 1-day gap)
│   ├── folds_spatial.json       # 5 spatial folds grouped by station ID (GroupKFold)
│   ├── folds_standard.json      # 5 random folds (shuffled K-Fold, Seed=42 - diagnostic)
│   └── .gitkeep
│
├── results/                     # Standardized evaluation tables (B18 and consolidated)
│   ├── Exploratory_Data.csv     # Variable-level numerical audit & outlier metrics
│   ├── Exploratory_temporal.csv # Station-level time series diagnostics & ACF/PACF
│   ├── results.csv              # Model performance metrics per fold and validation scheme
│   ├── hyperparameters.csv      # Model configurations and tuning parameters
│   ├── feature_importance.csv   # Permutation feature importance scores and rankings
│   ├── comparisons.csv          # Paired model comparisons and Wilcoxon p-values
│   ├── experiments.csv          # Execution metadata, software versions, and hardware specs
│   ├── ablation.csv             # Factor ablation performance variations (ΔRMSE)
│   ├── ranking_stability.csv    # Spearman rho and Jaccard stability indices
│   ├── B18/                     # Group-specific standardized CSV copies
│   ├── consolidated/            # Consolidated cohort evaluation results
│   └── .gitkeep
│
├── figures/                     # Publication-grade figures generated by scripts
│   ├── eda_histogrammes.png     # Distributions of PM2.5, AOD, temperature, gases, wind
│   ├── pm25_distribution.png    # Raw vs log1p-transformed target distributions
│   ├── correlation_matrix.png   # Spearman rank correlation matrix
│   ├── seasonal_pm25_boxplot.png# Monthly seasonal distribution boxplots
│   ├── temporal_trend_acf_pacf.png # Multi-year trajectory with ACF/PACF correlograms
│   ├── spatial_stations_map.png # Geographic station distribution and observation density
│   ├── ablation_barplot.png     # Feature ablation ΔRMSE barplot
│   └── .gitkeep
│
├── reports/                     # Final technical report
│   ├── technical_report.pdf     # 17-page scientific technical report (English)
│   └── .gitkeep
│
└── presentation/                # Oral defense presentation
    ├── slides.pdf               # 14-slide landscape presentation deck (15-min oral defense)
    └── .gitkeep
```

---

## 🚀 Reproduction Instructions

To reproduce all results, tables, figures, report, and slides from scratch:

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-username/pm25-forecasting-project.git
cd pm25-forecasting-project

# Install required Python packages
pip install -r requirements.txt
```

### 2. Run Exploratory Data Analysis & Preprocessing
Executes dataset auditing, removes invalid sentinels, constructs temporal features, generates JSON cross-validation folds, and outputs standardized CSVs and figures:
```bash
python scripts/run_eda.py
```

### 3. Run Baseline Model Benchmarking
Trains baseline models across cross-validation folds:
```bash
python scripts/run_training.py
python scripts/run_evaluation.py
```

### 4. Run Ablation & Explainability Pipelines
Generates ablation impact figures and ranking stability tables:
```bash
python scripts/run_ablation.py
python scripts/run_explicability.py
```

### 5. Compile Technical Report and Presentation Slides
Compiles the comprehensive 17-page Technical Report and 14-slide defense deck:
```bash
python scripts/generate_report_pdf.py
python scripts/generate_slides_pdf.py
```

---

## 🔬 Key Scientific Findings (Part 1 Summary)

| Empirical Finding | Metric / Evidence | Physical / Methodological Interpretation |
| :--- | :--- | :--- |
| **Dataset Cleaning** | 735 rows removed (1.76%) | $727$ rows with $\text{PM}_{2.5} \le 0$ (sensor baseline drift) and $8$ rows $\ge 500\ \mu g/m^3$ removed prior to splitting. |
| **Target Skewness** | Skewness = 17.83, Kurtosis = 651.67 | Severe right-skewed distribution (Mean = 9.46 vs Median = 7.85 $\mu g/m^3$). $4.8\%$ of days exceed WHO $25\ \mu g/m^3$ limit; $1.1\%$ exceed $50\ \mu g/m^3$. |
| **Stationarity** | ADF stat = -6.95 ($p = 9.87 \times 10^{-10}$) | Time series is mean-stationary; first-order differencing is unnecessary. |
| **Autocorrelation** | ACF lag-1 = 0.58, PACF lag-1 = 0.58 | Strong 24-hour autoregressive persistence; yesterday's air quality is the primary predictor for tomorrow. |
| **The Optimism Gap (RQ1)** | $\Delta\text{RMSE} = -2.30\ \mu g/m^3$ (-37.6%) | Random CV yields artificially low error ($3.82\ \mu g/m^3$) compared to Temporal CV ($6.12\ \mu g/m^3$) due to proximity leakage. |
| **Feature Ablation (RQ2)** | Lags: $\Delta = +2.49$, Meteo: $+1.00$, AOD: $+0.76$ | Temporal lags and surface meteorology dominate; satellite AOD and Sentinel gases provide essential physical constraints. |
| **Ranking Stability (RQ3)** | Spearman $\rho = 0.88 > 0.80$, Jaccard $= 80\% > 60\%$ | Feature importance hierarchies across temporal CV folds strongly satisfy the required stability thresholds. |

---

## 📑 Deliverables Summary

- **Technical Report:** [`reports/technical_report.pdf`](file:///c:/Users/imadb/OneDrive/Documents/pm25-forecasting-project%20(2)/pm25-forecasting-project/reports/technical_report.pdf) — Complete 17-page academic report in English covering all 15 required sections.
- **Presentation Slides:** [`presentation/slides.pdf`](file:///c:/Users/imadb/OneDrive/Documents/pm25-forecasting-project%20(2)/pm25-forecasting-project/presentation/slides.pdf) — 14-slide presentation deck designed for a 15-minute oral defense of Part 1.
- **Standardized Results CSVs:** Located in [`results/`](file:///c:/Users/imadb/OneDrive/Documents/pm25-forecasting-project%20(2)/pm25-forecasting-project/results/), [`results/B18/`](file:///c:/Users/imadb/OneDrive/Documents/pm25-forecasting-project%20(2)/pm25-forecasting-project/results/B18/), and [`results/consolidated/`](file:///c:/Users/imadb/OneDrive/Documents/pm25-forecasting-project%20(2)/pm25-forecasting-project/results/consolidated/).
- **Folds Partitions:** Located in [`folds/`](file:///c:/Users/imadb/OneDrive/Documents/pm25-forecasting-project%20(2)/pm25-forecasting-project/folds/).
- **Figures:** High-resolution figures in [`figures/`](file:///c:/Users/imadb/OneDrive/Documents/pm25-forecasting-project%20(2)/pm25-forecasting-project/figures/).

---

## 👥 Project Authors & Team Members

- **Imad Ben Chernine** — Group 1
- **Mohamed Abderraouf AOUF** — Group 1
- **Youcef DADDI ADDOUNE** — Group 2
- **Anes ZIDANE** — Group 2

*Master 1 Artificial Intelligence / Data Science — Mini Project (Academic Year 2026–2027)*

