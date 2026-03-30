import pandas as pd
import folium
from folium.plugins import HeatMap
import os

# Load dataset (with lat/lon already present)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

df = pd.read_csv(os.path.join(BASE_DIR, "data/raw/uber_rides_with_coords.csv"))

# Convert time
df['pickup_datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
df['hour'] = df['pickup_datetime'].dt.hour

# IMPORTANT: assumes lat/lon already exist
df = df.dropna(subset=['lat', 'lon'])


def generate_heatmap(hour=None):
    data = df.copy()

    if hour is not None:
        data = data[data['hour'] == hour]

    center_lat = data['lat'].mean()
    center_lon = data['lon'].mean()

    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    heat_data = data[['lat', 'lon']].values.tolist()

    HeatMap(heat_data).add_to(m)

    return m