"""
AgriSense - WSGI entry point for Render/Gunicorn deployment.
Initializes dataset and ML models, then exports the Flask app object.
"""

import os
import sys

# Ensure project root is in Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Pre-load dataset and models at startup
from backend.model import load_or_create_dataset, get_trained_models

load_or_create_dataset()
get_trained_models()

# Export Flask app for gunicorn (Procfile: gunicorn wsgi:app)
from backend.app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
