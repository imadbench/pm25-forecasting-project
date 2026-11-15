"""keep the simple cleaning and preprocessing steps for part 1."""

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler


def load_combined_data(path):
    """load the merged pm25 and gee table."""
    return pd.read_csv(path)


def clean_pm25_data(df):
    """remove invalid pm25 rows and exact duplicate rows."""
    missing_pm25 = df["pm25"].isna()
    invalid_low = df["pm25"].notna() & (df["pm25"] <= 0)
    invalid_high = df["pm25"].notna() & (df["pm25"] >= 500)
    cleaning_counts = pd.DataFrame({
        "reason": ["initial rows", "missing pm25", "pm25 <= 0", "pm25 >= 500"],
        "rows": [len(df), int(missing_pm25.sum()), int(invalid_low.sum()), int(invalid_high.sum())],
    })
    clean = df.loc[~(missing_pm25 | invalid_low | invalid_high)].copy()
    exact_duplicates = int(clean.duplicated().sum())
    clean = clean.drop_duplicates().copy()
    clean = clean.sort_values(["sensor_name", "date"]).reset_index(drop=True)
    extra = pd.DataFrame({
        "reason": ["exact duplicates after invalid-row removal", "final cleaned rows"],
        "rows": [exact_duplicates, len(clean)],
    })
    return clean, pd.concat([cleaning_counts, extra], ignore_index=True)


def make_audit_table(df, clean, cleaning_counts):
    """make the tidy audit table used in the data results file."""
    rows = []
    for column in df.columns:
        rows.append({"section": "audit", "variable": column, "metric": "missing_count", "value": float(df[column].isna().sum())})
        rows.append({"section": "audit", "variable": column, "metric": "missing_percentage", "value": float(100 * df[column].isna().mean())})
    for row in cleaning_counts.itertuples(index=False):
        rows.append({"section": "cleaning", "variable": "pm25", "metric": row.reason, "value": float(row.rows)})
    rows.append({"section": "audit", "variable": "dataset", "metric": "rows", "value": float(len(df))})
    rows.append({"section": "audit", "variable": "dataset", "metric": "columns", "value": float(df.shape[1])})
    rows.append({"section": "audit", "variable": "sensor_name", "metric": "unique_stations", "value": float(clean["sensor_name"].nunique())})
    rows.append({"section": "audit", "variable": "date", "metric": "unique_dates", "value": float(clean["date"].nunique())})
    return pd.DataFrame(rows)


def make_preprocessing_pipeline(feature_names):
    """make a training-fold-only median imputer and robust scaler."""
    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
        ("scaler", RobustScaler()),
    ])
    return ColumnTransformer([("numeric", numeric_transformer, feature_names)])
