import sys
import os

# Ensure src/ is on the path so model_pipeline can be imported
# regardless of how gunicorn launches the app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
import pandas as pd

from model_pipeline import predict_demand

app = Flask(__name__)

# ---------------- LOAD ZONE DATA ----------------
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
zone_path = os.path.join(BASE_DIR, "data", "processed", "zone_centers.csv")

zone_df = None

# Day name → integer mapping (used to accept int OR string from frontend)
DAY_INT_TO_NAME = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}

DAY_NAME_TO_INT = {v: k for k, v in DAY_INT_TO_NAME.items()}


def load_zones():
    try:
        print("📂 Loading zones from:", zone_path)
        df = pd.read_csv(zone_path)
        df.columns = df.columns.str.strip().str.lower()
        print("✅ Zones loaded:", len(df))
        return df
    except Exception as e:
        print("❌ CSV load failed:", e)
        print("⚠️  Using fallback sample data")
        return pd.DataFrame({
            "zone": [1, 2, 3],
            "lat":  [28.6, 28.7, 28.8],
            "lon":  [77.2, 77.3, 77.4],
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


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return "API Running 🚀"


@app.route("/locations")
def get_locations():
    df = get_zone_df()
    data = [
        {
            "location_id":   int(row["zone"]),
            "location_name": f"Zone {int(row['zone'])}",
            "latitude":      float(row["lat"]),
            "longitude":     float(row["lon"]),
        }
        for _, row in df.iterrows()
    ]
    return jsonify(data)


# ---------------- PREDICT ----------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)

        hour    = int(data.get("hour", 0))
        zone_id = int(data.get("location_id", 1))

        # Accept day as string ("Monday") or integer (0) from frontend
        raw_day = data.get("day", 0)
        if isinstance(raw_day, str):
            day_name = raw_day.strip().capitalize()
            # Validate
            if day_name not in DAY_NAME_TO_INT:
                return jsonify({"error": f"Invalid day name: '{day_name}'"}), 400
        else:
            day_name = DAY_INT_TO_NAME.get(int(raw_day), "Monday")

        # Zone lookup
        df  = get_zone_df()
        loc = df[df["zone"] == zone_id]

        if not loc.empty:
            row  = loc.iloc[0]
            lat  = float(row["lat"])
            lon  = float(row["lon"])
            name = f"Zone {zone_id}"
        else:
            lat, lon = 20.0, 78.0
            name = "Unknown"

        # Real model prediction (day passed as string name)
        prediction = predict_demand(hour, day_name, lat, lon)

        level = get_demand_level(prediction)

        return jsonify({
            "predicted_demand": round(prediction, 2),
            "demand_level":     level,
            "location":         name,
            "lat":              lat,
            "lon":              lon,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)