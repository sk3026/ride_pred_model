# RidePulse — Ride Demand Prediction System

RidePulse is a machine learning-based ride demand prediction system that forecasts ride demand across different city zones using temporal and geospatial features. The project includes data preprocessing, spatial clustering, demand forecasting, a REST API, and an interactive dashboard for visualization.

---

## Live Deployments

| Service | URL |
|---|---|
| Streamlit Dashboard | https://ridepulsev1.streamlit.app/ |
| Flask API | https://ridepulsev2.onrender.com/ |

---

## Features

- Real-time ride demand prediction by zone, hour, and day
- Zone-wise demand analysis and classification
- Spatial clustering using KMeans
- Interactive heatmap visualization
- REST API for model inference
- Streamlit dashboard integration
- Demand level classification — Low / Moderate / High

---

## Tech Stack

| Layer | Tools |
|---|---|
| Machine Learning | XGBoost, scikit-learn, KMeans, Pandas, NumPy |
| Backend | Flask, REST API |
| Frontend | Streamlit, Folium, Streamlit-Folium, Altair |
| Deployment | Render, Streamlit Cloud |

---

## Dataset

The project uses the publicly available Bangalore Uber ride dataset from Kaggle:

https://www.kaggle.com/datasets/roysouvik98/uber-ride-details-bangalore

The original dataset contains ride-booking and temporal information. Since it did not include latitude and longitude coordinates, geospatial coordinates were generated during preprocessing to enable spatial clustering, zone creation, heatmap visualization, and geospatial demand analysis.

---

## Project Structure

```
RIDE_MODEL/
│
├── dashboard/
│   ├── app.py
│   └── requirements.txt
│
├── data/
│   ├── processed/
│   │   ├── locations.csv
│   │   └── zone_centers.csv
│   └── raw/
│       └── uber_rides_with_coords.csv
│
├── models/
│   ├── demand_model.pkl
│   ├── kmeans.pkl
│   └── model_columns.pkl
│
├── notebooks/
│   └── RidePulse.ipynb
│
├── src/
│   ├── app.py
│   ├── model_pipeline.py
│   ├── spatial_pipeline.py
│   ├── train_pipeline.py
│   └── generate_zone_data.py
│
├── requirements.txt
├── render.yaml
└── README.md
```

## Project Workflow

1. Data preprocessing and cleaning
2. Geographic filtering — Bangalore coordinates only
3. Spatial clustering using KMeans (20 zones)
4. Feature engineering
5. Demand forecasting using XGBoost
6. Flask API development and deployment
7. Streamlit dashboard integration
8. Real-time inference

---

## Feature Engineering

| Feature | Description |
|---|---|
| `hour` | Hour of day (0–23) |
| `day` | Day of week |
| `is_weekend` | 1 if Saturday or Sunday |
| `is_peak` | 1 if hour is 8, 9, 17, 18, or 19 |
| `zone_N` | One-hot encoded zone ID |

**Target transformation:**

```
y = log(1 + demand)
```

**Inverse transformation during inference:**

```
predicted_demand = exp(prediction) - 1
```

---

## Model Performance

| Metric | Score |
|---|---|
| R² Score | 0.946 |
| MAE | 5.85 |

---

## API Usage

**Predict demand:**

```bash
curl -X POST https://ridepulsev2.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{"hour": 10, "day": "Monday", "location_id": 5}'
```

**Response:**

```json
{
  "predicted_demand": 51.54,
  "demand_level": "High",
  "location": "Zone 5",
  "hour": 10,
  "day": "Monday",
  "zone": 5
}
```

**Get all zones:**

```bash
curl https://ridepulsev2.onrender.com/locations
```