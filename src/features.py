"""
Feature Engineering Module for PM2.5 Forecasting.
Constructs temporal lags, rolling aggregations, day-of-year cyclical encoding,
and meteorological differentials per station without temporal leakage.
Master 1 Mini Project | Academic Year 2026-2027
"""

import numpy as np
import pandas as pd
from typing import List, Optional

try:
    from src.config import (
        TARGET_COL,
        STATION_COL,
        DATE_COL,
        METEO_COLS,
        SATELLITE_GAS_COLS,
        AOD_COLS,
    )
except ImportError:
    from config import (
        TARGET_COL,
        STATION_COL,
        DATE_COL,
        METEO_COLS,
        SATELLITE_GAS_COLS,
        AOD_COLS,
    )


def add_cyclical_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encodes temporal cyclical patterns (Section 5.3.4).
    Day-of-year, month, and day-of-week encoded with sine and cosine
    to preserve circular temporal continuity without data leakage.
    """
    df_out = df.copy()
    date_dt = pd.to_datetime(df_out[DATE_COL])

    # Day of Year
    doy = date_dt.dt.dayofyear
    df_out["doy_sin"] = np.sin(2 * np.pi * doy / 365.25)
    df_out["doy_cos"] = np.cos(2 * np.pi * doy / 365.25)

    # Month of Year
    month = date_dt.dt.month
    df_out["month_sin"] = np.sin(2 * np.pi * month / 12.0)
    df_out["month_cos"] = np.cos(2 * np.pi * month / 12.0)

    # Day of Week (Weekly cycles §5.2)
    dow = date_dt.dt.dayofweek
    df_out["dow_sin"] = np.sin(2 * np.pi * dow / 7.0)
    df_out["dow_cos"] = np.cos(2 * np.pi * dow / 7.0)

    return df_out


def add_missingness_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds binary missingness indicators for Sentinel-5P gas columns (Section 5.3.1).
    Helps models distinguish genuine physical zero/low from unobserved sensor passes.
    """
    df_out = df.copy()
    for col in SATELLITE_GAS_COLS:
        if col in df_out.columns:
            df_out[f"{col}_is_missing"] = df_out[col].isnull().astype(int)
    return df_out


def create_station_temporal_features(
    df: pd.DataFrame,
    lags: List[int] = [1, 2, 3],
    rolling_windows: List[int] = [3, 7],
    max_gap_days: int = 1,
) -> pd.DataFrame:
    """
    Creates station-specific past-only lag and rolling features (Section 5.3.4).
    Guarantees:
    1. Features are grouped per-station (never leaking across sensors).
    2. Consecutive dates only: multi-day observation gaps are not bridged.
    3. Excludes same-day target to prevent nowcasting target leakage.
    """
    df_out = df.copy()
    df_out["date_dt"] = pd.to_datetime(df_out[DATE_COL])
    df_out = df_out.sort_values(by=[STATION_COL, "date_dt"]).reset_index(drop=True)

    station_dfs = []
    for station, group in df_out.groupby(STATION_COL, as_index=False):
        group = group.sort_values("date_dt").copy()
        date_diff = group["date_dt"].diff().dt.days

        # Continuous flag: valid if difference from previous measurement is exactly 1 day
        is_continuous = date_diff == 1

        # Past Target Lags (t-1, t-2, t-3)
        for lag in lags:
            col_name = f"{TARGET_COL}_lag{lag}"
            # Shift past target
            group[col_name] = group[TARGET_COL].shift(lag)
            # Mask out lags across discontinuous multi-day gaps
            for l in range(1, lag + 1):
                group.loc[group["date_dt"].diff(l).dt.days != l, col_name] = np.nan

        # AOD Lags (t-1, t-2, t-3)
        for lag in lags:
            col_name = f"AOD_lag{lag}"
            group[col_name] = group["AOD"].shift(lag)
            for l in range(1, lag + 1):
                group.loc[group["date_dt"].diff(l).dt.days != l, col_name] = np.nan

        # NO2 Lag-1
        group["NO2_lag1"] = group["NO2"].shift(1)
        group.loc[~is_continuous, "NO2_lag1"] = np.nan

        # Rolling Statistics on Past Target (past-only: shifted by 1 day)
        for w in rolling_windows:
            past_target = group[TARGET_COL].shift(1)
            group[f"pm25_roll_mean_{w}d"] = past_target.rolling(window=w, min_periods=max(1, w // 2)).mean()
            group[f"pm25_roll_std_{w}d"] = past_target.rolling(window=w, min_periods=max(1, w // 2)).std()

        # Rolling Extremes: 7-day max AOD (past-only)
        past_aod = group["AOD"].shift(1)
        group["aod_roll_max_7d"] = past_aod.rolling(window=7, min_periods=3).max()

        # Day-to-Day Differences (Rates of change)
        group["temp_diff_1d"] = group["temperature_celsius"].diff(1)
        group.loc[~is_continuous, "temp_diff_1d"] = np.nan

        group["pressure_diff_1d"] = group["pressure_mb"].diff(1)
        group.loc[~is_continuous, "pressure_diff_1d"] = np.nan

        # Wind speed magnitude
        group["wind_speed"] = np.sqrt(group["wind_u"] ** 2 + group["wind_v"] ** 2)

        station_dfs.append(group)

    final_df = pd.concat(station_dfs, axis=0).sort_values(by=["date_dt", STATION_COL]).reset_index(drop=True)
    final_df = final_df.drop(columns=["date_dt"])
    return final_df


def build_full_feature_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """End-to-end feature pipeline execution."""
    df_feat = add_cyclical_calendar_features(df)
    df_feat = add_missingness_indicators(df_feat)
    df_feat = create_station_temporal_features(df_feat)
    return df_feat

