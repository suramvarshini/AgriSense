"""
AgriSense - Soil Health Analysis Engine
Calculates dynamic soil health scores, nutrient statuses, and agronomic recommendations.
"""

def calculate_soil_health(soil_ph, nitrogen, phosphorus, potassium, organic_carbon, soil_moisture, soil_temp=25.0):
    """
    Dynamically computes soil health score (0-100), condition grade, nutrient status,
    and actionable agronomical recommendations based on input parameters.
    """
    try:
        soil_ph = float(soil_ph)
        nitrogen = float(nitrogen)
        phosphorus = float(phosphorus)
        potassium = float(potassium)
        organic_carbon = float(organic_carbon)
        soil_moisture = float(soil_moisture)
        soil_temp = float(soil_temp)
    except (ValueError, TypeError):
        soil_ph = 6.5
        nitrogen = 280.0
        phosphorus = 35.0
        potassium = 200.0
        organic_carbon = 0.85
        soil_moisture = 45.0
        soil_temp = 25.0

    # Component Scoring Logic (Weighted 100 Points Total)
    
    # 1. pH Score (Max 20 pts)
    # Ideal range: 6.0 to 7.5
    if 6.2 <= soil_ph <= 7.3:
        ph_score = 20.0
    elif 5.8 <= soil_ph < 6.2 or 7.3 < soil_ph <= 7.8:
        ph_score = 16.0
    elif 5.2 <= soil_ph < 5.8 or 7.8 < soil_ph <= 8.3:
        ph_score = 11.0
    elif 4.5 <= soil_ph < 5.2 or 8.3 < soil_ph <= 9.0:
        ph_score = 6.0
    else:
        ph_score = 2.0

    # 2. Nitrogen Score (Max 20 pts)
    # Ideal range: 250 - 420 kg/ha
    if 260 <= nitrogen <= 400:
        n_score = 20.0
    elif (200 <= nitrogen < 260) or (400 < nitrogen <= 480):
        n_score = 16.0
    elif (140 <= nitrogen < 200) or (480 < nitrogen <= 550):
        n_score = 11.0
    elif (80 <= nitrogen < 140) or (550 < nitrogen <= 650):
        n_score = 6.0
    else:
        n_score = 3.0

    # 3. Phosphorus Score (Max 15 pts)
    # Ideal range: 25 - 55 kg/ha
    if 25 <= phosphorus <= 55:
        p_score = 15.0
    elif (18 <= phosphorus < 25) or (55 < phosphorus <= 70):
        p_score = 12.0
    elif (12 <= phosphorus < 18) or (70 < phosphorus <= 85):
        p_score = 8.0
    elif (6 <= phosphorus < 12) or (85 < phosphorus <= 100):
        p_score = 4.0
    else:
        p_score = 1.0

    # 4. Potassium Score (Max 15 pts)
    # Ideal range: 150 - 320 kg/ha
    if 150 <= potassium <= 320:
        k_score = 15.0
    elif (110 <= potassium < 150) or (320 < potassium <= 380):
        k_score = 12.0
    elif (70 <= potassium < 110) or (380 < potassium <= 440):
        k_score = 8.0
    elif (40 <= potassium < 70) or (440 < potassium <= 500):
        k_score = 4.0
    else:
        k_score = 1.0

    # 5. Organic Carbon Score (Max 15 pts)
    # Ideal range: 0.6% - 1.2%
    if 0.7 <= organic_carbon <= 1.2:
        oc_score = 15.0
    elif 0.5 <= organic_carbon < 0.7 or 1.2 < organic_carbon <= 1.5:
        oc_score = 12.0
    elif 0.35 <= organic_carbon < 0.5 or 1.5 < organic_carbon <= 2.0:
        oc_score = 8.0
    elif 0.2 <= organic_carbon < 0.35:
        oc_score = 4.0
    else:
        oc_score = 2.0

    # 6. Soil Moisture Score (Max 15 pts)
    # Ideal range: 35% - 60%
    if 38 <= soil_moisture <= 58:
        moisture_score = 15.0
    elif (28 <= soil_moisture < 38) or (58 < soil_moisture <= 68):
        moisture_score = 12.0
    elif (20 <= soil_moisture < 28) or (68 < soil_moisture <= 78):
        moisture_score = 8.0
    elif (12 <= soil_moisture < 20) or (78 < soil_moisture <= 85):
        moisture_score = 4.0
    else:
        moisture_score = 2.0

    total_score = round(ph_score + n_score + p_score + k_score + oc_score + moisture_score, 1)
    total_score = max(0.0, min(100.0, total_score))

    # Condition Grading
    if total_score >= 88:
        condition = "Excellent"
        color = "#2e7d32" # Green
    elif total_score >= 70:
        condition = "Good"
        color = "#4caf50" # Light green
    elif total_score >= 45:
        condition = "Moderate"
        color = "#ff9800" # Orange
    else:
        condition = "Poor"
        color = "#f44336" # Red

    # Nutrient Status Evaluation
    nutrient_status = {
        "pH": {"value": soil_ph, "status": "Optimal" if 6.0 <= soil_ph <= 7.5 else ("Acidic" if soil_ph < 6.0 else "Alkaline")},
        "Nitrogen": {"value": nitrogen, "unit": "kg/ha", "status": "Optimal" if 250 <= nitrogen <= 420 else ("Low" if nitrogen < 250 else "High")},
        "Phosphorus": {"value": phosphorus, "unit": "kg/ha", "status": "Optimal" if 25 <= phosphorus <= 55 else ("Low" if phosphorus < 25 else "High")},
        "Potassium": {"value": potassium, "unit": "kg/ha", "status": "Optimal" if 150 <= potassium <= 320 else ("Low" if potassium < 150 else "High")},
        "Organic_Carbon": {"value": organic_carbon, "unit": "%", "status": "Optimal" if 0.6 <= organic_carbon <= 1.2 else ("Low" if organic_carbon < 0.6 else "High")},
        "Soil_Moisture": {"value": soil_moisture, "unit": "%", "status": "Optimal" if 35 <= soil_moisture <= 60 else ("Low" if soil_moisture < 35 else "High")},
        "Soil_Temperature": {"value": soil_temp, "unit": "°C", "status": "Optimal" if 18 <= soil_temp <= 32 else ("Low" if soil_temp < 18 else "High")}
    }

    # Actionable Agronomic Recommendations
    recommendations = []

    if nitrogen < 250:
        recommendations.append("Apply nitrogen-rich fertilizers (such as Urea or Ammonium Sulfate at ~40-50 kg/ha) or cultivate nitrogen-fixing pulse crops.")
    elif nitrogen > 420:
        recommendations.append("Reduce nitrogen application. Excess nitrogen can trigger lodging and increase crop susceptibility to pests.")

    if phosphorus < 25:
        recommendations.append("Supplement with Single Super Phosphate (SSP) or DAP to stimulate strong root development.")
    elif phosphorus > 55:
        recommendations.append("Phosphorus status is abundant; skip phosphorus fertilizers in the upcoming cropping cycle.")

    if potassium < 150:
        recommendations.append("Apply Muriate of Potash (MOP) to boost crop grain filling and drought resistance.")

    if soil_ph < 6.0:
        recommendations.append("Soil is acidic (pH < 6.0). Incorporate agricultural lime (calcium carbonate) or dolomite to neutralize acidity.")
    elif soil_ph > 7.5:
        recommendations.append("Soil is alkaline (pH > 7.5). Apply gypsum (calcium sulphate) or elemental sulfur along with organic compost.")

    if organic_carbon < 0.6:
        recommendations.append("Organic matter is low (< 0.6%). Add well-rotted Farm Yard Manure (FYM), biochar, or vermicompost.")
    
    if soil_moisture < 35:
        recommendations.append("Soil moisture is low (< 35%). Schedule drip or furrow irrigation to alleviate crop water stress.")
    elif soil_moisture > 60:
        recommendations.append("High moisture (> 60%). Ensure drainage channels are clear to prevent waterlogging and root rot.")

    if not recommendations:
        recommendations.append("Soil parameters are well-balanced. Maintain current organic residue recycling and crop rotation practices.")

    return {
        "score": total_score,
        "condition": condition,
        "color": color,
        "nutrient_status": nutrient_status,
        "recommendations": recommendations,
        "breakdown": {
            "ph_score": ph_score,
            "n_score": n_score,
            "p_score": p_score,
            "k_score": k_score,
            "oc_score": oc_score,
            "moisture_score": moisture_score
        }
    }
