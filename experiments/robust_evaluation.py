"""
Robust Evaluation Script for ChainML Guard
===========================================
Paper-quality robustness evaluation including:
- 5-fold stratified cross-validation
- Repeated random splits (10 different seeds)
- Duplicate detection and sanity checks
- Label shuffle baseline test

Ensures no data leakage and reproducible results.
"""

import pandas as pd
import numpy as np
import os
import pickle
import random
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    precision_score, recall_score, f1_score, 
    roc_auc_score, accuracy_score
)
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
import tensorflow as tf
import warnings
warnings.filterwarnings('ignore')

# Set global random seeds for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)

print("="*80)
print("ROBUST EVALUATION FOR CHAINML GUARD")
print("="*80)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_mlp_model():
    """
    Create MLP model with exact same architecture as train_model.py:
    - Dense(16, relu, he_normal)
    - Dropout(0.3)
    - Dense(8, relu)
    - Dense(1, sigmoid)
    """
    model = Sequential([
        Dense(16, input_dim=3, activation='relu', kernel_initializer='he_normal'),
        Dropout(0.3),
        Dense(8, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    model.compile(
        loss='binary_crossentropy',
        optimizer=Adam(learning_rate=0.001),
        metrics=['accuracy']
    )
    return model


def train_and_evaluate_logreg(X_train, y_train, X_test, y_test):
    """Train Logistic Regression with scaling (fit on train only)"""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED, 
                               class_weight='balanced')
    model.fit(X_train_scaled, y_train)
    
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    return {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1': f1_score(y_test, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, y_pred_proba)
    }


def train_and_evaluate_rf(X_train, y_train, X_test, y_test):
    """Train Random Forest (no scaling needed)"""
    model = RandomForestClassifier(
        n_estimators=100, 
        max_depth=10, 
        random_state=RANDOM_SEED,
        class_weight='balanced',
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    return {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1': f1_score(y_test, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, y_pred_proba)
    }


def train_and_evaluate_mlp(X_train, y_train, X_test, y_test, verbose=0):
    """Train MLP with exact same settings as train_model.py"""
    # Set TF seed for this training run
    tf.random.set_seed(RANDOM_SEED)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = create_mlp_model()
    
    # Train with same parameters as train_model.py
    model.fit(
        X_train_scaled, y_train,
        epochs=120,
        batch_size=16,
        validation_split=0.1,  # Use validation split instead of validation_data
        shuffle=True,
        verbose=verbose
    )
    
    y_pred_proba = model.predict(X_test_scaled, verbose=0).flatten()
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    return {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1': f1_score(y_test, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, y_pred_proba)
    }


# ============================================================================
# 1. LOAD DATASET
# ============================================================================

print("\n[Step 1/5] Loading dataset...")
try:
    df = pd.read_csv('data/dataset_final.csv')
    print(f"✓ Dataset loaded: {len(df)} records")
except FileNotFoundError:
    print("✗ Error: data/dataset_final.csv not found.")
    exit(1)

X = df[['balance', 'tx_count', 'age_days']].values
y = df['is_fraud'].values

n_fraud = (y == 1).sum()
n_legit = (y == 0).sum()
print(f"✓ Class distribution: {n_legit} legitimate ({n_legit/len(y)*100:.1f}%), "
      f"{n_fraud} fraudulent ({n_fraud/len(y)*100:.1f}%)")

# Create output directory
os.makedirs('results/robust_eval', exist_ok=True)


# ============================================================================
# 2. DUPLICATE DETECTION & SANITY CHECKS
# ============================================================================

print("\n[Step 2/5] Running sanity checks (duplicate detection)...")

with open('results/robust_eval/duplicate_report.txt', 'w') as f:
    f.write("="*80 + "\n")
    f.write("DUPLICATE DETECTION REPORT\n")
    f.write("="*80 + "\n\n")
    
    # Check duplicate addresses
    dup_addresses = df['address'].duplicated().sum()
    f.write(f"1. Duplicate Addresses: {dup_addresses}\n")
    if dup_addresses > 0:
        f.write(f"   Duplicate address list:\n")
        dup_addr_list = df[df['address'].duplicated(keep=False)]['address'].unique()
        for addr in dup_addr_list[:10]:  # Show first 10
            f.write(f"   - {addr}\n")
    
    # Check duplicate full rows
    dup_rows = df.duplicated().sum()
    f.write(f"\n2. Duplicate Full Rows: {dup_rows}\n")
    
    # Check duplicate feature rows (excluding address)
    feature_df = df[['balance', 'tx_count', 'age_days', 'is_fraud']]
    dup_features = feature_df.duplicated().sum()
    f.write(f"\n3. Duplicate Feature Rows (balance, tx_count, age_days, is_fraud): {dup_features}\n")
    
    # Check duplicate features only (without label)
    feature_only_df = df[['balance', 'tx_count', 'age_days']]
    dup_features_only = feature_only_df.duplicated().sum()
    f.write(f"\n4. Duplicate Feature Rows (without label): {dup_features_only}\n")
    
    # Summary
    f.write("\n" + "="*80 + "\n")
    f.write("SUMMARY\n")
    f.write("="*80 + "\n")
    f.write(f"Total records: {len(df)}\n")
    f.write(f"Unique addresses: {df['address'].nunique()}\n")
    f.write(f"Unique feature combinations: {feature_only_df.drop_duplicates().shape[0]}\n")
    
    if dup_addresses == 0 and dup_rows == 0:
        f.write("\n✓ No duplicates found. Dataset is clean.\n")
    else:
        f.write("\n⚠ Duplicates detected. Review above for details.\n")

print("✓ Duplicate report saved to: results/robust_eval/duplicate_report.txt")


# ============================================================================
# 3. 5-FOLD CROSS-VALIDATION
# ============================================================================

print("\n[Step 3/5] Running 5-fold stratified cross-validation...")
print("   (This will take several minutes due to MLP training...)")

cv_results = {
    'Logistic Regression': [],
    'Random Forest': [],
    'MLP': []
}

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)

for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X, y), 1):
    print(f"   Fold {fold_idx}/5...", end=' ', flush=True)
    
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    # Logistic Regression
    metrics = train_and_evaluate_logreg(X_train, y_train, X_test, y_test)
    cv_results['Logistic Regression'].append(metrics)
    
    # Random Forest
    metrics = train_and_evaluate_rf(X_train, y_train, X_test, y_test)
    cv_results['Random Forest'].append(metrics)
    
    # MLP
    metrics = train_and_evaluate_mlp(X_train, y_train, X_test, y_test, verbose=0)
    cv_results['MLP'].append(metrics)
    
    print("✓")

