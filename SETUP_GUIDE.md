# Setup Guide: Explanation Feature

## Complete Installation & Setup Instructions

This guide walks you through setting up the explanation feature from scratch.

---

## Prerequisites

Before starting, ensure you have:

- ✅ Python 3.8+ installed
- ✅ All dependencies installed (`pip install -r requirements.txt`)
- ✅ `data/dataset_final.csv` exists
- ✅ Model trained (`models/fraud_model.h5` and `models/scaler.pkl` exist)

If you don't have the model trained yet:
```bash
python train_model.py
```

---

## Setup Steps

### Step 1: Compute Thresholds (Required - One Time Only)

Run the threshold computation script:

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
  age_p10  (very new wallet):           45.20 days
  tx_p90   (high tx count):             156 transactions
  bal_p05  (unusually low balance):     0.001234 ETH
  bal_p95  (unusually high balance):    12.456789 ETH
  rate_p90 (high activity rate):        2.3456 tx/day

✓ Thresholds saved to thresholds.json

You can now run the Flask app (app.py) to use these thresholds for explanations.
```

**What this does:**
- Loads your training dataset
- Splits it exactly as `train_model.py` does (80/20, stratified)
- Computes percentile thresholds from training set only
- Saves thresholds to `thresholds.json`

**Verify it worked:**
```bash
ls -la thresholds.json
cat thresholds.json
```

You should see a JSON file with 5 keys: age_p10, tx_p90, bal_p05, bal_p95, rate_p90

---

### Step 2: Test the Feature (Optional but Recommended)

Run the test script to verify everything works:

```bash
python test_explanation_feature.py
```

**Expected Output:**
```
Step 1: Computing thresholds from training data...
Command: python scripts/compute_thresholds.py

Step 2: Verify thresholds.json was created...
✓ thresholds.json found!
Thresholds:
  age_p10: 45.2
  tx_p90: 156.0
  bal_p05: 0.001234
  bal_p95: 12.456789
  rate_p90: 2.3456

Step 3: Testing explanation generation...

Test Case 1: New wallet with high activity
--------------------------------------------------
Reasons:
  → Very new wallet (age below 10th percentile)
  → High activity for its age (activity rate above 90th percentile)
  → Unusually low balance (below 5th percentile)

Test Case 2: Normal wallet
--------------------------------------------------
Reasons:
  → No strong risk indicators from the available features

Test Case 3: Old wallet with extreme high balance
--------------------------------------------------
Reasons:
  → Unusually high balance (above 95th percentile)

==================================================
Disclaimer:
These are heuristic indicators based on address-level features (balance, transaction count, wallet age) and do not prove malicious intent. The actual risk score is computed by a trained neural network model.
==================================================

Step 4: Ready to run Flask app!
Command: python app.py

Then visit: http://localhost:5000
Enter an Ethereum address to see the explanation feature in action!
```

---

### Step 3: Start the Flask App

```bash
python app.py
```

**Expected Console Output:**
```
AI and Scaler loaded successfully.
Explanation thresholds loaded successfully.
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
Press CTRL+C to quit
```

**Important:** Look for the line `Explanation thresholds loaded successfully.`

If you see `Warning: Thresholds file not found`, go back to Step 1.

---

### Step 4: Test in the Web UI

1. Open your browser and navigate to: **http://localhost:5000**

2. Connect your MetaMask wallet (optional, but recommended)

3. Enter a test Ethereum address in the "Recipient Address" field
   - Try a known high-risk address
   - Or any address you want to test

4. Enter an amount (any value is fine for testing, e.g., "1.0")

5. Click **"Analyze History"**

6. You should see results with the NEW explanation section:

```
┌─────────────────────────────────────────────────┐
│ Risk Score: XX%                                 │
│                                                 │
│ Feature Values:                                 │
│   Balance: X.XXX ETH                           │
│   Transactions: XXX                             │
│   Age: XXX days                                 │
│                                                 │
│ ⚡ Why this was flagged:                        │
│   → Reason 1                                    │
│   → Reason 2                                    │
│   → Reason 3                                    │
│                                                 │
│ ℹ️ These are heuristic indicators based on      │
│   address-level features and do not prove       │
│   malicious intent.                             │
└─────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Problem: "dataset_final.csv not found"

**Solution:**
```bash
# Check if file exists
ls -la data/dataset_final.csv

# If missing, you need to run data collection first
python data_collection.py
```

### Problem: "fraud_model.h5 or scaler.pkl not found"

**Solution:**
```bash
# Check if files exist
ls -la models/fraud_model.h5
ls -la models/scaler.pkl

# If missing, train the model
python train_model.py
```

### Problem: "Thresholds file not found" at Flask startup

**Solution:**
```bash
# Run the threshold computation script
python scripts/compute_thresholds.py

# Verify it was created
ls -la thresholds.json
```

### Problem: No explanation section appears in UI

**Check these:**
1. Is `thresholds.json` present in project root?
   ```bash
   cat thresholds.json
   ```

2. Did Flask load it successfully? Check console output for:
   ```
   Explanation thresholds loaded successfully.
   ```

3. Is the address analysis successful? Check for any errors in Flask console.

### Problem: Import errors for utils.explanations

**Solution:**
```bash
# Verify the utils package exists
ls -la utils/
# Should show: __init__.py, explanations.py

# If missing __init__.py, create it:
touch utils/__init__.py
```

### Problem: Thresholds seem incorrect or unexpected

