"""
Ablation Study Module for PM2.5 Forecasting.
Implements controlled factor removal across feature groups, preprocessing variants,
and validation schemes (Section 8).
Master 1 Mini Project | Academic Year 2026-2027
"""

from typing import List, Dict, Any
import numpy as np
import pandas as pd

try:
    from src.config import (
        METEO_COLS,
        SATELLITE_GAS_COLS,
        AOD_COLS,
        TARGET_COL,
    )
except ImportError:
    from config import (
        METEO_COLS,
        SATELLITE_GAS_COLS,
        AOD_COLS,
        TARGET_COL,
    )


# Feature families for controlled ablation (Section 8.2)
FEATURE_GROUPS = {
    "AOD": ["AOD", "AOD_lag1", "AOD_lag2", "AOD_lag3", "aod_roll_max_7d"],
    "NO2_CO_O3": [
        "NO2", "CO", "O3", "NO2_lag1",
        "NO2_is_missing", "CO_is_missing", "O3_is_missing"
    ],
    "Meteorological": [
        "temperature_celsius", "pressure_mb", "wind_u", "wind_v",
        "temp_diff_1d", "pressure_diff_1d", "wind_speed"
    ],
    "Calendar": [
        "doy_sin", "doy_cos", "month_sin", "month_cos", "dow_sin", "dow_cos"
    ],
    "Lags_Rolling": [
        f"{TARGET_COL}_lag1", f"{TARGET_COL}_lag2", f"{TARGET_COL}_lag3",
        "pm25_roll_mean_3d", "pm25_roll_std_3d",
        "pm25_roll_mean_7d", "pm25_roll_std_7d"
    ],
}


def get_ablated_feature_set(all_features: List[str], group_to_remove: str) -> List[str]:
    """
    Returns feature list excluding the specified feature family (Section 8.2).
    """
    cols_to_drop = set(FEATURE_GROUPS.get(group_to_remove, []))
    return [col for col in all_features if col not in cols_to_drop]


def calculate_delta_rmse(rmse_ablated: float, rmse_full: float) -> float:
    """
    Computes Delta RMSE = RMSE(ablated) - RMSE(full) (Section 8.2).
    Positive: feature removal hurt performance (feature was beneficial).
    Near zero: limited contribution.
    Negative: feature removal improved performance (feature was noisy/redundant).
    """
    return round(rmse_ablated - rmse_full, 4)

