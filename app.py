from flask import Flask, render_template, request, jsonify
import numpy as np
import pickle
import os
import json
from tensorflow.keras.models import load_model
from datetime import datetime
from data_collection import get_address_features 

app = Flask(__name__)

# CONFIGURATION AND PATHS
MODEL_PATH = 'models/fraud_model.h5'
SCALER_PATH = 'models/scaler.pkl'
HISTORY_FILE = 'history.json'

# 1. AI LOADING
if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
    model = load_model(MODEL_PATH)
    with open(SCALER_PATH, 'rb') as f:
        scaler = pickle.load(f)
    print("AI and Scaler loaded successfully.")
else:
    model = None
    scaler = None
    print("Error: AI files not found.")

# REAL SAVE FUNCTION
def save_to_history(address, score, is_fraud):
    """Saves the analysis into a JSON file for the dashboard"""
    new_entry = {
        "address": address,
        "reason": "Fraud Detected" if is_fraud else "Approved",
        "tech_detail": f"AI Analysis: {score}% risk score based on transactional flows.",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_fraud": is_fraud
    }
    
    data = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                data = json.load(f)
        except:
            data = []
    
    data.insert(0, new_entry)  # Add entry at the top of the list
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# 2. ROUTES

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    address = request.form.get('address', '').strip()
    amount = request.form.get('amount', '').strip()
    
    if not address.startswith('0x') or len(address) != 42:
        return render_template('index.html', error="Invalid address format.")

    # A. Real data retrieval
    raw_features = get_address_features(address)
    if raw_features is None:
        return render_template('index.html', error="Unable to reach the blockchain.")

    # B. AI prediction
    input_scaled = scaler.transform(np.array([raw_features]))
    prediction_prob = model.predict(input_scaled)[0][0]
    risk_score = round(float(prediction_prob) * 100, 2)
    
    # C. Binary decision logic (Legitimate or Fraud)
    # Threshold set to 50%
    is_fraud = risk_score >= 50
    
    if is_fraud:
        result_text, result_color = "DANGER: Fraud detected", "#dc2626"
    else:
        result_text, result_color = "HEALTHY: No fraud pattern detected", "#16a34a"

    # D. Save results for the dashboard
    save_to_history(address, risk_score, is_fraud)

    return render_template(
        'index.html', 
        address=address,
        amount=amount, 
        score=risk_score,
        status=result_text, 
        color=result_color,
        balance=raw_features[0],
        txs=raw_features[1],
        age=raw_features[2]
    )

@app.route('/dashboard')
def dashboard():
    # Load analysis history
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)

    # Filtering: show only detected frauds in the table
    frauds_only = [item for item in history if item['is_fraud']]
    
    # Statistics calculation for charts (real data)
    total_frauds = len(frauds_only)
    total_sains = len([item for item in history if not item['is_fraud']])

    return render_template(
        'dashboard.html', 
        blacklist=frauds_only,
        total_frauds=total_frauds,
        total_sains=total_sains
    )

# 3. APPLICATION LAUNCH
if __name__ == '__main__':
    app.run(debug=True, port=5000)
