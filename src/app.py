from flask import Flask, request, jsonify
import pandas as pd
import os
from model_pipeline import predict_demand

app = Flask(__name__)

# ---------------- LOAD DATA ----------------
try:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    loc_path = os.path.join(BASE_DIR, "data", "processed", "locations.csv")
    location_df = pd.read_csv(loc_path)

    print("📍 Locations loaded:", len(location_df))

except Exception as e:
    print("❌ Error loading locations:", e)
    location_df = None


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
    if location_df is not None:
        return jsonify(location_df.to_dict(orient="records"))
    return jsonify([])


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        hour = data.get("hour")
        day = data.get("day")
        location_id = data.get("location_id")

        # 🔮 Prediction (currently no location feature in model)
        prediction = predict_demand(hour, day)

        level = get_demand_level(prediction)

        # 📍 Get location info
        loc = location_df[location_df['location_id'] == location_id]

        if not loc.empty:
            row = loc.iloc[0]
            location_name = row["location_name"]
            lat = float(row["latitude"])
            lon = float(row["longitude"])
        else:
            location_name = "Unknown"
            lat, lon = 20.0, 78.0

        return jsonify({
            "predicted_demand": float(prediction),
            "demand_level": level,
            "location": location_name,
            "lat": lat,
            "lon": lon
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)