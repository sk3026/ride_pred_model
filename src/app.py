from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os

app = Flask(__name__)

# Load model
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

model = joblib.load(os.path.join(BASE_DIR, "models/demand_model.pkl"))
columns = joblib.load(os.path.join(BASE_DIR, "models/model_columns.pkl"))


@app.route("/")
def home():
    return "🚀 Demand Prediction API Running"


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        input_df = pd.DataFrame([data])

        input_df = pd.get_dummies(input_df)
        input_df = input_df.reindex(columns=columns, fill_value=0)

        pred_log = model.predict(input_df)[0]
        pred_actual = np.expm1(pred_log)

        return jsonify({
            "predicted_demand": float(pred_actual)
        })

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)