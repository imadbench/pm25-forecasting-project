"""
Model Registry and Factory Module for PM2.5 Forecasting.
Contains model definitions across mandatory model families (Section 4.1 & 6.6).
Master 1 Mini Project | Academic Year 2026-2027
"""

from typing import Dict, Any
from sklearn.linear_model import Lasso, ElasticNet, HuberRegressor, Ridge
from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    AdaBoostRegressor,
    VotingRegressor,
    StackingRegressor,
)
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR

try:
    from src.config import SEED
except ImportError:
    from config import SEED


def get_baseline_models(random_state: int = SEED) -> Dict[str, Any]:
    """
    Returns initial model configurations specified in Section 6.6.
    """
    models = {
        # G1: Regularized Linear Regression
        "G1_Lasso": Lasso(alpha=1.0, fit_intercept=True, max_iter=1000, random_state=random_state),
        # G2: ElasticNet
        "G2_ElasticNet": ElasticNet(alpha=1.0, l1_ratio=0.5, max_iter=1000, random_state=random_state),
        # G3: Robust Regression
        "G3_Huber": HuberRegressor(epsilon=1.35, alpha=0.0001, max_iter=200),
        # G4: Instance-Based
        "G4_KNN": KNeighborsRegressor(n_neighbors=5, weights="distance", p=2),
        # G5: Support Vector Regression
        "G5_SVR_RBF": SVR(kernel="rbf", C=1.0, gamma="scale", epsilon=0.1),
        "G5_SVR_Linear": SVR(kernel="linear", C=1.0, epsilon=0.1),
        # G6: Extra Trees
        "G6_ExtraTrees": ExtraTreesRegressor(n_estimators=100, max_depth=20, random_state=random_state, n_jobs=-1),
        # G7: Gradient Boosting
        "G7_GradientBoosting": GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=random_state),
        # G26: AdaBoost
        "G26_AdaBoost": AdaBoostRegressor(n_estimators=50, learning_rate=0.1, random_state=random_state),
    }
    return models


# Hyperparameter search spaces (Section 6.5)
SEARCH_SPACES = {
    "G1_Lasso": {
        "alpha": [0.001, 0.01, 0.1, 1.0, 10.0],
        "fit_intercept": [True, False],
    },
    "G2_ElasticNet": {
        "alpha": [0.001, 0.01, 0.1, 1.0, 10.0],
        "l1_ratio": [0.1, 0.3, 0.5, 0.7, 0.9],
    },
    "G3_Huber": {
        "epsilon": [1.1, 1.35, 1.5, 2.0],
        "alpha": [1e-5, 1e-4, 1e-3, 1e-2],
    },
    "G4_KNN": {
        "n_neighbors": [3, 5, 7, 10, 15, 20],
        "weights": ["uniform", "distance"],
        "p": [1, 2],
    },
    "G5_SVR": {
        "kernel": ["rbf", "linear"],
        "C": [0.1, 1.0, 10.0, 100.0],
        "epsilon": [0.01, 0.1, 0.5, 1.0],
    },
}

