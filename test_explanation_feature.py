"""
Quick Start Guide: Testing the Explanation Feature
===================================================

This guide will walk you through testing the new explanation feature.

Prerequisites:
- dataset_final.csv exists in data/
- fraud_model.h5 and scaler.pkl exist in models/
- All dependencies installed (pip install -r requirements.txt)
"""

# Step 1: Compute Thresholds
# ---------------------------
print("Step 1: Computing thresholds from training data...")
print("Command: python scripts/compute_thresholds.py")
print()

# Expected output will show:
# - Dataset loaded
# - Train/test split
# - Computed percentile values
# - Saved to thresholds.json

# Step 2: Verify Thresholds File
# --------------------------------
print("Step 2: Verify thresholds.json was created...")
import os
import json

if os.path.exists('thresholds.json'):
    with open('thresholds.json', 'r') as f:
        thresholds = json.load(f)
    print("✓ thresholds.json found!")
    print("Thresholds:")
    for key, value in thresholds.items():
        print(f"  {key}: {value}")
else:
    print("✗ thresholds.json not found. Run Step 1 first.")
    exit(1)

print()

# Step 3: Test Explanation Function
# -----------------------------------
print("Step 3: Testing explanation generation...")

from utils.explanations import generate_reason_summary, get_explanation_disclaimer

# Test Case 1: New wallet with high activity
print("\nTest Case 1: New wallet with high activity")
print("-" * 50)
reasons = generate_reason_summary(
    balance=0.005,  # Low balance
    tx_count=500,   # High tx count
    wallet_age_days=5,  # Very new
    thresholds=thresholds
)
print("Reasons:")
for r in reasons:
    print(f"  → {r}")

# Test Case 2: Normal wallet
print("\nTest Case 2: Normal wallet")
print("-" * 50)
reasons = generate_reason_summary(
    balance=1.5,
    tx_count=50,
    wallet_age_days=365,
    thresholds=thresholds
)
print("Reasons:")
for r in reasons:
    print(f"  → {r}")

# Test Case 3: Old wallet with extreme balance
print("\nTest Case 3: Old wallet with extreme high balance")
print("-" * 50)
reasons = generate_reason_summary(
    balance=1000.0,  # Very high
    tx_count=100,
    wallet_age_days=730,
    thresholds=thresholds
)
print("Reasons:")
for r in reasons:
    print(f"  → {r}")

print("\n" + "=" * 50)
print("Disclaimer:")
print(get_explanation_disclaimer())
print("=" * 50)

# Step 4: Run Flask App
# -----------------------
print("\n\nStep 4: Ready to run Flask app!")
print("Command: python app.py")
print("\nThen visit: http://localhost:5000")
print("Enter an Ethereum address to see the explanation feature in action!")
