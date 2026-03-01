"""
Setup script to organize model artifacts into the new structure
================================================================
This script copies existing MLP artifacts to models/mlp/ folder
while maintaining backward compatibility (original files stay in place).
"""

import os
import shutil

print("="*60)
print("ORGANIZING MODEL ARTIFACTS")
print("="*60)

# Ensure directories exist
os.makedirs('models/mlp', exist_ok=True)
os.makedirs('models/logreg', exist_ok=True)
os.makedirs('models/rf', exist_ok=True)

# Copy MLP artifacts if they don't already exist in new location
if os.path.exists('models/fraud_model.h5'):
    if not os.path.exists('models/mlp/model.h5'):
        shutil.copy2('models/fraud_model.h5', 'models/mlp/model.h5')
        print("✓ Copied models/fraud_model.h5 -> models/mlp/model.h5")
    else:
        print("✓ models/mlp/model.h5 already exists")
else:
    print("✗ models/fraud_model.h5 not found (will need to train MLP)")

if os.path.exists('models/scaler.pkl'):
    if not os.path.exists('models/mlp/scaler.pkl'):
        shutil.copy2('models/scaler.pkl', 'models/mlp/scaler.pkl')
        print("✓ Copied models/scaler.pkl -> models/mlp/scaler.pkl")
    else:
        print("✓ models/mlp/scaler.pkl already exists")
else:
    print("✗ models/scaler.pkl not found (will need to train MLP)")

# Copy thresholds.json if it exists (for explanation feature)
if os.path.exists('thresholds.json'):
    if not os.path.exists('models/mlp/thresholds.json'):
        shutil.copy2('thresholds.json', 'models/mlp/thresholds.json')
        print("✓ Copied thresholds.json -> models/mlp/thresholds.json")
    else:
        print("✓ models/mlp/thresholds.json already exists")

print("\n" + "="*60)
print("✓ ARTIFACT ORGANIZATION COMPLETE")
print("="*60)
print("\nNote: Original files remain in place for Flask compatibility.")
print("      Flask app will continue to work without modification.")
