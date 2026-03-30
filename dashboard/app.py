import streamlit as st
import requests
from streamlit_folium import st_folium
import sys
import os

sys.path.append(os.path.abspath("../src"))
from spatial_pipeline import generate_heatmap


# ---------------- CONFIG ----------------
st.set_page_config(page_title="Ride Demand", layout="wide")
st.title("🚕 Smart Ride Demand Dashboard")


# ---------------- LOAD LOCATIONS ----------------
@st.cache_data
def load_locations():
    try:
        res = requests.get("http://127.0.0.1:5000/locations")
        return res.json()
    except:
        return []

locations = load_locations()

# ---------------- INPUT ----------------
st.sidebar.header("⚙️ Inputs")

hour = st.sidebar.slider("Hour", 0, 23, 10)
day = st.sidebar.selectbox("Day",
    ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
)

# 🔥 Create dropdown with names
location_dict = {
    f"{loc['location_name']} ({loc['latitude']}, {loc['longitude']})": loc['location_id']
    for loc in locations
}

selected_label = st.sidebar.selectbox("📍 Select Location", list(location_dict.keys()))
selected_location_id = location_dict[selected_label]


# ---------------- API ----------------
def get_prediction(hour, day, location_id):
    try:
        res = requests.post(
            "http://127.0.0.1:5000/predict",
            json={
                "hour": hour,
                "day": day,
                "location_id": location_id
            }
        )
        return res.json()
    except:
        return None


# ---------------- PREDICTION ----------------
st.subheader("📊 Prediction")

if "result" not in st.session_state:
    st.session_state.result = None

if st.button("🚀 Predict"):
    st.session_state.result = get_prediction(hour, day, selected_location_id)

result = st.session_state.result

if result:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📍 Location", result["location"])

    with col2:
        st.metric("🔮 Demand", round(result["predicted_demand"], 2))

    with col3:
        level = result["demand_level"]

        if level == "High":
            st.error(f"🔥 {level} Demand")
        elif level == "Moderate":
            st.warning(f"⚠️ {level} Demand")
        else:
            st.success(f"✅ {level} Demand")

else:
    st.info("Click Predict")


# ---------------- MAP ----------------
st.subheader("🗺️ Heatmap")

try:
    map_obj = generate_heatmap(hour=hour)
    st_folium(map_obj, width=1000, height=500)
except:
    st.warning("Map not available")