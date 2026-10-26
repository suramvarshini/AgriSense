"""
AgriSense - Dataset Generator & Scikit-Learn Machine Learning Models
Trains RandomForest ML models for Crop Yield Prediction & Crop Recommendation.
Includes Geographical Coordinate Centroids for Indian Agriculture Map Integration.
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
CSV_PATH = os.path.join(DATA_DIR, "agriculture_data.csv")
YIELD_MODEL_PATH = os.path.join(MODELS_DIR, "yield_model.pkl")
CROP_MODEL_PATH = os.path.join(MODELS_DIR, "crop_recommendation_model.pkl")

# Geographical Coordinate Centroids (Latitude, Longitude) for Locations
LOCATION_COORDINATES = {
    "Telangana": {
        "coords": [17.8749, 78.1008],
        "districts": {
            "Hanamkonda": {"coords": [18.0124, 79.5506], "villages": {"Hanamkonda Rural": [18.0150, 79.5520], "Kazipet": [17.9814, 79.5255], "Inavolu": [17.8921, 79.6012], "Hasanparthy": [18.0833, 79.5417]}},
            "Warangal": {"coords": [17.9784, 79.5941], "villages": {"Warangal Fort": [17.9542, 79.6175], "Geesugonda": [17.9421, 79.7120], "Atmakur": [18.1150, 79.7340], "Narsampet": [17.9245, 79.8961]}},
            "Hyderabad": {"coords": [17.3850, 78.4867], "villages": {"Rajendranagar": [17.3195, 78.4021], "Hayathnagar": [17.3292, 78.6015], "Secunderabad": [17.4399, 78.4983], "Medchal": [17.6294, 78.4813]}},
            "Karimnagar": {"coords": [18.4386, 79.1288], "villages": {"Karimnagar Rural": [18.4410, 79.1350], "Choppadandi": [18.5781, 79.1721], "Manakondur": [18.3912, 79.2014], "Huzurabad": [18.1915, 79.4081]}},
            "Nizamabad": {"coords": [18.6725, 78.0941], "villages": {"Armoor": [18.7885, 78.2881], "Bodhan": [18.6582, 77.8941], "Balkonda": [18.8612, 78.3410], "Dichpally": [18.5591, 78.2015]}},
            "Khammam": {"coords": [17.2473, 80.1514], "villages": {"Wyra": [17.1952, 80.3541], "Sathupally": [17.2140, 80.8321], "Kalluru": [17.2015, 80.5512], "Penuballi": [17.1812, 80.7105]}},
            "Nalgonda": {"coords": [17.0577, 79.2684], "villages": {"Miryalaguda": [16.8715, 79.5621], "Devarakonda": [16.6941, 78.9214], "Nakarakal": [17.2015, 79.4102], "Huzurnagar": [16.9012, 79.8712]}},
            "Adilabad": {"coords": [19.6641, 78.5320], "villages": {"Utnoor": [19.3621, 78.7891], "Boath": [19.3321, 78.3312], "Bela": [19.6812, 78.7901], "Jainath": [19.7412, 78.6214]}},
            "Bhadrachalam": {"coords": [17.6688, 80.8936], "villages": {"Bhadradri": [17.6710, 80.8990], "Manuguru": [17.9812, 80.7512], "Burgampahad": [17.6521, 80.8124], "Aswapuram": [17.7912, 80.8102]}}
        }
    },
    "Andhra Pradesh": {
        "coords": [15.9129, 79.7400],
        "districts": {
            "Vijayawada": {"coords": [16.5062, 80.6480], "villages": {"Kankipadu": [16.4421, 80.7812], "Gannavaram": [16.5412, 80.8015], "Penamaluru": [16.4712, 80.7214], "Ibrahimpatnam": [16.5912, 80.5124]}},
            "Guntur": {"coords": [16.3067, 80.4365], "villages": {"Tenali": [16.2431, 80.6412], "Narasaraopet": [16.2361, 80.0512], "Bapatla": [15.9042, 80.4671], "Mangalagiri": [16.4312, 80.5521]}},
            "Visakhapatnam": {"coords": [17.6868, 83.2185], "villages": {"Anakapalle": [17.6912, 83.0041], "Bheemunipatnam": [17.8912, 83.4412], "Pendurthi": [17.7612, 83.2014], "Narsipatnam": [17.6712, 82.6102]}},
            "Tirupati": {"coords": [13.6288, 79.4192], "villages": {"Chandragiri": [13.5812, 79.3124], "Srikalahasti": [13.7512, 79.7012], "Puttur": [13.4412, 79.5512], "Nagari": [13.3312, 79.5901]}},
            "Kurnool": {"coords": [15.8281, 78.0373], "villages": {"Nandyal": [15.4812, 78.4812], "Adoni": [15.6312, 77.2812], "Yemmiganur": [15.7712, 77.4812], "Dhone": [15.4012, 77.8812]}}
        }
    },
    "Punjab": {
        "coords": [31.1471, 75.3412],
        "districts": {
            "Ludhiana": {"coords": [30.9010, 75.8573], "villages": {"Jagraon": [30.7812, 75.4812], "Khanna": [30.7012, 76.2214], "Samrala": [30.8312, 76.1901], "Raikot": [30.6512, 75.6012]}},
            "Amritsar": {"coords": [31.6340, 74.8723], "villages": {"Ajnala": [31.8412, 74.7612], "Baba Bakala": [31.5512, 75.2612], "Majitha": [31.7612, 74.9612], "Attari": [31.6012, 74.6012]}},
            "Jalandhar": {"coords": [31.3260, 75.5762], "villages": {"Nakodar": [31.1212, 75.4812], "Phillaur": [31.0212, 75.7812], "Shahkot": [31.0812, 75.3412], "Kartarpur": [31.4412, 75.5012]}},
            "Bathinda": {"coords": [30.2110, 74.9455], "villages": {"Talwandi Sabo": [29.9812, 75.0812], "Rampur Phul": [30.2712, 75.2412], "Mauri": [30.0812, 75.2214], "Bhucho": [30.2512, 75.0512]}}
        }
    },
    "Maharashtra": {
        "coords": [19.7515, 75.7139],
        "districts": {
            "Nashik": {"coords": [19.9975, 73.7898], "villages": {"Niphad": [20.0812, 74.1102], "Malegaon": [20.5512, 74.5312], "Sinnar": [19.8512, 74.0012], "Yeola": [20.0412, 74.4812]}},
            "Pune": {"coords": [18.5204, 73.8567], "villages": {"Baramati": [18.1512, 74.5812], "Shirur": [18.8312, 74.3712], "Indapur": [18.1124, 75.0312], "Daund": [18.4612, 74.5912]}},
            "Nagpur": {"coords": [21.1458, 79.0882], "villages": {"Katol": [21.2812, 78.5812], "Saoner": [21.3812, 78.9102], "Umred": [20.8512, 79.3312], "Kalameshwar": [21.2312, 78.9124]}},
            "Aurangabad": {"coords": [19.8762, 75.3433], "villages": {"Paithan": [19.4812, 75.3812], "Gangapur": [19.7012, 75.0012], "Kannad": [20.2612, 75.1312], "Sillod": [20.3012, 75.6512]}}
        }
    },
    "Karnataka": {
        "coords": [15.3173, 75.7139],
        "districts": {
            "Mandya": {"coords": [12.5218, 76.8951], "villages": {"Maddur": [12.5812, 77.0412], "Pandavapura": [12.5012, 76.6712], "Malavalli": [12.3812, 77.0612], "Srirangapatna": [12.4212, 76.6912]}},
            "Belagavi": {"coords": [15.8497, 74.4977], "villages": {"Chikodi": [16.4312, 74.5912], "Gokak": [16.1612, 74.8312], "Bailhongal": [15.8124, 74.8512], "Athani": [16.7312, 75.0612]}},
            "Shimoga": {"coords": [13.9299, 75.5681], "villages": {"Bhadravathi": [13.8412, 75.7012], "Sagar": [14.1612, 75.0312], "Shikaripura": [14.2612, 75.3512], "Soraba": [14.3812, 75.1012]}}
        }
    },
    "Tamil Nadu": {
        "coords": [11.1271, 78.6569],
        "districts": {
            "Thanjavur": {"coords": [10.7870, 79.1378], "villages": {"Kumbakonam": [10.9612, 79.3812], "Orathanadu": [10.6214, 79.2512], "Papanasam": [10.9212, 79.2712], "Pattukkottai": [10.4312, 79.3124]}},
            "Coimbatore": {"coords": [11.0168, 76.9558], "villages": {"Pollachi": [10.6612, 77.0012], "Mettupalayam": [11.3012, 76.9412], "Sulur": [11.0312, 77.1214], "Anaimalai": [10.5812, 76.9312]}},
            "Madurai": {"coords": [9.9252, 78.1198], "villages": {"Melur": [10.0412, 78.3412], "Tirumangalam": [9.8212, 77.9912], "Usilampatti": [9.9712, 77.7912], "Vadipatti": [10.0812, 77.9612]}}
        }
    },
    "Uttar Pradesh": {
        "coords": [26.8467, 80.9462],
        "districts": {
            "Varanasi": {"coords": [25.3176, 82.9739], "villages": {"Pindra": [25.5312, 82.8312], "Rohaniya": [25.2612, 82.9412], "Sewapuri": [25.3412, 82.7812], "Cholapur": [25.4612, 83.0512]}},
            "Lucknow": {"coords": [26.8467, 80.9462], "villages": {"Malihabad": [26.9212, 80.7102], "Mohanlalganj": [26.6812, 80.9812], "Bakshi Ka Talab": [26.9812, 80.9312], "Gosainganj": [26.7712, 81.1214]}},
            "Kanpur": {"coords": [26.4499, 80.3319], "villages": {"Bilhour": [26.8512, 80.0612], "Ghatampur": [26.1512, 80.1612], "Chaubepur": [26.6112, 80.2012], "Kalyanpur": [26.5012, 80.2712]}}
        }
    },
    "Gujarat": {
        "coords": [22.2587, 71.1924],
        "districts": {
            "Anand": {"coords": [22.5645, 72.9289], "villages": {"Petlad": [22.4712, 72.8012], "Borsad": [22.4112, 72.9012], "Khambhat": [22.3112, 72.6102], "Umeta": [22.4512, 73.0214]}},
            "Surat": {"coords": [21.1702, 72.8311], "villages": {"Bardoli": [21.1212, 73.1102], "Kamrej": [21.2612, 72.9612], "Olpad": [21.3312, 72.7512], "Mahuva": [21.0212, 73.1612]}},
            "Rajkot": {"coords": [22.3039, 70.8022], "villages": {"Gondal": [21.9612, 70.8012], "Jetpur": [21.7612, 70.6214], "Jasdan": [22.0312, 71.2012], "Dhoraji": [21.7312, 70.4512]}}
        }
    },
    "Haryana": {
        "coords": [29.0588, 76.0856],
        "districts": {
            "Karnal": {"coords": [29.6857, 76.9905], "villages": {"Nilokheri": [29.8312, 76.9214], "Gharaunda": [29.5312, 76.9712], "Indri": [29.8812, 77.0612], "Assandh": [29.5212, 76.6012]}},
            "Hisar": {"coords": [29.1492, 75.7217], "villages": {"Hansi": [29.1012, 75.9612], "Barwala": [29.3612, 75.9102], "Narnaund": [29.2214, 76.1312], "Adampur": [29.2812, 75.4612]}}
        }
    },
    "Madhya Pradesh": {
        "coords": [22.9734, 78.6569],
        "districts": {
            "Indore": {"coords": [22.7196, 75.8577], "villages": {"Sanwer": [22.9712, 75.8312], "Depalpur": [22.8512, 75.5312], "Mhow": [22.5512, 75.7612], "Hatod": [22.8012, 75.7102]}},
            "Ujjain": {"coords": [23.1765, 75.7885], "villages": {"Nagda": [23.4512, 75.4102], "Khachrod": [23.4212, 75.2812], "Barnagar": [23.0512, 75.3712], "Tarana": [23.3312, 76.0412]}},
            "Hoshangabad": {"coords": [22.7519, 77.7289], "villages": {"Itarsi": [22.6112, 77.7612], "Pipariya": [22.7612, 78.3512], "Seoni Malwa": [22.4512, 77.4612], "Babai": [22.7012, 77.9312]}}
        }
    }
}

CROP_PROFILES = {
    "Rice": {"N": (280, 420), "P": (25, 45), "K": (150, 260), "pH": (5.5, 7.2), "temp": (24, 34), "humidity": (70, 90), "rainfall": (1000, 1800), "moisture": (50, 75), "yield": (3.5, 6.2)},
    "Wheat": {"N": (250, 380), "P": (20, 40), "K": (140, 240), "pH": (6.0, 7.5), "temp": (15, 26), "humidity": (50, 70), "rainfall": (450, 850), "moisture": (35, 55), "yield": (3.2, 5.5)},
    "Maize": {"N": (260, 400), "P": (22, 50), "K": (140, 250), "pH": (5.8, 7.4), "temp": (20, 32), "humidity": (55, 75), "rainfall": (500, 1000), "moisture": (40, 60), "yield": (4.0, 7.5)},
    "Cotton": {"N": (220, 350), "P": (18, 38), "K": (130, 230), "pH": (6.0, 8.0), "temp": (24, 36), "humidity": (45, 65), "rainfall": (600, 1100), "moisture": (30, 50), "yield": (2.2, 4.2)},
    "Groundnut": {"N": (140, 240), "P": (25, 55), "K": (120, 220), "pH": (5.8, 7.2), "temp": (22, 33), "humidity": (50, 75), "rainfall": (500, 900), "moisture": (35, 55), "yield": (2.0, 3.8)},
    "Soybean": {"N": (160, 260), "P": (28, 60), "K": (130, 240), "pH": (6.0, 7.2), "temp": (20, 30), "humidity": (60, 80), "rainfall": (650, 1100), "moisture": (40, 65), "yield": (2.2, 4.0)},
    "Sugarcane": {"N": (320, 480), "P": (30, 65), "K": (180, 320), "pH": (6.0, 7.8), "temp": (25, 38), "humidity": (65, 88), "rainfall": (1200, 2200), "moisture": (55, 80), "yield": (65.0, 110.0)},
    "Tomato": {"N": (220, 340), "P": (30, 65), "K": (160, 280), "pH": (6.0, 7.2), "temp": (18, 30), "humidity": (55, 75), "rainfall": (400, 800), "moisture": (40, 60), "yield": (25.0, 48.0)},
    "Chilli": {"N": (200, 320), "P": (25, 55), "K": (150, 260), "pH": (6.0, 7.5), "temp": (20, 34), "humidity": (50, 70), "rainfall": (500, 950), "moisture": (35, 55), "yield": (12.0, 24.0)},
    "Pulses": {"N": (120, 200), "P": (22, 50), "K": (100, 200), "pH": (6.2, 7.6), "temp": (18, 30), "humidity": (45, 65), "rainfall": (400, 750), "moisture": (30, 50), "yield": (1.2, 2.5)},
    "Mustard": {"N": (180, 300), "P": (20, 45), "K": (110, 210), "pH": (6.0, 7.5), "temp": (12, 25), "humidity": (40, 65), "rainfall": (350, 650), "moisture": (30, 50), "yield": (1.4, 2.8)},
    "Potato": {"N": (240, 380), "P": (35, 70), "K": (180, 320), "pH": (5.2, 6.8), "temp": (15, 24), "humidity": (60, 80), "rainfall": (450, 800), "moisture": (45, 65), "yield": (20.0, 38.0)}
}

LOCATION_DATA = {state: {dist: list(info["villages"].keys()) for dist, info in data["districts"].items()} for state, data in LOCATION_COORDINATES.items()}

def generate_sample_dataset(num_records=1600):
    """
    Generates realistic multi-state agricultural CSV dataset for training and dashboard analytics.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    np.random.seed(42)

    records = []
    states = list(LOCATION_DATA.keys())
    crops = list(CROP_PROFILES.keys())

    for i in range(num_records):
        state = np.random.choice(states, p=[0.25, 0.20, 0.10, 0.10, 0.08, 0.07, 0.06, 0.05, 0.05, 0.04])
        districts = list(LOCATION_DATA[state].keys())
        district = np.random.choice(districts)
        villages = LOCATION_DATA[state][district]
        village = np.random.choice(villages)

        crop = np.random.choice(crops)
        prof = CROP_PROFILES[crop]

        # Generate realistic values around crop optimal profile with natural variability
        use_optimal = np.random.rand() > 0.35
        
        if use_optimal:
            n = round(np.random.uniform(prof["N"][0] - 20, prof["N"][1] + 20), 1)
            p = round(np.random.uniform(prof["P"][0] - 5, prof["P"][1] + 10), 1)
            k = round(np.random.uniform(prof["K"][0] - 15, prof["K"][1] + 20), 1)
            ph = round(np.random.uniform(prof["pH"][0] - 0.3, prof["pH"][1] + 0.3), 2)
            temp = round(np.random.uniform(prof["temp"][0] - 2, prof["temp"][1] + 2), 1)
            humidity = round(np.random.uniform(prof["humidity"][0] - 5, prof["humidity"][1] + 5), 1)
            rainfall = round(np.random.uniform(prof["rainfall"][0] - 100, prof["rainfall"][1] + 150), 1)
            moisture = round(np.random.uniform(prof["moisture"][0] - 5, prof["moisture"][1] + 5), 1)
            yield_multiplier = np.random.uniform(0.9, 1.15)
        else:
            n = round(np.random.uniform(100, 480), 1)
            p = round(np.random.uniform(10, 75), 1)
            k = round(np.random.uniform(80, 360), 1)
            ph = round(np.random.uniform(4.8, 8.5), 2)
            temp = round(np.random.uniform(12, 40), 1)
            humidity = round(np.random.uniform(35, 95), 1)
            rainfall = round(np.random.uniform(250, 2200), 1)
            moisture = round(np.random.uniform(15, 80), 1)
            
            penalty = 1.0
            if not (prof["N"][0] <= n <= prof["N"][1]): penalty *= 0.82
            if not (prof["P"][0] <= p <= prof["P"][1]): penalty *= 0.88
            if not (prof["K"][0] <= k <= prof["K"][1]): penalty *= 0.88
            if not (prof["pH"][0] <= ph <= prof["pH"][1]): penalty *= 0.78
            if not (prof["temp"][0] <= temp <= prof["temp"][1]): penalty *= 0.80
            if not (prof["rainfall"][0] <= rainfall <= prof["rainfall"][1]): penalty *= 0.75
            yield_multiplier = max(0.35, penalty * np.random.uniform(0.6, 0.95))

        base_yield = np.random.uniform(prof["yield"][0], prof["yield"][1])
        crop_yield = round(base_yield * yield_multiplier, 2)
        oc = round(np.random.uniform(0.3, 1.35), 2)
        wind_speed = round(np.random.uniform(4.0, 24.0), 1)
        area_ha = round(np.random.uniform(0.5, 10.0), 1)

        # Get exact lat/lng for village with slight random jitter for field spread
        base_coords = LOCATION_COORDINATES[state]["districts"][district]["villages"][village]
        lat = round(base_coords[0] + np.random.uniform(-0.015, 0.015), 4)
        lng = round(base_coords[1] + np.random.uniform(-0.015, 0.015), 4)

        if rainfall > 1100:
            weather_cond = "Heavy Rain"
        elif rainfall > 700:
            weather_cond = "Moderate Rain / Humid"
        elif temp > 34:
            weather_cond = "Hot & Dry"
        elif temp < 18:
            weather_cond = "Cool & Clear"
        else:
            weather_cond = "Partly Cloudy / Ideal"

        records.append({
            "Record_ID": f"AGR-{1000 + i}",
            "State": state,
            "District": district,
            "Village": village,
            "Latitude": lat,
            "Longitude": lng,
            "Crop": crop,
            "Soil_pH": ph,
            "Nitrogen_N": n,
            "Phosphorus_P": p,
            "Potassium_K": k,
            "Organic_Carbon": oc,
            "Soil_Moisture": moisture,
            "Soil_Temp": temp,
            "Rainfall_mm": rainfall,
            "Temperature_C": temp,
            "Humidity_pct": humidity,
            "Wind_Speed_kmh": wind_speed,
            "Area_ha": area_ha,
            "Weather_Condition": weather_cond,
            "Crop_Yield_tonnes_ha": crop_yield
        })

    df = pd.DataFrame(records)
    df.to_csv(CSV_PATH, index=False)
    print(f"Dataset successfully generated with {len(df)} records at {CSV_PATH}")
    return df

