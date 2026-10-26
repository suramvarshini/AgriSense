"""
AgriSense - Precision Agriculture Analytics Platform Launcher Script
Initializes dataset, trains ML models if required, starts Flask API backend, and opens web dashboard.
"""

import os
import sys
import webbrowser
import threading
import time

def launch():
    print("=" * 70)
    print("  AgriSense - Precision Agriculture Analytics Platform Launcher")
    print("=" * 70)

    # 1. Add current directory to Python Path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, base_dir)

    # 2. Check and ensure dataset and models exist
    from backend.model import load_or_create_dataset, get_trained_models
    print("\n[1/3] Verifying agricultural dataset and ML models...")
    df = load_or_create_dataset()
    print(f"      Dataset loaded successfully ({len(df)} records).")
    get_trained_models()
    print("      Scikit-learn ML models ready.")

    # 3. Auto-open browser after 1.5s
    def open_browser():
        time.sleep(1.5)
        url = "http://localhost:5000"
        print(f"\n[3/3] Opening AgriSense Dashboard in browser at {url}")
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()

    # 4. Start Flask Server
    print("\n[2/3] Starting Flask Backend Server on http://localhost:5000 ...")
    from backend.app import app
    app.run(host="0.0.0.0", port=5000, debug=False)

if __name__ == "__main__":
    launch()
