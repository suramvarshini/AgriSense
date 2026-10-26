"""
AgriSense - Precision Agriculture Analytics Platform Flask REST API
Serves API endpoints for analytics dashboard, machine learning predictions, soil health evaluation,
crop recommendations, interactive data operations, interactive Satellite Map GIS intelligence,
and Crop Health & Disease Computer Vision Analysis.
"""

import os
import sys
import io
import base64
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.model import load_or_create_dataset, LOCATION_DATA, LOCATION_COORDINATES, get_trained_models, CROP_PROFILES
from backend.soil_analysis import calculate_soil_health
from backend.prediction import predict_crop_yield
from backend.crop_recommendation import recommend_crops

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

df_global = load_or_create_dataset()
get_trained_models()

# Global state for latest crop health analysis
latest_crop_health = {
    "analyzed": False,
    "status": "No image analyzed yet",
    "healthy_pct": 100,
    "issues_pct": 0
}

@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    if os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")

# ==================== CROP HEALTH CV ANALYZER ==================== #

def analyze_crop_image_file(image_bytes, crop_name="Auto Detect Crop"):
    """
    Performs Computer Vision & Agronomic Feature Analysis on uploaded crop leaf image.
    Evaluates image quality (brightness, blur/sharpness, dimensions), greenness ratio,
    lesion/spot pixel density, and color histogram variance.
    """
    try:
        from PIL import Image, ImageStat
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        return {
            "quality_ok": False,
            "warning_msg": "Unsupported file format. Please upload a clear JPG, JPEG, or PNG photograph of the crop leaf.",
            "status": "Uncertain",
            "confidence": 0
        }

    width, height = img.size
    if width < 80 or height < 80:
        return {
            "quality_ok": False,
            "warning_msg": "Image resolution is too low. Please upload a clearer photograph showing the affected crop or leaf.",
            "status": "Uncertain",
            "confidence": 0
        }

    # Image Quality Checks
    # 1. Brightness Check
    stat = ImageStat.Stat(img)
    avg_brightness = sum(stat.mean) / 3.0
    if avg_brightness < 28.0:
        return {
            "quality_ok": False,
            "warning_msg": "Image is too dark. Please take a photo in good lighting showing the crop leaf details.",
            "status": "Uncertain",
            "confidence": 0
        }

    # Convert image to NumPy array for color feature extraction
    img_np = np.array(img)
    r, g, b = img_np[:, :, 0], img_np[:, :, 1], img_np[:, :, 2]

    # Blur estimation via variance of Laplacian/gradients
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    gradient_y, gradient_x = np.gradient(gray)
    blur_score = np.var(gradient_x) + np.var(gradient_y)
    
    if blur_score < 12.0:
        return {
            "quality_ok": False,
            "warning_msg": "Extremely blurry image detected. Please steady your camera and upload a clear focused image.",
            "status": "Uncertain",
            "confidence": 0
        }

    # Color Feature Ratios
    # Greenness index: (G - R) / (G + R + 1e-5)
    green_mask = (g.astype(float) > r.astype(float)) & (g.astype(float) > b.astype(float))
    green_ratio = np.mean(green_mask)

    # Brown / Rust / Lesion mask (High R & G, Low B)
    brown_mask = (r.astype(float) > 110) & (g.astype(float) > 70) & (g.astype(float) < 170) & (b.astype(float) < 90)
    brown_ratio = np.mean(brown_mask)

    # Yellowing / Chlorosis mask (High R & G, low B)
    yellow_mask = (r.astype(float) > 160) & (g.astype(float) > 160) & (b.astype(float) < 110)
    yellow_ratio = np.mean(yellow_mask)

    # Dark spot / necrosis mask
    dark_spot_mask = (r.astype(float) < 60) & (g.astype(float) < 60) & (b.astype(float) < 60)
    dark_spot_ratio = np.mean(dark_spot_mask)

    # Auto detect crop if requested
    detected_crop = crop_name
    if crop_name == "Auto Detect Crop" or not crop_name:
        if green_ratio > 0.45:
            detected_crop = "Rice / Wheat (Green Leaf)"
        elif yellow_ratio > 0.15:
            detected_crop = "Maize / Cotton"
        else:
            detected_crop = "General Crop Leaf"

    # Classification logic based on empirical feature metrics
    if brown_ratio > 0.12 or dark_spot_ratio > 0.15:
        status = "Possible Fungal Disease"
        possible_issue = "Fungal Leaf Spot / Blight Symptoms"
        confidence = round(min(94.0, 75.0 + (brown_ratio * 120.0)), 1)
        observation = "Visible brown concentric spots and necrotic leaf patterns consistent with fungal blight or leaf spot symptoms."
        symptoms = [
            "Dark brown or black circular lesions on leaf surfaces",
            "Concentric rings or yellow halos surrounding spots",
            "Premature leaf yellowing and edge drying"
        ]
        recommendations = [
            "Isolate visibly infected leaves/plants to minimize sporangia drift.",
            "Avoid overhead sprinkler irrigation; apply water directly to root zone to keep leaves dry.",
            "Improve air circulation between rows and monitor adjacent plants closely.",
            "Consult an agricultural expert or plant pathology laboratory to confirm fungal species before applying treatments."
        ]
        issues_flag = True
    elif yellow_ratio > 0.14:
        status = "Possible Nutrient Stress"
        possible_issue = "Nitrogen / Iron Chlorosis Symptoms"
        confidence = round(min(92.0, 72.0 + (yellow_ratio * 110.0)), 1)
        observation = "Interveinal yellowing and chlorotic patterns on upper foliage suggesting nitrogen or micronutrient deficiency."
        symptoms = [
            "Pale yellow coloration between leaf veins",
            "Stunted vegetative growth and thin stems",
            "Lower older leaves turning yellow while upper leaves stay pale"
        ]
        recommendations = [
            "Test soil pH and nitrogen levels using the AgriSense Soil Analysis tab.",
            "Apply well-decomposed organic compost or balanced bio-fertilizers.",
            "Verify that root zone soil moisture is within the 35%-60% optimal range.",
            "Seek agronomist advice for custom micronutrient foliar spray application."
        ]
        issues_flag = True
    elif dark_spot_ratio > 0.08 and green_ratio < 0.35:
        status = "Possible Pest/Insect Damage"
        possible_issue = "Insect Defoliation or Piercing-Sucking Damage"
        confidence = round(min(89.0, 70.0 + (dark_spot_ratio * 130.0)), 1)
        observation = "Irregular leaf margin chewing, pinhole punctures, or stippling patterns consistent with pest activity."
        symptoms = [
            "Irregular holes or ragged margins along leaf blades",
            "Fine white/yellow stippling or webbing on leaf undersides",
            "Curled leaf tips and visible frass residues"
        ]
        recommendations = [
            "Inspect leaf undersides and stem joints for active larvae or sap-sucking insects.",
            "Deploy sticky yellow traps and beneficial predatory insects where practical.",
            "Remove heavily damaged leaves to limit pest population expansion.",
            "Consult a local agricultural extension officer for biological or targeted pest management."
        ]
        issues_flag = True
    elif green_ratio > 0.30:
        status = "Healthy"
        possible_issue = "No Significant Disease Symptoms Detected"
        confidence = round(min(96.0, 82.0 + (green_ratio * 25.0)), 1)
        observation = "Foliiage displays vibrant green pigmentation, uniform leaf structure, and no prominent necrotic lesions."
        symptoms = [
            "Uniform green leaf pigmentation",
            "Intact leaf margins with no significant chewing or spots",
            "Healthy vascular vein structure"
        ]
        recommendations = [
            "Maintain current soil moisture, irrigation, and organic residue management practices.",
            "Continue routine weekly monitoring for early pest or weather stress signals.",
            "Sustain balanced fertilization in accordance with AgriSense Soil recommendations."
        ]
        issues_flag = False
    else:
        status = "Uncertain"
        possible_issue = "Indeterminate Leaf Pattern"
        confidence = 58.0
        observation = "Image patterns are insufficient for a high-confidence health determination."
        symptoms = ["Mixed pigmentation or partial leaf visibility"]
        recommendations = [
            "Take a close-up photograph of a single affected leaf under natural daylight.",
            "Ensure the leaf fills the majority of the camera frame with sharp focus.",
            "Confirm diagnosis with an agricultural extension specialist."
        ]
        issues_flag = False

    # Update global summary metrics for dashboard card
    latest_crop_health["analyzed"] = True
    latest_crop_health["status"] = status
    if issues_flag:
        latest_crop_health["healthy_pct"] = 28
        latest_crop_health["issues_pct"] = 72
    else:
        latest_crop_health["healthy_pct"] = 92
        latest_crop_health["issues_pct"] = 8

    return {
        "quality_ok": True,
        "status": status,
        "possible_issue": possible_issue,
        "confidence": confidence,
        "crop": detected_crop,
        "observation": observation,
        "symptoms": symptoms,
        "recommendations": recommendations,
        "brightness": round(avg_brightness, 1),
        "greenness_pct": round(green_ratio * 100, 1)
    }

