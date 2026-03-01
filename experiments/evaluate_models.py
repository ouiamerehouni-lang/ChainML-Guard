"""
Unified Model Evaluation Script for ChainML Guard
==================================================
Evaluates all three models (MLP, Logistic Regression, Random Forest)
on the same test set with consistent metrics.

Metrics computed:
- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC
- Confusion Matrix

All models use the same dataset split (random_state=42, 80/20 stratified).
"""

import pandas as pd
import numpy as np
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from tensorflow.keras.models import load_model
import warnings
warnings.filterwarnings('ignore')

# Set random seeds for reproducibility
np.random.seed(42)

print("="*70)
print("UNIFIED MODEL EVALUATION - ChainML Guard")
print("="*70)

# 1. LOAD DATASET
print("\n[1/3] Loading dataset and creating test split...")
try:
    df = pd.read_csv('data/dataset_final.csv')
    print(f"✓ Dataset loaded: {len(df)} total records")
except FileNotFoundError:
    print("✗ Error: data/dataset_final.csv not found.")
    exit(1)

# Extract features and labels
X = df[['balance', 'tx_count', 'age_days']].values
y = df['is_fraud'].values

# Count class distribution
n_fraud = (y == 1).sum()
n_legit = (y == 0).sum()
print(f"✓ Class distribution: {n_legit} legitimate ({n_legit/len(y)*100:.1f}%), "
      f"{n_fraud} fraudulent ({n_fraud/len(y)*100:.1f}%)")

# CRITICAL: Use the exact same split as training (random_state=42, 80/20 stratified)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"✓ Test set: {len(X_test)} samples (20% of data)")

# 2. LOAD MODELS
print("\n[2/3] Loading trained models...")

models = {}
results = []

# ----- MLP Model -----
try:
    # Check both old and new paths
    if os.path.exists('models/mlp/model.h5'):
        mlp_model = load_model('models/mlp/model.h5')
        mlp_scaler_path = 'models/mlp/scaler.pkl'
    elif os.path.exists('models/fraud_model.h5'):
        mlp_model = load_model('models/fraud_model.h5')
        mlp_scaler_path = 'models/scaler.pkl'
    else:
        raise FileNotFoundError("MLP model not found")
    
    with open(mlp_scaler_path, 'rb') as f:
        mlp_scaler = pickle.load(f)
    
    models['MLP'] = {
        'model': mlp_model,
        'scaler': mlp_scaler,
        'needs_scaling': True
    }
    print("✓ MLP model loaded")
except Exception as e:
    print(f"✗ Failed to load MLP model: {e}")

# ----- Logistic Regression -----
try:
    with open('models/logreg/model.pkl', 'rb') as f:
        logreg_model = pickle.load(f)
    with open('models/logreg/scaler.pkl', 'rb') as f:
        logreg_scaler = pickle.load(f)
    
    models['Logistic Regression'] = {
        'model': logreg_model,
        'scaler': logreg_scaler,
        'needs_scaling': True
    }
    print("✓ Logistic Regression model loaded")
except Exception as e:
    print(f"✗ Failed to load Logistic Regression: {e}")

# ----- Random Forest -----
try:
    with open('models/rf/model.pkl', 'rb') as f:
        rf_model = pickle.load(f)
    
    models['Random Forest'] = {
        'model': rf_model,
        'scaler': None,
        'needs_scaling': False  # RF doesn't need scaling
    }
    print("✓ Random Forest model loaded")
except Exception as e:
    print(f"✗ Failed to load Random Forest: {e}")

if not models:
    print("\n✗ No models loaded. Please train models first.")
    exit(1)

# 3. EVALUATE ALL MODELS
print("\n[3/3] Evaluating models on test set...")
print("\n" + "="*70)
print("EVALUATION RESULTS")
print("="*70)

for model_name, model_info in models.items():
    print(f"\n{'─'*70}")
    print(f"Model: {model_name}")
    print(f"{'─'*70}")
    
    try:
        # Prepare test data
        if model_info['needs_scaling']:
            X_test_processed = model_info['scaler'].transform(X_test)
        else:
            X_test_processed = X_test
        
        # Get predictions
        model = model_info['model']
        
        # For MLP (Keras), predictions are different
        if model_name == 'MLP':
            y_pred_prob = model.predict(X_test_processed, verbose=0).flatten()
            y_pred = (y_pred_prob >= 0.5).astype(int)
        else:
            y_pred_prob = model.predict_proba(X_test_processed)[:, 1]
            y_pred = model.predict(X_test_processed)
        
        # Compute metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_pred_prob)
        cm = confusion_matrix(y_test, y_pred)
        
        # Store results
        results.append({
            'Model': model_name,
            'Accuracy': accuracy,
            'Precision': precision,
            'Recall': recall,
            'F1 Score': f1,
            'ROC-AUC': roc_auc
        })
        
        # Print metrics
        print(f"\nMetrics (threshold=0.5):")
        print(f"  Accuracy:  {accuracy*100:6.2f}%")
        print(f"  Precision: {precision*100:6.2f}%")
        print(f"  Recall:    {recall*100:6.2f}%")
        print(f"  F1 Score:  {f1*100:6.2f}%")
        print(f"  ROC-AUC:   {roc_auc:6.4f}")
        
        # Print confusion matrix
        print(f"\nConfusion Matrix:")
        print(f"                    Predicted")
        print(f"                  Legit  Fraud")
        print(f"  Actual  Legit    {cm[0,0]:4d}   {cm[0,1]:4d}")
        print(f"          Fraud    {cm[1,0]:4d}   {cm[1,1]:4d}")
        
        # Classification report
        print(f"\nDetailed Classification Report:")
        print(classification_report(y_test, y_pred, 
                                  target_names=['Legitimate', 'Fraudulent'],
                                  digits=4))
        
    except Exception as e:
        print(f"✗ Error evaluating {model_name}: {e}")
        import traceback
        traceback.print_exc()

# 4. SUMMARY TABLE
print("\n" + "="*70)
print("SUMMARY: MODEL COMPARISON")
print("="*70)

if results:
    results_df = pd.DataFrame(results)
    
    # Format as percentage for better readability
    print("\n" + results_df.to_string(index=False, 
                                      float_format=lambda x: f'{x*100:.2f}%' 
                                      if x < 1.1 else f'{x:.4f}'))
    
    # Save to CSV
    os.makedirs('results', exist_ok=True)
    csv_path = 'results/metrics.csv'
    results_df.to_csv(csv_path, index=False)
    print(f"\n✓ Results saved to: {csv_path}")
    
    # Identify best model for each metric
    print("\n" + "─"*70)
    print("Best Model per Metric:")
    print("─"*70)
    for metric in ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'ROC-AUC']:
        best_idx = results_df[metric].idxmax()
        best_model = results_df.loc[best_idx, 'Model']
        best_value = results_df.loc[best_idx, metric]
        print(f"  {metric:12s}: {best_model:20s} ({best_value*100:.2f}%)")

print("\n" + "="*70)
print("✓ EVALUATION COMPLETE")
print("="*70)
