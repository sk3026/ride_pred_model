import pandas as pd
import joblib
import os

# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

data_path = os.path.join(BASE_DIR, "data", "raw", "uber_rides_with_coords.csv")
model_path = os.path.join(BASE_DIR, "models", "kmeans.pkl")

# ---------------- LOAD ----------------
df = pd.read_csv(data_path)
kmeans = joblib.load(model_path)

# Clean
df = df.dropna(subset=['lat','lon'])

# ---------------- ASSIGN ZONES ----------------
df['zone'] = kmeans.predict(df[['lat','lon']])

# ---------------- CREATE ZONE CENTERS ----------------
zone_centers = df.groupby('zone')[['lat','lon']].mean().reset_index()

# ---------------- SAVE ----------------
output_path = os.path.join(BASE_DIR, "data", "processed", "zone_centers.csv")

zone_centers.to_csv(output_path, index=False)

print("✅ Zone dataset saved at:", output_path)
print(zone_centers.head())