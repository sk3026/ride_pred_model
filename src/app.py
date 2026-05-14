import os

from flask import Flask, request, jsonify
import pandas as pd

from src.model_pipeline import predict_demand

app = Flask(__name__)

# ---------------- LOAD ZONE DATA ----------------
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

zone_path = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "zone_centers.csv"
)

zone_df = None

# ---------------- DAY MAPPINGS ----------------
DAY_INT_TO_NAME = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}

DAY_NAME_TO_INT = {
    v: k for k, v in DAY_INT_TO_NAME.items()
}


# ---------------- LOAD ZONES ----------------
def load_zones():

    try:

        print("Loading zones from:", zone_path)

        df = pd.read_csv(zone_path)

        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
        )

        print("Zones loaded:", len(df))

        return df

    except Exception as e:

        print("CSV load failed:", e)

        print(" Using fallback sample data")

        return pd.DataFrame({
            "zone": [1, 2, 3],
            "lat": [12.97, 12.98, 13.00],
            "lon": [77.59, 77.60, 77.61],
        })


def get_zone_df():

    global zone_df

    if zone_df is None:
        zone_df = load_zones()

    return zone_df


# ---------------- DEMAND LEVEL ----------------
def get_demand_level(value: float) -> str:

    if value < 10:
        return "Low"

    elif value < 25:
        return "Moderate"

    else:
        return "High"


# ---------------- HOME ----------------
@app.route("/")
def home():

    return "RidePulse API Running "


# ---------------- LOCATIONS ----------------
@app.route("/locations")
def get_locations():

    df = get_zone_df()

    data = []

    for _, row in df.iterrows():

        data.append({

            "location_id": int(row["zone"]),

            "location_name": f"Zone {int(row['zone'])}",

            "latitude": float(row["lat"]),

            "longitude": float(row["lon"]),
        })

    return jsonify(data)


# ---------------- PREDICT ----------------
@app.route("/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json(force=True)

        # ---------------- INPUTS ----------------
        hour = int(data.get("hour", 0))

        zone_id = int(data.get("location_id", 1))

        # ---------------- DAY ----------------
        raw_day = data.get("day", 0)

        if isinstance(raw_day, str):

            day_name = raw_day.strip().capitalize()

            if day_name not in DAY_NAME_TO_INT:

                return jsonify({
                    "error": f"Invalid day name: '{day_name}'"
                }), 400

        else:

            day_name = DAY_INT_TO_NAME.get(
                int(raw_day),
                "Monday"
            )

        # ---------------- ZONE LOOKUP ----------------
        df = get_zone_df()

        loc = df[df["zone"] == zone_id]

        if not loc.empty:

            row = loc.iloc[0]

            lat = float(row["lat"])

            lon = float(row["lon"])

            location_name = f"Zone {zone_id}"

        else:

            lat = 0.0

            lon = 0.0

            location_name = f"Zone {zone_id}"

        # ---------------- MODEL PREDICTION ----------------
        prediction = predict_demand(
            zone_id,
            hour,
            day_name
        )

        # ---------------- DEMAND LEVEL ----------------
        level = get_demand_level(prediction)

        # ---------------- RESPONSE ----------------
        return jsonify({

            "predicted_demand": round(prediction, 2),

            "demand_level": level,

            "location": location_name,

            "lat": lat,

            "lon": lon,

            "hour": hour,

            "day": day_name,

            "zone": zone_id
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ---------------- RUN ----------------
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )