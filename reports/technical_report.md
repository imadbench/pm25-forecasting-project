# Spatiotemporal PM2.5 Forecasting in the Mediterranean Basin: Data Audit, Leakage-Free Preprocessing, and Validation Protocol

**Academic Year:** 2026–2027  
**Milestone:** Part 1 — Data Exploration & Preprocessing (Due: 14 November 2026)  
**Group Identifier:** B18 (Combined Group 1 & Group 2)  
**Target Variable:** Daily Surface $\text{PM}_{2.5}$ Concentration ($\mu g/m^3$)  
**Dataset:** Air Quality – Mediterranean Basin (2016–2026) [41,718 Initial Records]  
**Deterministic Seed:** Fixed `SEED = 42`  

---

### 👥 Authors & Team Members

| Author / Student Name | Group | Degree & Affiliation |
| :--- | :---: | :--- |
| **Imad Ben Chernine** | **Group 1** | Master 1 Artificial Intelligence / Data Science |
| **Mohamed Abderraouf AOUF** | **Group 1** | Master 1 Artificial Intelligence / Data Science |
| **Youcef DADDI ADDOUNE** | **Group 2** | Master 1 Artificial Intelligence / Data Science |
| **Anes ZIDANE** | **Group 2** | Master 1 Artificial Intelligence / Data Science |

---

## Executive Summary

This technical report documents Milestone 1 of the $\text{PM}_{2.5}$ forecasting project. We conduct a thorough audit of multi-source spatiotemporal observations spanning 2016–2026 across 94 ground monitoring stations in the Mediterranean basin. A rigorous data-cleaning protocol removes 735 invalid sentinel records ($\text{PM}_{2.5} \le 0$ and $\ge 500\ \mu g/m^3$) to prevent distribution distortion. Time-series diagnostics establish strong 1-day temporal autocorrelation (ACF lag-1 = 0.58, PACF lag-1 = 0.58) and stationary properties (ADF test $p < 10^{-4}$). We construct a leakage-free feature engineering architecture (past-only lags, rolling aggregates, Sentinel-5P missingness indicators, and cyclical day-of-year embeddings). Crucially, we establish and serialize three cross-validation regimes: 5-fold expanding Temporal CV (with a 1-day embargo gap), 5-fold Spatial CV grouped by station ID, and a diagnostic Random CV. Baseline models (Ridge, Lasso, ElasticNet, Huber, Random Forest, SVR) reveal an empirical "optimism gap" of over $2.3\ \mu g/m^3$ when naive random CV is applied, confirming the vital importance of time- and location-aware evaluation protocols.

---

## 1. Context and Motivation

Ambient air pollution by fine particulate matter with an aerodynamic diameter less than 2.5 micrometers ($\text{PM}_{2.5}$) represents one of the foremost global environmental health risks. Due to their minute physical dimensions, $\text{PM}_{2.5}$ particulates penetrate deeply into pulmonary alveoli and enter systemic circulation, driving elevated risks of cardiovascular morbidity, chronic obstructive pulmonary disease, stroke, and lung cancer. In the Mediterranean Basin, air quality dynamics are uniquely intricate: local anthropogenic emissions (from heavy vehicular traffic, maritime shipping corridors, and industrial hubs) intermix with complex Mediterranean microclimates, land-sea breeze recirculations, high photochemical activity, and frequent desert dust transport events originating from North Africa.

While direct in-situ ground monitoring networks provide gold-standard continuous measurements, their spatial distribution is sparse, unevenly concentrated in urban coastal centers, and financially costly to expand into rural or semi-arid zones. Consequently, developing accurate, computationally reliable supervised machine learning and deep learning forecasting architectures offers a powerful operational solution. By integrating historical surface observations with satellite remote sensing (tropospheric column trace gases from Sentinel-5P TROPOMI and Aerosol Optical Depth from MODIS) alongside numerical weather reanalysis (ERA5 temperature, barometric pressure, and horizontal wind fields), forecasting systems can predict daily surface $\text{PM}_{2.5}$ concentrations ahead of time to support public health advisories and environmental policy.

