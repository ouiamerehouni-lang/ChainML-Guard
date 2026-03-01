# Model Training and Evaluation Guide

This guide explains how to train baseline models and evaluate all models in the ChainML Guard project.

## Overview

The project now includes three fraud detection models:
1. **MLP (Multi-Layer Perceptron)** - Neural network with 2 hidden layers (existing)
2. **Logistic Regression** - Linear baseline model (new)
3. **Random Forest** - Tree-based ensemble model (new)

All models use:
- **Same dataset**: `data/dataset_final.csv`
- **Same features**: `balance`, `tx_count`, `age_days` (3 features)
- **Same label**: `is_fraud` (0=legitimate, 1=fraudulent)
- **Same split**: 80/20 stratified with `random_state=42`
- **No data leakage**: Preprocessing fit on train, applied to test

## Folder Structure

```
ChainML-Guard/
├── training/
│   ├── train_logreg.py          # Train Logistic Regression
│   ├── train_rf.py              # Train Random Forest
│   └── setup_model_structure.py # Organize artifacts
├── experiments/
│   └── evaluate_models.py       # Unified evaluation
├── models/
│   ├── mlp/                     # MLP artifacts (copied from root)
│   │   ├── model.h5
│   │   ├── scaler.pkl
│   │   └── thresholds.json
│   ├── logreg/                  # Logistic Regression artifacts
│   │   ├── model.pkl
│   │   └── scaler.pkl
│   └── rf/                      # Random Forest artifacts
│       └── model.pkl
└── results/
    └── metrics.csv              # Evaluation results
```

## Quick Start

### Step 1: Organize Existing MLP Artifacts (Optional)

This copies the existing MLP model to the new structure:

```bash
python training/setup_model_structure.py
```

**Note**: This is optional. The evaluation script will automatically detect the old paths if new ones don't exist.

### Step 2: Train Baseline Models

Train Logistic Regression:
```bash
python training/train_logreg.py
```

Train Random Forest:
```bash
python training/train_rf.py
```

### Step 3: Evaluate All Models

Run unified evaluation to compare all three models:
```bash
python experiments/evaluate_models.py
```

This will:
- Load all three models
- Evaluate on the same test set
- Compute Accuracy, Precision, Recall, F1, ROC-AUC
- Print confusion matrices
- Save results to `results/metrics.csv`
- Identify best model per metric

## Expected Output

### Training Output

Each training script shows:
- Dataset statistics (class distribution)
- Train/test split sizes
- Model training progress
- Test set accuracy
- Classification report
- Saved artifact paths

### Evaluation Output

The evaluation script produces:
- Individual model metrics with confusion matrices
- Summary comparison table
- Best model per metric
- CSV export to `results/metrics.csv`

Example output:
```
SUMMARY: MODEL COMPARISON
======================================================================

                 Model  Accuracy  Precision    Recall  F1 Score  ROC-AUC
                   MLP    95.83%     94.44%    94.44%    94.44%   0.9889
  Logistic Regression    91.67%     88.89%    88.89%    88.89%   0.9556
        Random Forest    94.44%     91.67%    91.67%    91.67%   0.9722

Best Model per Metric:
──────────────────────────────────────────────────────────────────────
  Accuracy    : MLP                  (95.83%)
  Precision   : MLP                  (94.44%)
  Recall      : MLP                  (94.44%)
  F1 Score    : MLP                  (94.44%)
  ROC-AUC     : MLP                  (0.9889)
```

## Docker Execution

Since you run the app in Docker, use these commands:

### Build Docker image (if needed)
```bash
docker build -t chainml-guard .
```

### Train models in Docker
```bash
docker run --rm -v $(pwd):/app chainml-guard python training/train_logreg.py
docker run --rm -v $(pwd):/app chainml-guard python training/train_rf.py
```

### Evaluate models in Docker
```bash
docker run --rm -v $(pwd):/app chainml-guard python experiments/evaluate_models.py
```

## Flask App Compatibility

**IMPORTANT**: The Flask app continues to work without any changes!

The evaluation script automatically checks both:
- New path: `models/mlp/model.h5`
- Old path: `models/fraud_model.h5`

The original MLP artifacts remain in place at:
- `models/fraud_model.h5`
- `models/scaler.pkl`

So `app.py` continues to load from the original paths without modification.

## Model Details

### MLP (Multi-Layer Perceptron)
- Architecture: Dense(16, relu) → Dropout(0.3) → Dense(8, relu) → Dense(1, sigmoid)
- Optimizer: Adam (lr=0.001)
- Epochs: 120
- Preprocessing: StandardScaler

### Logistic Regression
- Solver: lbfgs
- Max iterations: 1000
- Class weight: balanced
- Preprocessing: StandardScaler

### Random Forest
- Estimators: 100 trees
- Max depth: 10
- Class weight: balanced
- Preprocessing: None (RF doesn't need scaling)

## Reproducibility

All models use:
- `random_state=42` for reproducibility
- Same train/test split (stratified 80/20)
- Same feature extraction
- Consistent evaluation metrics

## Troubleshooting

### "Module not found" errors
Run in Docker where all dependencies are installed:
```bash
docker run --rm -v $(pwd):/app chainml-guard python <script>
```

### "Model file not found"
- For MLP: Ensure `models/fraud_model.h5` exists (run `python train_model.py` if needed)
- For baselines: Run the training scripts first

### Different results than expected
- Check dataset hasn't changed
- Verify `random_state=42` is used consistently
- Ensure preprocessing is applied correctly

## Next Steps

1. **Compare models**: Review `results/metrics.csv` to see which performs best
2. **Feature engineering**: Consider adding new features to improve performance
3. **Hyperparameter tuning**: Optimize model parameters for better results
4. **Deployment**: Update Flask app to use best-performing model
