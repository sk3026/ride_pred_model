from flask import Flask, request, jsonify
import pandas as pd
import os

# 🔥 TEMP: comment model import for deployment stability
# from model_pipeline import predict_demand

app = Flask(__name__)

# ---------------- LOAD DATA ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
zone_path = os.path.join(BASE_DIR, "data", "processed", "zone_centers.csv")

zone_df = None

def load_zones():
    try:
        print("📂 Loading zones from:", zone_path)
        df = pd.read_csv(zone_path)
        df.columns = df.columns.str.strip().str.lower()
        print("✅ Zones loaded:", len(df))
        return df
    except Exception as e:
        print("❌ CSV load failed:", e)

        # 🔥 fallback data (prevents crash)
        print("⚠️ Using fallback sample data")
        return pd.DataFrame({
            "zone": [1, 2, 3],
            "lat": [28.6, 28.7, 28.8],
            "lon": [77.2, 77.3, 77.4]
        })

def get_zone_df():
    global zone_df
    if zone_df is None:
        zone_df = load_zones()
    return zone_df


# ---------------- DEMAND LEVEL ----------------
def get_demand_level(value):
    if value < 40:
        return "Low"
    elif value < 45:
        return "Moderate"
    else:
        return "High"


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return "API Running 🚀"


@app.route("/locations")
def get_locations():
    zone_df = get_zone_df()
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

        hour = int(data.get("hour", 0))
        day = int(data.get("day", 0))
        zone_id = int(data.get("location_id", 1))

        zone_df = get_zone_df()

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

        # 🔥 TEMP DUMMY PREDICTION (fast + safe)
        prediction = 100 + (hour * 5) + (day * 3)

        # 🔥 When stable, replace with:
        # prediction = predict_demand(hour, day, lat, lon)

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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)