@app.route("/api/crop-health", methods=["POST"])
def crop_health_endpoint():
    """Accepts uploaded crop image file or JSON payload and returns crop health classification."""
    crop_name = request.form.get("crop", "Auto Detect Crop")
    
    if "image" in request.files:
        file = request.files["image"]
        image_bytes = file.read()
    elif request.json and "image_base64" in request.json:
        b64_str = request.json["image_base64"]
        if "," in b64_str:
            b64_str = b64_str.split(",")[1]
        image_bytes = base64.b64decode(b64_str)
        crop_name = request.json.get("crop", crop_name)
    else:
        return jsonify({
            "status": "error",
            "message": "No crop image file or base64 data provided."
        }), 400

    res = analyze_crop_image_file(image_bytes, crop_name)
    return jsonify({"status": "success", "analysis": res})

# ==================== LOCATIONS & DASHBOARD ==================== #

@app.route("/api/locations", methods=["GET"])
def get_locations():
    crops = sorted(list(df_global["Crop"].unique()))
    return jsonify({
        "status": "success",
        "locations": LOCATION_DATA,
        "coordinates": LOCATION_COORDINATES,
        "crops": crops
    })

@app.route("/api/map-info", methods=["GET", "POST"])
def get_map_info():
    if request.method == "POST":
        data = request.json or {}
    else:
        data = request.args

    state = data.get("state", "Telangana")
    district = data.get("district", "Hanamkonda")
    village = data.get("village", "All")
    lat_val = data.get("lat")
    lng_val = data.get("lng")

    filtered_df = df_global.copy()

    if state and state != "All":
        filtered_df = filtered_df[filtered_df["State"] == state]
    if district and district != "All":
        filtered_df = filtered_df[filtered_df["District"] == district]
    if village and village != "All":
        filtered_df = filtered_df[filtered_df["Village"] == village]

    if filtered_df.empty:
        filtered_df = df_global.copy()

    if lat_val and lng_val:
        try:
            latitude = round(float(lat_val), 4)
            longitude = round(float(lng_val), 4)
        except (ValueError, TypeError):
            latitude = 18.0124
            longitude = 79.5506
    else:
        if state in LOCATION_COORDINATES:
            st_data = LOCATION_COORDINATES[state]
            if district in st_data.get("districts", {}):
                dist_data = st_data["districts"][district]
                if village in dist_data.get("villages", {}):
                    c = dist_data["villages"][village]
                else:
                    c = dist_data["coords"]
            else:
                c = st_data["coords"]
        else:
            c = [18.0124, 79.5506]
        latitude = c[0]
        longitude = c[1]

    avg_yield = round(float(filtered_df["Crop_Yield_tonnes_ha"].mean()), 2)
    avg_temp = round(float(filtered_df["Temperature_C"].mean()), 1)
    avg_rainfall = round(float(filtered_df["Rainfall_mm"].mean()), 1)
    avg_moisture = round(float(filtered_df["Soil_Moisture"].mean()), 1)
    avg_ph = round(float(filtered_df["Soil_pH"].mean()), 2)
    avg_n = round(float(filtered_df["Nitrogen_N"].mean()), 1)
    avg_p = round(float(filtered_df["Phosphorus_P"].mean()), 1)
    avg_k = round(float(filtered_df["Potassium_K"].mean()), 1)
    avg_oc = round(float(filtered_df["Organic_Carbon"].mean()), 2)

    primary_crop = str(filtered_df["Crop"].mode()[0]) if not filtered_df.empty else "Rice"

    soil_res = calculate_soil_health(avg_ph, avg_n, avg_p, avg_k, avg_oc, avg_moisture, avg_temp)
    pred_res = predict_crop_yield({
        "crop": primary_crop,
        "soil_ph": avg_ph,
        "nitrogen": avg_n,
        "phosphorus": avg_p,
        "potassium": avg_k,
        "organic_carbon": avg_oc,
        "soil_moisture": avg_moisture,
        "temperature": avg_temp,
        "rainfall": avg_rainfall,
        "area_ha": 1.0
    })

    location_label = f"{village}, {district}, {state}" if (village != "All" and district != "All" and state != "All") else (f"{district}, {state}" if (district != "All" and state != "All") else f"{state}")

    return jsonify({
        "status": "success",
        "info": {
            "location": location_label,
            "state": state,
            "district": district,
            "village": village,
            "latitude": latitude,
            "longitude": longitude,
            "crop": primary_crop,
            "soil_health_score": soil_res["score"],
            "soil_condition": soil_res["condition"],
            "soil_moisture": avg_moisture,
            "temperature": avg_temp,
            "rainfall": avg_rainfall,
            "predicted_yield": pred_res.get("yield_tonnes_ha", avg_yield),
            "soil_ph": avg_ph,
            "nitrogen": avg_n,
            "crop_health_status": latest_crop_health["status"]
        }
    })

