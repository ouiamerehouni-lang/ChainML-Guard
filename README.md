# ChainML Guard: AI-Powered Ethereum Fraud Detection

<div align="center">

**Proactive blockchain security using Machine Learning to detect fraudulent Ethereum addresses before transactions**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)](https://www.tensorflow.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

*Developed by: REHOUNI Ouiame and ANINI Hiba*

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Model Performance](#-model-performance)
- [Project Structure](#-project-structure)
- [Usage Guide](#-usage-guide)
- [Development](#-development)

---

## 🎯 Overview

ChainML Guard is an intelligent fraud detection system that combines **Deep Learning**, **Blockchain technology**, and **Real-time Analysis** to protect users from malicious Ethereum addresses (wallet drainers, scams, etc.) before completing transactions.

### Key Capabilities
- ✅ Real-time fraud prediction using ML models
- ✅ Analyzes blockchain transaction patterns  
- ✅ Explainable AI with reason-based alerts
- ✅ Web interface with MetaMask integration
- ✅ Multiple model comparison (MLP, Random Forest, Logistic Regression)

---

## ✨ Features

### 🤖 Machine Learning Models
- **Multi-Layer Perceptron (MLP)**: Deep neural network for pattern recognition
- **Random Forest**: Best performer (99% accuracy, 0.9996 ROC-AUC)
- **Logistic Regression**: Fast baseline model
- **Robust Evaluation**: 5-fold CV + repeated splits validation

### 🔍 Analysis Features
- 3 key features: Balance, Transaction Count, Wallet Age
- Real-time Etherscan API integration
- Explainable predictions with risk indicators
- Historical analysis dashboard

### 🛡️ Security Features
- Pre-transaction fraud detection
- Risk score calculation (0-100%)
- Data-driven threshold alerts
- Label shuffle validation (no data leakage)

### 🌐 Web Interface
- Flask-based dashboard
- MetaMask wallet integration
- Transaction history tracking
- Visual risk indicators

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ChainML Guard                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │   Frontend   │◄──►│   Backend    │◄──►│  AI Engine   │     │
│  │   (Flask)    │    │  (Python)    │    │ (TensorFlow) │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│         │                    │                     │            │
│         ▼                    ▼                     ▼            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │   MetaMask   │    │  Etherscan   │    │   Models     │     │
│  │ Integration  │    │     API      │    │  (MLP/RF)    │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack
- **Backend**: Python, Flask
- **ML/AI**: TensorFlow, scikit-learn
- **Blockchain**: Ethereum, Solidity, Truffle
- **API**: Etherscan
- **Deployment**: Docker, Docker Compose

---

## 🚀 Quick Start

### Prerequisites
- **Docker Desktop** (installed and running)
- **MetaMask** browser extension
- **Ganache** (optional, for local blockchain testing)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ouiamerehouni-lang/ChainML-Guard.git
cd ChainML-Guard
```

2. **Build Docker image**
```bash
docker build -t chainml-guard .
```

3. **Run the application**
```bash
docker run -p 5000:5000 -v $(pwd):/app chainml-guard
```

4. **Access the web interface**
```
Open browser: http://localhost:5000
```

### Using Docker Compose (Alternative)
```bash
docker-compose up
```

---

## 📊 Model Performance

### Best Model: Random Forest

| Evaluation Method | F1 Score | ROC-AUC | Accuracy |
|-------------------|----------|---------|----------|
| **5-Fold CV** | 99.01% ± 0.92% | 0.9993 ± 0.0014 | 98.89% ± 1.04% |
| **10 Repeated Splits** | 98.88% ± 1.03% | 0.9996 ± 0.0005 | 98.75% ± 1.15% |

### Model Comparison

| Model | F1 Score (CV) | ROC-AUC (CV) | Stability |
|-------|---------------|--------------|-----------|
| **Random Forest** | **0.990±0.009** | **0.9993±0.001** | ⭐⭐⭐⭐⭐ |
| MLP | 0.976±0.008 | 0.9967±0.004 | ⭐⭐⭐⭐ |
| Logistic Regression | 0.971±0.006 | 0.9973±0.003 | ⭐⭐⭐⭐ |

### Dataset
- **Size**: 360 Ethereum addresses
- **Features**: balance, tx_count, age_days
- **Labels**: 44.4% legitimate, 55.6% fraudulent
- **Source**: ethereum-lists (darklist/lightlist)

---

## 📁 Project Structure

```
ChainML-Guard/
├── app.py                      # Flask web application
├── data_collection.py          # Etherscan API data fetcher
├── train_model.py              # MLP model training
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── requirements.txt            # Python dependencies
│
├── data/
│   └── dataset_final.csv       # Training dataset (360 records)
│
├── models/
│   ├── fraud_model.h5          # Trained MLP model
│   ├── scaler.pkl              # Feature scaler
│   ├── mlp/                    # MLP artifacts
│   ├── logreg/                 # Logistic Regression artifacts
│   └── rf/                     # Random Forest artifacts
│
├── training/
│   ├── train_logreg.py         # Train Logistic Regression
│   ├── train_rf.py             # Train Random Forest
│   └── setup_model_structure.py # Organize model files
│
├── experiments/
│   ├── evaluate_models.py      # Compare all models
│   └── robust_evaluation.py    # 5-fold CV + repeated splits
│
├── utils/
│   └── explanations.py         # Explainable AI logic
│
├── scripts/
│   └── compute_thresholds.py   # Generate explanation thresholds
│
├── templates/
│   ├── index.html              # Main interface
│   └── dashboard.html          # Analysis dashboard
│
├── contracts/
│   └── FraudGuard.sol          # Solidity smart contract
│
└── migrations/
    └── 2_deploy_contracts.js   # Truffle deployment
```

---

## 📖 Usage Guide

### 1. Web Interface

**Analyze an Ethereum Address:**
1. Navigate to http://localhost:5000
2. Enter target Ethereum address
3. Click "Analyze Address"
4. View risk score and explanation

**Risk Indicators:**
- 🟢 **Safe** (< 50%): No fraud pattern detected
- 🔴 **Danger** (≥ 50%): Fraud detected with reasons

### 2. Model Training

**Train individual models:**
```bash
# Train Logistic Regression
docker run --rm -v $(pwd):/app chainml-guard python training/train_logreg.py

# Train Random Forest
docker run --rm -v $(pwd):/app chainml-guard python training/train_rf.py

# Train MLP (original)
docker run --rm -v $(pwd):/app chainml-guard python train_model.py
```

### 3. Model Evaluation

**Compare all models:**
```bash
docker run --rm -v $(pwd):/app chainml-guard python experiments/evaluate_models.py
```

**Robust evaluation (paper-quality):**
```bash
docker run --rm -v $(pwd):/app chainml-guard python experiments/robust_evaluation.py
```
*Runtime: ~15-25 minutes (trains 45 models)*

### 4. View Results

```bash
# Model comparison
cat results/metrics.csv

# Cross-validation results
cat results/robust_eval/cv_5fold_summary.csv
```

---

## 🛠️ Development

### Running Tests

```bash
# Run evaluation
docker run --rm -v $(pwd):/app chainml-guard python experiments/evaluate_models.py

# Test data collection
docker run --rm -v $(pwd):/app chainml-guard python data_collection.py
```

### Local Development (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Flask app
python app.py
```

### Blockchain Development

```bash
# Compile contracts
truffle compile

# Deploy to Ganache
truffle migrate --network development

# Run tests
truffle test
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👥 Authors

- **REHOUNI Ouiame** - [@ouiamerehouni-lang](https://github.com/ouiamerehouni-lang)
- **ANINI Hiba**

---

## 🙏 Acknowledgments

- Ethereum Lists for fraud/legit address datasets
- Etherscan API for real-time blockchain data
- TensorFlow and scikit-learn communities

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

</div>
