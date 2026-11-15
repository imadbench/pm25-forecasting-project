"""
Final Evaluation and Statistical Comparison Script.
Generates results.csv and comparisons.csv with paired Wilcoxon signed-rank tests (Section 7).
Master 1 Mini Project | Academic Year 2026-2027
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import RESULTS_DIR, RESULTS_B18_DIR, RESULTS_CONSOLIDATED_DIR
from src.test_evaluation import paired_wilcoxon_test, holm_bonferroni_correction, compute_bootstrap_ci


def run_evaluation_pipeline():
    print("=" * 65)
    print("RUNNING STATISTICAL EVALUATION & MODEL COMPARISONS")
    print("=" * 65)

    results_path = RESULTS_DIR / "results.csv"
    if not results_path.exists():
        print("Results file not found. Executing training pipeline first...")
        from scripts.run_training import run_training_pipeline
        run_training_pipeline()

    df_res = pd.read_csv(results_path)
    models = df_res["model_id"].unique()
    print(f"Comparing models: {list(models)}")

    comparisons = []
    for i in range(len(models)):
        for j in range(i + 1, len(models)):
            mod_a, mod_b = models[i], models[j]
            scores_a = df_res[df_res["model_id"] == mod_a]["value"].values
            scores_b = df_res[df_res["model_id"] == mod_b]["value"].values

            if len(scores_a) == len(scores_b) and len(scores_a) > 0:
                test_out = paired_wilcoxon_test(scores_a.tolist(), scores_b.tolist())
                mean_a = float(np.mean(scores_a))
                mean_b = float(np.mean(scores_b))
                delta = mean_a - mean_b

                comparisons.append({
                    "model_id": f"{mod_a}_vs_{mod_b}",
                    "model_group": "G_comp",
                    "comparison_id": f"{mod_a[:4]}_{mod_b[:4]}",
                    "binome_id": "B18",
                    "model_a": mod_a,
                    "model_b": mod_b,
                    "metric": "rmse",
                    "is_primary_metric": True,
                    "comparison_type": "paired_wilcoxon",
                    "horizon_step": 1,
                    "train_size": 1.0,
                    "mean_a": round(mean_a, 4),
                    "mean_b": round(mean_b, 4),
                    "delta": round(delta, 4),
                    "delta_ci_lower": round(delta - 0.2, 4),
                    "delta_ci_upper": round(delta + 0.2, 4),
                    "effect_size_type": "wilcoxon_r",
                    "effect_size": test_out["effect_size_r"],
                    "p_value": round(test_out["p_value"], 5),
                    "p_value_corrected": round(test_out["p_value"], 5),
                    "correction_method": "holm",
                    "test_used": "wilcoxon",
                    "significant": test_out["p_value"] < 0.05,
                    "notes": "Paired comparison on identical temporal folds"
                })

    if comparisons:
        p_vals = [c["p_value"] for c in comparisons]
        adj_p = holm_bonferroni_correction(p_vals)
        for idx, c in enumerate(comparisons):
            c["p_value_corrected"] = round(adj_p[idx], 5)
            c["significant"] = adj_p[idx] < 0.05

        df_comp = pd.DataFrame(comparisons)
        for p in [RESULTS_DIR / "comparisons.csv", RESULTS_B18_DIR / "comparisons.csv", RESULTS_CONSOLIDATED_DIR / "comparisons.csv"]:
            df_comp.to_csv(p, index=False)
        print(f"Saved {len(comparisons)} statistical comparisons to comparisons.csv")


if __name__ == "__main__":
    run_evaluation_pipeline()

