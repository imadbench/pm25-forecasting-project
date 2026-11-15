"""make and save the three part 1 validation schemes."""

import json
import numpy as np
from sklearn.model_selection import GroupKFold, KFold, TimeSeriesSplit


def separate_test_year(features, test_year=2025):
    """separate development, complete test year, and later partial rows."""
    test = features.loc[features["date"].dt.year == test_year].copy()
    dev = features.loc[features["date"].dt.year < test_year].copy()
    post_test = features.loc[features["date"].dt.year > test_year].copy()
    return dev, test, post_test


def make_folds(dev, seed=42):
    """make date, station, and shuffled folds on development rows."""
    unique_dates = np.array(sorted(dev["date"].dropna().unique()))
    temporal_folds = []
    for train_date_idx, val_date_idx in TimeSeriesSplit(n_splits=5, gap=1).split(unique_dates):
        train_dates = set(unique_dates[train_date_idx])
        val_dates = set(unique_dates[val_date_idx])
        temporal_folds.append((np.where(dev["date"].isin(train_dates))[0], np.where(dev["date"].isin(val_dates))[0]))
    y = dev["pm25"]
    spatial_folds = list(GroupKFold(n_splits=5).split(dev, y, groups=dev["sensor_name"]))
    standard_folds = list(KFold(n_splits=5, shuffle=True, random_state=seed).split(dev, y))
    return temporal_folds, spatial_folds, standard_folds, unique_dates


def save_folds(folds, path):
    """save fold indices as plain python integers."""
    simple_folds = []
    for train_index, validation_index in folds:
        simple_folds.append({"train_idx": [int(value) for value in train_index], "val_idx": [int(value) for value in validation_index]})
    with open(path, "w", encoding="utf-8") as file:
        json.dump(simple_folds, file, indent=2)
    return simple_folds