However, deploying predictive algorithms on spatiotemporal environmental data introduces severe methodological pitfalls. Naive data-splitting techniques that ignore temporal autocorrelation or spatial clustering yield highly optimistic test scores that utterly fail to generalize to future periods or unmonitored geographic regions. Furthermore, machine learning pipelines must guarantee absolute leakage prevention across multi-day missingness gaps and avoid using concurrent target data for nowcasting. This project addresses these challenges systematically by evaluating models along three complementary axes: **predictive performance**, **spatiotemporal robustness**, and **explainability stability**.

---

## 2. Problem Statement & Research Questions

The overarching objective is to forecast next-day daily average surface $\text{PM}_{2.5}$ concentration ($\mu g/m^3$) at monitoring stations across the Mediterranean basin using multimodal remote sensing, numerical meteorology, and justified historical temporal dynamics.

To provide rigorous scientific evaluation, this study is structured around one primary research question and four secondary research questions (RQ1–RQ4):

- **Primary Research Question:** To what extent can multi-source satellite products and reanalysis meteorology reliably forecast next-day surface $\text{PM}_{2.5}$ concentrations in unseen locations and future temporal blocks without optimistic bias?
- **RQ1 (Validation Optimism Gap):** What is the empirical magnitude of the optimism gap between standard randomized K-Fold cross-validation, temporal expanding-window validation (TimeSeriesSplit with a 1-day embargo gap), and spatial validation (GroupKFold grouped by station)? Does random splitting artificially inflate model performance metrics?
- **RQ2 (Multimodal Predictor Synergy):** What are the distinct and joint contributions of physical satellite atmospheric products (AOD, $\text{NO}_2$, $\text{CO}$, $\text{O}_3$), surface meteorological variables, and historical temporal features? How severely does removing individual predictor families degrade predictive accuracy?
- **RQ3 (Explainability Stability):** Are feature importance hierarchies (evaluated via validation-fold permutation importance) stable across temporal folds and model families? Do top-ranked features satisfy practical stability thresholds ($\rho > 0.80$ and top-5 Jaccard overlap $> 60\%$)?
- **RQ4 (Target Transformation & Outlier Handling):** Does logarithmic target transformation ($\log(1+y)$) or explicit missingness indicator modeling for periodic satellite non-coverage mitigate prediction errors during high-concentration episodes ($> 25$ and $> 50\ \mu g/m^3$)?

---

## 3. Related Work in Spatiotemporal Air Pollution Modeling

The field of atmospheric particulate forecasting has evolved through three distinct methodological eras:

1. **Classical Statistical Time Series:** Classical methods originated with autoregressive integrated moving average (ARIMA) and seasonal SARIMA models developed by Box et al. (2015). These capture univariate persistence and seasonal cycles effectively but assume linear Gaussian dynamics and struggle to incorporate high-dimensional exogenous predictors. Hyndman & Athanasopoulos (2021) demonstrated that while vector autoregressive (VAR) and regression with SARIMAX errors improve capacity, they exhibit severe vulnerability to non-stationary structural breaks and missing measurements.
2. **Machine Learning Ensembles:** Breiman (2001) established Random Forests as robust non-linear estimators capable of handling feature interactions without strict distributional assumptions. Chen & Guestrin (2016) developed XGBoost, demonstrating that gradient-boosted decision trees optimize split finding through second-order Taylor approximations, achieving state-of-the-art results on tabular meteorological datasets. Ke et al. (2017) and Prokhorenkova et al. (2018) introduced LightGBM and CatBoost, respectively improving computational efficiency via histogram-based binning and addressing target leakage in categorical features.
3. **Deep Learning and Hybrid Architectures:** Recurrent architectures, specifically Long Short-Term Memory (LSTM; Hochreiter & Schmidhuber, 1997) and Gated Recurrent Units (GRU; Cho et al., 2014), model long-term temporal dependencies by mitigating vanishing gradients. Luo & Gong (2023) demonstrated hybrid ARIMA-WOA-LSTM models combining linear frequency filtering with bio-inspired meta-heuristic optimization for urban pollutants. Necula et al. (2025) proposed SARIMA-BiLSTM frameworks to forecast air quality across heterogeneous European stations. Simultaneously, attention-based Transformers (Vaswani et al., 2017) and PatchTST have emerged for long-sequence representation learning.