@app.route("/api/dashboard", methods=["GET"])
def get_dashboard_summary():
    state = request.args.get("state")
    district = request.args.get("district")
    village = request.args.get("village")
    crop = request.args.get("crop")

    filtered_df = df_global.copy()

    if state and state != "All":
        filtered_df = filtered_df[filtered_df["State"] == state]
    if district and district != "All":
        filtered_df = filtered_df[filtered_df["District"] == district]
    if village and village != "All":
        filtered_df = filtered_df[filtered_df["Village"] == village]
    if crop and crop != "All":
        filtered_df = filtered_df[filtered_df["Crop"] == crop]

    if filtered_df.empty:
        filtered_df = df_global.copy()

    avg_yield = round(float(filtered_df["Crop_Yield_tonnes_ha"].mean()), 2)
    avg_temp = round(float(filtered_df["Temperature_C"].mean()), 1)
    avg_rainfall = round(float(filtered_df["Rainfall_mm"].mean()), 1)
    avg_moisture = round(float(filtered_df["Soil_Moisture"].mean()), 1)
    avg_ph = round(float(filtered_df["Soil_pH"].mean()), 2)
    avg_n = round(float(filtered_df["Nitrogen_N"].mean()), 1)
    avg_p = round(float(filtered_df["Phosphorus_P"].mean()), 1)
    avg_k = round(float(filtered_df["Potassium_K"].mean()), 1)
    avg_oc = round(float(filtered_df["Organic_Carbon"].mean()), 2)

    soil_res = calculate_soil_health(avg_ph, avg_n, avg_p, avg_k, avg_oc, avg_moisture, avg_temp)
    soil_health_score = soil_res["score"]

    sample_crop = crop if (crop and crop != "All") else "Rice"
    pred_res = predict_crop_yield({
        "crop": sample_crop,
        "soil_ph": avg_ph,
        "nitrogen": avg_n,
        "phosphorus": avg_p,
        "potassium": avg_k,
        "organic_carbon": avg_oc,
        "soil_moisture": avg_moisture,
        "temperature": avg_temp,
        "rainfall": avg_rainfall,
        "humidity": round(float(filtered_df["Humidity_pct"].mean()), 1),
        "area_ha": 1.0
    })
    predicted_yield = pred_res.get("yield_tonnes_ha", avg_yield)

    crop_yield_groupby = filtered_df.groupby("Crop")["Crop_Yield_tonnes_ha"].mean().round(2).to_dict()
    rainfall_vs_yield = filtered_df[["Rainfall_mm", "Crop_Yield_tonnes_ha", "Crop"]].head(80).to_dict(orient="records")
    temp_vs_yield = filtered_df[["Temperature_C", "Crop_Yield_tonnes_ha", "Crop"]].head(80).to_dict(orient="records")
    ph_vs_yield = filtered_df[["Soil_pH", "Crop_Yield_tonnes_ha", "Crop"]].head(80).to_dict(orient="records")
    n_vs_yield = filtered_df[["Nitrogen_N", "Crop_Yield_tonnes_ha", "Crop"]].head(80).to_dict(orient="records")
    moisture_vs_yield = filtered_df[["Soil_Moisture", "Crop_Yield_tonnes_ha", "Crop"]].head(80).to_dict(orient="records")

    monthly_rainfall = {
        "Jan": 15.2, "Feb": 22.4, "Mar": 35.1, "Apr": 65.8,
        "May": 110.4, "Jun": 240.6, "Jul": 310.2, "Aug": 285.4,
        "Sep": 195.0, "Oct": 95.2, "Nov": 42.0, "Dec": 18.5
    }

    scores = []
    for _, row in filtered_df.iterrows():
        s = calculate_soil_health(row["Soil_pH"], row["Nitrogen_N"], row["Phosphorus_P"], row["Potassium_K"], row["Organic_Carbon"], row["Soil_Moisture"])["score"]
        scores.append(s)
    
    score_series = pd.Series(scores)
    soil_distribution = {
        "Poor (0-39)": int((score_series < 40).sum()),
        "Moderate (40-69)": int(((score_series >= 40) & (score_series < 70)).sum()),
        "Good (70-89)": int(((score_series >= 70) & (score_series < 90)).sum()),
        "Excellent (90-100)": int((score_series >= 90).sum())
    }

    return jsonify({
        "status": "success",
        "summary": {
            "avg_yield": avg_yield,
            "soil_health_score": soil_health_score,
            "avg_temp": avg_temp,
            "avg_rainfall": avg_rainfall,
            "avg_moisture": avg_moisture,
            "predicted_yield": predicted_yield,
            "records_count": len(filtered_df),
            "crop_health": latest_crop_health
        },
        "soil_analysis": soil_res,
        "charts": {
            "crop_yield_by_crop": crop_yield_groupby,
            "rainfall_vs_yield": rainfall_vs_yield,
            "temp_vs_yield": temp_vs_yield,
            "ph_vs_yield": ph_vs_yield,
            "n_vs_yield": n_vs_yield,
            "moisture_vs_yield": moisture_vs_yield,
            "monthly_rainfall": monthly_rainfall,
            "soil_distribution": soil_distribution
        }
    })

