"""
Configuration module for PM2.5 forecasting project.
Contains directory paths, seeds, and dataset constants.
Master 1 Mini Project | Academic Year 2026-2027
"""

import os
from pathlib import Path

# Fix random seed across all stochastic steps (Section 6.1)
SEED = 42
RANDOM_STATE = 42

# Root & Subdirectory Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
FOLDS_DIR = PROJECT_ROOT / "folds"
RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_B18_DIR = RESULTS_DIR / "B18"
RESULTS_CONSOLIDATED_DIR = RESULTS_DIR / "consolidated"
FIGURES_DIR = PROJECT_ROOT / "figures"
REPORTS_DIR = PROJECT_ROOT / "reports"
PRESENTATION_DIR = PROJECT_ROOT / "presentation"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Default Raw Data Filenames
RAW_CSV_NAME = "combined_gee_pm25.csv"
RAW_CSV_PATH = DATA_RAW_DIR / RAW_CSV_NAME
PROCESSED_CLEANED_CSV = DATA_PROCESSED_DIR / "data_cleaned.csv"
PROCESSED_FEATURES_CSV = DATA_PROCESSED_DIR / "data_features.csv"

# Column Metadata
TARGET_COL = "pm25"
STATION_COL = "sensor_name"
GRID_ID_COL = "id"
DATE_COL = "date"
DATETIME_COL = "datetime_utc"
LAT_COL = "latitude"
LON_COL = "longitude"

METEO_COLS = ["temperature_celsius", "pressure_mb", "wind_u", "wind_v"]
SATELLITE_GAS_COLS = ["NO2", "CO", "O3"]
AOD_COLS = ["AOD"]
BASE_NUMERICAL_COLS = [TARGET_COL] + METEO_COLS + SATELLITE_GAS_COLS + AOD_COLS

# Thresholds (§5.1)
PM25_MIN_VALID = 0.0  # PM2.5 <= 0 is invalid sentinel
PM25_MAX_VALID = 500.0  # PM2.5 >= 500 is invalid sentinel
PM25_MODERATE_THRESH = 25.0
PM25_EXTREME_THRESH = 50.0

# Cross-Validation Configuration (§5.4)
N_SPLITS = 5
TEMPORAL_GAP_DAYS = 1

