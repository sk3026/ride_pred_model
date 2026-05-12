import pandas as pd
import numpy as np
import joblib
import os

# ---------------- CORRECT BASE PATH ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model_path = os.path.join(BASE_DIR, "models", "demand_model.pkl")
columns_path = os.path.join(BASE_DIR, "models", "model_columns.pkl")
kmeans_path = os.path.join(BASE_DIR, "models", "kmeans.pkl")

print("📦 Loading model from:", model_path)

# ---------------- LOAD ----------------
model = joblib.load(model_path)
columns = joblib.load(columns_path)
kmeans = joblib.load(kmeans_path)


def predict_demand(hour, day, lat, lon):

    zone = kmeans.predict(
        pd.DataFrame([[lat, lon]], columns=['lat', 'lon'])
    )[0]

    df = pd.DataFrame([{
        "hour": hour,
        "is_weekend": 1 if day in ['Saturday', 'Sunday'] else 0,
        "is_peak": 1 if hour in [8, 9, 17, 18, 19] else 0,
    }])

    # ✅ FIX: manually encode day and zone instead of pd.get_dummies
    for col in columns:
        if col.startswith("day_"):
            df[col] = 1 if col == f"day_{day}" else 0
        if col.startswith("zone_"):
            df[col] = 1 if col == f"zone_{zone}" else 0

    df = df.reindex(columns=columns, fill_value=0)

    pred_log = model.predict(df)[0]

    return float(np.expm1(pred_log))