print("✓ 5-fold CV complete")

# Save raw CV results
cv_raw_data = []
for model_name, folds in cv_results.items():
    for fold_idx, metrics in enumerate(folds, 1):
        row = {'model': model_name, 'fold': fold_idx}
        row.update(metrics)
        cv_raw_data.append(row)

cv_raw_df = pd.DataFrame(cv_raw_data)
cv_raw_df.to_csv('results/robust_eval/cv_5fold_raw.csv', index=False)
print("✓ Raw CV results saved to: results/robust_eval/cv_5fold_raw.csv")

# Compute CV summary (mean ± std)
cv_summary_data = []
for model_name, folds in cv_results.items():
    for metric in ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']:
        values = [fold[metric] for fold in folds]
        cv_summary_data.append({
            'model': model_name,
            'metric': metric,
            'mean': np.mean(values),
            'std': np.std(values)
        })

cv_summary_df = pd.DataFrame(cv_summary_data)
cv_summary_df.to_csv('results/robust_eval/cv_5fold_summary.csv', index=False)
print("✓ CV summary saved to: results/robust_eval/cv_5fold_summary.csv")


# ============================================================================
# 4. REPEATED RANDOM SPLITS
# ============================================================================

print("\n[Step 4/5] Running repeated random splits (10 seeds)...")
print("   (This will also take several minutes...)")

