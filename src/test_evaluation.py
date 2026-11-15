"""
Evaluation and Statistical Testing Module for PM2.5 Forecasting.
Computes RMSE, MAE, R2, MAPE, SMAPE, bootstrap 95% confidence intervals,
paired Wilcoxon signed-rank tests, and Holm-Bonferroni adjustments (Section 6.3 & 7.3).
Master 1 Mini Project | Academic Year 2026-2027
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from scipy import stats
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

try:
    from src.config import SEED
except ImportError:
    from config import SEED


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Computes standard regression metrics (Section 6.3).
    Includes handling of near-zero values for percentage metrics.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))

    # MAPE with epsilon to avoid division by zero
    nonzero_mask = np.abs(y_true) > 0.5
    if np.sum(nonzero_mask) > 0:
        mape = float(np.mean(np.abs((y_true[nonzero_mask] - y_pred[nonzero_mask]) / y_true[nonzero_mask])) * 100.0)
    else:
        mape = float("nan")

    # Symmetric MAPE (SMAPE)
    denom = (np.abs(y_true) + np.abs(y_pred)) / 2.0
    valid_denom = denom > 1e-4
    if np.sum(valid_denom) > 0:
        smape = float(np.mean(np.abs(y_pred[valid_denom] - y_true[valid_denom]) / denom[valid_denom]) * 100.0)
    else:
        smape = float("nan")

    return {
        "rmse": round(rmse, 4),
        "mae": round(mae, 4),
        "r2": round(r2, 4),
        "mape": round(mape, 2) if not np.isnan(mape) else None,
        "smape": round(smape, 2) if not np.isnan(smape) else None,
    }


def compute_bootstrap_ci(
    values: List[float],
    n_bootstrap: int = 2000,
    ci: float = 0.95,
    random_state: int = SEED,
) -> Tuple[float, float]:
    """Computes 95% bootstrap confidence interval for mean metric (Section 6.3)."""
    rng = np.random.default_rng(random_state)
    val_arr = np.array(values)
    if len(val_arr) <= 1:
        return float(val_arr[0]), float(val_arr[0])

    boot_means = []
    for _ in range(n_bootstrap):
        sample = rng.choice(val_arr, size=len(val_arr), replace=True)
        boot_means.append(np.mean(sample))

    alpha = (1.0 - ci) / 2.0
    lower = float(np.percentile(boot_means, alpha * 100.0))
    upper = float(np.percentile(boot_means, (1.0 - alpha) * 100.0))
    return round(lower, 4), round(upper, 4)


def paired_wilcoxon_test(
    errors_model_a: List[float],
    errors_model_b: List[float],
) -> Dict[str, Any]:
    """
    Primary statistical comparison: paired Wilcoxon signed-rank test on fold-level errors (Section 7.3).
    Reports p-value and Wilcoxon effect size r = Z / sqrt(N).
    """
    diffs = np.array(errors_model_a) - np.array(errors_model_b)
    if np.all(diffs == 0):
        return {"stat": 0.0, "p_value": 1.0, "effect_size_r": 0.0}

    res = stats.wilcoxon(diffs, zero_method="wilcox", correction=True)
    n = len(diffs)
    # Approximate Z-statistic
    z_stat = stats.norm.ppf(res.pvalue / 2.0) if res.pvalue > 0 else -3.0
    effect_r = abs(z_stat) / np.sqrt(n)

    return {
        "stat": float(res.statistic),
        "p_value": float(res.pvalue),
        "effect_size_r": round(float(effect_r), 4),
    }


def holm_bonferroni_correction(p_values: List[float]) -> List[float]:
    """Corrects p-values for multiple hypothesis testing using Holm-Bonferroni method (Section 7.3)."""
    m = len(p_values)
    sorted_indices = np.argsort(p_values)
    sorted_p = np.array(p_values)[sorted_indices]

    corrected = np.empty(m)
    current_max = 0.0
    for k, p in enumerate(sorted_p):
        adjusted = p * (m - k)
        current_max = max(current_max, adjusted)
        corrected[sorted_indices[k]] = min(current_max, 1.0)

    return corrected.tolist()