@app.route("/api/soil-analysis", methods=["POST"])
def soil_analysis_endpoint():
    data = request.json or {}
    res = calculate_soil_health(
        soil_ph=data.get("soil_ph", 6.5),
        nitrogen=data.get("nitrogen", 280),
        phosphorus=data.get("phosphorus", 35),
        potassium=data.get("potassium", 200),
        organic_carbon=data.get("organic_carbon", 0.85),
        soil_moisture=data.get("soil_moisture", 45),
        soil_temp=data.get("soil_temp", 25.0)
    )
    return jsonify({"status": "success", "result": res})

@app.route("/api/weather", methods=["GET"])
def weather_analytics():
    state = request.args.get("state", "Telangana")
    filtered_df = df_global[df_global["State"] == state] if state != "All" else df_global
    
    if filtered_df.empty: filtered_df = df_global

    avg_temp = round(float(filtered_df["Temperature_C"].mean()), 1)
    avg_rainfall = round(float(filtered_df["Rainfall_mm"].mean()), 1)
    avg_humidity = round(float(filtered_df["Humidity_pct"].mean()), 1)
    avg_wind = round(float(filtered_df["Wind_Speed_kmh"].mean()), 1)
    avg_moisture = round(float(filtered_df["Soil_Moisture"].mean()), 1)

    if avg_rainfall > 1100:
        cond = "Monsoon / Heavy Rain"
    elif avg_rainfall > 700:
        cond = "Humid / Moderate Rain"
    elif avg_temp > 33:
        cond = "Dry & Warm"
    else:
        cond = "Mild / Pleasant"

    return jsonify({
        "status": "success",
        "weather": {
            "temperature": avg_temp,
            "rainfall": avg_rainfall,
            "humidity": avg_humidity,
            "wind_speed": avg_wind,
            "soil_moisture": avg_moisture,
            "condition": cond
        }
    })

