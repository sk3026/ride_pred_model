# RidePulse — Ride Demand Prediction System

RidePulse is a machine learning-based ride demand prediction system that forecasts ride demand across different city zones using temporal and geospatial features. The project includes data preprocessing, spatial clustering, demand forecasting, REST API integration, and an interactive dashboard for visualization and analysis.

---

##

Streamlit Dashboard:  
https://ridepulsev1.streamlit.app/

Flask API:  
https://ridepulsev2.onrender.com/

---

## Features

- Real-time ride demand prediction
- Zone-wise demand analysis
- Spatial clustering using KMeans
- Interactive heatmap visualization
- REST API for inference
- Streamlit dashboard integration
- Demand classification based on prediction thresholds

---

## Tech Stack

### Machine Learning
- Python
- XGBoost
- scikit-learn
- KMeans Clustering
- Pandas
- NumPy

### Backend
- Flask
- REST API

### Frontend & Visualization
- Streamlit
- Folium
- Streamlit-Folium
- Altair

### Deployment
- Render
- Streamlit Cloud

---

## Dataset

The project uses the publicly available Bangalore Uber ride dataset from Kaggle:

https://www.kaggle.com/datasets/roysouvik98/uber-ride-details-bangalore

The original dataset primarily contains ride-booking and temporal information. Since the dataset did not include latitude and longitude coordinates, geospatial coordinates were additionally generated during preprocessing to enable:

- spatial clustering
- zone creation
- heatmap visualization
- geospatial demand analysis

---
PROJECT STRUCTURE:

RIDE_MODEL/
│
├── dashboard/
├── data/
├── models/
├── notebooks/
├── src/
├── requirements.txt
└── README.md


## Project Workflow

1. Data preprocessing and cleaning  
2. Spatial clustering using KMeans  
3. Feature engineering  
4. Demand forecasting using XGBoost  
5. Flask API development  
6. Streamlit dashboard integration  
7. Deployment and real-time inference 

## Model Performance

| Metric | Score |
|---|---|
| R² Score | 0.946 |
| MAE | 5.85 |



 

---

## Feature Engineering

Features used for prediction:

- Hour of day
- Day of week
- Weekend indicator
- Peak-hour indicator
- Zone encoding

Target transformation:

y = log(1 + demand)

Inverse transformation during inference:

predicted_demand = exp(prediction) - 1

---