repeated_results = {
    'Logistic Regression': [],
    'Random Forest': [],
    'MLP': []
}

seeds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

for seed_idx, seed in enumerate(seeds, 1):
    print(f"   Seed {seed_idx}/10 (seed={seed})...", end=' ', flush=True)
    
    # Set seed for this split
    np.random.seed(seed)
    random.seed(seed)
    tf.random.set_seed(seed)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed, stratify=y
    )
    
    # Logistic Regression
    metrics = train_and_evaluate_logreg(X_train, y_train, X_test, y_test)
    repeated_results['Logistic Regression'].append(metrics)
    
    # Random Forest
    metrics = train_and_evaluate_rf(X_train, y_train, X_test, y_test)
    repeated_results['Random Forest'].append(metrics)
    
    # MLP
    metrics = train_and_evaluate_mlp(X_train, y_train, X_test, y_test, verbose=0)
    repeated_results['MLP'].append(metrics)
    
    print("✓")

print("✓ Repeated splits complete")

# Save raw repeated splits results
repeated_raw_data = []
for model_name, runs in repeated_results.items():
    for seed_idx, metrics in enumerate(runs):
        row = {'model': model_name, 'seed': seeds[seed_idx]}
        row.update(metrics)
        repeated_raw_data.append(row)

repeated_raw_df = pd.DataFrame(repeated_raw_data)
repeated_raw_df.to_csv('results/robust_eval/repeated_splits_raw.csv', index=False)
print("✓ Raw repeated splits results saved to: results/robust_eval/repeated_splits_raw.csv")

# Compute repeated splits summary (mean ± std)
repeated_summary_data = []
for model_name, runs in repeated_results.items():
    for metric in ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']:
        values = [run[metric] for run in runs]
        repeated_summary_data.append({
            'model': model_name,
            'metric': metric,
            'mean': np.mean(values),
            'std': np.std(values)
        })

repeated_summary_df = pd.DataFrame(repeated_summary_data)
repeated_summary_df.to_csv('results/robust_eval/repeated_splits_summary.csv', index=False)
print("✓ Repeated splits summary saved to: results/robust_eval/repeated_splits_summary.csv")


# ============================================================================
# 5. LABEL SHUFFLE TEST (SANITY CHECK)
# ============================================================================

print("\n[Step 5/5] Running label shuffle test (sanity check)...")

# Reset seed
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)

# Shuffle labels
y_shuffled = y.copy()
np.random.shuffle(y_shuffled)

# Split (stratify not meaningful after shuffle, so omit)
X_train, X_test, y_train_shuf, y_test_shuf = train_test_split(
    X, y_shuffled, test_size=0.2, random_state=RANDOM_SEED
)

