import streamlit as st
import requests

st.title("🚕 Ride Demand Prediction")

hour = st.slider("Select Hour", 0, 23, 10)

day = st.selectbox(
    "Select Day",
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
)

if st.button("Predict Demand"):
    input_data = {
        "hour": hour,
        "day": day
    }

    response = requests.post(
        "http://127.0.0.1:5000/predict",
        json=input_data
    )

    if response.status_code == 200:
        result = response.json()
        st.success(f"Predicted Demand: {round(result['predicted_demand'], 2)}")
    else:
        st.error("API Error")