import pandas as pd
import numpy as np
import joblib
import os

# ---------------- BASE PATH ----------------
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

model_path = os.path.join(
    BASE_DIR,
    "models",
    "demand_model.pkl"
)

columns_path = os.path.join(
    BASE_DIR,
    "models",
    "model_columns.pkl"
)

kmeans_path = os.path.join(
    BASE_DIR,
    "models",
    "kmeans.pkl"
)

print(" Loading model from:", model_path)

# ---------------- LOAD MODELS ----------------
model = joblib.load(model_path)

columns = joblib.load(columns_path)

kmeans = joblib.load(kmeans_path)

print(" Model loaded successfully")


# ---------------- PREDICTION FUNCTION ----------------
def predict_demand(zone, hour=10, day="Monday"):

    # Validate zone
    max_zone = len(kmeans.cluster_centers_) - 1

    if zone < 0 or zone > max_zone:
        raise ValueError(
            f"Zone must be between 0 and {max_zone}"
        )

    # ---------------- CREATE INPUT ----------------
    input_df = pd.DataFrame(
        0,
        index=[0],
        columns=columns
    )

    # Basic features
    input_df.loc[0, 'hour'] = hour

    input_df.loc[0, 'is_weekend'] = int(
        day in ['Saturday', 'Sunday']
    )

    input_df.loc[0, 'is_peak'] = int(
        hour in [8, 9, 17, 18, 19]
    )

    # ---------------- DAY ENCODING ----------------
    day_col = f"day_{day}"

    if day_col in input_df.columns:
        input_df.loc[0, day_col] = 1

    # ---------------- ZONE ENCODING ----------------
    zone_col = f"zone_{zone}"

    if zone_col in input_df.columns:
        input_df.loc[0, zone_col] = 1

    # ---------------- PREDICT ----------------
    pred_log = model.predict(input_df)[0]

    prediction = np.expm1(pred_log)

    return round(float(prediction), 2)


# ---------------- TEST ----------------
if __name__ == "__main__":

    print("\n Sample Predictions:\n")

    print("Zone 1  →",
          predict_demand(1, 10, "Monday"))

    print("Zone 5  →",
          predict_demand(5, 18, "Friday"))

    print("Zone 10 →",
          predict_demand(10, 9, "Saturday"))