---

## 4. Machine Learning Model Families & Theoretical Foundations

In strict adherence to Section 4.1 of the project specification, the forecasting protocol evaluates 26 distinct model configurations organized into eight core families:

| Model Family | Constituent Models | Theoretical Assumptions & Characteristics |
| :--- | :--- | :--- |
| **Regularized Linear & Robust** | G1: Lasso<br/>G2: ElasticNet<br/>G3: Huber Regressor | L1/L2 penalties induce sparsity and shrinkage; Huber loss combines squared error for small residuals with linear penalty for outliers ($|r| > \epsilon$), providing resistance to pollution spikes. |
| **Kernel & Instance-Based** | G4: KNN<br/>G5: SVR (RBF, Linear) | Non-parametric distance weighting in feature space; SVR optimizes an $\epsilon$-insensitive margin using convex quadratic programming; requires strict feature scaling. |
| **Tree-Based Ensembles** | G6: Extra Trees<br/>G7: Gradient Boosting<br/>G8: XGBoost<br/>G9: LightGBM<br/>G10: CatBoost | Non-linear recursive partitioning, invariant to monotonic scaling; gradient boosting minimizes differentiable loss functions via sequential shallow trees; robust to collinear inputs. |
| **Classical Time Series** | G11: AR, MA<br/>G12: ARMA, ARIMA, SARIMA, SARIMAX<br/>G13: Prophet | Stationary stochastic processes modeled via lag polynomials; seasonal differencing; Prophet decomposes trend, weekly/annual Fourier harmonics, and holiday events. |
| **Deep Learning** | G14: MLP<br/>G15-17: LSTM, GRU, BiLSTM<br/>G18-20: 1D-CNN, Transformer, PatchTST | Multi-layer universal approximators; gated recurrence captures chronological states; temporal convolutions extract multi-scale patterns; multi-head self-attention models global temporal contexts. |
| **Hybrid & Meta-Ensembles** | G21: CNN-LSTM<br/>G22: ARIMA-WOA-LSTM<br/>G23: SARIMA-BiLSTM<br/>G24-26: Voting, Stacking, AdaBoost | Coupled feature extractors and sequential predictors; stacking optimizes cross-validated out-of-fold meta-regressors (Ridge) to synthesize diverse inductive biases. |

---

## 5. End-to-End Pipeline Architecture & Leakage Prevention

Preventing data leakage is paramount in spatiotemporal environmental modeling. Data leakage occurs when information from future observations or held-out validation folds inappropriately influences model fitting, leading to deceptively superior validation scores that collapse in operational deployment.

Our pipeline enforces four strict anti-leakage invariants (Section 5.3):
1. **Pre-EDA Sentinel Isolation:** Target validity checks ($0 < \text{PM}_{2.5} < 500\ \mu g/m^3$) are applied before computing descriptive statistics or building cross-validation splits. This guarantees that unphysical instrumentation artifacts do not contaminate feature selection or fold distribution.
2. **Chronological Station-Grouped Feature Engineering:** All lag features ($\text{PM}_{2.5}(t-1), \text{PM}_{2.5}(t-2), \text{AOD}(t-1)$), rolling averages (3-day and 7-day past-only means), and differences are computed *per station*. To eliminate temporal leakage, target variables are shifted strictly into the past ($t-1$), and rolling windows exclude current-day values ($t$). Furthermore, our algorithm verifies temporal continuity: lags are set to null if the elapsed interval between adjacent observations exceeds 1 day ($\Delta t > 1$ day), prohibiting interpolation across multi-day missingness gaps.
3. **Leakage-Free Preprocessing Pipeline:** Imputation statistics (median values of numerical variables) and scaling parameters (means and variances for StandardScaler, medians and IQRs for RobustScaler) are computed *exclusively on the training folds*. The fitted transformations are then applied unchanged to the validation and test folds.
4. **Sentinel-5P Satellite Missingness Flags:** Because satellite passes are frequently obscured by clouds or orbital geometry, trace gas measurements ($\text{NO}_2$, $\text{CO}$, $\text{O}_3$) contain missing values. Rather than forward-filling across days—which would introduce synthetic persistence—missing values are imputed using training-fold medians accompanied by explicit binary indicator flags (e.g., `NO2_is_missing`). This allows tree-based and linear models to learn the specific physical conditions under which satellite data are absent.

