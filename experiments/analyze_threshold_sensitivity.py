"""
Threshold sensitivity analysis for deployed MLP using pooled out-of-fold predictions.

Protocol is aligned with existing evaluation scripts:
- Dataset: data/dataset_final.csv
- Features: balance, tx_count, age_days
- Label: is_fraud
- CV: StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
- MLP architecture/training: same as robust_evaluation.py and generate_model_diagnostics.py

Outputs:
- results/threshold_sensitivity.csv
- results/threshold_sensitivity.json
"""

import json
import random
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam

RANDOM_SEED = 42
FEATURE_COLUMNS = ["balance", "tx_count", "age_days"]
LABEL_COLUMN = "is_fraud"
THRESHOLDS = [0.30, 0.40, 0.50, 0.60, 0.70]


def set_global_seed() -> None:
    np.random.seed(RANDOM_SEED)
    random.seed(RANDOM_SEED)
    tf.random.set_seed(RANDOM_SEED)


def create_mlp_model() -> Sequential:
    model = Sequential(
        [
            Dense(16, input_dim=3, activation="relu", kernel_initializer="he_normal"),
            Dropout(0.3),
            Dense(8, activation="relu"),
            Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(
        loss="binary_crossentropy",
        optimizer=Adam(learning_rate=0.001),
        metrics=["accuracy"],
    )
    return model


def generate_mlp_oof_probabilities(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    n_samples = len(y)
    oof_proba = np.full(n_samples, np.nan, dtype=float)
    oof_seen = np.zeros(n_samples, dtype=int)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    fold_num = 0
    for train_idx, val_idx in skf.split(x, y):
        fold_num += 1
        print(f"Fold {fold_num}/5 | train={len(train_idx)} val={len(val_idx)}")

        x_train, x_val = x[train_idx], x[val_idx]
        y_train = y[train_idx]

        scaler = StandardScaler()
        x_train_scaled = scaler.fit_transform(x_train)
        x_val_scaled = scaler.transform(x_val)

        tf.random.set_seed(RANDOM_SEED)
        model = create_mlp_model()
        model.fit(
            x_train_scaled,
            y_train,
            epochs=120,
            batch_size=16,
            validation_split=0.1,
            shuffle=True,
            verbose=0,
        )

        fold_proba = model.predict(x_val_scaled, verbose=0).flatten()
        oof_proba[val_idx] = fold_proba
        oof_seen[val_idx] += 1

    if np.isnan(oof_proba).any():
        raise RuntimeError(f"Missing OOF probabilities: {int(np.isnan(oof_proba).sum())}")

    if not np.all(oof_seen == 1):
        uniques, counts = np.unique(oof_seen, return_counts=True)
        seen_hist = {int(k): int(v) for k, v in zip(uniques, counts)}
        raise RuntimeError(f"Each sample must be predicted exactly once. Seen histogram: {seen_hist}")

    return oof_proba


def evaluate_thresholds(y_true: np.ndarray, y_proba: np.ndarray) -> list[dict]:
    rows = []
    for t in THRESHOLDS:
        y_pred = (y_proba >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        cm_total = int(tn + fp + fn + tp)

        if cm_total != len(y_true):
            raise RuntimeError(
                f"Confusion matrix total mismatch at threshold {t}: {cm_total} != {len(y_true)}"
            )

        rows.append(
            {
                "threshold": float(t),
                "precision": float(precision_score(y_true, y_pred, zero_division=0)),
                "recall": float(recall_score(y_true, y_pred, zero_division=0)),
                "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
                "accuracy": float(accuracy_score(y_true, y_pred)),
                "TN": int(tn),
                "FP": int(fp),
                "FN": int(fn),
                "TP": int(tp),
                "predicted_malicious_count": int(y_pred.sum()),
                "predicted_legitimate_count": int(len(y_pred) - y_pred.sum()),
                "confusion_total": cm_total,
            }
        )
    return rows


def main() -> None:
    set_global_seed()
    Path("results").mkdir(parents=True, exist_ok=True)

    df = pd.read_csv("data/dataset_final.csv")
    x = df[FEATURE_COLUMNS].values
    y = df[LABEL_COLUMN].values

    dataset_size = int(len(y))
    legitimate_count = int((y == 0).sum())
    malicious_count = int((y == 1).sum())

    oof_proba = generate_mlp_oof_probabilities(x, y)
    threshold_rows = evaluate_thresholds(y, oof_proba)

    # Hard verification against existing diagnostic reference at threshold 0.50
    row_050 = next(r for r in threshold_rows if abs(r["threshold"] - 0.5) < 1e-12)
    expected = {"TN": 151, "FP": 9, "FN": 1, "TP": 199}
    actual = {k: int(row_050[k]) for k in ["TN", "FP", "FN", "TP"]}
    if actual != expected:
        raise RuntimeError(
            "Threshold 0.50 confusion matrix does not match existing MLP diagnostics. "
            f"Expected {expected}, got {actual}."
        )

    csv_path = Path("results/threshold_sensitivity.csv")
    pd.DataFrame(threshold_rows).to_csv(csv_path, index=False)

    json_path = Path("results/threshold_sensitivity.json")
    out_json = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "dataset_size": dataset_size,
            "class_counts": {
                "legitimate": legitimate_count,
                "malicious": malicious_count,
            },
            "n_out_of_fold_predictions": int(len(oof_proba)),
            "thresholds_evaluated": THRESHOLDS,
            "random_seed": RANDOM_SEED,
            "cross_validation_protocol": "Stratified 5-fold cross-validation (shuffle=True, random_state=42), pooled out-of-fold probabilities.",
            "probability_thresholding_confirmation": "Metrics were computed by thresholding pooled out-of-fold probability outputs, not binary model outputs.",
            "single_held_out_prediction_confirmation": "Verified: each sample received exactly one held-out prediction.",
            "feature_columns": FEATURE_COLUMNS,
            "label_column": LABEL_COLUMN,
            "mlp_training_configuration": {
                "epochs": 120,
                "batch_size": 16,
                "validation_split": 0.1,
                "shuffle": True,
                "optimizer": "Adam(learning_rate=0.001)",
            },
            "threshold_0_50_reference_check": {
                "expected": expected,
                "actual": actual,
                "match": True,
            },
        },
        "threshold_results": threshold_rows,
    }
    with open(json_path, "w") as f:
        json.dump(out_json, f, indent=2)

    print(f"Saved: {csv_path}")
    print(f"Saved: {json_path}")
    print("Threshold 0.50 reference check passed: TN=151, FP=9, FN=1, TP=199")


if __name__ == "__main__":
    main()
