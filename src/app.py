from flask import Flask, request, jsonify
import pandas as pd
import os

# Import model prediction function
from model_pipeline import predict_demand

app = Flask(__name__)

# ---------------- LOAD DATA ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
zone_path = os.path.join(BASE_DIR, "data", "processed", "zone_centers.csv")

zone_df = None

# Map day name → integer (matches frontend's selectbox order)
DAY_NAME_TO_INT = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}


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
# Thresholds tuned to the dummy formula:
#   prediction = 100 + (hour * 5) + (day_int * 3)
#   range ≈ 100 – 100 + (23*5) + (6*3) = 100 – 233
def get_demand_level(value: float) -> str:
    if value < 140:
        return "Low"
    elif value < 180:
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

        # ── Day: accept both string ("Monday") and integer (0) ──
        raw_day = data.get("day", 0)
        if isinstance(raw_day, str):
            day_int = DAY_NAME_TO_INT.get(raw_day.strip().capitalize(), 0)
        else:
            day_int = int(raw_day)

        df = get_zone_df()

        # ── Zone lookup ──
        loc = df[df["zone"] == zone_id]
        if not loc.empty:
            row  = loc.iloc[0]
            lat  = float(row["lat"])
            lon  = float(row["lon"])
            name = f"Zone {zone_id}"
        else:
            lat, lon = 20.0, 78.0
            name = "Unknown"

        # ── Dummy prediction (replace with real model when ready) ──
        prediction = 100 + (hour * 5) + (day_int * 3)
        # prediction = predict_demand(hour, day_int, lat, lon)

        level = get_demand_level(prediction)

        return jsonify({
            "predicted_demand": float(prediction),
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