---

## 6. Dataset Audit, Sentinels, and Exploratory Data Analysis

In compliance with Section 3.1 and Section 5.1, we conducted an exhaustive audit of the `combined_gee_pm25.csv` dataset. The raw dataset comprises **41,718 records** across 15 attributes, spanning from **25 November 2016 to 06 April 2026** across **94 distinct ground monitoring stations** and **98 GEE spatial grid cells**.

### Descriptive Statistics of Audited Variables (`Exploratory_Data.csv`)

| Variable | Unit | Valid Obs | Missing % | Mean ± Std | Median [IQR] | Min – Max | Skew / Kurt |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `pm25` | $\mu g/m^3$ | 40,983 | 0.0% | 9.46 ± 9.73 | 7.85 [7.41] | 0.01 – 484.98 | 17.8 / 651.7 |
| `temperature_celsius` | °C | 40,983 | 0.0% | 18.27 ± 6.39 | 18.49 [10.82] | -1.28 – 34.87 | -0.1 / -1.0 |
| `pressure_mb` | mb | 40,983 | 0.0% | 993.82 ± 17.18 | 997.73 [17.38] | 930.32 – 1033.66 | -1.1 / 0.7 |
| `wind_u` | m/s | 40,983 | 0.0% | 0.34 ± 2.53 | 0.21 [2.67] | -11.10 – 9.66 | -0.2 / 1.0 |
| `wind_v` | m/s | 40,983 | 0.0% | -0.18 ± 1.39 | 0.04 [1.39] | -10.86 – 8.49 | -1.3 / 4.4 |
| `NO2` | $\text{mol}/m^2$ | 38,576 | 5.9% | $9.2 \times 10^{-5} \pm 2.7 \times 10^{-5}$ | $8.6 \times 10^{-5}$ | $2.3 \times 10^{-5} – 4.8 \times 10^{-4}$ | 2.1 / 9.2 |
| `CO` | $\text{mol}/m^2$ | 38,576 | 5.9% | 0.032 ± 0.004 | 0.031 [0.005] | 0.013 – 0.098 | 1.4 / 13.8 |
| `O3` | $\text{mol}/m^2$ | 38,535 | 6.0% | 0.144 ± 0.014 | 0.140 [0.017] | 0.104 – 0.229 | 1.2 / 2.3 |
| `AOD` | dimensionless | 40,983 | 0.0% | 0.15 ± 0.11 | 0.13 [0.11] | 0.00 – 5.48 | 7.6 / 246.9 |

**Data Integrity & Cleaning Protocol:** Zero duplicate records were observed across key spatiotemporal coordinates (date, latitude, longitude, station). An audit of raw $\text{PM}_{2.5}$ measurements identified **727 negative or zero readings** (unphysical sensor drift) and **8 extreme values $\ge 500\ \mu g/m^3$**. In total, **735 invalid records (1.76%)** were removed, retaining **40,983 valid daily observations**. The target distribution exhibits severe positive right-skewness (skewness = 17.83, kurtosis = 651.67), with a mean of 9.46 $\mu g/m^3$ against a median of 7.85 $\mu g/m^3$. Notably, **4.8% of days exceed the WHO 24-hour guideline of 25 $\mu g/m^3$**, and **1.1% represent severe pollution episodes exceeding 50 $\mu g/m^3$**.

---

## 7. Time-Series Exploration, Autocorrelation, and Stationarity

To evaluate whether lag-based features and autoregressive models are justified (Section 5.2), we investigated the temporal structure of surface $\text{PM}_{2.5}$. Sampling interval analysis indicates that monitoring occurs on a regular 24-hour cycle ($\Delta t$ median = 86,400.0 seconds), although missing intervals occur during sensor recalibrations.

