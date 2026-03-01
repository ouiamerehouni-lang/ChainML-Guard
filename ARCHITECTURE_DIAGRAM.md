# Data Flow Diagram: Explanation Feature

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ONE-TIME SETUP PHASE                             │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────┐
    │ dataset_final.csv   │
    │  (full dataset)     │
    └──────────┬──────────┘
               │
               │ Load & Split (80/20, stratify=y)
               ↓
    ┌──────────────────────────────────────┐
    │  scripts/compute_thresholds.py       │
    │                                      │
    │  1. Split train/test                │
    │  2. Compute from TRAIN only:        │
    │     - age_p10 (10th percentile)     │
    │     - tx_p90 (90th percentile)      │
    │     - bal_p05, bal_p95 (5th, 95th)  │
    │     - rate_p90 (tx/age ratio)       │
    └──────────┬───────────────────────────┘
               │
               │ Save JSON
               ↓
    ┌─────────────────────┐
    │  thresholds.json    │
    │  {                  │
    │    "age_p10": 45.2, │
    │    "tx_p90": 156,   │
    │    "bal_p05": 0.001,│
    │    "bal_p95": 12.45,│
    │    "rate_p90": 2.34 │
    │  }                  │
    └─────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                      FLASK APP STARTUP PHASE                             │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────┐     ┌─────────────────────┐
    │ fraud_model.h5      │     │ thresholds.json     │
    │ scaler.pkl          │     │                     │
    └──────────┬──────────┘     └──────────┬──────────┘
               │                           │
               │ Load                      │ Load
               ↓                           ↓
    ┌───────────────────────────────────────────────┐
    │              app.py (startup)                 │
    │                                               │
    │  - Load model & scaler                       │
    │  - Load thresholds (graceful if missing)     │
    │  - Start Flask server                        │
    └───────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                    RUNTIME: ADDRESS ANALYSIS FLOW                        │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────┐
    │   User submits      │
    │  Ethereum address   │
    │  (via web form)     │
    └──────────┬──────────┘
               │
               ↓
    ┌───────────────────────────────────────────────┐
    │  app.py: /analyze route                       │
    │                                               │
    │  1. Validate address format                  │
    └──────────┬────────────────────────────────────┘
               │
               ↓
    ┌───────────────────────────────────────────────┐
    │  data_collection.py:                          │
    │  get_address_features(address)                │
    │                                               │
    │  Fetch from Etherscan API:                   │
    │  - balance (ETH)                             │
    │  - tx_count (number)                         │
    │  - wallet_age_days (calculated)              │
    └──────────┬────────────────────────────────────┘
               │
               │ [balance, tx_count, age_days]
               ↓
    ┌───────────────────────────────────────────────┐
    │  MLP Model Prediction                         │
    │                                               │
    │  1. Scale features (scaler)                  │
    │  2. Predict (model)                          │
    │  3. Output: risk_score (0-100%)              │
    └──────────┬────────────────────────────────────┘
               │
               │ risk_score
               ↓
    ┌───────────────────────────────────────────────┐
    │  NEW: Explanation Generation                  │
    │  utils/explanations.py                        │
    │                                               │
    │  generate_reason_summary(                    │
    │    balance, tx_count, age_days, thresholds)  │
    │                                               │
    │  Apply heuristic rules:                      │
    │  IF age_days < age_p10:                      │
    │    → "Very new wallet"                       │
    │  IF tx/age > rate_p90:                       │
    │    → "High activity for its age"             │
    │  IF tx_count > tx_p90:                       │
    │    → "Unusually high transaction count"      │
    │  IF balance < bal_p05 OR > bal_p95:          │
    │    → "Unusually low/high balance"            │
    │  ELSE:                                       │
    │    → "No strong risk indicators"             │
    └──────────┬────────────────────────────────────┘
               │
               │ reasons[] + disclaimer
               ↓
    ┌───────────────────────────────────────────────┐
    │  Render HTML Template                         │
    │  templates/index.html                         │
    │                                               │
    │  Display:                                    │
    │  ┌─────────────────────────────────────┐    │
    │  │ Risk Score: 85% (DANGER)            │    │
    │  │                                     │    │
    │  │ Balance: 0.005 ETH                 │    │
    │  │ Transactions: 500                   │    │
    │  │ Age: 5 days                         │    │
    │  │                                     │    │
    │  │ ⚡ Why this was flagged:            │    │
    │  │  → Very new wallet                  │    │
    │  │  → High activity for its age        │    │
    │  │  → Unusually low balance            │    │
    │  │                                     │    │
    │  │ ℹ️ Disclaimer: These are heuristic  │    │
    │  │   indicators...                     │    │
    │  └─────────────────────────────────────┘    │
    └───────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                          KEY DESIGN POINTS                               │
└─────────────────────────────────────────────────────────────────────────┘

1. SEPARATION OF CONCERNS
   ├─ Model prediction (app.py) → Risk score
   └─ Explanation generation (utils/explanations.py) → Human-readable reasons

2. DATA-DRIVEN THRESHOLDS
   ├─ Computed from training data (not hardcoded)
   └─ No data leakage (training set only)

3. HEURISTIC RULES (NOT MODEL INTERNALS)
   ├─ Simple interpretable rules
   ├─ Based on same 3 features as model
   └─ Does NOT attempt to explain MLP weights/activations

4. GRACEFUL DEGRADATION
   ├─ App works without thresholds.json
   └─ Explanations simply don't appear if missing

5. CAUTIOUS LANGUAGE
   ├─ "Indicators" not "proof"
   ├─ Disclaimer always shown
   └─ Matches paper scope (sender EOA only)


┌─────────────────────────────────────────────────────────────────────────┐
│                         FILE DEPENDENCIES                                │
└─────────────────────────────────────────────────────────────────────────┘

app.py
  ├─ imports: utils.explanations
  ├─ reads: thresholds.json
  ├─ calls: generate_reason_summary()
  └─ renders: index.html (with reasons, disclaimer)

utils/explanations.py
  ├─ loads: thresholds.json
  └─ exports: 3 functions

scripts/compute_thresholds.py
  ├─ reads: data/dataset_final.csv
  └─ writes: thresholds.json

templates/index.html
  ├─ displays: reasons list
  └─ displays: disclaimer


┌─────────────────────────────────────────────────────────────────────────┐
│                       THRESHOLD PERCENTILES RATIONALE                    │
└─────────────────────────────────────────────────────────────────────────┘

age_p10 (10th percentile)
  → Captures "very new" wallets
  → More conservative than p05 (catches more suspicious cases)

tx_p90 (90th percentile)
  → Flags unusually active wallets
  → Common pattern in bot/spam addresses

bal_p05, bal_p95 (5th/95th percentiles)
  → Extreme values on both ends
  → Low: potential dust/test accounts
  → High: potential money laundering staging

rate_p90 (90th percentile of tx/age)
  → High frequency relative to wallet age
  → Classic bot behavior: new wallet + many txs
  → More informative than absolute tx_count alone
```
