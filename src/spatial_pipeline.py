import folium
from folium.plugins import HeatMap
import pandas as pd
import os


def generate_heatmap(hour=10, selected_zone=None):
    try:
        # ---------------- PATH ----------------
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(BASE_DIR, "data", "processed", "zone_centers.csv")

        df = pd.read_csv(data_path)
        df.columns = df.columns.str.strip().str.lower()

        # ---------------- AUTO CENTER ----------------
        if selected_zone is not None:
            selected_row = df[df["zone"] == selected_zone].iloc[0]
            center_lat = selected_row["lat"]
            center_lon = selected_row["lon"]
            zoom = 13
        else:
            center_lat, center_lon = 28.6, 77.2
            zoom = 10

        m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom)

        heat_data = []

        for _, row in df.iterrows():
            lat = row["lat"]
            lon = row["lon"]
            zone = int(row["zone"])

            # 🔥 heat weight (still dummy for now)
            weight = (lat * lon * (hour + 1)) % 100
            heat_data.append([lat, lon, weight])

            # ---------------- HIGHLIGHT SELECTED ZONE ----------------
            if zone == selected_zone:
                color = "yellow"
                radius = 1200
            else:
                color = "red"
                radius = 800

            # 🔴 boundary circle
            folium.Circle(
                location=[lat, lon],
                radius=radius,
                color=color,
                fill=False,
                weight=3
            ).add_to(m)

            # 🔵 zone number marker
            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(html=f"""
                    <div style="
                        background-color: blue;
                        color: white;
                        border-radius: 50%;
                        width: 30px;
                        height: 30px;
                        text-align: center;
                        line-height: 30px;
                        font-weight: bold;
                        border: 2px solid red;
                    ">
                        {zone}
                    </div>
                """)
            ).add_to(m)

        # ---------------- HEATMAP ----------------
        HeatMap(heat_data).add_to(m)

        return m

    except Exception as e:
        print("❌ Heatmap Error:", e)
        return folium.Map(location=[20, 78], zoom_start=5)