import pandas as pd
import numpy as np
import joblib
from sklearn.cluster import KMeans
from xgboost import XGBRegressor


def train_model(data_path):
    df = pd.read_csv(data_path)

    # ---------------- CLEANING ----------------
    df['pickup_datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    df['hour'] = df['pickup_datetime'].dt.hour
    df['day'] = df['pickup_datetime'].dt.day_name()

    df = df.dropna(subset=['lat', 'lon'])

    # ---------------- CLUSTERING ----------------
    kmeans = KMeans(n_clusters=20, random_state=42)
    df['zone'] = kmeans.fit_predict(df[['lat','lon']])

    # ---------------- MODEL DATA ----------------
    model_data = df.groupby(['hour','day','zone']).size().reset_index(name='demand')

    # Features
    model_data['is_weekend'] = model_data['day'].isin(['Saturday','Sunday']).astype(int)
    model_data['is_peak'] = model_data['hour'].isin([8,9,17,18,19]).astype(int)

    # Encoding
    model_data = pd.get_dummies(model_data, columns=['day','zone'], drop_first=True)

    # Target
    model_data['demand'] = np.log1p(model_data['demand'])

    X = model_data.drop(columns=['demand'])
    y = model_data['demand']

    # ---------------- MODEL ----------------
    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8
    )

    model.fit(X, y)

    # ---------------- SAVE ----------------
    joblib.dump(model, "models/demand_model.pkl")
    joblib.dump(X.columns, "models/model_columns.pkl")
    joblib.dump(kmeans, "models/kmeans.pkl")

    print("✅ Model trained and saved")


if __name__ == "__main__":
    train_model("data/uber_rides_with_coords.csv")