def load_or_create_dataset():
    if not os.path.exists(CSV_PATH):
        return generate_sample_dataset()
    return pd.read_csv(CSV_PATH)

def train_models():
    """
    Trains Scikit-learn RandomForest models for Yield Prediction and Crop Recommendation.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)
    df = load_or_create_dataset()

    crop_dummies = pd.get_dummies(df["Crop"], prefix="Crop")
    
    feature_cols = [
        "Soil_pH", "Nitrogen_N", "Phosphorus_P", "Potassium_K",
        "Organic_Carbon", "Soil_Moisture", "Temperature_C", "Rainfall_mm",
        "Humidity_pct", "Area_ha"
    ]
    
    X_reg = pd.concat([df[feature_cols], crop_dummies], axis=1)
    y_reg = df["Crop_Yield_tonnes_ha"]

    X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)

    yield_model = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42)
    yield_model.fit(X_train_r, y_train_r)

    r2_score = round(yield_model.score(X_test_r, y_test_r), 3)

    X_clf = df[["Soil_pH", "Nitrogen_N", "Phosphorus_P", "Potassium_K", "Temperature_C", "Humidity_pct", "Rainfall_mm", "Soil_Moisture"]]
    y_clf = df["Crop"]

    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_clf, y_clf, test_size=0.2, random_state=42)

    crop_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    crop_model.fit(X_train_c, y_train_c)

    acc_score = round(crop_model.score(X_test_c, y_test_c), 3)

    joblib.dump({"model": yield_model, "columns": list(X_reg.columns), "r2": r2_score}, YIELD_MODEL_PATH)
    joblib.dump({"model": crop_model, "classes": list(crop_model.classes_), "acc": acc_score}, CROP_MODEL_PATH)

    return yield_model, crop_model

def get_trained_models():
    if not (os.path.exists(YIELD_MODEL_PATH) and os.path.exists(CROP_MODEL_PATH)):
        return train_models()
    try:
        yield_data = joblib.load(YIELD_MODEL_PATH)
        crop_data = joblib.load(CROP_MODEL_PATH)
        return yield_data, crop_data
    except Exception as e:
        return train_models()

if __name__ == "__main__":
    generate_sample_dataset()
    train_models()
