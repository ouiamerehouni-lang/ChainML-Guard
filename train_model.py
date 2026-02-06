import pandas as pd
import numpy as np
import os
import pickle
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

#PRÉPARATION DE L'ENVIRONNEMENT 
if not os.path.exists('models'):
    os.makedirs('models')

print(" Chargement du nouveau dataset équilibré...")
try:
    df = pd.read_csv('data/dataset_final.csv')
except FileNotFoundError:
    print(" Erreur : dataset_final.csv introuvable. Lancez data_collection.py d'abord.")
    exit()

# Extraction des caractéristiques (Features) et de la cible (Label)
X = df[['balance', 'tx_count', 'age_days']].values
y = df['is_fraud'].values

# --- 2. PRÉ-TRAITEMENT DES DONNÉES ---
# Division 80% Entraînement / 20% Test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Normalisation (Standardisation)
# On calcule la moyenne/écart-type sur le train et on l'applique sur le test
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Sauvegarde du scaler (Indispensable pour app.py)
with open('models/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print(" Scaler sauvegardé dans models/scaler.pkl")

# --- 3. ARCHITECTURE DU RÉSEAU DE NEURONES (DEEP LEARNING) ---
model = Sequential([
    # Couche d'entrée : 16 neurones, ReLU gère bien la non-linéarité
    Dense(16, input_dim=3, activation='relu', kernel_initializer='he_normal'),
    
    # Dropout de 30% pour forcer le modèle à être plus robuste (évite la paranoïa)
    Dropout(0.3),
    
    # Couche cachée intermédiaire
    Dense(8, activation='relu'),
    
    # Couche de sortie : Sigmoid pour transformer le signal en probabilité (0 à 1)
    Dense(1, activation='sigmoid')
])

# Compilation avec l'optimiseur Adam (très performant pour la classification binaire)
model.compile(
    loss='binary_crossentropy', 
    optimizer=Adam(learning_rate=0.001), 
    metrics=['accuracy']
)

# --- 4. ENTRAÎNEMENT ---
print("\n Entraînement du nouveau modèle IA...")
history = model.fit(
    X_train, y_train, 
    epochs=120,           
    batch_size=16,        
    validation_data=(X_test, y_test),
    shuffle=True,         
    verbose=1
)

# --- 5. SAUVEGARDE ET VALIDATION ---
model.save('models/fraud_model.h5')

print("\n" + "="*40)
print(" ENTRAÎNEMENT RÉUSSI")
print(f" Modèle exporté : models/fraud_model.h5")
print("="*40)

# Évaluation finale sur les données que l'IA n'a jamais vues
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f" Précision finale sur les tests : {accuracy*100:.2f}%")