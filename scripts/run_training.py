"""
Model Training and Hyperparameter Tuning Execution Script.
Executes baseline & model training across validation folds (Milestone 2 / Section 6).
Master 1 Mini Project | Academic Year 2026-2027
"""

import os
import sys
import json
import time
import numpy as np
import pandas as pd
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    SEED,
    PROCESSED_FEATURES_CSV,
    FOLDS_DIR,
    RESULTS_DIR,
    TARGET_COL,
    STATION_COL,
    DATE_COL,
)
from src.preprocessing import LeakageFreePreprocessor
from src.models import get_baseline_models
from src.test_evaluation import compute_metrics


def run_training_pipeline():
    print("=" * 65)
    print("RUNNING MODEL TRAINING PIPELINE (BASELINE & CV EVALUATION)")
    print("=" * 65)

    if not PROCESSED_FEATURES_CSV.exists():
        print("Feature dataset not found. Running EDA pipeline first...")
        from scripts.run_eda import run_full_eda
        run_full_eda()

    df = pd.read_csv(PROCESSED_FEATURES_CSV)
    print(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")

    with open(FOLDS_DIR / "folds_temporal.json", "r", encoding="utf-8") as f:
        temporal_splits = json.load(f)["folds"]

    feature_cols = [
        c for c in df.select_dtypes(include=[np.number]).columns
        if c not in [TARGET_COL, "id", "latitude", "longitude"]
    ]

    models = get_baseline_models(random_state=SEED)
    results_records = []

    print(f"Evaluating {len(models)} model families on Temporal Cross-Validation...")

    for model_name, model in models.items():
        print(f"\n--> Training: {model_name}")
        t0 = time.time()

        for fold_key, fold_info in list(temporal_splits.items())[:3]:  # Evaluates initial folds
            train_idx = fold_info["train_indices"]
            val_idx = fold_info["val_indices"]

            train_df = df.iloc[train_idx]
            val_df = df.iloc[val_idx]

            # Leakage-free preprocessing fitted exclusively on train_df
            preprocessor = LeakageFreePreprocessor(scaler_type="standard")
            X_train = preprocessor.fit_transform(train_df[feature_cols])
            y_train = train_df[TARGET_COL].values

            X_val = preprocessor.transform(val_df[feature_cols])
            y_val = val_df[TARGET_COL].values

            model.fit(X_train, y_train)
            preds = model.predict(X_val)

            metrics = compute_metrics(y_val, preds)
            results_records.append({
                "model_id": model_name.lower(),
                "model_group": model_name.split("_")[0],
                "model_family": model_name.split("_")[1],
                "dataset_split": "validation",
                "cv_scheme": "temporal",
                "cv_purpose": "selection",
                "cv_repetition": 0,
                "cv_fold": int(fold_key.split("_")[1]),
                "niveau": "fold",
                "metric": "rmse",
                "is_primary": True,
                "value": metrics["rmse"],
                "std": 0.0,
                "ci_lower": metrics["rmse"],
                "ci_upper": metrics["rmse"],
            })

        elapsed = round(time.time() - t0, 2)
        print(f"    Completed in {elapsed}s")

    df_res = pd.DataFrame(results_records)
    out_path = RESULTS_DIR / "results.csv"
    df_res.to_csv(out_path, index=False)
    print(f"\nTraining execution finished. Saved results to: {out_path}")


if __name__ == "__main__":
    run_training_pipeline()

