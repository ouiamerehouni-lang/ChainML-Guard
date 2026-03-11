"""
Logistic Regression Training Script for ChainML Guard
======================================================
Trains a Logistic Regression baseline model using the same dataset,
features, split, and preprocessing as the MLP model.

Features: balance, tx_count, age_days (3 features)
Label: is_fraud (0=legit, 1=fraud)
Split: 80/20 stratified with random_state=42
"""

import pandas as pd
import numpy as np
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Set random seeds for reproducibility
np.random.seed(42)

print("="*60)
print("LOGISTIC REGRESSION TRAINING - ChainML Guard")
print("="*60)

# 1. LOAD DATASET
print("\n[1/5] Loading dataset...")
try:
    df = pd.read_csv('data/dataset_final.csv')
    print(f"✓ Dataset loaded: {len(df)} total records")
except FileNotFoundError:
    print("✗ Error: data/dataset_final.csv not found.")
    exit(1)

# 2. FEATURE EXTRACTION
print("\n[2/5] Extracting features and labels...")
X = df[['balance', 'tx_count', 'age_days']].values
y = df['is_fraud'].values

# Count class distribution
n_fraud = (y == 1).sum()
n_legit = (y == 0).sum()
print(f"✓ Features extracted: 3 features (balance, tx_count, age_days)")
print(f"✓ Label distribution:")
print(f"   - Legitimate (0): {n_legit} ({n_legit/len(y)*100:.1f}%)")
print(f"   - Fraudulent (1): {n_fraud} ({n_fraud/len(y)*100:.1f}%)")

# 3. TRAIN/TEST SPLIT (SAME AS MLP)
print("\n[3/5] Splitting data (80/20 stratified, random_state=42)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"✓ Train set: {len(X_train)} samples")
print(f"✓ Test set:  {len(X_test)} samples")

# 4. PREPROCESSING (FIT ON TRAIN ONLY)
print("\n[4/5] Scaling features (StandardScaler fit on train)...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("✓ Features scaled (zero mean, unit variance)")

# 5. TRAIN LOGISTIC REGRESSION
print("\n[5/5] Training Logistic Regression model...")
logreg = LogisticRegression(
    max_iter=1000,
    random_state=42,
    solver='lbfgs',
    class_weight='balanced'  # Handle class imbalance if present
)
logreg.fit(X_train_scaled, y_train)
print("✓ Model training complete")

# 6. EVALUATE ON TEST SET
print("\n" + "="*60)
print("TRAINING RESULTS")
print("="*60)

y_test_pred = logreg.predict(X_test_scaled)
test_accuracy = accuracy_score(y_test, y_test_pred)

print(f"\n✓ Test Accuracy: {test_accuracy*100:.2f}%")
print("\nClassification Report (Test Set):")
print(classification_report(y_test, y_test_pred, 
                          target_names=['Legitimate', 'Fraudulent'],
                          digits=4))

# 7. SAVE MODEL ARTIFACTS
print("\n" + "="*60)
print("SAVING MODEL ARTIFACTS")
print("="*60)

os.makedirs('models/logreg', exist_ok=True)

# Save model
model_path = 'models/logreg/model.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(logreg, f)
print(f"✓ Model saved: {model_path}")

# Save scaler
scaler_path = 'models/logreg/scaler.pkl'
with open(scaler_path, 'wb') as f:
    pickle.dump(scaler, f)
print(f"✓ Scaler saved: {scaler_path}")

print("\n" + "="*60)
print("✓ LOGISTIC REGRESSION TRAINING COMPLETE")
print("="*60)
