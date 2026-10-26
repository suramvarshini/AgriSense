"""
AgriSense - ML Crop Recommendation Engine
Evaluates soil & weather conditions to recommend top suitable crops with match percentages.
"""

import pandas as pd
import numpy as np
from backend.model import CROP_PROFILES, get_trained_models

def recommend_crops(data):
    """
    Evaluates soil N, P, K, pH, moisture, climate temp, humidity, rainfall
    and returns ranked crop recommendations with suitability percentages.
    """
    try:
        soil_ph = float(data.get("soil_ph", 6.5))
        nitrogen = float(data.get("nitrogen", 280))
        phosphorus = float(data.get("phosphorus", 35))
        potassium = float(data.get("potassium", 200))
        temperature = float(data.get("temperature", 26))
        humidity = float(data.get("humidity", 70))
        rainfall = float(data.get("rainfall", 900))
        soil_moisture = float(data.get("soil_moisture", 45))
    except (ValueError, TypeError) as e:
        return {"error": f"Invalid parameter format: {str(e)}"}

    _, crop_data = get_trained_models()

    # Feature input
    X_in = pd.DataFrame([{
        "Soil_pH": soil_ph,
        "Nitrogen_N": nitrogen,
        "Phosphorus_P": phosphorus,
        "Potassium_K": potassium,
        "Temperature_C": temperature,
        "Humidity_pct": humidity,
        "Rainfall_mm": rainfall,
        "Soil_Moisture": soil_moisture
    }])

    recommendations = []

    if isinstance(crop_data, dict):
        model = crop_data["model"]
        classes = crop_data["classes"]
        
        # Get ML predicted probabilities
        probs = model.predict_proba(X_in)[0]
        
        for crop_name, prob in zip(classes, probs):
            # Calculate agronomic distance benchmark for extra stability
            prof = CROP_PROFILES.get(crop_name, CROP_PROFILES["Rice"])
            score_acc = prob * 100.0
            
            # Additional rule adjustment based on agronomic bounds
            in_range = 0
            if prof["pH"][0] <= soil_ph <= prof["pH"][1]: in_range += 1
            if prof["N"][0] <= nitrogen <= prof["N"][1]: in_range += 1
            if prof["temp"][0] <= temperature <= prof["temp"][1]: in_range += 1
            if prof["rainfall"][0] <= rainfall <= prof["rainfall"][1]: in_range += 1
            
            rule_bonus = (in_range / 4.0) * 35.0
            final_suitability = round(min(98.5, max(12.0, (score_acc * 0.65) + rule_bonus + 15.0)), 1)
            
            if final_suitability >= 85:
                tag = "Highly Recommended"
                badge_class = "badge-success"
            elif final_suitability >= 68:
                tag = "Recommended"
                badge_class = "badge-info"
            else:
                tag = "Moderate Suitability"
                badge_class = "badge-warning"

            recommendations.append({
                "crop": crop_name,
                "suitability_pct": final_suitability,
                "tag": tag,
                "badge_class": badge_class,
                "ideal_ph": f"{prof['pH'][0]} - {prof['pH'][1]}",
                "ideal_temp": f"{prof['temp'][0]} - {prof['temp'][1]} °C",
                "ideal_rainfall": f"{prof['rainfall'][0]} - {prof['rainfall'][1]} mm",
                "expected_yield_range": f"{prof['yield'][0]} - {prof['yield'][1]} t/ha"
            })

    # Sort descending by suitability
    recommendations.sort(key=lambda x: x["suitability_pct"], reverse=True)

    return {
        "top_recommendation": recommendations[0]["crop"] if recommendations else "Rice",
        "recommendations": recommendations[:6],  # Return Top 6
        "all_rankings": recommendations
    }