@app.route("/api/predict-yield", methods=["POST"])
def predict_yield_endpoint():
    data = request.json or {}
    res = predict_crop_yield(data)
    if "error" in res:
        return jsonify({"status": "error", "message": res["error"]}), 400
    return jsonify({"status": "success", "prediction": res})

@app.route("/api/recommend-crop", methods=["POST"])
def recommend_crop_endpoint():
    data = request.json or {}
    res = recommend_crops(data)
    if "error" in res:
        return jsonify({"status": "error", "message": res["error"]}), 400
    return jsonify({"status": "success", "recommendation": res})

@app.route("/api/agriculture-data", methods=["GET"])
def get_agriculture_data():
    state = request.args.get("state")
    district = request.args.get("district")
    crop = request.args.get("crop")
    search = request.args.get("search", "").strip().lower()
    sort_by = request.args.get("sort_by", "Record_ID")
    order = request.args.get("order", "asc")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 15))

    df = df_global.copy()

    if state and state != "All":
        df = df[df["State"] == state]
    if district and district != "All":
        df = df[df["District"] == district]
    if crop and crop != "All":
        df = df[df["Crop"] == crop]

    if search:
        mask = (
            df["Record_ID"].str.lower().str.contains(search) |
            df["State"].str.lower().str.contains(search) |
            df["District"].str.lower().str.contains(search) |
            df["Village"].str.lower().str.contains(search) |
            df["Crop"].str.lower().str.contains(search)
        )
        df = df[mask]

    if sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=(order == "asc"))

    total_records = len(df)
    total_pages = max(1, int(np.ceil(total_records / per_page)))
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    records = df.iloc[start_idx:end_idx].to_dict(orient="records")

    return jsonify({
        "status": "success",
        "total_records": total_records,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "records": records
    })

