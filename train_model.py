import pandas as pd
import numpy as np
import os
import pickle
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# ENVIRONMENT PREPARATION
if not os.path.exists('models'):
    os.makedirs('models')

print(" Loading the new balanced dataset...")
try:
    df = pd.read_csv('data/dataset_final.csv')
except FileNotFoundError:
    print(" Error: dataset_final.csv not found. Run data_collection.py first.")
    exit()

# Feature extraction (Features) and target (Label)
X = df[['balance', 'tx_count', 'age_days']].values
y = df['is_fraud'].values

# DATA PREPROCESSING
# 80% Training / 20% Test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Normalization (Standardization)
# Mean and standard deviation are computed on training data and applied to test data
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Save the scaler (Required for app.py)
with open('models/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print(" Scaler saved in models/scaler.pkl")

# NEURAL NETWORK ARCHITECTURE (DEEP LEARNING)
model = Sequential([
    # Input layer: 16 neurons, ReLU handles non-linearity well
    Dense(16, input_dim=3, activation='relu', kernel_initializer='he_normal'),
    
    # 30% dropout to make the model more robust (prevents overfitting)
    Dropout(0.3),
    
    # Intermediate hidden layer
    Dense(8, activation='relu'),
    
    # Output layer: Sigmoid converts output into a probability (0 to 1)
    Dense(1, activation='sigmoid')
])

# Compilation using Adam optimizer (very efficient for binary classification)
model.compile(
    loss='binary_crossentropy',
    optimizer=Adam(learning_rate=0.001),
    metrics=['accuracy']
)

# TRAINING
print("\n Training the new AI model...")
history = model.fit(
    X_train, y_train,
    epochs=120,
    batch_size=16,
    validation_data=(X_test, y_test),
    shuffle=True,
    verbose=1
)

# SAVING AND VALIDATION
model.save('models/fraud_model.h5')

print("\n" + "="*40)
print(" TRAINING SUCCESSFUL")
print(f" Model exported: models/fraud_model.h5")
print("="*40)

# Final evaluation on unseen test data
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f" Final test accuracy: {accuracy*100:.2f}%")