**Solutions:**

1. Check dataset quality:
   ```bash
   python -c "import pandas as pd; df = pd.read_csv('data/dataset_final.csv'); print(df.describe())"
   ```

2. Verify columns exist:
   ```bash
   python -c "import pandas as pd; df = pd.read_csv('data/dataset_final.csv'); print(df.columns.tolist())"
   ```
   Should include: balance, tx_count, age_days, is_fraud

3. Check for missing values:
   ```bash
   python -c "import pandas as pd; df = pd.read_csv('data/dataset_final.csv'); print(df.isnull().sum())"
   ```

4. Re-run threshold computation:
   ```bash
   rm thresholds.json
   python scripts/compute_thresholds.py
   ```

---

## Verifying Everything Works

### Quick Verification Checklist

```bash
# 1. Check all files exist
ls -la scripts/compute_thresholds.py      # Should exist
ls -la utils/explanations.py               # Should exist
ls -la utils/__init__.py                   # Should exist
ls -la thresholds.json                     # Should exist after Step 1
ls -la data/dataset_final.csv              # Should exist
ls -la models/fraud_model.h5               # Should exist
ls -la models/scaler.pkl                   # Should exist

# 2. Test Python imports
python -c "from utils.explanations import load_thresholds, generate_reason_summary; print('✓ Imports work')"

# 3. Test threshold loading
python -c "from utils.explanations import load_thresholds; t = load_thresholds(); print('✓ Thresholds loaded:', list(t.keys()))"

# 4. Test explanation generation
python test_explanation_feature.py

# 5. Start app and check console
python app.py
# Look for: "Explanation thresholds loaded successfully."
```

---

## Advanced: Custom Configuration

### Changing Percentile Thresholds

Edit `scripts/compute_thresholds.py`, lines 45-56:

```python
thresholds = {
    # Change these values to adjust sensitivity
    "age_p10": float(np.percentile(train_df['age_days'], 10)),    # ← Change 10 to 5 or 15
    "tx_p90": float(np.percentile(train_df['tx_count'], 90)),     # ← Change 90 to 85 or 95
    "bal_p05": float(np.percentile(train_df['balance'], 5)),      # ← Change 5 to 1 or 10
    "bal_p95": float(np.percentile(train_df['balance'], 95)),     # ← Change 95 to 90 or 99
    "rate_p90": float(np.percentile(train_df['activity_rate'], 90))  # ← Change 90 to 85 or 95
}
```

After editing, re-run:
```bash
python scripts/compute_thresholds.py
```

### Changing Explanation Rules

Edit `utils/explanations.py`, the `generate_reason_summary()` function:

```python
# Add a new rule
if tx_count == 0:
    reasons.append("Wallet has no transaction history")

# Modify existing rule wording
if wallet_age_days < thresholds['age_p10']:
    reasons.append("Wallet is very new")  # ← Change this text
```

No need to recompute thresholds, just restart Flask.

### Changing UI Styling

Edit `templates/index.html`, the CSS section:

```css
.explanation-section {
    margin-top: 2rem;
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.05);  /* ← Change background */
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.reasons-list li {
    border-left: 3px solid #f59e0b;  /* ← Change accent color */
}
```

---

## Production Deployment

### Before Deploying to Production:

1. **Compute final thresholds** from your production training data:
   ```bash
   python scripts/compute_thresholds.py
   ```

2. **Backup thresholds.json**:
   ```bash
   cp thresholds.json thresholds.json.backup
   ```

3. **Test thoroughly** with real addresses

4. **Set up monitoring** for:
   - Threshold loading errors
   - Explanation generation failures
   - Unusual reason patterns

5. **Update regularly**: Recompute thresholds when you retrain the model

---

## Maintenance

### When to Recompute Thresholds

Run `python scripts/compute_thresholds.py` when:
- ✓ You retrain the model with new data
- ✓ Your dataset is updated
- ✓ You change train/test split parameters
- ✓ Quarterly (as a best practice)

### Monitoring Checklist

- [ ] Verify thresholds.json is loaded at startup
- [ ] Check that explanations appear for analyzed addresses
- [ ] Monitor for any new error patterns
- [ ] Review explanation relevance (user feedback)
- [ ] Verify thresholds still make sense as data evolves

---

## Getting Help

If you encounter issues not covered here:

1. Check the comprehensive documentation:
   - `EXPLANATION_FEATURE.md` - Full feature guide
   - `IMPLEMENTATION_SUMMARY.md` - Technical details
   - `ARCHITECTURE_DIAGRAM.md` - System flow
   - `QUICK_REFERENCE.txt` - Quick commands

2. Check Flask console logs for errors

3. Run test script to isolate issues:
   ```bash
   python test_explanation_feature.py
   ```

4. Verify file integrity:
   ```bash
   python -c "import json; print(json.load(open('thresholds.json')))"
   ```

---

## Summary

You've successfully set up the explanation feature! 🎉

**What you now have:**
- ✅ Data-driven threshold computation
- ✅ Rule-based explanation generation
- ✅ Beautiful UI display with reasons and disclaimer
- ✅ Full documentation and test scripts
- ✅ Maintainable, production-ready code

**Next steps:**
1. Start analyzing addresses with explanations
2. Gather user feedback on explanation quality
3. Consider customizing thresholds/rules based on your use case
4. Set up regular threshold recomputation schedule

**Happy analyzing!** 🚀
