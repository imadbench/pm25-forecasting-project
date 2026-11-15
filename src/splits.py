"""
Data Splitting and Cross-Validation Module for PM2.5 Forecasting.
Generates and serializes the 3 mandatory validation schemes (Section 5.4):
1. Temporal CV (TimeSeriesSplit, 5 folds, 1-day gap)
2. Spatial CV (GroupKFold, 5 folds grouped by station)
3. Random CV (Shuffled K-Fold, 5 folds, fixed seed=42 - diagnostic only)
Master 1 Mini Project | Academic Year 2026-2027
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any
from sklearn.model_selection import KFold, GroupKFold, TimeSeriesSplit

try:
    from src.config import (
        STATION_COL,
        DATE_COL,
        FOLDS_DIR,
        SEED,
        N_SPLITS,
    )
except ImportError:
    from config import (
        STATION_COL,
        DATE_COL,
        FOLDS_DIR,
        SEED,
        N_SPLITS,
    )


def generate_temporal_folds(
    df: pd.DataFrame,
    n_splits: int = N_SPLITS,
    gap: int = 1,
) -> Dict[str, Any]:
    """
    Mandatory Temporal Cross-Validation (Section 5.4).
    TimeSeriesSplit with n_splits=5 and 1-day gap.
    Evaluates forecasting on future unseen dates.
    """
    # Sort chronologically by date
    df_sorted = df.sort_values(by=DATE_COL).reset_index(drop=True)
    n_samples = len(df_sorted)

    # TimeSeriesSplit with gap parameter (available in modern scikit-learn)
    tscv = TimeSeriesSplit(n_splits=n_splits, gap=gap)
    
    folds_dict = {
        "scheme": "temporal",
        "description": "TimeSeriesSplit, 5 folds, 1-day gap for future observation forecasting",
        "n_splits": n_splits,
        "gap": gap,
        "n_samples": n_samples,
        "folds": {}
    }

    for fold_idx, (train_idx, val_idx) in enumerate(tscv.split(df_sorted)):
        # Convert to native python int for JSON serialization
        folds_dict["folds"][f"fold_{fold_idx}"] = {
            "train_indices": train_idx.tolist(),
            "val_indices": val_idx.tolist(),
            "train_count": len(train_idx),
            "val_count": len(val_idx),
            "train_date_min": str(df_sorted.iloc[train_idx][DATE_COL].min()),
            "train_date_max": str(df_sorted.iloc[train_idx][DATE_COL].max()),
            "val_date_min": str(df_sorted.iloc[val_idx][DATE_COL].min()),
            "val_date_max": str(df_sorted.iloc[val_idx][DATE_COL].max()),
        }

    return folds_dict


def generate_spatial_folds(
    df: pd.DataFrame,
    n_splits: int = N_SPLITS,
    group_col: str = STATION_COL,
) -> Dict[str, Any]:
    """
    Mandatory Spatial Cross-Validation (Section 5.4).
    GroupKFold with 5 folds grouped by station ID.
    Evaluates model generalization to unseen locations.
    """
    groups = df[group_col].values
    gkf = GroupKFold(n_splits=n_splits)

    folds_dict = {
        "scheme": "spatial",
        "description": "GroupKFold, 5 folds grouped by station ID for unseen location evaluation",
        "n_splits": n_splits,
        "group_column": group_col,
        "n_groups": int(df[group_col].nunique()),
        "n_samples": len(df),
        "folds": {}
    }

    for fold_idx, (train_idx, val_idx) in enumerate(gkf.split(df, groups=groups)):
        train_stations = df.iloc[train_idx][group_col].unique().tolist()
        val_stations = df.iloc[val_idx][group_col].unique().tolist()
        
        # Verify strict station separation
        assert len(set(train_stations).intersection(set(val_stations))) == 0, "Spatial leak detected!"

        folds_dict["folds"][f"fold_{fold_idx}"] = {
            "train_indices": train_idx.tolist(),
            "val_indices": val_idx.tolist(),
            "train_count": len(train_idx),
            "val_count": len(val_idx),
            "train_stations_count": len(train_stations),
            "val_stations_count": len(val_stations),
        }

    return folds_dict


def generate_standard_folds(
    df: pd.DataFrame,
    n_splits: int = N_SPLITS,
    random_state: int = SEED,
) -> Dict[str, Any]:
    """
    Diagnostic Random Cross-Validation (Section 5.4).
    Shuffled K-Fold, 5 folds, fixed seed.
    Diagnostic only: illustrates artificial optimism due to spatio-temporal leakage.
    """
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    folds_dict = {
        "scheme": "standard_random",
        "description": "Shuffled K-Fold, 5 folds, fixed seed=42 (Diagnostic only: illustrates optimism)",
        "n_splits": n_splits,
        "random_state": random_state,
        "n_samples": len(df),
        "folds": {}
    }

    for fold_idx, (train_idx, val_idx) in enumerate(kf.split(df)):
        folds_dict["folds"][f"fold_{fold_idx}"] = {
            "train_indices": train_idx.tolist(),
            "val_indices": val_idx.tolist(),
            "train_count": len(train_idx),
            "val_count": len(val_idx),
        }

    return folds_dict


def save_all_folds(df: pd.DataFrame, output_dir=FOLDS_DIR) -> Dict[str, str]:
    """Generates and writes all 3 validation split files to disk."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    # 1. Temporal
    temporal_folds = generate_temporal_folds(df)
    temp_path = output_dir / "folds_temporal.json"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(temporal_folds, f, indent=2)

    # 2. Spatial
    spatial_folds = generate_spatial_folds(df)
    spat_path = output_dir / "folds_spatial.json"
    with open(spat_path, "w", encoding="utf-8") as f:
        json.dump(spatial_folds, f, indent=2)

    # 3. Standard
    standard_folds = generate_standard_folds(df)
    std_path = output_dir / "folds_standard.json"
    with open(std_path, "w", encoding="utf-8") as f:
        json.dump(standard_folds, f, indent=2)

    return {
        "temporal": str(temp_path),
        "spatial": str(spat_path),
        "standard": str(std_path),
    }

