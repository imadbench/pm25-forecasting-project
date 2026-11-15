"""store the project paths and the random seed."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = PROJECT_ROOT / "figures"
FOLDS_DIR = PROJECT_ROOT / "folds"
PRESENTATION_DIR = PROJECT_ROOT / "presentation"
SEED = 42