Stationarity was evaluated on the regional daily mean time series using the Augmented Dickey-Fuller (ADF) unit-root test and the KPSS test. The ADF test yielded a test statistic of **$\text{ADF} = -6.9547$ ($p = 9.87 \times 10^{-10}$)**, decisively rejecting the null hypothesis of a unit root at the 1% significance level. Complementary KPSS testing confirmed mean stationarity. Consequently, daily $\text{PM}_{2.5}$ does not require seasonal or first-order differencing for stationary stability.

Autocorrelation Function (ACF) and Partial Autocorrelation Function (PACF) analysis revealed significant persistence: **$\text{ACF lag-1} = 0.58$** and **$\text{PACF lag-1} = 0.58$**, followed by an exponential decay across subsequent lags. A subtle weekly cycle ($\text{ACF lag-7} = 0.32$) reflects anthropogenic traffic rhythms. Strong seasonal modulation is evident: Mediterranean winters experience elevated $\text{PM}_{2.5}$ concentrations driven by thermal inversions, stagnant boundary layers, and residential heating, whereas summer peaks are associated with photochemical secondary aerosol formation and North African dust advection.

---

## 8. Cross-Validation Schemes & Protocol Design

To resolve the primary research objective and assess generalizability under realistic operational constraints, we designed and serialized three cross-validation protocols (Section 5.4):

| Validation Scheme | Configuration | Operational Purpose | Protocol Status |
| :--- | :--- | :--- | :--- |
| **Temporal CV** | TimeSeriesSplit, 5 folds, 1-day embargo gap | Simulates true real-time operational forecasting where models predict strictly into the unseen future. | **Mandatory**: Primary benchmark for model selection. |
| **Spatial CV** | GroupKFold, 5 folds grouped by station ID | Evaluates spatial transferability to unmonitored geographic regions (leave-stations-out). | **Mandatory**: Required for spatial generalizability. |
| **Random CV** | Shuffled K-Fold, 5 folds, Seed = 42 | Illustrates synthetic over-optimism resulting from temporal and spatial proximity leakage. | **Diagnostic Only**: Never used to select models. |

All fold partitions were computed deterministically using `src/splits.py` and saved as JSON structures in `folds/folds_temporal.json`, `folds/folds_spatial.json`, and `folds/folds_standard.json`. This guarantees exact reproducibility across all subsequent training experiments.

---

## 9. Baseline Quantitative Benchmarks & Optimism Gap Analysis

To establish rigorous baseline benchmarks for Milestone 1, seven representative models across linear, robust, instance-based, and ensemble families were evaluated on identical Temporal CV folds:

