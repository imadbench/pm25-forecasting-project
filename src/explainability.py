"""
Explainability and Feature Importance Stability Module.
Computes validation-fold permutation importance, Spearman rank correlation,
and Jaccard top-k similarity indices (Section 6.7).
Master 1 Mini Project | Academic Year 2026-2027
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Set, Any
from scipy import stats
from sklearn.inspection import permutation_importance

try:
    from src.config import SEED
except ImportError:
    from config import SEED


def compute_permutation_feature_importance(
    model: Any,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    n_repeats: int = 10,
    random_state: int = SEED,
) -> pd.DataFrame:
    """
    Computes permutation importance on held-out validation fold (Section 6.7.1).
    Mandatory explainability metric for all model families.
    """
    perm = permutation_importance(
        model,
        X_val,
        y_val,
        n_repeats=n_repeats,
        random_state=random_state,
        scoring="neg_root_mean_squared_error",
        n_jobs=-1,
    )

    df_importance = pd.DataFrame({
        "feature": X_val.columns,
        "importance_mean": perm.importances_mean,
        "importance_std": perm.importances_std,
    }).sort_values(by="importance_mean", ascending=False).reset_index(drop=True)

    df_importance["rank"] = df_importance.index + 1
    return df_importance


def compute_spearman_ranking_stability(
    ranks_a: List[int],
    ranks_b: List[int],
) -> float:
    """Computes Spearman rank correlation between two feature rankings."""
    rho, _ = stats.spearmanr(ranks_a, ranks_b)
    return float(rho)


def compute_jaccard_top_k(
    top_k_set_a: Set[str],
    top_k_set_b: Set[str],
) -> float:
    """Computes Jaccard similarity index between top-k feature sets."""
    intersection = len(top_k_set_a.intersection(top_k_set_b))
    union = len(top_k_set_a.union(top_k_set_b))
    return float(intersection / union) if union > 0 else 0.0


def evaluate_explanation_stability(
    rankings_by_fold: List[pd.DataFrame],
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    Evaluates stability across 5 folds against reference thresholds (Section 6.7.2):
    - Spearman rho > 0.8
    - Top-5 Jaccard overlap > 60% (0.60)
    """
    n_folds = len(rankings_by_fold)
    spearman_rhos = []
    jaccards = []

    for i in range(n_folds):
        for j in range(i + 1, n_folds):
            df_i = rankings_by_fold[i].sort_values("feature")
            df_j = rankings_by_fold[j].sort_values("feature")

            rho = compute_spearman_ranking_stability(df_i["rank"].tolist(), df_j["rank"].tolist())
            spearman_rhos.append(rho)

            top_i = set(rankings_by_fold[i].head(top_k)["feature"])
            top_j = set(rankings_by_fold[j].head(top_k)["feature"])
            jaccard = compute_jaccard_top_k(top_i, top_j)
            jaccards.append(jaccard)

    mean_rho = float(np.mean(spearman_rhos))
    mean_jaccard = float(np.mean(jaccards))

    return {
        "mean_spearman_rho": round(mean_rho, 4),
        "mean_top5_jaccard": round(mean_jaccard, 4),
        "rho_threshold_met": mean_rho > 0.8,
        "jaccard_threshold_met": mean_jaccard > 0.60,
    }

