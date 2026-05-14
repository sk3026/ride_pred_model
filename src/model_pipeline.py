import pandas as pd
import numpy as np
import joblib
import os

# ---------------- BASE PATH ----------------
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_DIR = os.path.join(BASE_DIR, "models")

PEAK_HOURS   = {8, 9, 17, 18, 19}
WEEKEND_DAYS = {"Saturday", "Sunday"}


# ---------------- PREDICTION FUNCTION ----------------
def predict_demand(zone, hour=10, day="Monday"):

    # reload fresh from disk every call — fixes Render caching issue
    model   = joblib.load(os.path.join(MODEL_DIR, "demand_model.pkl"))
    columns = joblib.load(os.path.join(MODEL_DIR, "model_columns.pkl"))

    # ---------------- CREATE INPUT ----------------
    input_df = pd.DataFrame(
        0,
        index=[0],
        columns=columns
    )

    input_df.loc[0, 'hour']       = hour
    input_df.loc[0, 'is_weekend'] = int(day in WEEKEND_DAYS)
    input_df.loc[0, 'is_peak']    = int(hour in PEAK_HOURS)

    # ---------------- DAY ENCODING ----------------
    day_col = f"day_{day}"
    if day_col in input_df.columns:
        input_df.loc[0, day_col] = 1

    # ---------------- ZONE ENCODING ----------------
    zone_col = f"zone_{zone}"
    if zone_col in input_df.columns:
        input_df.loc[0, zone_col] = 1

    # ---------------- PREDICT ----------------
    pred_log   = model.predict(input_df)[0]
    prediction = max(0.0, float(np.expm1(pred_log)))

    return round(prediction, 2)


# ---------------- TEST ----------------
if __name__ == "__main__":

    print("\n Sample Predictions:\n")
    print("Zone 1  →", predict_demand(1,  10, "Monday"))
    print("Zone 5  →", predict_demand(5,  18, "Friday"))
    print("Zone 10 →", predict_demand(10,  9, "Saturday"))