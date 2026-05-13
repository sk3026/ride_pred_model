import folium
from folium.plugins import HeatMap
import pandas as pd
import os

from model_pipeline import predict_demand


def generate_heatmap(hour=10, selected_zone=None, day="Monday"):

    try:

        # ---------------- PATH ----------------
        BASE_DIR = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        data_path = os.path.join(
            BASE_DIR,
            "data",
            "processed",
            "zone_centers.csv"
        )

        # ---------------- LOAD DATA ----------------
        df = pd.read_csv(data_path)

        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
        )

        # ---------------- DEFAULT CENTER ----------------
        center_lat = df["lat"].mean()
        center_lon = df["lon"].mean()

        zoom = 11

        # ---------------- SELECTED ZONE CENTER ----------------
        if selected_zone is not None:

            selected = df[df["zone"] == selected_zone]

            if not selected.empty:

                selected_row = selected.iloc[0]

                center_lat = selected_row["lat"]
                center_lon = selected_row["lon"]

                zoom = 13

        # ---------------- CREATE MAP ----------------
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom
        )

        heat_data = []

        # ---------------- LOOP THROUGH ZONES ----------------
        for _, row in df.iterrows():

            lat = float(row["lat"])
            lon = float(row["lon"])

            zone = int(row["zone"])

            # ---------------- REAL MODEL PREDICTION ----------------
            predicted_demand = predict_demand(
                zone,
                hour,
                day
            )

            # Heatmap weight
            heat_data.append([
                lat,
                lon,
                predicted_demand
            ])

            # ---------------- HIGHLIGHT SELECTED ZONE ----------------
            if zone == selected_zone:

                color = "yellow"
                radius = 1200
                fill_color = "yellow"

            else:

                color = "red"
                radius = 800
                fill_color = "red"

            # ---------------- BOUNDARY CIRCLE ----------------
            folium.Circle(
                location=[lat, lon],
                radius=radius,
                color=color,
                fill=True,
                fill_color=fill_color,
                fill_opacity=0.15,
                weight=3,
                popup=f"""
                    <b>Zone:</b> {zone}<br>
                    <b>Predicted Demand:</b> {predicted_demand}<br>
                    <b>Hour:</b> {hour}:00<br>
                    <b>Day:</b> {day}
                """
            ).add_to(m)

            # ---------------- ZONE MARKER ----------------
            folium.Marker(
                location=[lat, lon],

                popup=f"""
                    <b>Zone:</b> {zone}<br>
                    <b>Demand:</b> {predicted_demand}
                """,

                icon=folium.DivIcon(
                    html=f"""
                        <div style="
                            background-color: blue;
                            color: white;
                            border-radius: 50%;
                            width: 30px;
                            height: 30px;
                            text-align: center;
                            line-height: 30px;
                            font-weight: bold;
                            border: 2px solid white;
                            box-shadow: 0 0 6px rgba(0,0,0,0.5);
                        ">
                            {zone}
                        </div>
                    """
                )
            ).add_to(m)

        # ---------------- HEATMAP ----------------
        HeatMap(
            heat_data,
            radius=25,
            blur=20,
            max_zoom=13
        ).add_to(m)

        return m

    except Exception as e:

        print(" Heatmap Error:", e)

        return folium.Map(
            location=[12.97, 77.59],
            zoom_start=10
        )