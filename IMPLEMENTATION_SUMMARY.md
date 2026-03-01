# Implementation Summary: Reason Summary Feature

## Files Created

### 1. `/scripts/compute_thresholds.py` (NEW)
**Purpose:** Compute data-driven thresholds from training dataset

**Key Functions:**
- Loads `data/dataset_final.csv`
- Splits train/test (80/20, random_state=42) - same as `train_model.py`
- Computes percentiles from TRAINING SET ONLY:
  - age_p10 (10th percentile of wallet age)
  - tx_p90 (90th percentile of transaction count)
  - bal_p05, bal_p95 (5th/95th percentiles of balance)
  - rate_p90 (90th percentile of tx_count / wallet_age_days)
- Saves to `thresholds.json`

**Run Once:** After training model or when dataset changes

---

### 2. `/utils/explanations.py` (NEW)
**Purpose:** Rule-based explanation generation

**Key Functions:**

#### `load_thresholds(thresholds_path='thresholds.json')`
- Loads thresholds from JSON
- Raises FileNotFoundError if missing

#### `generate_reason_summary(balance, tx_count, wallet_age_days, thresholds)`
- Returns list of reason strings based on heuristic rules:
  - Very new wallet (age < age_p10)
  - High activity for its age (rate > rate_p90)
  - Unusually high transaction count (tx_count > tx_p90)
  - Unusually low balance (balance < bal_p05)
  - Unusually high balance (balance > bal_p95)
- Returns ["No strong risk indicators..."] if no rules triggered

#### `get_explanation_disclaimer()`
- Returns disclaimer text for UI

---

### 3. `/utils/__init__.py` (NEW)
**Purpose:** Package initialization for utils module

**Exports:**
- load_thresholds
- generate_reason_summary
- get_explanation_disclaimer

---

### 4. `/EXPLANATION_FEATURE.md` (NEW)
**Purpose:** Complete documentation for the feature

**Contents:**
- Architecture overview
- Setup instructions
- File structure
- Example outputs
- Design principles
- Troubleshooting guide
- Future enhancements

---

### 5. `/test_explanation_feature.py` (NEW)
**Purpose:** Quick test script to verify implementation

**What it does:**
- Checks if thresholds.json exists
- Tests explanation generation with 3 test cases
- Shows expected output format

---

## Files Modified

### 1. `/app.py`

#### Change 1: Added imports (Line 8)
```python
from utils.explanations import load_thresholds, generate_reason_summary, get_explanation_disclaimer
```

#### Change 2: Added THRESHOLDS_PATH constant (Line 15)
```python
THRESHOLDS_PATH = 'thresholds.json'
```

#### Change 3: Load thresholds at startup (Lines 27-33)
```python
# Load thresholds for explanations (optional - will handle gracefully if missing)
try:
    thresholds = load_thresholds(THRESHOLDS_PATH)
    print("Explanation thresholds loaded successfully.")
except FileNotFoundError as e:
    thresholds = None
    print(f"Warning: {e}")
    print("Explanations will not be available. Run scripts/compute_thresholds.py to enable.")
```

#### Change 4: Generate reasons in /analyze route (Lines 89-100)
```python
# E. Generate explanation reasons (if thresholds available)
reasons = []
disclaimer = ""
if thresholds:
    reasons = generate_reason_summary(
        balance=raw_features[0],
        tx_count=raw_features[1],
        wallet_age_days=raw_features[2],
        thresholds=thresholds
    )
    disclaimer = get_explanation_disclaimer()
```

#### Change 5: Pass reasons to template (Lines 102-112)
```python
return render_template(
    'index.html', 
    address=address,
    amount=amount, 
    score=risk_score,
    status=result_text, 
    color=result_color,
    balance=raw_features[0],
    txs=raw_features[1],
    age=raw_features[2],
    reasons=reasons,        # NEW
    disclaimer=disclaimer   # NEW
)
```

---

### 2. `/templates/index.html`

