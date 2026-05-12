import pandas as pd
import numpy as np
import joblib
import os

# ---------------- BASE PATH ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model_path   = os.path.join(BASE_DIR, "models", "demand_model.pkl")
columns_path = os.path.join(BASE_DIR, "models", "model_columns.pkl")
kmeans_path  = os.path.join(BASE_DIR, "models", "kmeans.pkl")

print("📦 Loading model from:", model_path)

# ---------------- LOAD ----------------
model   = joblib.load(model_path)
columns = joblib.load(columns_path)
kmeans  = joblib.load(kmeans_path)


def predict_demand(hour: int, day: str, lat: float, lon: float) -> float:
    """
    Predict ride demand for a given hour, day name, and location.

    Parameters:
        hour : int   — 0 to 23
        day  : str   — Full day name e.g. "Monday", "Saturday"
        lat  : float — Latitude
        lon  : float — Longitude

    Returns:
        float — predicted demand (original scale, not log)
    """

    # Map lat/lon → zone (cast to str to match training column names like "zone_5")
    zone = str(kmeans.predict(
        pd.DataFrame([[lat, lon]], columns=['lat', 'lon'])
    )[0])

    # Base features
    df = pd.DataFrame([{
        "hour":       hour,
        "is_weekend": 1 if day in ['Saturday', 'Sunday'] else 0,
        "is_peak":    1 if hour in [8, 9, 17, 18, 19] else 0,
    }])

    # One-hot encode day and zone manually to match training columns
    for col in columns:
        if col.startswith("day_"):
            df[col] = 1 if col == f"day_{day}" else 0
        if col.startswith("zone_"):
            df[col] = 1 if col == f"zone_{zone}" else 0

    # Align columns exactly as during training
    df = df.reindex(columns=columns, fill_value=0)

    pred_log = model.predict(df)[0]

    return float(np.expm1(pred_log))