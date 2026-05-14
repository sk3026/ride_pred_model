import pandas as pd
import joblib
import os

# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

data_path = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "uber_rides_with_coords.csv"
)

model_path = os.path.join(
    BASE_DIR,
    "models",
    "kmeans.pkl"
)

output_path = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "zone_centers.csv"
)

# ---------------- CITY BOUNDARY ----------------
CITY_LAT_MIN, CITY_LAT_MAX = 12.5, 13.5
CITY_LON_MIN, CITY_LON_MAX = 77.0, 78.2

# ---------------- LOAD DATA ----------------
print(" Loading dataset...")

df = pd.read_csv(data_path)

print(" Dataset loaded:", df.shape)

# ---------------- LOAD MODEL ----------------
print(" Loading KMeans model...")

kmeans = joblib.load(model_path)

print(" KMeans loaded")

# ---------------- CLEAN DATA ----------------
df = df.dropna(subset=['lat', 'lon'])

# ---------------- FILTER BANGALORE ----------------
before = len(df)

df = df[
    (df['lat'] >= CITY_LAT_MIN) &
    (df['lat'] <= CITY_LAT_MAX) &
    (df['lon'] >= CITY_LON_MIN) &
    (df['lon'] <= CITY_LON_MAX)
]

after = len(df)

print(f" Removed rows outside Bangalore: {before - after}")
print(f" Remaining Bangalore rows: {after}")

# ---------------- ASSIGN ZONES ----------------
print("Assigning zones...")

df['zone'] = kmeans.predict(
    df[['lat', 'lon']]
)

# ---------------- CREATE ZONE CENTERS ----------------
print("Creating zone centers...")

zone_centers = (
    df.groupby('zone')[['lat', 'lon']]
      .mean()
      .reset_index()
)

# Sort zones
zone_centers = zone_centers.sort_values(
    by='zone'
).reset_index(drop=True)

# ---------------- SAVE ----------------
zone_centers.to_csv(
    output_path,
    index=False
)

print("Zone dataset saved at:")
print(output_path)

print("\n Zone Centers:")
print(zone_centers.head(20))