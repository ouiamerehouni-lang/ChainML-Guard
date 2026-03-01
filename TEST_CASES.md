# ChainML Guard - Test Cases for Explanation Feature

## Overview
This document provides test cases to verify the explanation feature works correctly.

---

## 🎯 Test Prerequisites

Before testing, ensure:
- ✅ `thresholds.json` exists in project root
- ✅ Flask app is running (http://localhost:5000)
- ✅ Model files exist (fraud_model.h5, scaler.pkl)

**Current Thresholds (from your data):**
```json
{
    "age_p10": 16.75 days,
    "tx_p90": 20 transactions,
    "bal_p05": 0.0 ETH,
    "bal_p95": 36.53 ETH,
    "rate_p90": 0.1607 tx/day
}
```

---

## 📋 Test Cases

### Test Case 1: Very New Wallet (High Risk)
**Scenario:** Test if the system detects very new wallets

**Test Data:**
- **Address:** Any address with age < 16.75 days
- **Expected Reason:** "Very new wallet (age below 10th percentile)"

**How to Test:**
1. Find or use a recently created Ethereum address
2. Enter address in the web UI
3. Check if "Very new wallet" appears in reasons

**Expected Result:**
```
⚡ Why this was flagged:
  → Very new wallet (age below 10th percentile)
  [+ possibly other reasons]
```

---

### Test Case 2: High Transaction Count (Suspicious Activity)
**Scenario:** Test if the system detects unusually high transaction volume

**Test Data:**
- **Address:** Address with > 20 transactions
- **Expected Reason:** "Unusually high transaction count (above 90th percentile)"

**How to Test:**
1. Use an address like: `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb` (has many txs)
2. Enter in the UI
3. Check for high transaction count reason

**Expected Result:**
```
⚡ Why this was flagged:
  → Unusually high transaction count (above 90th percentile)
```

---

### Test Case 3: High Activity Rate for Age
**Scenario:** Test if system detects burst activity (many txs in short time)

**Test Data:**
- **Calculation:** tx_count / wallet_age_days > 0.1607
- **Example:** Wallet with 10 transactions and 10 days old = 1.0 tx/day (HIGH)

**Expected Reason:** "High activity for its age (activity rate above 90th percentile)"

**How to Test:**
1. Use an address that was created recently but has many transactions
2. Check if high activity rate is detected

**Expected Result:**
```
⚡ Why this was flagged:
  → High activity for its age (activity rate above 90th percentile)
```

---

### Test Case 4: Unusually Low Balance
**Scenario:** Test dust accounts or drained wallets

**Test Data:**
- **Balance:** Exactly 0.0 ETH or very close to 0
- **Expected Reason:** "Unusually low balance (below 5th percentile)"

**How to Test:**
1. Use an address with 0 or near-0 balance
2. Enter in the UI

**Expected Result:**
```
⚡ Why this was flagged:
  → Unusually low balance (below 5th percentile)
```

---

### Test Case 5: Unusually High Balance
**Scenario:** Test whale accounts or potential money laundering staging

**Test Data:**
- **Balance:** > 36.53 ETH
- **Expected Reason:** "Unusually high balance (above 95th percentile)"

**How to Test:**
1. Use an address with high balance (> 36.53 ETH)
2. Popular whale addresses work well

**Expected Result:**
```
⚡ Why this was flagged:
  → Unusually high balance (above 95th percentile)
```

---

### Test Case 6: Normal/Safe Wallet
**Scenario:** Test that normal wallets don't get flagged with specific reasons

**Test Data:**
- **Age:** > 16.75 days (not too new)
- **Transactions:** < 20 (normal activity)
- **Balance:** Between 0.0 and 36.53 ETH (normal range)
- **Activity Rate:** < 0.1607 tx/day

**Expected Reason:** "No strong risk indicators from the available features"

**How to Test:**
1. Use an old wallet with moderate activity
2. Enter in the UI

**Expected Result:**
```
⚡ Why this was flagged:
  → No strong risk indicators from the available features
```

---

### Test Case 7: Multiple Flags (High Risk)
**Scenario:** Test wallet that triggers multiple rules

**Test Data:**
- **Age:** < 16.75 days (new)
- **Transactions:** > 20 (high)
- **Balance:** 0 ETH (low)
- **Activity Rate:** > 0.1607 tx/day (high)

**Expected:** Multiple reasons displayed

**Expected Result:**
```
⚡ Why this was flagged:
  → Very new wallet (age below 10th percentile)
  → High activity for its age (activity rate above 90th percentile)
  → Unusually high transaction count (above 90th percentile)
  → Unusually low balance (below 5th percentile)
```

---

### Test Case 8: Risk Score Correlation
**Scenario:** Verify that high risk scores correlate with more explanation reasons

**Test Steps:**
1. Analyze 3-5 different addresses
2. Compare risk scores with number of reasons
3. Verify that:
   - High risk (>70%) → Multiple reasons
   - Medium risk (40-70%) → 1-2 reasons
   - Low risk (<40%) → Few/no strong indicators

---

### Test Case 9: Invalid Address Handling
**Scenario:** Test error handling for invalid addresses

**Test Data:**
- Invalid format: `0x123` (too short)
- Non-hex: `hello world`
- Empty string

**Expected Result:**
- Error message: "Invalid address format"
- No crash or 500 error
- No explanation section shown

---

### Test Case 10: API Connection Failure
**Scenario:** Test behavior when Etherscan API fails

**Test Data:**
- Use invalid address: `0x0000000000000000000000000000000000000000`
- Or disconnect internet momentarily

**Expected Result:**
- Error message: "Unable to reach the blockchain"
- No crash
- No explanation section shown

---

### Test Case 11: Missing Thresholds File
**Scenario:** Test graceful degradation when thresholds.json is missing

**Test Steps:**
1. Stop Flask app
2. Rename/delete `thresholds.json`
3. Start Flask app
4. Try to analyze an address

**Expected Result:**
- App starts with warning: "Explanation thresholds not loaded"
- Address analysis works (risk score shown)
- Explanation section does NOT appear (graceful degradation)

---

### Test Case 12: UI Display Verification
**Scenario:** Verify the UI displays explanations correctly

**Checklist:**
- [ ] "Why this was flagged" header with lightbulb icon appears
- [ ] Reasons displayed as bullet points with arrow (→)
- [ ] Each reason has proper styling (orange border-left)
- [ ] Disclaimer removed (no longer shown)
- [ ] Section appears AFTER feature stats (Balance, Transactions, Age)
- [ ] Section appears BEFORE status message (Transaction secured/blocked)

---

### Test Case 13: Different Risk Levels
**Scenario:** Test UI changes based on risk score

**Test Data:**

**Low Risk (<50%):**
- Status: "HEALTHY: No fraud pattern detected" (green)
- Button: "Pay via FraudGuard" (shown)

**High Risk (≥50%):**
- Status: "DANGER: Fraud detected" (red)
- Button: Hidden
- Message: "Transaction blocked: Risk detected"

**Verify:** Explanation section appears for BOTH risk levels

---

### Test Case 14: Feature Values Display
**Scenario:** Verify the 3 core features are displayed correctly

**Checklist:**
- [ ] Balance shown in ETH (e.g., "1.234 ETH")
- [ ] Transactions shown as integer (e.g., "50")
- [ ] Age shown as rounded integer (e.g., "123 days")
- [ ] All three values match the analysis

---

### Test Case 15: Docker Environment
**Scenario:** Test everything works in Docker

**Test Steps:**
```bash
# 1. Compute thresholds in Docker
docker compose run --rm compute-thresholds

# 2. Verify thresholds created
cat thresholds.json

# 3. Run app in Docker
docker compose up

# 4. Test in browser
# Visit http://localhost:5000
# Analyze an address
```

**Expected Result:**
- Thresholds generated successfully
- App starts without errors
- Console shows: "Explanation thresholds loaded successfully"
- Explanation section appears in UI

---

## 🧪 Quick Test Script

Here's a Python script to test the explanation logic directly:

```python
# test_explanations.py
from utils.explanations import load_thresholds, generate_reason_summary

# Load thresholds
thresholds = load_thresholds()
print("Current Thresholds:")
print(f"  age_p10: {thresholds['age_p10']:.2f} days")
print(f"  tx_p90: {thresholds['tx_p90']:.0f} transactions")
print(f"  bal_p05: {thresholds['bal_p05']:.6f} ETH")
print(f"  bal_p95: {thresholds['bal_p95']:.6f} ETH")
print(f"  rate_p90: {thresholds['rate_p90']:.4f} tx/day")
print()

# Test Case 1: New wallet with high activity
print("Test 1: New wallet with high activity")
reasons = generate_reason_summary(
    balance=0.001,
    tx_count=50,
    wallet_age_days=5,
    thresholds=thresholds
)
for r in reasons:
    print(f"  → {r}")
print()

# Test Case 2: Normal wallet
print("Test 2: Normal wallet")
reasons = generate_reason_summary(
    balance=5.0,
    tx_count=10,
    wallet_age_days=365,
    thresholds=thresholds
)
for r in reasons:
    print(f"  → {r}")
print()

# Test Case 3: High balance whale
print("Test 3: High balance whale")
reasons = generate_reason_summary(
    balance=100.0,
    tx_count=15,
    wallet_age_days=730,
    thresholds=thresholds
)
for r in reasons:
    print(f"  → {r}")
```

**Run it:**
```bash
docker compose run --rm chainml-guard python test_explanations.py
```

---

## ✅ Acceptance Criteria

The feature passes if:

1. **Thresholds Generation:**
   - [x] `docker compose run --rm compute-thresholds` succeeds
   - [x] `thresholds.json` created with 5 keys
   - [x] Values are reasonable (not NaN or infinity)

2. **Flask Startup:**
   - [x] App starts without errors
   - [x] Console shows: "Explanation thresholds loaded successfully"
   - [x] Or warning if missing (graceful degradation)

3. **UI Display:**
   - [x] "Why this was flagged" section appears
   - [x] Reasons displayed as bullets with arrows
   - [x] No disclaimer shown (removed as requested)
   - [x] Styling looks good (orange accents)

4. **Logic Correctness:**
   - [x] New wallets flagged correctly
   - [x] High activity detected
   - [x] Extreme balances flagged
   - [x] Normal wallets show "No strong risk indicators"

5. **Error Handling:**
   - [x] Invalid addresses handled gracefully
   - [x] API failures don't crash the app
   - [x] Missing thresholds.json → graceful degradation

6. **Docker Integration:**
   - [x] All scripts work in Docker
   - [x] Volume mounts save files correctly
   - [x] No dependency issues

---

## 🐛 Common Issues to Check

| Issue | Check | Fix |
|-------|-------|-----|
| No explanation section | Console for "thresholds loaded" | Run `docker compose run --rm compute-thresholds` |
| Wrong reasons shown | Verify thresholds.json values | Regenerate thresholds |
| App crashes | Check console for errors | Verify all dependencies installed |
| Reasons don't make sense | Check feature values | Verify Etherscan API returns correct data |
| Disclaimer still shows | Check `explanations.py` | Verify `get_explanation_disclaimer()` returns `""` |

---

## 📊 Test Checklist

Use this checklist to track your testing:

- [ ] Test Case 1: Very new wallet detection
- [ ] Test Case 2: High transaction count detection
- [ ] Test Case 3: High activity rate detection
- [ ] Test Case 4: Low balance detection
- [ ] Test Case 5: High balance detection
- [ ] Test Case 6: Normal wallet (no flags)
- [ ] Test Case 7: Multiple flags
- [ ] Test Case 8: Risk score correlation
- [ ] Test Case 9: Invalid address handling
- [ ] Test Case 10: API failure handling
- [ ] Test Case 11: Missing thresholds (graceful degradation)
- [ ] Test Case 12: UI display verification
- [ ] Test Case 13: Different risk levels
- [ ] Test Case 14: Feature values display
- [ ] Test Case 15: Docker environment

---

## 📝 Test Report Template

```
ChainML Guard - Explanation Feature Test Report
Date: _______________
Tester: _______________

Environment:
- Docker Version: _______________
- Dataset Records: _______________
- Thresholds Generated: Yes / No

Test Results:
1. Threshold Generation: PASS / FAIL
2. Flask Startup: PASS / FAIL
3. UI Display: PASS / FAIL
4. Logic Correctness: PASS / FAIL
5. Error Handling: PASS / FAIL
6. Docker Integration: PASS / FAIL

Issues Found:
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

Overall Status: PASS / FAIL
```

---

**Happy Testing!** 🚀

If you find any issues, check:
1. `DOCKER_USAGE.md` - Docker troubleshooting
2. `SETUP_GUIDE.md` - Setup troubleshooting
3. Console logs for error messages
