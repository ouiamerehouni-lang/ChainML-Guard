# ChainML Guard - Explanation Feature

## Overview

This feature adds human-readable explanations for why an Ethereum address was flagged as potentially malicious. The explanations are based on **heuristic rules** using the same 3 features that the MLP model uses: balance, transaction count, and wallet age.

**Important**: These explanations are NOT derived from the model's internal weights or decision-making process. They are simple, interpretable rules based on data-driven thresholds computed from the training dataset.

---

## Architecture

### 1. **Thresholds Computation** (`scripts/compute_thresholds.py`)
- Loads `data/dataset_final.csv`
- Splits into train/test (80/20) using the same parameters as `train_model.py`
- Computes percentile-based thresholds from the **training set only**:
  - `age_p10`: 10th percentile of wallet age (very new wallet indicator)
  - `tx_p90`: 90th percentile of transaction count (high activity indicator)
  - `bal_p05`: 5th percentile of balance (unusually low balance)
  - `bal_p95`: 95th percentile of balance (unusually high balance)
  - `rate_p90`: 90th percentile of activity rate (tx_count / wallet_age_days)
- Saves these thresholds to `thresholds.json` in the project root

### 2. **Explanation Logic** (`utils/explanations.py`)
- `load_thresholds()`: Loads thresholds from JSON file
- `generate_reason_summary()`: Applies heuristic rules to generate bullet-point reasons:
  - Very new wallet (age < age_p10)
  - High activity for its age (rate > rate_p90)
  - Unusually high transaction count (tx_count > tx_p90)
  - Unusually low balance (balance < bal_p05)
  - Unusually high balance (balance > bal_p95)
  - If no rules trigger: "No strong risk indicators from the available features"
- `get_explanation_disclaimer()`: Returns the disclaimer text

### 3. **Flask Integration** (`app.py`)
- Loads thresholds at startup (gracefully handles missing file)
- In the `/analyze` route, after computing the risk score:
  - Calls `generate_reason_summary()` with the 3 feature values
  - Passes `reasons` list and `disclaimer` to the template
  
### 4. **UI Display** (`templates/index.html`)
- New "Why this was flagged" section below the feature stats
- Displays reasons as styled bullet points
- Shows disclaimer at the bottom
- Uses cautious language: "indicators" not "proof"

---

## Setup Instructions

### Step 1: Run the Thresholds Computation (One-Time Setup)

After training your model or whenever the dataset changes, compute the thresholds:

```bash
cd /home/mahmoud/Desktop/ChainML-Guard
python scripts/compute_thresholds.py
```

**Expected Output:**
```
Loading dataset_final.csv...
✓ Loaded 10000 records
✓ Split into train (8000) and test (2000) sets

Computing percentile thresholds from training data...

Computed thresholds:
  age_p10  (very new wallet):           X.XX days
  tx_p90   (high tx count):             XXX transactions
  bal_p05  (unusually low balance):     X.XXXXXX ETH
  bal_p95  (unusually high balance):    X.XXXXXX ETH
  rate_p90 (high activity rate):        X.XXXX tx/day

✓ Thresholds saved to thresholds.json
```

This creates `thresholds.json` in the project root.

### Step 2: Run the Flask App

The app will automatically load the thresholds at startup:

```bash
python app.py
```

**Expected Startup Output:**
```
AI and Scaler loaded successfully.
Explanation thresholds loaded successfully.
 * Running on http://0.0.0.0:5000
```

If `thresholds.json` is missing, you'll see a warning but the app will still work (without explanations):
```
Warning: Thresholds file not found at thresholds.json. Please run scripts/compute_thresholds.py first.
Explanations will not be available. Run scripts/compute_thresholds.py to enable.
```

### Step 3: Use the Feature

1. Navigate to `http://localhost:5000`
2. Enter an Ethereum address to analyze
3. After analysis, you'll see:
   - Risk score and label (DANGER/HEALTHY)
   - The 3 feature values (balance, transactions, age)
   - **NEW**: "Why this was flagged" section with bullet-point reasons
   - **NEW**: Disclaimer explaining these are heuristic indicators

