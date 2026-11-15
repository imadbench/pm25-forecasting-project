"""run the complete part 1 exploration and preprocessing pipeline."""

import json
import random
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import zscore
from sklearn.ensemble import IsolationForest
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tsa.stattools import adfuller

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import FIGURES_DIR, FOLDS_DIR, PROCESSED_DIR, RAW_DIR, RESULTS_DIR, SEED
from src.features import add_calendar_columns, add_high_aod_time, engineer_features, finish_feature_groups
from src.preprocessing import clean_pm25_data, load_combined_data, make_audit_table, make_preprocessing_pipeline
from src.splits import make_folds, save_folds, separate_test_year


def prepare_folders():
    """create the folders needed by the part 1 pipeline."""
    for folder in [PROCESSED_DIR, RESULTS_DIR, FIGURES_DIR, FOLDS_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def run_eda():
    """load, explore, engineer, split, and save the part 1 outputs."""
    prepare_folders()
    random.seed(SEED)
    np.random.seed(SEED)
    sns.set_theme(style="whitegrid")
    source = RAW_DIR / "combined_gee_pm25.csv"
    if not source.exists():
        source = PROJECT_ROOT / "data" / "combined_gee_pm25.csv"
    df = load_combined_data(source)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["datetime_utc"] = pd.to_datetime(df["datetime_utc"], errors="coerce")
    clean, cleaning_counts = clean_pm25_data(df)
    numeric_columns = clean.select_dtypes(include="number").columns.tolist()
    clean = add_calendar_columns(clean)
    exploratory = make_audit_table(df, clean, cleaning_counts)
    numeric_summary = clean[numeric_columns].describe().T
    numeric_summary["skewness"] = clean[numeric_columns].skew()
    numeric_summary["kurtosis"] = clean[numeric_columns].kurtosis()

    plot_columns = ["pm25", "AOD", "NO2", "CO", "O3", "temperature_celsius", "pressure_mb", "wind_u", "wind_v"]
    plot_columns = [column for column in plot_columns if column in clean.columns]
    fig, axes = plt.subplots(len(plot_columns), 2, figsize=(12, 3 * len(plot_columns)))
    for row, column in enumerate(plot_columns):
        sns.histplot(clean[column], bins=40, ax=axes[row, 0])
        axes[row, 0].set_title(column + " histogram")
        sns.boxplot(x=clean[column], ax=axes[row, 1])
        axes[row, 1].set_title(column + " boxplot")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "main_variables_histograms_boxplots.png", dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    sns.histplot(clean["pm25"], bins=50, ax=axes[0])
    axes[0].set_title("pm25 distribution")
    sns.histplot(np.log1p(clean["pm25"]), bins=50, ax=axes[1])
    axes[1].set_title("log1p(pm25) for inspection")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "pm25_distribution.png", dpi=150)
    plt.close(fig)

    q1 = clean["pm25"].quantile(0.25)
    q3 = clean["pm25"].quantile(0.75)
    iqr = q3 - q1
    iqr_flag = (clean["pm25"] < q1 - 1.5 * iqr) | (clean["pm25"] > q3 + 1.5 * iqr)
    z_flag = zscore(clean["pm25"].to_numpy()) > 3
    isolation_flag = IsolationForest(random_state=SEED, contamination="auto").fit_predict(clean[["pm25"]]) == -1
    print("IQR flagged:", int(iqr_flag.sum()))
    print("absolute z-score above 3:", int(np.abs(zscore(clean["pm25"].to_numpy())) .gt if False else (np.abs(zscore(clean["pm25"].to_numpy())) > 3).sum()))
    print("Isolation Forest flagged:", int(isolation_flag.sum()))

    excluded = ["pm25", "id", "latitude", "longitude", "month", "year"]
    predictor_numeric = [column for column in clean.select_dtypes(include="number").columns if column not in excluded]
    pearson = clean[predictor_numeric].corr(method="pearson")
    spearman = clean[predictor_numeric].corr(method="spearman")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.heatmap(pearson, cmap="coolwarm", center=0, ax=axes[0])
    axes[0].set_title("pearson correlations")
    sns.heatmap(spearman, cmap="coolwarm", center=0, ax=axes[1])
    axes[1].set_title("spearman correlations")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "correlation_heatmaps.png", dpi=150)
    plt.close(fig)
    vif_data = clean[predictor_numeric].copy().fillna(clean[predictor_numeric].median())
    _ = pd.DataFrame({"variable": vif_data.columns, "vif": [variance_inflation_factor(vif_data.to_numpy(), i) for i in range(vif_data.shape[1])]})

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    sample = clean.sample(min(5000, len(clean)), random_state=SEED)
    sns.scatterplot(data=sample, x="AOD", y="pm25", hue="season", alpha=0.35, ax=axes[0])
    axes[0].set_title("pm25 and AOD by season")
    sns.scatterplot(data=sample, x="AOD", y="pm25", hue="wind_group", alpha=0.35, ax=axes[1])
    axes[1].set_title("pm25 and AOD by wind group")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "pm25_predictor_relationships.png", dpi=150)
    plt.close(fig)

    station_rows = []
    for station, group in clean.groupby("sensor_name"):
        dates = group["date"].drop_duplicates().sort_values()
        gaps = dates.diff().dt.days.dropna()
        expected_days = (dates.max() - dates.min()).days + 1
        station_rows.append({"station": station, "rows": len(group), "unique_days": len(dates), "days_present_percent": 100 * len(dates) / expected_days, "longest_gap_days": int(gaps.max()) if len(gaps) else 0, "duplicate_station_days": int(group.duplicated(["date"]).sum())})
    station_regularity = pd.DataFrame(station_rows)
    daily_mean = clean.groupby("date")["pm25"].mean().asfreq("D").interpolate(limit=7).dropna()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    plot_acf(daily_mean, lags=30, ax=axes[0])
    axes[0].set_title("acf of daily mean pm25")
    plot_pacf(daily_mean, lags=30, ax=axes[1], method="ywm")
    axes[1].set_title("pacf of daily mean pm25")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "acf_pacf_daily_mean_pm25.png", dpi=150)
    plt.close(fig)
    ljung = acorr_ljungbox(daily_mean, lags=[7], return_df=True)
    adf = adfuller(daily_mean)
    monthly = clean.groupby("month")["pm25"].agg(median="median", q25=lambda x: x.quantile(0.25), q75=lambda x: x.quantile(0.75), mean="mean")
    yearly = clean.groupby("year")["pm25"].agg(median="median", q25=lambda x: x.quantile(0.25), q75=lambda x: x.quantile(0.75), mean="mean")
    monthly["above_25_percent"] = clean.groupby("month")["pm25"].apply(lambda x: 100 * (x > 25).mean())
    monthly["above_50_percent"] = clean.groupby("month")["pm25"].apply(lambda x: 100 * (x > 50).mean())
    yearly["above_25_percent"] = clean.groupby("year")["pm25"].apply(lambda x: 100 * (x > 25).mean())
    yearly["above_50_percent"] = clean.groupby("year")["pm25"].apply(lambda x: 100 * (x > 50).mean())
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    monthly["median"].plot(kind="bar", ax=axes[0], title="monthly median pm25")
    yearly["median"].plot(kind="bar", ax=axes[1], title="yearly median pm25")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "pm25_monthly_yearly_drift.png", dpi=150)
    plt.close(fig)

    features, feature_groups = engineer_features(clean)
    features, high_aod_threshold = add_high_aod_time(features)
    feature_groups, feature_list = finish_feature_groups(features, feature_groups)
    dev, test, post_test = separate_test_year(features)
    dev.to_csv(PROCESSED_DIR / "dev.csv", index=False, encoding="utf-8")
    test.to_csv(PROCESSED_DIR / "test.csv", index=False, encoding="utf-8")
    features.to_csv(PROCESSED_DIR / "features_all.csv", index=False, encoding="utf-8")
    with open(PROCESSED_DIR / "feature_groups.json", "w", encoding="utf-8") as file:
        json.dump(feature_groups, file, indent=2)

    for column in numeric_columns:
        for metric in ["min", "max", "mean", "std", "25%", "50%", "75%", "skewness", "kurtosis"]:
            if metric in numeric_summary.columns:
                exploratory.loc[len(exploratory)] = ["numeric_summary", column, metric, float(numeric_summary.loc[column, metric])]
    for column in ["NO2", "CO", "O3"]:
        for month, group in clean.groupby("month"):
            exploratory.loc[len(exploratory)] = ["missing_by_month", column, "month_" + str(month), float(group[column].isna().sum())]
        for station, group in clean.groupby("sensor_name"):
            exploratory.loc[len(exploratory)] = ["missing_by_station", column, station, float(group[column].isna().sum())]
    exploratory.to_csv(RESULTS_DIR / "Exploratory_Data.csv", index=False, encoding="utf-8", decimal=".")

    temporal_rows = []
    def add_temporal(variable, metric, value):
        """add one value to the temporal result table."""
        temporal_rows.append({"section": "temporal", "variable": variable, "metric": metric, "value": float(value)})
    add_temporal("date", "unique_dates", clean["date"].nunique())
    add_temporal("date", "invalid_dates", df["date"].isna().sum())
    add_temporal("station", "number_of_stations", clean["sensor_name"].nunique())
    add_temporal("station", "longest_gap_days", station_regularity["longest_gap_days"].max())
    add_temporal("station", "mean_days_present_percent", station_regularity["days_present_percent"].mean())
    add_temporal("pm25", "ljung_box_pvalue_lag_7", ljung["lb_pvalue"].iloc[0])
    add_temporal("pm25", "adf_statistic", adf[0])
    add_temporal("pm25", "adf_pvalue", adf[1])
    for year, value in yearly["median"].items():
        add_temporal("pm25", "median_year_" + str(year), value)
    for month, value in monthly["median"].items():
        add_temporal("pm25", "median_month_" + str(month), value)

    model_features = [column for column in feature_list if column in dev.columns]
    temporal_folds, spatial_folds, standard_folds, unique_dates = make_folds(dev, SEED)
    preprocessor = make_preprocessing_pipeline(model_features)
    first_train, first_val = temporal_folds[0]
    X_train = dev.iloc[first_train][model_features]
    X_val = dev.iloc[first_val][model_features]
    preprocessor.fit(X_train)
    preprocessor.transform(X_val)
    sentinel_columns = [column for column in ["NO2", "CO", "O3"] if column in dev.columns]
    fold_correlations = [dev.iloc[train_index][sentinel_columns].corr() for train_index, _ in temporal_folds]
    max_difference = 0
    for first_index in range(len(fold_correlations)):
        for second_index in range(first_index + 1, len(fold_correlations)):
            max_difference = max(max_difference, (fold_correlations[first_index] - fold_correlations[second_index]).abs().to_numpy().max())
    save_folds(temporal_folds, FOLDS_DIR / "folds_temporal.json")
    save_folds(spatial_folds, FOLDS_DIR / "folds_spatial.json")
    save_folds(standard_folds, FOLDS_DIR / "folds_standard.json")

    fig, ax = plt.subplots(figsize=(12, 3))
    for number, (train_index, val_index) in enumerate(temporal_folds, start=1):
        ax.scatter(dev.iloc[train_index]["date"], [number] * len(train_index), s=2, label="train" if number == 1 else None)
        ax.scatter(dev.iloc[val_index]["date"], [number] * len(val_index), s=2, label="validation" if number == 1 else None)
    ax.set_title("temporal validation folds")
    ax.set_xlabel("date")
    ax.set_ylabel("fold")
    ax.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "temporal_folds.png", dpi=150)
    plt.close(fig)

    lead_lag_columns = ["AOD", "NO2", "CO", "O3", "wind_speed", "temperature_celsius"]
    daily_values = clean.groupby("date")[["pm25"] + lead_lag_columns].mean()
    lead_lag_rows = []
    for column in lead_lag_columns:
        for lag in range(8):
            pair = pd.concat([daily_values["pm25"], daily_values[column].shift(lag)], axis=1).dropna()
            lead_lag_rows.append({"variable": column, "lag_days": lag, "correlation": pair.iloc[:, 0].corr(pair.iloc[:, 1])})
    lead_lag = pd.DataFrame(lead_lag_rows)
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.barplot(data=lead_lag, x="lag_days", y="correlation", hue="variable", ax=ax)
    ax.set_title("pm25 and past predictor correlations")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "lead_lag_correlations.png", dpi=150)
    plt.close(fig)
    for column in lead_lag_columns:
        one_column = lead_lag[lead_lag["variable"] == column]
        best = one_column.iloc[one_column["correlation"].abs().argmax()]
        add_temporal(column, "strongest_absolute_correlation_lag", best["lag_days"])
        add_temporal(column, "strongest_absolute_correlation", best["correlation"])
    pd.DataFrame(temporal_rows).to_csv(RESULTS_DIR / "Exploratory_temporal.csv", index=False, encoding="utf-8", decimal=".")
    print("saved part 1 outputs")


if __name__ == "__main__":
    run_eda()
