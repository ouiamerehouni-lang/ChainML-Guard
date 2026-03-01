"""
Compute data-driven thresholds from the training dataset for explainability.

This script:
1. Loads dataset_final.csv
2. Splits into train/test using the same split as train_model.py (80/20, random_state=42)
3. Computes percentile thresholds from the TRAINING set only
4. Saves thresholds to thresholds.json in the project root

Run this script once after training the model or when the dataset changes.
"""

import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split

# Load the dataset
print("Loading dataset_final.csv...")
try:
    df = pd.read_csv('data/dataset_final.csv')
    print(f"✓ Loaded {len(df)} records")
except FileNotFoundError:
    print("✗ Error: data/dataset_final.csv not found.")
    print("  Please ensure the dataset exists before running this script.")
    exit(1)

# Extract features and labels
X = df[['balance', 'tx_count', 'age_days']].values
y = df['is_fraud'].values

# Split using the SAME parameters as train_model.py
# This ensures we compute thresholds from the training set only
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"✓ Split into train ({len(X_train)}) and test ({len(X_test)}) sets")

# Create a DataFrame for easier percentile computation
train_df = pd.DataFrame(X_train, columns=['balance', 'tx_count', 'age_days'])

# Compute the activity rate (tx_count per day of wallet age)
# Use max(age, 1) to avoid division by zero
train_df['activity_rate'] = train_df['tx_count'] / train_df['age_days'].clip(lower=1)

print("\nComputing percentile thresholds from training data...")

# Compute thresholds based on data-driven percentiles
thresholds = {
    # Very new wallet: 10th percentile of wallet age
    "age_p10": float(np.percentile(train_df['age_days'], 10)),
    
    # Unusually high transaction count: 90th percentile
    "tx_p90": float(np.percentile(train_df['tx_count'], 90)),
    
    # Extreme balance indicators: 5th and 95th percentiles
    "bal_p05": float(np.percentile(train_df['balance'], 5)),
    "bal_p95": float(np.percentile(train_df['balance'], 95)),
    
    # High activity rate for wallet age: 90th percentile
    "rate_p90": float(np.percentile(train_df['activity_rate'], 90))
}

# Display the computed thresholds
print("\nComputed thresholds:")
print(f"  age_p10  (very new wallet):           {thresholds['age_p10']:.2f} days")
print(f"  tx_p90   (high tx count):             {thresholds['tx_p90']:.0f} transactions")
print(f"  bal_p05  (unusually low balance):     {thresholds['bal_p05']:.6f} ETH")
print(f"  bal_p95  (unusually high balance):    {thresholds['bal_p95']:.6f} ETH")
print(f"  rate_p90 (high activity rate):        {thresholds['rate_p90']:.4f} tx/day")

# Save to JSON file in the project root
output_path = 'thresholds.json'
with open(output_path, 'w') as f:
    json.dump(thresholds, f, indent=4)

print(f"\n✓ Thresholds saved to {output_path}")
print("\nYou can now run the Flask app (app.py) to use these thresholds for explanations.")
