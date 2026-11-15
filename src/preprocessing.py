"""
Data Preprocessing Module for PM2.5 Forecasting.
Handles auditing, cleaning of invalid sentinels, missing value imputation,
and leakage-free scaling.
Master 1 Mini Project | Academic Year 2026-2027
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, Optional
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler, RobustScaler

try:
    from src.config import (
        TARGET_COL,
        STATION_COL,
        DATE_COL,
        DATETIME_COL,
        LAT_COL,
        LON_COL,
        METEO_COLS,
        SATELLITE_GAS_COLS,
        AOD_COLS,
        BASE_NUMERICAL_COLS,
        PM25_MIN_VALID,
        PM25_MAX_VALID,
        SEED,
    )
except ImportError:
    from config import (
        TARGET_COL,
        STATION_COL,
        DATE_COL,
        DATETIME_COL,
        LAT_COL,
        LON_COL,
        METEO_COLS,
        SATELLITE_GAS_COLS,
        AOD_COLS,
        BASE_NUMERICAL_COLS,
        PM25_MIN_VALID,
        PM25_MAX_VALID,
        SEED,
    )


def audit_raw_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Mandatory dataset audit (Section 3.1 & Section 5.1).
    Quantifies row counts, columns, dates, stations, and key-field duplicates.
    """
    total_rows = len(df)
    total_cols = len(df.columns)
    date_min = str(df[DATE_COL].min())
    date_max = str(df[DATE_COL].max())
    n_stations = df[STATION_COL].nunique() if STATION_COL in df.columns else 0
    n_grids = df["id"].nunique() if "id" in df.columns else 0

    exact_duplicates = int(df.duplicated().sum())
    key_fields = [c for c in [DATE_COL, LAT_COL, LON_COL, STATION_COL] if c in df.columns]
    key_duplicates = int(df.duplicated(subset=key_fields).sum()) if key_fields else 0

    missing_by_col = df.isnull().sum().to_dict()

    return {
        "total_rows": total_rows,
        "total_cols": total_cols,
        "date_min": date_min,
        "date_max": date_max,
        "n_stations": n_stations,
        "n_grids": n_grids,
        "exact_duplicates": exact_duplicates,
        "key_duplicates": key_duplicates,
        "missing_counts": missing_by_col,
    }


def clean_target_sentinels(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Removes invalid PM2.5 measurements (Section 5.1):
    Rows with missing PM2.5 or PM2.5 <= 0 or PM2.5 >= 500 ug/m3.
    Must be executed BEFORE EDA and splitting.
    """
    initial_count = len(df)
    missing_pm25 = int(df[TARGET_COL].isnull().sum())
    low_sentinels = int((df[TARGET_COL] <= PM25_MIN_VALID).sum())
    high_sentinels = int((df[TARGET_COL] >= PM25_MAX_VALID).sum())

    invalid_mask = (
        df[TARGET_COL].isnull()
        | (df[TARGET_COL] <= PM25_MIN_VALID)
        | (df[TARGET_COL] >= PM25_MAX_VALID)
    )

    df_cleaned = df[~invalid_mask].copy()
    removed_total = initial_count - len(df_cleaned)

    # Standardize datetime and sort chronologically by date
    if DATETIME_COL in df_cleaned.columns:
        df_cleaned["datetime"] = pd.to_datetime(df_cleaned[DATETIME_COL])
    elif DATE_COL in df_cleaned.columns:
        df_cleaned["datetime"] = pd.to_datetime(df_cleaned[DATE_COL])
    df_cleaned["date"] = pd.to_datetime(df_cleaned[DATE_COL])
    df_cleaned = df_cleaned.sort_values(by=["date", STATION_COL]).reset_index(drop=True)

    counts_dict = {
        "initial_rows": initial_count,
        "missing_target": missing_pm25,
        "sentinel_low_le0": low_sentinels,
        "sentinel_high_ge500": high_sentinels,
        "removed_total": removed_total,
        "retained_rows": len(df_cleaned),
    }

    return df_cleaned, counts_dict


class LeakageFreePreprocessor(BaseEstimator, TransformerMixin):
    """
    Leakage-free Preprocessing Pipeline (Section 5.3).
    Fits all imputation medians, missingness flags, and scalers
    EXCLUSIVELY on the training partition.
    """

    def __init__(
        self,
        scaler_type: str = "standard",  # 'standard', 'robust', or None
        target_log_transform: bool = False,
    ):
        self.scaler_type = scaler_type
        self.target_log_transform = target_log_transform
        self.impute_medians_: Dict[str, float] = {}
        self.scaler_: Optional[Any] = None
        self.feature_cols_: list = []

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """Fit imputation statistics and scalers on training fold only."""
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        self.impute_medians_ = {
            col: float(X[col].median()) for col in numeric_cols if not col.endswith("_is_missing")
        }

        # Determine feature columns to scale
        cols_to_scale = [c for c in numeric_cols if not c.endswith("_is_missing")]
        self.feature_cols_ = cols_to_scale

        if self.scaler_type == "standard":
            self.scaler_ = StandardScaler()
            X_imputed = X[cols_to_scale].fillna(self.impute_medians_)
            self.scaler_.fit(X_imputed)
        elif self.scaler_type == "robust":
            self.scaler_ = RobustScaler()
            X_imputed = X[cols_to_scale].fillna(self.impute_medians_)
            self.scaler_.fit(X_imputed)
        else:
            self.scaler_ = None

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Apply learned transformations to validation or test data."""
        X_out = X.copy()

        # Add missingness indicators for Sentinel-5P gases if not present
        for col in SATELLITE_GAS_COLS:
            if col in X_out.columns and f"{col}_is_missing" not in X_out.columns:
                X_out[f"{col}_is_missing"] = X_out[col].isnull().astype(int)

        # Impute numerical features using training medians
        for col, med in self.impute_medians_.items():
            if col in X_out.columns:
                X_out[col] = X_out[col].fillna(med)

        # Apply scaling if configured
        if self.scaler_ is not None and self.feature_cols_:
            scaled_vals = self.scaler_.transform(X_out[self.feature_cols_])
            scaled_df = pd.DataFrame(
                scaled_vals, columns=self.feature_cols_, index=X_out.index
            )
            for c in self.feature_cols_:
                X_out[c] = scaled_df[c]

        return X_out

