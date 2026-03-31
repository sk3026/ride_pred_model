from flask import Flask, request, jsonify
import pandas as pd
import os
from model_pipeline import predict_demand


app = Flask(__name__)

# ---------------- LOAD DATA ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
zone_path = os.path.join(BASE_DIR, "data", "processed", "zone_centers.csv")

zone_df = pd.read_csv(zone_path)
zone_df.columns = zone_df.columns.str.strip().str.lower()

print("📍 Zones loaded:", len(zone_df))


# ---------------- DEMAND LEVEL ----------------
def get_demand_level(value):
    if value < 50:
        return "Low"
    elif value < 150:
        return "Moderate"
    else:
        return "High"


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return "API Running"


@app.route("/locations")
def get_locations():
    data = []

    for _, row in zone_df.iterrows():
        data.append({
            "location_id": int(row["zone"]),
            "location_name": f"Zone {int(row['zone'])}",
            "latitude": float(row["lat"]),
            "longitude": float(row["lon"])
        })

    return jsonify(data)


# ---------------- PREDICT ----------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        hour = data.get("hour")
        day = data.get("day")
        zone_id = int(data.get("location_id"))

        # ---------------- GET LAT/LON ----------------
        loc = zone_df[zone_df['zone'] == zone_id]

        if not loc.empty:
            row = loc.iloc[0]
            lat = float(row["lat"])
            lon = float(row["lon"])
            name = f"Zone {zone_id}"
        else:
            lat, lon = 20.0, 78.0
            name = "Unknown"

        # ---------------- ✅ FIXED ML CALL ----------------
        prediction = predict_demand(hour, day, lat, lon)

        # ---------------- DEMAND LEVEL ----------------
        level = get_demand_level(prediction)

        return jsonify({
            "predicted_demand": float(prediction),
            "demand_level": level,
            "location": name,
            "lat": lat,
            "lon": lon
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)