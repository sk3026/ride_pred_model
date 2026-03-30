import pandas as pd
import numpy as np
import joblib
import os

# Base path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Load model + columns
model = joblib.load(os.path.join(BASE_DIR, "models/demand_model.pkl"))
columns = joblib.load(os.path.join(BASE_DIR, "models/model_columns.pkl"))


def predict_demand(hour, day):
    input_data = {
        "hour": hour,
        "day": day
    }

    df = pd.DataFrame([input_data])

    df = pd.get_dummies(df)
    df = df.reindex(columns=columns, fill_value=0)

    pred_log = model.predict(df)[0]

    # convert log → actual
    pred_actual = np.expm1(pred_log)

    return float(pred_actual)