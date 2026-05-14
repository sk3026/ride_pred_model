import pandas as pd
import numpy as np
import joblib
import os

# ---------------- PATHS ----------------
_THIS_FILE = os.path.abspath(__file__)

_SRC_DIR = os.path.dirname(_THIS_FILE)

BASE_DIR = os.path.dirname(_SRC_DIR)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

# ---------------- CONSTANTS ----------------
PEAK_HOURS = {
    8, 9, 17, 18, 19
}

WEEKEND_DAYS = {
    "Saturday",
    "Sunday"
}

# ---------------- LOAD MODELS ----------------
print(
    "\nLoading models from:",
    MODEL_DIR
)

model = joblib.load(
    os.path.join(
        MODEL_DIR,
        "demand_model.pkl"
    )
)

columns = joblib.load(
    os.path.join(
        MODEL_DIR,
        "model_columns.pkl"
    )
)

print(
    "\nModels loaded successfully"
)

print(
    "\nZone Columns:\n"
)

for col in columns:

    if "zone_" in col:

        print(col)


# ---------------- PREDICTION FUNCTION ----------------
def predict_demand(
    zone,
    hour=10,
    day="Monday"
):

    print("\n--------------------------------")

    print(
        f"Predict Request -> "
        f"Zone={zone}, "
        f"Hour={hour}, "
        f"Day={day}"
    )

    # ---------------- CREATE INPUT ----------------
    input_df = pd.DataFrame(
        0,
        index=[0],
        columns=columns
    )

    # ---------------- BASIC FEATURES ----------------
    input_df.loc[0, "hour"] = hour

    input_df.loc[0, "is_weekend"] = int(
        day in WEEKEND_DAYS
    )

    input_df.loc[0, "is_peak"] = int(
        hour in PEAK_HOURS
    )

    # ---------------- DAY ENCODING ----------------
    day_col = f"day_{day}"

    print(
        "Using day column:",
        day_col
    )

    print(
        "Day column exists:",
        day_col in input_df.columns
    )

    if day_col in input_df.columns:

        input_df.loc[0, day_col] = 1

    # ---------------- ZONE ENCODING ----------------
    zone_col = f"zone_{zone}"

    print(
        "Using zone column:",
        zone_col
    )

    print(
        "Zone column exists:",
        zone_col in input_df.columns
    )

    if zone_col in input_df.columns:

        input_df.loc[0, zone_col] = 1

    # ---------------- RAW MODEL PREDICTION ----------------
    pred_log = model.predict(
        input_df
    )[0]

    print(
        "Raw pred_log:",
        pred_log
    )

    # ---------------- SAFETY FIX ----------------
    pred_log = max(
        0,
        pred_log
    )

    print(
        "Clamped pred_log:",
        pred_log
    )

    # ---------------- INVERSE TRANSFORM ----------------
    prediction = float(
        np.expm1(pred_log)
    )

    print(
        "Prediction after expm1:",
        prediction
    )

    # ---------------- FINAL SAFETY ----------------
    prediction = max(
        0.0,
        prediction
    )

    print(
        "Final prediction:",
        prediction
    )

    return round(
        prediction,
        2
    )


# ---------------- TEST ----------------
if __name__ == "__main__":

    print("\nSample Predictions:\n")

    for z in range(20):

        print(
            f"Zone {z} ->",
            predict_demand(
                z,
                13,
                "Monday"
            )
        )