with open('results/robust_eval/label_shuffle_report.txt', 'w') as f:
    f.write("="*80 + "\n")
    f.write("LABEL SHUFFLE TEST REPORT\n")
    f.write("="*80 + "\n")
    f.write("This test trains models on randomly shuffled labels.\n")
    f.write("Expected: All metrics should be around random chance (~50% for balanced data).\n")
    f.write("If models still achieve high performance, there may be data leakage.\n")
    f.write("\n")
    
    # Train Logistic Regression on shuffled labels
    print("   Training Logistic Regression on shuffled labels...", end=' ', flush=True)
    logreg_shuf = train_and_evaluate_logreg(X_train, y_train_shuf, X_test, y_test_shuf)
    print("✓")
    
    f.write("Logistic Regression (shuffled labels):\n")
    f.write(f"  Accuracy:  {logreg_shuf['accuracy']*100:6.2f}%\n")
    f.write(f"  Precision: {logreg_shuf['precision']*100:6.2f}%\n")
    f.write(f"  Recall:    {logreg_shuf['recall']*100:6.2f}%\n")
    f.write(f"  F1 Score:  {logreg_shuf['f1']*100:6.2f}%\n")
    f.write(f"  ROC-AUC:   {logreg_shuf['roc_auc']:.4f}\n")
    f.write("\n")
    
    # Train Random Forest on shuffled labels
    print("   Training Random Forest on shuffled labels...", end=' ', flush=True)
    rf_shuf = train_and_evaluate_rf(X_train, y_train_shuf, X_test, y_test_shuf)
    print("✓")
    
    f.write("Random Forest (shuffled labels):\n")
    f.write(f"  Accuracy:  {rf_shuf['accuracy']*100:6.2f}%\n")
    f.write(f"  Precision: {rf_shuf['precision']*100:6.2f}%\n")
    f.write(f"  Recall:    {rf_shuf['recall']*100:6.2f}%\n")
    f.write(f"  F1 Score:  {rf_shuf['f1']*100:6.2f}%\n")
    f.write(f"  ROC-AUC:   {rf_shuf['roc_auc']:.4f}\n")
    f.write("\n")
    
    f.write("="*80 + "\n")
    f.write("INTERPRETATION\n")
    f.write("="*80 + "\n")
    f.write("If ROC-AUC is close to 0.5 and F1 is low, the models are NOT learning from\n")
    f.write("data leakage. This is the expected behavior for shuffled labels.\n")
    f.write("\n")
    f.write("If performance is still high (>70% F1, >0.7 AUC), investigate for:\n")
    f.write("- Feature leakage (features that directly encode the label)\n")
    f.write("- Data leakage (test samples in training set)\n")
    f.write("- Duplicate rows\n")

print("✓ Label shuffle report saved to: results/robust_eval/label_shuffle_report.txt")


# ============================================================================
# 6. SUMMARY TABLE (PAPER-READY)
# ============================================================================

print("\n" + "="*80)
print("ROBUST EVALUATION SUMMARY")
print("="*80)

print("\nDataset Information:")
print(f"  Total samples: {len(df)}")
print(f"  Legitimate: {n_legit} ({n_legit/len(y)*100:.1f}%)")
print(f"  Fraudulent: {n_fraud} ({n_fraud/len(y)*100:.1f}%)")
print(f"  Features: balance, tx_count, age_days (3 features)")

print("\n" + "-"*80)
print("Cross-Validation Results (5-Fold Stratified)")
print("-"*80)

# Create CV summary table
cv_pivot = cv_summary_df.pivot(index='model', columns='metric', values=['mean', 'std'])
print("\nModel Performance (Mean ± Std):")
for model in ['Logistic Regression', 'Random Forest', 'MLP']:
    f1_mean = cv_summary_df[(cv_summary_df['model']==model) & (cv_summary_df['metric']=='f1')]['mean'].values[0]
    f1_std = cv_summary_df[(cv_summary_df['model']==model) & (cv_summary_df['metric']=='f1')]['std'].values[0]
    auc_mean = cv_summary_df[(cv_summary_df['model']==model) & (cv_summary_df['metric']=='roc_auc')]['mean'].values[0]
    auc_std = cv_summary_df[(cv_summary_df['model']==model) & (cv_summary_df['metric']=='roc_auc')]['std'].values[0]
    acc_mean = cv_summary_df[(cv_summary_df['model']==model) & (cv_summary_df['metric']=='accuracy')]['mean'].values[0]
    acc_std = cv_summary_df[(cv_summary_df['model']==model) & (cv_summary_df['metric']=='accuracy')]['std'].values[0]
    
    print(f"\n{model}:")
    print(f"  Accuracy: {acc_mean*100:.2f}% ± {acc_std*100:.2f}%")
    print(f"  F1 Score: {f1_mean*100:.2f}% ± {f1_std*100:.2f}%")
    print(f"  ROC-AUC:  {auc_mean:.4f} ± {auc_std:.4f}")

print("\n" + "-"*80)
print("Repeated Random Splits Results (10 seeds)")
print("-"*80)