---

## File Structure

```
ChainML-Guard/
├── app.py                          # Flask app (modified to integrate explanations)
├── thresholds.json                 # Data-driven thresholds (generated)
├── data/
│   └── dataset_final.csv           # Training dataset
├── scripts/
│   └── compute_thresholds.py       # NEW: Computes thresholds from training data
├── utils/
│   └── explanations.py             # NEW: Explanation generation logic
└── templates/
    └── index.html                  # UI (modified to display explanations)
```

---

## Example Explanation Output

### High-Risk Address (Risk Score: 85%)
**Why this was flagged:**
- ➔ Very new wallet (age below 10th percentile)
- ➔ High activity for its age (activity rate above 90th percentile)
- ➔ Unusually low balance (below 5th percentile)

**Disclaimer:** These are heuristic indicators based on address-level features (balance, transaction count, wallet age) and do not prove malicious intent. The actual risk score is computed by a trained neural network model.

### Low-Risk Address (Risk Score: 25%)
**Why this was flagged:**
- ➔ No strong risk indicators from the available features

**Disclaimer:** These are heuristic indicators based on address-level features (balance, transaction count, wallet age) and do not prove malicious intent. The actual risk score is computed by a trained neural network model.

---

## Key Design Principles

1. **Data-Driven Thresholds**: All thresholds are computed from the training dataset, not hardcoded
2. **Training Set Only**: Thresholds use only the training split to avoid data leakage
3. **Heuristic Rules**: Explanations are simple, interpretable rules - NOT model internals
4. **Cautious Language**: Uses "indicators" not "proof"; includes disclaimer
5. **Sender-Only Scope**: Matches paper scope (sender EOA screening only)
6. **Graceful Degradation**: App works even if thresholds.json is missing (no explanations)

---

## Maintenance

### When to Recompute Thresholds
- After retraining the model with new data
- After modifying the dataset
- After changing the train/test split parameters

### Customizing Thresholds
Edit `scripts/compute_thresholds.py` to adjust percentiles:
- Change percentile values (e.g., 5th → 10th for balance)
- Add new features (must update model training too)
- Modify the activity rate calculation

### Customizing Explanation Rules
Edit `utils/explanations.py` → `generate_reason_summary()`:
- Add/remove rules
- Change wording
- Adjust rule conditions

---

## Troubleshooting

**Problem:** "Thresholds file not found" warning at startup
- **Solution:** Run `python scripts/compute_thresholds.py` to generate `thresholds.json`

**Problem:** No "Why this was flagged" section appears in UI
- **Solution:** Check that `thresholds.json` exists and is valid JSON
- **Solution:** Check Flask console for any errors during threshold loading

**Problem:** Thresholds seem incorrect
- **Solution:** Verify `dataset_final.csv` has the expected columns: `balance`, `tx_count`, `age_days`, `is_fraud`
- **Solution:** Check that the dataset has enough samples for meaningful percentiles

---

## Future Enhancements

Potential improvements (not currently implemented):
- Add confidence intervals for thresholds
- Compute separate thresholds for fraud vs. legitimate classes
- Add time-based explanations (e.g., "wallet created during a known phishing campaign period")
- Integrate with external threat intelligence feeds
- Add visualization of where the address falls in the distribution

---

## Technical Notes

### Why Not SHAP/LIME?
These model-agnostic explanation methods require computing many predictions and can be slow. For a production web app, simple heuristic rules provide instant explanations while maintaining transparency.

### Why Percentiles?
Percentiles are robust to outliers and distribution changes, making them more reliable than hardcoded thresholds (e.g., "age < 30 days").

### Why Training Set Only?
Computing thresholds from the training set ensures they reflect the data the model was trained on, avoiding data leakage and overfitting to the test set.

---

## Contact & Support

For questions or issues related to the explanation feature, please refer to the main README.md or contact the development team.
