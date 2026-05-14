import pandas as pd
import numpy as np
import joblib
import os

from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

from xgboost import XGBRegressor


# ---------------- CITY BOUNDARY ----------------
CITY_LAT_MIN, CITY_LAT_MAX = 12.5, 13.5
CITY_LON_MIN, CITY_LON_MAX = 77.0, 78.2


# ---------------- TRAIN FUNCTION ----------------
def train_model(data_path):

    print("Loading dataset...")

    df = pd.read_csv(data_path)

    print("Dataset shape:", df.shape)

    # ---------------- CLEANING ----------------
    print("Cleaning dataset...")

    df['pickup_datetime'] = pd.to_datetime(
        df['Date'] + ' ' + df['Time']
    )

    df['hour'] = df['pickup_datetime'].dt.hour

    df['day'] = df['pickup_datetime'].dt.day_name()

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

    print(f"Removed outside Bangalore: {before - after}")
    print(f"Remaining rows: {after}")

    # ---------------- CLUSTERING ----------------
    print(" Creating zones...")

    kmeans = KMeans(
        n_clusters=20,
        random_state=42
    )

    df['zone'] = kmeans.fit_predict(
        df[['lat', 'lon']]
    )

    # ---------------- MODEL DATA ----------------
    print("Building model dataset...")

    model_data = (
        df.groupby(['hour', 'day', 'zone'])
          .size()
          .reset_index(name='demand')
    )

    # ---------------- FEATURE ENGINEERING ----------------
    model_data['is_weekend'] = (
        model_data['day']
        .isin(['Saturday', 'Sunday'])
        .astype(int)
    )

    model_data['is_peak'] = (
        model_data['hour']
        .isin([8, 9, 17, 18, 19])
        .astype(int)
    )

    # ---------------- ENCODING ----------------
    model_data = pd.get_dummies(
        model_data,
        columns=['day', 'zone'],
        drop_first=False
    )

    # ---------------- TARGET TRANSFORMATION ----------------
    model_data['demand'] = np.log1p(
        model_data['demand']
    )

    # ---------------- SPLIT ----------------
    X = model_data.drop(columns=['demand'])

    y = model_data['demand']

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    print("Train size:", len(X_train))
    print("Test size :", len(X_test))

    # ---------------- MODEL ----------------
    print("Training XGBoost model...")

    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8
    )

    model.fit(X_train, y_train)

    print("Model training completed")

    # ---------------- EVALUATION ----------------
    y_pred = model.predict(X_test)

    y_pred_actual = np.expm1(y_pred)

    y_test_actual = np.expm1(y_test)

    mae = mean_absolute_error(
        y_test_actual,
        y_pred_actual
    )

    r2 = r2_score(
        y_test_actual,
        y_pred_actual
    )

    print("\nEvaluation Results")
    print("----------------------")
    print("MAE :", round(mae, 2))
    print("R²  :", round(r2, 4))

    # ---------------- CREATE MODELS FOLDER ----------------
    os.makedirs("models", exist_ok=True)

    # ---------------- SAVE ----------------
    print("\n💾 Saving models...")

    joblib.dump(
        model,
        "models/demand_model.pkl"
    )

    joblib.dump(
        X.columns,
        "models/model_columns.pkl"
    )

    joblib.dump(
        kmeans,
        "models/kmeans.pkl"
    )

    print("Models saved successfully")

    return model


# ---------------- RUN ----------------
if __name__ == "__main__":

    train_model(
        "data/raw/uber_rides_with_coords.csv"
    )