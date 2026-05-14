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
    print("Creating zones...")

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
        model_data['demand'].clip(lower=0)
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
        n_estimators=301,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
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

    # ---------------- SAMPLE TEST PREDICTIONS ----------------
    print("\nSample Predictions")
    print("----------------------")

    sample_tests = [
        (1, 15, "Tuesday"),
        (5, 10, "Monday"),
        (10, 10, "Monday"),
        (15, 10, "Monday"),
        (6, 13, "Monday")
    ]

    for zone, hour, day in sample_tests:

        input_df = pd.DataFrame(
            0,
            index=[0],
            columns=X.columns
        )

        input_df.loc[0, 'hour'] = hour

        input_df.loc[0, 'is_weekend'] = int(
            day in ['Saturday', 'Sunday']
        )

        input_df.loc[0, 'is_peak'] = int(
            hour in [8, 9, 17, 18, 19]
        )

        day_col = f"day_{day}"

        if day_col in input_df.columns:
            input_df.loc[0, day_col] = 1

        zone_col = f"zone_{zone}"

        if zone_col in input_df.columns:
            input_df.loc[0, zone_col] = 1

        pred_log = model.predict(input_df)[0]

        pred = np.expm1(pred_log)

        pred = max(0, pred)

        print(
            f"Zone {zone} | Hour {hour} | {day}"
            f" -> Demand: {round(float(pred), 2)}"
        )

    # ---------------- BASE PATH ----------------
    BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    # ---------------- MODELS DIRECTORY ----------------
    models_dir = os.path.join(
        BASE_DIR,
        "models"
    )

    os.makedirs(models_dir, exist_ok=True)

    print("\nSaving models to:", models_dir)

    # ---------------- SAVE MODEL ----------------
    joblib.dump(
        model,
        os.path.join(
            models_dir,
            "demand_model.pkl"
        )
    )

    # ---------------- SAVE COLUMNS ----------------
    joblib.dump(
        X.columns,
        os.path.join(
            models_dir,
            "model_columns.pkl"
        )
    )

    # ---------------- SAVE KMEANS ----------------
    joblib.dump(
        kmeans,
        os.path.join(
            models_dir,
            "kmeans.pkl"
        )
    )

    print("Models saved successfully")

    return model


# ---------------- RUN ----------------
if __name__ == "__main__":

    train_model(
        "data/raw/uber_rides_with_coords.csv"
    )