print("\nModel Performance (Mean ± Std):")
for model in ['Logistic Regression', 'Random Forest', 'MLP']:
    f1_mean = repeated_summary_df[(repeated_summary_df['model']==model) & (repeated_summary_df['metric']=='f1')]['mean'].values[0]
    f1_std = repeated_summary_df[(repeated_summary_df['model']==model) & (repeated_summary_df['metric']=='f1')]['std'].values[0]
    auc_mean = repeated_summary_df[(repeated_summary_df['model']==model) & (repeated_summary_df['metric']=='roc_auc')]['mean'].values[0]
    auc_std = repeated_summary_df[(repeated_summary_df['model']==model) & (repeated_summary_df['metric']=='roc_auc')]['std'].values[0]
    acc_mean = repeated_summary_df[(repeated_summary_df['model']==model) & (repeated_summary_df['metric']=='accuracy')]['mean'].values[0]
    acc_std = repeated_summary_df[(repeated_summary_df['model']==model) & (repeated_summary_df['metric']=='accuracy')]['std'].values[0]
    
    print(f"\n{model}:")
    print(f"  Accuracy: {acc_mean*100:.2f}% ± {acc_std*100:.2f}%")
    print(f"  F1 Score: {f1_mean*100:.2f}% ± {f1_std*100:.2f}%")
    print(f"  ROC-AUC:  {auc_mean:.4f} ± {auc_std:.4f}")

print("\n" + "-"*80)
print("Compact Summary Table (Paper-Ready)")
print("-"*80)
print(f"\n{'Model':<20} | {'CV F1':>15} | {'CV AUC':>15} | {'RepSplit F1':>15} | {'RepSplit AUC':>15}")
print("-"*106)

for model in ['Logistic Regression', 'Random Forest', 'MLP']:
    cv_f1_mean = cv_summary_df[(cv_summary_df['model']==model) & (cv_summary_df['metric']=='f1')]['mean'].values[0]
    cv_f1_std = cv_summary_df[(cv_summary_df['model']==model) & (cv_summary_df['metric']=='f1')]['std'].values[0]
    cv_auc_mean = cv_summary_df[(cv_summary_df['model']==model) & (cv_summary_df['metric']=='roc_auc')]['mean'].values[0]
    cv_auc_std = cv_summary_df[(cv_summary_df['model']==model) & (cv_summary_df['metric']=='roc_auc')]['std'].values[0]
    
    rep_f1_mean = repeated_summary_df[(repeated_summary_df['model']==model) & (repeated_summary_df['metric']=='f1')]['mean'].values[0]
    rep_f1_std = repeated_summary_df[(repeated_summary_df['model']==model) & (repeated_summary_df['metric']=='f1')]['std'].values[0]
    rep_auc_mean = repeated_summary_df[(repeated_summary_df['model']==model) & (repeated_summary_df['metric']=='roc_auc')]['mean'].values[0]
    rep_auc_std = repeated_summary_df[(repeated_summary_df['model']==model) & (repeated_summary_df['metric']=='roc_auc')]['std'].values[0]
    
    print(f"{model:<20} | {cv_f1_mean:.3f}±{cv_f1_std:.3f} | {cv_auc_mean:.4f}±{cv_auc_std:.4f} | "
          f"{rep_f1_mean:.3f}±{rep_f1_std:.3f} | {rep_auc_mean:.4f}±{rep_auc_std:.4f}")

print("\n" + "="*80)
print("✓ ROBUST EVALUATION COMPLETE")
print("="*80)
print("\nGenerated files:")
print("  - results/robust_eval/duplicate_report.txt")
print("  - results/robust_eval/label_shuffle_report.txt")
print("  - results/robust_eval/cv_5fold_raw.csv")
print("  - results/robust_eval/cv_5fold_summary.csv")
print("  - results/robust_eval/repeated_splits_raw.csv")
print("  - results/robust_eval/repeated_splits_summary.csv")
print("\nUse these results for paper reporting and robustness analysis.")
print("="*80)