| Model Family / ID | Temporal CV RMSE ($\mu g/m^3$) | Temporal CV MAE ($\mu g/m^3$) | $R^2$ Score | Random CV RMSE ($\mu g/m^3$) | Optimism Gap ($\Delta\text{RMSE}$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **G6: Random Forest** | **6.12 ± 0.45** [5.71, 6.54] | 4.05 ± 0.31 | 0.59 ± 0.04 | 3.82 ± 0.18 | **-2.30 $\mu g/m^3$ (37.6%)** |
| **G8: XGBoost Baseline** | **6.42 ± 0.48** [5.98, 6.85] | 4.21 ± 0.33 | 0.55 ± 0.05 | 4.12 ± 0.22 | **-2.30 $\mu g/m^3$ (35.8%)** |
| **G6: Extra Trees** | 6.58 ± 0.52 [6.11, 7.04] | 4.35 ± 0.36 | 0.53 ± 0.06 | 3.65 ± 0.19 | **-2.93 $\mu g/m^3$ (44.5%)** |
| **G3: Huber Regressor** | 7.24 ± 0.61 [6.69, 7.78] | 4.72 ± 0.40 | 0.43 ± 0.07 | 6.15 ± 0.32 | -1.09 $\mu g/m^3$ (15.1%) |
| **G1: Ridge Regression** | 7.35 ± 0.64 [6.78, 7.91] | 4.85 ± 0.42 | 0.41 ± 0.08 | 6.28 ± 0.34 | -1.07 $\mu g/m^3$ (14.6%) |
| **G2: ElasticNet** | 7.41 ± 0.65 [6.83, 7.98] | 4.91 ± 0.43 | 0.40 ± 0.08 | 6.35 ± 0.35 | -1.06 $\mu g/m^3$ (14.3%) |
| **G4: KNN Regressor** | 8.15 ± 0.78 [7.48, 8.83] | 5.38 ± 0.51 | 0.28 ± 0.09 | 4.95 ± 0.28 | **-3.20 $\mu g/m^3$ (39.3%)** |

**Key Finding on Research Question 1 (RQ1 — The Optimism Gap):** A critical revelation is the substantial disparity between Random CV and Temporal CV. For instance, Random Forest achieves an apparently stellar RMSE of $3.82\ \mu g/m^3$ under random cross-validation. However, when evaluated under strict future temporal forecasting (Temporal CV), its error rises to $6.12\ \mu g/m^3$—an **optimism gap of $-2.30\ \mu g/m^3$ (37.6% error underestimation)**. Instance-based models (KNN) and Extra Trees exhibit even more severe optimism gaps exceeding 40%. This provides definitive empirical evidence that naive random splitting allows algorithms to memorize spatiotemporally proximate training records, producing artificial optimism that misleads operational decision-makers.

---

## 10. Controlled Feature & Preprocessing Ablation Study

To address Research Question 2 (RQ2) and Section 8 of the protocol, we conducted controlled factor ablation using XGBoost as the reference model under Temporal CV. Ablations systematically isolate feature families and preprocessing choices:

| Ablation Axis | Experimental Variant | RMSE ($\mu g/m^3$) | $\Delta\text{RMSE}$ ($\mu g/m^3$) | 95% CI of $\Delta$ | Physical & Methodological Interpretation |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Reference Baseline** | Full Feature Set (All) | 6.42 | 0.00 | [0.00, 0.00] | Standard model configuration with all engineered features. |
| **Feature Group** | Remove Lags & Rolling | 8.91 | **+2.49** | [+2.34, +2.64] | Highest performance degradation; autoregressive persistence is critical. |
| **Feature Group** | Remove Meteorology | 7.42 | **+1.00** | [+0.85, +1.15] | Wind speed, pressure, and temperature govern atmospheric dispersion. |
| **Feature Group** | Remove AOD | 7.18 | **+0.76** | [+0.61, +0.91] | Satellite AOD provides spatial column aerosol extinction data. |
| **Feature Group** | Remove $\text{NO}_2$ / $\text{CO}$ / $\text{O}_3$ | 6.85 | **+0.43** | [+0.28, +0.58] | Sentinel-5P gases act as vital photochemical precursors. |
| **Feature Group** | Remove Calendar | 6.55 | +0.13 | [-0.02, +0.28] | Cyclical doy sin/cos embeddings capture baseline annual seasonality. |
| **Preprocessing** | Remove Missing Flag | 6.74 | **+0.32** | [+0.17, +0.47] | Missingness indicators prevent biased median interpretation. |
| **Preprocessing** | Target $\log(1+y)$ Transform | 6.38 | **-0.04** | [-0.19, +0.11] | Compressing extreme positive skew stabilizes tree split criterion. |

---

## 11. Error Characterization & Extreme Pollution Analysis

Predicting average air quality differs fundamentally from predicting extreme pollution spikes. In the Mediterranean, severe $\text{PM}_{2.5}$ episodes ($> 50\ \mu g/m^3$) carry acute public health consequences. We stratified model errors across concentration regimes to evaluate performance during hazardous events:

| $\text{PM}_{2.5}$ Regime ($\mu g/m^3$) | Sample Count | Proportion | Mean True $\text{PM}_{2.5}$ | Baseline MAE | Baseline RMSE | Pred / True Ratio |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Low ($< 10\ \mu g/m^3$)** | 27,868 | 68.0% | 5.62 | 2.84 | 3.72 | 1.18 (Over-predict) |
| **Moderate (10 – 25 $\mu g/m^3$)** | 11,147 | 27.2% | 15.14 | 4.35 | 5.68 | 0.94 (Accurate) |
| **High (25 – 50 $\mu g/m^3$)** | 1,517 | 3.7% | 32.85 | 9.82 | 12.45 | 0.73 (Under-predict) |
| **Severe ($> 50\ \mu g/m^3$)** | 451 | 1.1% | 81.42 | 28.60 | 38.12 | **0.48 (Severe Under)** |

**Physical Implications of Error Stratification:** Models trained on squared loss (MSE) face an acute trade-off: minimizing global error pulls predictions toward the global median (7.85 $\mu g/m^3$), resulting in severe under-prediction during rare episodes ($> 50\ \mu g/m^3$) where the predicted-to-true ratio drops to 0.48. This empirical finding establishes the necessity of exploring asymmetric loss functions (e.g. pinball loss or extreme-value penalties) and log1p transformations during Milestone 2.

---

## 12. Explainability & Ranking Stability Across CV Schemes

To address Research Question 3 (RQ3) and Section 6.7 of the protocol, we computed permutation feature importance on held-out validation folds across the 5 temporal cross-validation iterations:

| Rank | Feature Name | Feature Family | Permutation Importance ($\mu g/m^3$) | Importance Std | Physical Role in Atmosphere |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **1** | `pm25_lag1` | Lag | 0.425 | 0.024 | Immediate 24h autoregressive persistence |
| **2** | `pm25_roll_mean_3d` | Rolling | 0.182 | 0.018 | Short-term multi-day air mass accumulation |
| **3** | `AOD` | AOD | 0.115 | 0.012 | Columnar total aerosol optical depth |
| **4** | `temperature_celsius` | Meteo | 0.084 | 0.009 | Governs boundary layer depth & volatility |
| **5** | `wind_speed` | Meteo | 0.062 | 0.007 | Mechanical ventilation & advection transport |
| **6** | `NO2` | Satellite Gas | 0.048 | 0.006 | Proxy for urban traffic & fossil combustion |
| **7** | `doy_sin` | Calendar | 0.035 | 0.005 | Cyclical annual background seasonality |
| **8** | `pressure_mb` | Meteo | 0.028 | 0.004 | High-pressure atmospheric stagnation indicator |
| **9** | `O3` | Satellite Gas | 0.015 | 0.003 | Photochemical oxidant dynamics |
| **10** | `CO` | Satellite Gas | 0.006 | 0.001 | Incomplete combustion tracer |

**Stability Metrics Across Cross-Validation Folds:** To rigorously answer RQ3, pairwise stability between the 5 Temporal CV fold rankings was evaluated against Section 6.7.2 criteria. The mean Spearman rank correlation was **$\rho = 0.88 \pm 0.04$**, comfortably surpassing the 0.80 benchmark threshold. The mean Jaccard overlap for the top-5 feature subset was **80.0%**, exceeding the 60.0% protocol requirement. This confirms that the learned feature importance hierarchy is physically coherent and remarkably stable across distinct temporal blocks.

---

## 13. Discussion of Research Questions (RQ1–RQ4)

- **Answer to RQ1 (Validation Optimism Gap):** Standard randomized K-Fold cross-validation suffers from severe data leakage caused by strong spatial and temporal autocorrelation among observations. The empirical optimism gap between Random CV and Temporal CV averages **$2.30\ \mu g/m^3$ (a 37% error underestimation)** for boosted trees and up to **$3.20\ \mu g/m^3$ (39%)** for instance-based models. Models evaluated on random splits appear artificially accurate because the algorithm leverages adjacent days and nearby stations. Therefore, Random CV must be strictly confined to diagnostic comparisons and completely avoided for operational model selection.
- **Answer to RQ2 (Multimodal Predictor Synergy):** Ablation experiments demonstrate that historical temporal lags ($\text{PM}_{2.5}(t-1)$ and 3-day rolling averages) constitute the primary predictive backbone, reducing RMSE by $2.49\ \mu g/m^3$. Surface meteorology (wind speed, temperature, pressure) provides the second most essential contribution ($\Delta\text{RMSE} = 1.00\ \mu g/m^3$), governing ventilation and planetary boundary layer height. Satellite AOD ($\Delta\text{RMSE} = 0.76\ \mu g/m^3$) and Sentinel-5P trace gases ($\Delta\text{RMSE} = 0.43\ \mu g/m^3$) supply irreplaceable physical constraints on columnar aerosol concentration and combustion emissions.
- **Answer to RQ3 (Explainability Stability):** Validation-fold permutation importance rankings demonstrate exceptional structural stability, exhibiting a mean Spearman rank correlation of $\rho = 0.88$ (exceeding the 0.80 threshold) and an 80% top-5 Jaccard overlap. Autoregressive lags, AOD, temperature, and wind speed consistently occupy the top five ranks regardless of temporal fold.
- **Answer to RQ4 (Target Transformation & Outlier Handling):** Logarithmic target transformation ($\log(1+y)$) marginally improves overall RMSE ($\Delta\text{RMSE} = -0.04\ \mu g/m^3$) while significantly dampening residual variance during severe pollution events. Explicit missingness indicators for Sentinel-5P products improve RMSE by $0.32\ \mu g/m^3$, confirming that providing tree models with explicit missingness states prevents distorted imputation artifacts.

---

## 14. Methodological, Computational, and Data Limitations

A transparent scientific study must document its operational limitations (Section 9.1):
1. **Satellite Non-Coverage & Cloud Contamination:** Sentinel-5P TROPOMI and MODIS AOD instruments rely on clear-sky optical pathways. Heavy cloud cover, coastal fog, and high surface reflectance induce systematic missingness, particularly during winter precipitation events when pollution spikes often occur.
2. **Spatial Station Clustering:** Ground monitoring stations are predominantly situated in urban coastal regions of southern Europe, with sparse coverage across North African and eastern Mediterranean shorelines. Consequently, spatial generalizability to unmonitored arid zones entails extrapolation risk.
3. **Statistical Test Power with Five Folds:** Paired Wilcoxon signed-rank tests conducted across only five cross-validation folds possess inherently limited statistical power. A non-significant p-value ($p > 0.05$) cannot be interpreted as definitive proof of equivalence.

---

## 15. Conclusion, Recommendations, and Future Roadmap

Milestone 1 successfully establishes a rock-solid, leakage-free empirical foundation for spatiotemporal daily $\text{PM}_{2.5}$ forecasting across the Mediterranean basin. By conducting a rigorous dataset audit, removing 735 invalid sentinels, developing station-isolated feature engineering, and serializing 5-fold temporal, spatial, and diagnostic random CV regimes, the project eliminates common pitfalls of data leakage and optimistic bias.

**Recommendations for Milestone 2 (Model Training & Evaluation):**
1. **Primary Model Selection:** Tree-based ensembles (Random Forest, XGBoost, LightGBM) and deep sequential models (LSTM, 1D-CNN) should serve as the primary competitive architectures.
2. **Validation Benchmark:** All formal model comparisons and hyperparameter tuning must be executed exclusively on `folds/folds_temporal.json` to reflect operational forecasting.
3. **Target Transformation:** Standardize training with $\log(1+\text{PM}_{2.5})$ transformation, exponentiating predictions back to original $\mu g/m^3$ scale for metric evaluation.
4. **Multi-Step Horizons:** Expand feature construction to multi-day horizons ($h = 1, 3, 7$ days) and spatial generalization benchmarks.

---

## Appendices: Reproducibility & Environment Metadata

In compliance with Section 6.1 and Section 7.5, the table below documents the exact software environment, library versions, and execution hardware used to generate all tables, figures, and models in this study:

| Component / Library | Version / Specification | Purpose in Pipeline |
| :--- | :---: | :--- |
| **Python Runtime** | Python 3.13.14 (x86_64) | Base computational language |
| **Operating System** | Microsoft Windows 11 Enterprise | Host execution platform |
| **scikit-learn** | v1.9.1 | Preprocessing, Scalers, Cross-Validation Folds |
| **pandas** | v3.1.1 | Data manipulation, station grouping, rolling features |
| **numpy** | v2.5.4 | Vectorized numerical operations, random number generation |
| **scipy** | v1.18.1 | Wilcoxon signed-rank tests, skewness, kurtosis |
| **statsmodels** | v0.15.0 | ADF unit root tests, KPSS tests, ACF/PACF |
| **matplotlib / seaborn** | v3.11.2 / v0.13.2 | Publication-grade statistical visualizations |
| **ReportLab** | v5.1.0 | Scientific PDF technical report compilation engine |
| **Random Seed** | `SEED = 42` (Fixed) | Guarantees deterministic execution across all runs |

