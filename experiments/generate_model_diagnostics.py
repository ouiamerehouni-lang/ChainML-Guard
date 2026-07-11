"""
Generate model diagnostics (confusion matrices + ROC curves)

This script follows the same evaluation protocol as `experiments/robust_evaluation.py`:
- Stratified 5-fold cross-validation (shuffle=True, random_state=42)
- MLP architecture and training settings identical to the paper
- Logistic Regression uses scaling fit on train folds
- Random Forest trained without scaling

Outputs:
 - results/model_diagnostics.png (300 dpi)
 - results/model_diagnostics.pdf
 - results/model_diagnostics.json

Usage:
  python experiments/generate_model_diagnostics.py

This script produces out-of-fold predictions (each sample predicted exactly once).
"""

import os
import json
import numpy as np
import pandas as pd
import random
from pathlib import Path
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, roc_curve, roc_auc_score

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam

# Reuse the same global seed as the paper
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)


def create_mlp_model():
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


def ensure_results_dir():
    Path('results').mkdir(parents=True, exist_ok=True)


def run():
    ensure_results_dir()

    # Load dataset (same features used in paper)
    df = pd.read_csv('data/dataset_final.csv')
    X = df[['balance', 'tx_count', 'age_days']].values
    y = df['is_fraud'].values
    n = len(y)

    # Prepare OOF storage
    models = ['Logistic Regression', 'Random Forest', 'MLP']
    oof_probas = {m: np.full(n, np.nan, dtype=float) for m in models}
    oof_preds = {m: np.full(n, np.nan, dtype=int) for m in models}

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)

    fold = 0
    for train_idx, val_idx in skf.split(X, y):
        fold += 1
        print(f"Fold {fold}/5 | train={len(train_idx)} val={len(val_idx)}")

        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        # Logistic Regression (with scaling fit on train only)
        scaler_lr = StandardScaler()
        X_train_lr = scaler_lr.fit_transform(X_train)
        X_val_lr = scaler_lr.transform(X_val)

        logreg = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED, class_weight='balanced')
        logreg.fit(X_train_lr, y_train)
        proba_lr = logreg.predict_proba(X_val_lr)[:, 1]
        pred_lr = (proba_lr >= 0.5).astype(int)
        oof_probas['Logistic Regression'][val_idx] = proba_lr
        oof_preds['Logistic Regression'][val_idx] = pred_lr

        # Random Forest (no scaling)
        rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=RANDOM_SEED,
                                    class_weight='balanced', n_jobs=-1)
        rf.fit(X_train, y_train)
        proba_rf = rf.predict_proba(X_val)[:, 1]
        pred_rf = (proba_rf >= 0.5).astype(int)
        oof_probas['Random Forest'][val_idx] = proba_rf
        oof_preds['Random Forest'][val_idx] = pred_rf

        # MLP (scale features, train per fold with same settings)
        scaler_mlp = StandardScaler()
        X_train_mlp = scaler_mlp.fit_transform(X_train)
        X_val_mlp = scaler_mlp.transform(X_val)

        # Reset TF seed for reproducibility per fold
        tf.random.set_seed(RANDOM_SEED)
        mlp = create_mlp_model()
        # Train with same settings as paper (silent)
        mlp.fit(X_train_mlp, y_train, epochs=120, batch_size=16, validation_split=0.1,
                shuffle=True, verbose=0)
        proba_mlp = mlp.predict(X_val_mlp, verbose=0).flatten()
        pred_mlp = (proba_mlp >= 0.5).astype(int)
        oof_probas['MLP'][val_idx] = proba_mlp
        oof_preds['MLP'][val_idx] = pred_mlp

    # Verification: each sample must be predicted exactly once
    for m in models:
        if np.isnan(oof_probas[m]).any():
            missing = int(np.isnan(oof_probas[m]).sum())
            raise RuntimeError(f"Model {m} has {missing} missing OOF predictions")
        if np.isnan(oof_preds[m]).any():
            missing = int(np.isnan(oof_preds[m]).sum())
            raise RuntimeError(f"Model {m} has {missing} missing OOF binary predictions")

    # Compute confusion matrices and ROC for each model
    results = {}
    for m in models:
        y_proba = oof_probas[m]
        y_pred = (y_proba >= 0.5).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, y_pred).ravel()
        fpr, tpr, _ = roc_curve(y, y_proba)
        auc_score = roc_auc_score(y, y_proba)

        results[m] = {
            'TN': int(tn), 'FP': int(fp), 'FN': int(fn), 'TP': int(tp),
            'roc_auc': float(auc_score),
            'fpr': [float(x) for x in fpr],
            'tpr': [float(x) for x in tpr],
            'n_oof_predictions': int(len(y_proba))
        }

        # Sanity check: confusion matrix total equals dataset size
        total_cm = tn + fp + fn + tp
        if total_cm != n:
            raise RuntimeError(f"Confusion matrix total for {m} ({total_cm}) != dataset size ({n})")

    # Save JSON
    out_json = {
        'metadata': {
            'random_seed': RANDOM_SEED,
            'evaluation_protocol': 'Stratified 5-fold cross-validation. Out-of-fold predictions aggregated across folds. Scaling: Logistic Regression and MLP use StandardScaler fit on train fold; Random Forest uses raw features.',
            'timestamp': datetime.now().isoformat(),
            'n_samples': int(n),
            'features': ['balance', 'tx_count', 'age_days']
        },
        'models': results
    }
    json_path = Path('results/model_diagnostics.json')
    with open(json_path, 'w') as f:
        json.dump(out_json, f, indent=2)
    print(f"Saved JSON results to: {json_path}")

    # Plot composite figure
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    cmap = 'Blues'

    # Confusion plotting helper
    def plot_confusion(ax, cm, title):
        im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
        ax.set_title(title, fontsize=10)
        classes = ['Legitimate', 'Malicious']
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(classes)
        ax.set_yticklabels(classes)
        ax.set_xlabel('Predicted class')
        ax.set_ylabel('Actual class')
        # Annotate counts
        thresh = cm.max() / 2.
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, format(int(cm[i, j]), 'd'),
                        ha='center', va='center',
                        color='white' if cm[i, j] > thresh else 'black', fontsize=12)

    # Top-left: Logistic Regression CM
    cm_lr = np.array([[results['Logistic Regression']['TN'], results['Logistic Regression']['FP']],
                      [results['Logistic Regression']['FN'], results['Logistic Regression']['TP']]])
    plot_confusion(axes[0, 0], cm_lr, 'Logistic Regression')

    # Top-right: Random Forest CM
    cm_rf = np.array([[results['Random Forest']['TN'], results['Random Forest']['FP']],
                      [results['Random Forest']['FN'], results['Random Forest']['TP']]])
    plot_confusion(axes[0, 1], cm_rf, 'Random Forest')

    # Bottom-left: MLP CM
    cm_mlp = np.array([[results['MLP']['TN'], results['MLP']['FP']],
                       [results['MLP']['FN'], results['MLP']['TP']]])
    plot_confusion(axes[1, 0], cm_mlp, 'MLP')

    # Bottom-right: ROC curves
    axroc = axes[1, 1]
    for m, color in zip(models, ['C0', 'C1', 'C2']):
        fpr = np.array(results[m]['fpr'])
        tpr = np.array(results[m]['tpr'])
        auc_score = results[m]['roc_auc']
        axroc.plot(fpr, tpr, label=f"{m} (AUC={auc_score:.3f})", color=color)
    # Diagonal
    axroc.plot([0, 1], [0, 1], color='gray', linestyle='--', label='Random')
    axroc.set_xlabel('False Positive Rate')
    axroc.set_ylabel('True Positive Rate')
    axroc.set_title('ROC Curves')
    axroc.legend(fontsize=8)

    plt.tight_layout()

    png_path = Path('results/model_diagnostics.png')
    pdf_path = Path('results/model_diagnostics.pdf')
    fig.savefig(png_path, dpi=300, bbox_inches='tight')
    fig.savefig(pdf_path, dpi=300, bbox_inches='tight')
    print(f"Saved figure: {png_path} and {pdf_path}")

    # Final verification prints
    print('\nConfusion matrices (TN, FP, FN, TP) and ROC-AUC:')
    for m in models:
        cm = results[m]
        print(f"- {m}: TN={cm['TN']} FP={cm['FP']} FN={cm['FN']} TP={cm['TP']} | AUC={cm['roc_auc']:.4f}")


if __name__ == '__main__':
    run()