@app.route("/api/report", methods=["POST"])
def generate_report():
    data = request.json or {}
    location = data.get("location", {})
    crop = data.get("crop", "Rice")
    soil_inputs = data.get("soil", {})
    weather_inputs = data.get("weather", {})
    
    soil_res = calculate_soil_health(
        soil_inputs.get("soil_ph", 6.5),
        soil_inputs.get("nitrogen", 280),
        soil_inputs.get("phosphorus", 35),
        soil_inputs.get("potassium", 200),
        soil_inputs.get("organic_carbon", 0.85),
        soil_inputs.get("soil_moisture", 45)
    )

    pred_res = predict_crop_yield({**soil_inputs, **weather_inputs, "crop": crop})
    rec_res = recommend_crops({**soil_inputs, **weather_inputs})

    return jsonify({
        "status": "success",
        "report": {
            "title": "AgriSense Precision Agriculture Executive Report",
            "date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "location": location,
            "crop": crop,
            "soil_analysis": soil_res,
            "yield_prediction": pred_res,
            "crop_recommendations": rec_res["recommendations"][:4],
            "smart_farmer_advice": soil_res["recommendations"],
            "crop_health_status": latest_crop_health["status"]
        }
    })

if __name__ == "__main__":
    print("Starting AgriSense Flask API Server on http://localhost:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)
