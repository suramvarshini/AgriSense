# AgriSense – Precision Agriculture Crop Yield & Soil Health Analytics Platform

**AgriSense** is a modern, full-stack precision agriculture web application designed to empower farmers, agronomists, and agricultural researchers to answer the fundamental question:
> **“How do soil, weather, satellite spatial imagery, and visual crop health influence agricultural productivity?”**

---

## 🚀 Netlify Deployment Guide

AgriSense is fully configured for zero-configuration, instant deployment on **Netlify**.

### Method 1: Instant Drag & Drop (Fastest - No CLI Needed)
1. Log in to [Netlify](https://app.netlify.com).
2. Go to **[app.netlify.com/drop](https://app.netlify.com/drop)**.
3. Drag & drop the **`frontend/`** directory into the browser drop zone.
4. Your application will be live immediately with a free HTTPS Netlify domain (e.g. `https://agrisense-platform.netlify.app`)!

### Method 2: Deployment via Netlify CLI
Run the following terminal command in VS Code:
```bash
npx netlify-cli deploy --prod --dir=frontend
```

### Method 3: GitHub Repository Deployment
1. Push this project to your GitHub repository.
2. Log in to Netlify and click **"Add new site" → "Import an existing project"**.
3. Select your GitHub repository.
4. Configure site settings:
   - **Build Command**: `echo 'Building AgriSense'`
   - **Publish Directory**: `frontend`
5. Click **"Deploy Site"**.

---

## 🌾 Key Features

1. **Interactive Analytics Dashboard**:
   - Live summary metrics: Average Yield, Soil Health Score, Temperature, Rainfall, Soil Moisture, Predicted Yield, and Crop Health diagnostic status.
   - 8 dynamic interactive Chart.js visualizations (Crop Yield by Crop, Rainfall vs Yield, Temperature vs Yield, Soil pH vs Yield, Nitrogen vs Yield, Moisture vs Yield, Monthly Rainfall, Soil Health Distribution).

2. **🛰️ Interactive Satellite Map (GIS)**:
   - Built with **Leaflet.js** supporting high-resolution **Esri World Imagery (Satellite View)** and **OpenStreetMap (Street View)**.
   - Layer switcher control (`L.control.layers`) with no hard-coded API key required.
   - Location search box, quick-jump presets (Hanamkonda, Vijayawada, Ludhiana, Nashik, Indore), interactive green field marker, and live Latitude/Longitude coordinate tracking.
   - Selected Location Information Panel displaying Crop, Soil Score, Moisture %, Temperature °C, Rainfall mm, and Predicted Yield.
   - **“Analyze This Location”** button linking map spatial selection directly to soil health and machine learning yield predictions.

3. **🌿 Crop Health & Disease Computer Vision Analyzer**:
   - Upload or drag-and-drop crop leaf photographs (`.jpg`, `.jpeg`, `.png`).
   - Image quality check engine detecting dark photos, blurry images, or invalid subjects (`"Please upload a clear photograph showing the affected crop or leaf."`).
   - Categorizes crop health into **Healthy**, **Possible Fungal Disease**, **Possible Pest/Insect Damage**, **Possible Bacterial/Other Disease**, **Possible Nutrient Stress**, or **Uncertain**.
   - Outputs confidence score %, visual observation, common symptoms, and non-hazardous field stewardship recommendations.
   - Integrated with regional agronomic context (**Location + Soil + Weather + Yield + Crop Photo**).

4. **Dynamic Soil Health Score Engine**:
   - Real-time scoring algorithm (0–100) based on Soil pH, Nitrogen (N), Phosphorus (P), Potassium (K), Organic Carbon, Soil Moisture, and Soil Temperature.
   - Categorizes condition into **Poor / Moderate / Good / Excellent**.

5. **Machine Learning Crop Yield Prediction**:
   - Trained `RandomForestRegressor` Scikit-learn model predicting yield in **kg/ha** and **tonnes/ha**, total harvest, model confidence percentage, and key yield driver breakdown.

6. **ML Crop Recommendation Engine**:
   - Trained `RandomForestClassifier` recommending top suitable crops (Rice, Wheat, Maize, Cotton, Groundnut, Soybean, Sugarcane, Tomato, Chilli, Pulses, Mustard, Potato) with suitability percentages.

7. **Agricultural Dataset Explorer**:
   - Interactive data table with keyword search, multi-column sorting, location/crop filtering, pagination, and CSV Export.

8. **Executive Report Generation & Export**:
   - Built-in printable executive report view with client-side PDF export using `html2pdf.js`.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.14, Flask, Flask-CORS, Scikit-learn, Pandas, NumPy, Joblib, Pillow (PIL image analysis).
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Leaflet.js, Chart.js, FontAwesome, html2pdf.js.
- **Deployment**: Netlify static & serverless configuration (`netlify.toml`, `frontend/_redirects`).
- **Dataset**: 1,600 realistic agricultural records with lat/lng coordinates (`backend/data/agriculture_data.csv`).

---

## 📁 Project Structure

```
38.Precision Agriculture Crop Yield & Soil Health Analytics Platform/
│
├── frontend/                       # Netlify Publish Directory
│   ├── index.html                  # Single Page Application
│   ├── style.css                   # CSS design system
│   ├── script.js                   # JS logic & fallback offline algorithms
│   └── _redirects                  # Netlify single-page rewrite configuration
│
├── backend/                        # Flask REST API Backend
│   ├── app.py                      # Flask server, CV & GIS endpoint host
│   ├── model.py                    # Dataset generator & ML models
│   ├── soil_analysis.py            # Soil health scoring algorithm
│   ├── crop_recommendation.py      # Crop recommendation logic
│   ├── prediction.py               # Yield prediction engine
│   ├── data/                       # CSV agricultural dataset
│   └── requirements.txt            # Python requirements
│
├── netlify.toml                    # Netlify configuration file
├── run.py                          # Local launcher script
├── README.md                       # Comprehensive guide
└── run_instructions.txt            # Quick setup guide
```
