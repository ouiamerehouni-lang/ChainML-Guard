import pandas as pd
import numpy as np
import pickle
from tensorflow.keras.models import load_model
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load data and model
df = pd.read_csv('data/dataset_final.csv')
model = load_model('models/fraud_model.h5')
with open('models/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

# 2. Prepare test data (same logic as train_model)
X = df[['balance', 'tx_count', 'age_days']].values
y_true = df['is_fraud'].values

# Normalization
X_scaled = scaler.transform(X)

# 3. Prediction
y_pred_prob = model.predict(X_scaled)
y_pred = (y_pred_prob > 0.5).astype(int)  # 50% threshold to decide whether it is fraud

# 4. Classification report
print("\nCLASSIFICATION REPORT")
print(classification_report(y_true, y_pred, target_names=['Legitimate (0)', 'Fraud (1)']))

# 5. Confusion matrix
cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(8,6))
sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues',
    xticklabels=['Predicted Legitimate', 'Predicted Fraud'],
    yticklabels=['Actual Legitimate', 'Actual Fraud']
)
plt.xlabel('Prediction')
plt.ylabel('Actual')
plt.title('Confusion Matrix - Fraud Detection')
plt.show()
