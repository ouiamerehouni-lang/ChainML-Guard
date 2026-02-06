import pandas as pd
import numpy as np
import pickle
from tensorflow.keras.models import load_model
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Charger les données et le modèle
df = pd.read_csv('data/dataset_final.csv')
model = load_model('models/fraud_model.h5')
with open('models/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

# 2. Préparer les données de test (on reprend la même logique que train_model)
X = df[['balance', 'tx_count', 'age_days']].values
y_true = df['is_fraud'].values

# Normalisation
X_scaled = scaler.transform(X)

# 3. Prédiction
y_pred_prob = model.predict(X_scaled)
y_pred = (y_pred_prob > 0.5).astype(int) # Seuil de 50% pour décider si c'est une fraude

# 4. Rapport de classification
print("\n--- RAPPORT DE CLASSIFICATION ---")
print(classification_report(y_true, y_pred, target_names=['Sain (0)', 'Fraude (1)']))

# 5. Matrice de Confusion
cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Prédit Sain', 'Prédit Fraude'], 
            yticklabels=['Réel Sain', 'Réel Fraude'])
plt.xlabel('Prédiction')
plt.ylabel('Réalité')
plt.title('Matrice de Confusion - Détection de Fraude')
plt.show()