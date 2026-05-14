import pandas as pd
import numpy as np
import joblib
import os

_THIS_FILE = os.path.abspath(__file__)
_SRC_DIR   = os.path.dirname(_THIS_FILE)
BASE_DIR   = os.path.dirname(_SRC_DIR)
MODEL_DIR  = os.path.join(BASE_DIR, "models")

PEAK_HOURS   = {8, 9, 17, 18, 19}
WEEKEND_DAYS = {"Saturday", "Sunday"}


def predict_demand(zone, hour=10, day="Monday"):

    model   = joblib.load(os.path.join(MODEL_DIR, "demand_model.pkl"))
    columns = joblib.load(os.path.join(MODEL_DIR, "model_columns.pkl"))

    input_df = pd.DataFrame(0, index=[0], columns=columns)
    input_df.loc[0, 'hour']       = hour
    input_df.loc[0, 'is_weekend'] = int(day in WEEKEND_DAYS)
    input_df.loc[0, 'is_peak']    = int(hour in PEAK_HOURS)

    day_col = f"day_{day}"
    if day_col in input_df.columns:
        input_df.loc[0, day_col] = 1

    zone_col = f"zone_{zone}"
    if zone_col in input_df.columns:
        input_df.loc[0, zone_col] = 1

    pred_log   = model.predict(input_df)[0]
    prediction = max(0.0, float(np.expm1(pred_log)))

    return round(prediction, 2)