#### Change 1: Added CSS for explanation section (After line 368)
```css
/* Explanation Section */
.explanation-section {
    margin-top: 2rem;
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.explanation-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
    font-size: 1.1rem;
    font-weight: 700;
    color: #f59e0b;
}

.explanation-header i {
    font-size: 1.3rem;
}

.reasons-list {
    list-style: none;
    padding: 0;
    margin: 0 0 1rem 0;
}

.reasons-list li {
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    background: rgba(255, 255, 255, 0.08);
    border-left: 3px solid #f59e0b;
    border-radius: 8px;
    font-size: 0.95rem;
    line-height: 1.5;
}

.reasons-list li::before {
    content: "→";
    color: #f59e0b;
    font-weight: bold;
    margin-right: 0.75rem;
}

.explanation-disclaimer {
    padding: 1rem;
    background: rgba(59, 130, 246, 0.1);
    border-left: 3px solid #3b82f6;
    border-radius: 8px;
    font-size: 0.85rem;
    line-height: 1.6;
    color: #93c5fd;
    font-style: italic;
}

.explanation-disclaimer i {
    margin-right: 0.5rem;
    color: #3b82f6;
}
```

#### Change 2: Added explanation section HTML (After stats-grid div)
```html
{% if reasons %}
<div class="explanation-section">
    <div class="explanation-header">
        <i class="fa-solid fa-lightbulb"></i>
        <span>Why this was flagged</span>
    </div>
    <ul class="reasons-list">
        {% for reason in reasons %}
        <li>{{ reason }}</li>
        {% endfor %}
    </ul>
    {% if disclaimer %}
    <div class="explanation-disclaimer">
        <i class="fa-solid fa-info-circle"></i>
        {{ disclaimer }}
    </div>
    {% endif %}
</div>
{% endif %}
```

---

## Usage Flow

### One-Time Setup
```bash
cd /home/mahmoud/Desktop/ChainML-Guard
python scripts/compute_thresholds.py
```

This creates `thresholds.json` containing:
```json
{
    "age_p10": 45.2,
    "tx_p90": 156.0,
    "bal_p05": 0.001234,
    "bal_p95": 12.456789,
    "rate_p90": 2.3456
}
```

### Run Flask App
```bash
python app.py
```

App will:
1. Load thresholds.json at startup
2. For each address analyzed:
   - Compute risk score (existing)
   - Generate explanation reasons (NEW)
   - Display in UI with disclaimer (NEW)

---

## Key Features

✅ **Data-Driven:** All thresholds computed from training data, not hardcoded
✅ **No Data Leakage:** Uses training set only for threshold computation
✅ **Heuristic Rules:** Simple, interpretable explanations (not model internals)
✅ **Cautious Language:** Uses "indicators" not "proof"; includes disclaimer
✅ **Graceful Degradation:** App works without thresholds.json (no explanations shown)
✅ **Sender-Only Scope:** Matches paper scope (sender EOA screening)
✅ **3 Features Only:** balance, tx_count, wallet_age_days (+ derived activity rate)

---

## Testing

### Manual Test
1. Run `python scripts/compute_thresholds.py`
2. Verify `thresholds.json` exists
3. Run `python test_explanation_feature.py` to see example outputs
4. Run `python app.py`
5. Visit http://localhost:5000
6. Enter test addresses and verify explanation section appears

### Test Cases
- **High-risk address:** Should show multiple reasons (new wallet, high activity, etc.)
- **Low-risk address:** Should show "No strong risk indicators..."
- **Missing thresholds.json:** App should run but not show explanation section

---

## Maintenance

### When to Recompute Thresholds
- After retraining model with new data
- After modifying dataset_final.csv
- After changing train/test split parameters

### How to Customize
- **Thresholds:** Edit `scripts/compute_thresholds.py` (change percentiles)
- **Rules:** Edit `utils/explanations.py` (modify `generate_reason_summary()`)
- **UI:** Edit `templates/index.html` (change styling or layout)
- **Wording:** Edit `utils/explanations.py` (change reason strings and disclaimer)

---

## Deliverables Checklist

✅ **A) Offline thresholds script:** `scripts/compute_thresholds.py`
✅ **B) Reason summary function:** `utils/explanations.py::generate_reason_summary()`
✅ **C) Flask route modifications:** `app.py` (lines 89-112)
✅ **D) HTML template updates:** `templates/index.html` (CSS + explanation section)
✅ **E) Instructions:** `EXPLANATION_FEATURE.md` (complete documentation)

---

## Questions or Issues?

Refer to:
- `EXPLANATION_FEATURE.md` for detailed documentation
- `test_explanation_feature.py` for testing
- This file for implementation summary

All files are properly documented with docstrings and comments.
