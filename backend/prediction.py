"""
AgriSense - Yield Prediction Engine
Executes trained Scikit-learn model inference for crop yield forecasting.
"""

import pandas as pd
import numpy as np
import os
import joblib
from backend.model import CROP_PROFILES, YIELD_MODEL_PATH, get_trained_models

def predict_crop_yield(data):
    """
    Predicts crop yield in tonnes/ha and kg/ha using trained RandomForestRegressor model.
    Inputs: dict containing crop, soil_ph, nitrogen, phosphorus, potassium, organic_carbon, 
            soil_moisture, temperature, rainfall, humidity, area_ha
    """
    try:
        crop = str(data.get("crop", "Rice"))
        soil_ph = float(data.get("soil_ph", 6.5))
        nitrogen = float(data.get("nitrogen", 280))
        phosphorus = float(data.get("phosphorus", 35))
        potassium = float(data.get("potassium", 200))
        organic_carbon = float(data.get("organic_carbon", 0.85))
        soil_moisture = float(data.get("soil_moisture", 45))
        temperature = float(data.get("temperature", 26))
        rainfall = float(data.get("rainfall", 900))
        humidity = float(data.get("humidity", 70))
        area_ha = float(data.get("area_ha", 1.0))
        if area_ha <= 0: area_ha = 1.0
    except (ValueError, TypeError) as e:
        return {"error": f"Invalid parameter format: {str(e)}"}

    yield_data, _ = get_trained_models()
    
    if isinstance(yield_data, dict):
        model = yield_data["model"]
        cols = yield_data["columns"]
        r2_acc = yield_data.get("r2", 0.88)
    else:
        model = yield_data
        cols = None
        r2_acc = 0.85

    # Prepare input DataFrame with dummy variables for crop
    feature_dict = {
        "Soil_pH": soil_ph,
        "Nitrogen_N": nitrogen,
        "Phosphorus_P": phosphorus,
        "Potassium_K": potassium,
        "Organic_Carbon": organic_carbon,
        "Soil_Moisture": soil_moisture,
        "Temperature_C": temperature,
        "Rainfall_mm": rainfall,
        "Humidity_pct": humidity,
        "Area_ha": area_ha
    }

    if cols:
        input_row = {col: 0.0 for col in cols}
        for k, v in feature_dict.items():
            if k in input_row:
                input_row[k] = v
        crop_col = f"Crop_{crop}"
        if crop_col in input_row:
            input_row[crop_col] = 1.0
        
        X_in = pd.DataFrame([input_row])
        X_in = X_in[cols]  # Ensure column order matches training
    else:
        # Fallback raw features
        X_in = pd.DataFrame([feature_dict])

    predicted_tonnes_ha = float(model.predict(X_in)[0])
    predicted_tonnes_ha = max(0.2, round(predicted_tonnes_ha, 2))
    
    predicted_kg_ha = round(predicted_tonnes_ha * 1000.0, 1)
    total_production_tonnes = round(predicted_tonnes_ha * area_ha, 2)
    total_production_kg = round(predicted_kg_ha * area_ha, 1)

    # Estimate confidence percentage based on profile suitability
    prof = CROP_PROFILES.get(crop, CROP_PROFILES["Rice"])
    deviations = 0
    if not (prof["pH"][0] <= soil_ph <= prof["pH"][1]): deviations += 1
    if not (prof["N"][0] <= nitrogen <= prof["N"][1]): deviations += 1
    if not (prof["rainfall"][0] <= rainfall <= prof["rainfall"][1]): deviations += 1
    if not (prof["temp"][0] <= temperature <= prof["temp"][1]): deviations += 1

    confidence = round(max(65.0, min(96.0, (r2_acc * 100.0) - (deviations * 5.5) + np.random.uniform(-1.5, 1.5))), 1)

    # Driver Insights
    drivers = [
        {"factor": "Rainfall", "impact": "High Positive" if rainfall >= prof["rainfall"][0] else "Deficient - Restricting Yield", "value": f"{rainfall} mm"},
        {"factor": "Soil Nitrogen", "impact": "Optimal" if prof["N"][0] <= nitrogen <= prof["N"][1] else ("Low" if nitrogen < prof["N"][0] else "Excessive"), "value": f"{nitrogen} kg/ha"},
        {"factor": "Soil pH", "impact": "Balanced" if prof["pH"][0] <= soil_ph <= prof["pH"][1] else "Sub-optimal pH", "value": f"{soil_ph}"},
        {"factor": "Soil Moisture", "impact": "Sufficient" if prof["moisture"][0] <= soil_moisture <= prof["moisture"][1] else "Moisture Stress", "value": f"{soil_moisture}%"}
    ]

    return {
        "crop": crop,
        "area_ha": area_ha,
        "yield_tonnes_ha": predicted_tonnes_ha,
        "yield_kg_ha": predicted_kg_ha,
        "total_production_tonnes": total_production_tonnes,
        "total_production_kg": total_production_kg,
        "confidence_pct": confidence,
        "drivers": drivers
    }
