"""create past-only features without crossing station date gaps."""

import numpy as np
import pandas as pd


def add_calendar_columns(clean):
    """add month, year, season, and wind speed for exploration."""
    clean["month"] = clean["date"].dt.month
    clean["year"] = clean["date"].dt.year
    clean["season"] = clean["month"].map({12: "winter", 1: "winter", 2: "winter", 3: "spring", 4: "spring", 5: "spring", 6: "summer", 7: "summer", 8: "summer", 9: "autumn", 10: "autumn", 11: "autumn"})
    clean["wind_speed"] = np.sqrt(clean["wind_u"] ** 2 + clean["wind_v"] ** 2)
    clean["wind_group"] = pd.qcut(clean["wind_speed"], q=2, labels=["low wind", "high wind"])
    return clean


def add_gap_safe_lags(features, column, lags):
    """add lags only when the station dates are exactly consecutive."""
    for lag in lags:
        name = column + "_lag_" + str(lag)
        features[name] = features.groupby("sensor_name")[column].shift(lag)
        day_difference = features.groupby("sensor_name")["date"].diff(lag).dt.days
        features.loc[day_difference != lag, name] = np.nan
    return features


def engineer_features(clean):
    """create all past-only lags, rolling values, and calendar features."""
    features = clean.copy().sort_values(["sensor_name", "date"]).reset_index(drop=True)
    feature_groups = {"AOD": [], "NO2_CO_O3": [], "meteorological": [], "calendar": [], "lag_rolling": []}
    for column, lags in {"AOD": [1, 2, 3], "NO2": [1], "pm25": [1, 2, 3, 7]}.items():
        if column in features.columns:
            add_gap_safe_lags(features, column, lags)
            feature_groups["lag_rolling"].extend([column + "_lag_" + str(lag) for lag in lags])
    for column in ["AOD", "temperature_celsius", "NO2"]:
        if column not in features.columns:
            continue
        name = column + "_diff_1"
        features[name] = features.groupby("sensor_name")[column].diff(1)
        day_difference = features.groupby("sensor_name")["date"].diff(1).dt.days
        features.loc[day_difference != 1, name] = np.nan
        feature_groups["lag_rolling"].append(name)
    for station, group in features.groupby("sensor_name"):
        index = group.index
        dates = group["date"]
        for column in ["AOD", "temperature_celsius", "NO2"]:
            if column not in features.columns:
                continue
            for window in [3, 7]:
                mean_name = column + "_past_mean_" + str(window)
                std_name = column + "_past_std_" + str(window)
                shifted = group[column].shift(1)
                features.loc[index, mean_name] = shifted.rolling(window).mean().to_numpy()
                features.loc[index, std_name] = shifted.rolling(window).std().to_numpy()
                complete_days = dates.diff(window).dt.days == window
                features.loc[index[~complete_days.fillna(False)], [mean_name, std_name]] = np.nan
                feature_groups["lag_rolling"].extend([mean_name, std_name])
        if "AOD" in features.columns:
            extreme_name = "AOD_past_max_7"
            features.loc[index, extreme_name] = group["AOD"].shift(1).rolling(7).max().to_numpy()
            complete_days = dates.diff(7).dt.days == 7
            features.loc[index[~complete_days.fillna(False)], extreme_name] = np.nan
    if "AOD" in features.columns:
        features["AOD_change_3"] = features.groupby("sensor_name")["AOD"].diff(3)
        day_difference_3 = features.groupby("sensor_name")["date"].diff(3).dt.days
        features.loc[day_difference_3 != 3, "AOD_change_3"] = np.nan
        feature_groups["lag_rolling"].append("AOD_change_3")
    features["day_of_year_sin"] = np.sin(2 * np.pi * features["date"].dt.dayofyear / 365.25)
    features["day_of_year_cos"] = np.cos(2 * np.pi * features["date"].dt.dayofyear / 365.25)
    feature_groups["calendar"] = ["day_of_year_sin", "day_of_year_cos"]
    return features, feature_groups


def add_high_aod_time(features, development_year=2025):
    """add days since the previous high-aod event using development data."""
    development_aod = features.loc[features["date"].dt.year < development_year, "AOD"]
    threshold = development_aod.quantile(0.75)
    features["previous_high_aod_date"] = np.datetime64("NaT")
    for station, group in features.groupby("sensor_name"):
        previous_high = group["date"].where(group["AOD"] >= threshold).shift(1).ffill()
        features.loc[group.index, "previous_high_aod_date"] = previous_high.to_numpy()
    features["days_since_high_AOD"] = (features["date"] - features["previous_high_aod_date"]).dt.days
    features = features.drop(columns=["previous_high_aod_date"])
    return features, threshold


def finish_feature_groups(features, feature_groups):
    """keep only real columns in the saved feature families."""
    for key in feature_groups:
        feature_groups[key] = sorted(set(feature_groups[key]))
    feature_groups["AOD"] = [column for column in ["AOD"] if column in features.columns]
    feature_groups["NO2_CO_O3"] = [column for column in ["NO2", "CO", "O3"] if column in features.columns]
    feature_groups["meteorological"] = [column for column in ["temperature_celsius", "pressure_mb", "wind_u", "wind_v", "wind_speed"] if column in features.columns]
    feature_list = []
    for group in feature_groups.values():
        feature_list.extend(group)
    return feature_groups, sorted(set(feature_list))
