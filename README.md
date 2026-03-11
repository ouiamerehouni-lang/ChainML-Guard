# 🛡️ ChainML Guard

<div align="center">

### AI-Powered Ethereum Fraud Detection System

**Protect yourself from malicious addresses before it's too late**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)](https://www.tensorflow.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Features](#-features) • [Quick Start](#-quick-start) • [Usage](#-usage) • [API](#-api-reference) • [Development](#-development)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [How It Works](#-how-it-works)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [API Reference](#-api-reference)
- [Model Performance](#-model-performance)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Authors](#-authors)

---

## 🎯 Overview

**ChainML Guard** is an intelligent fraud detection system that leverages **Machine Learning** and **Real-time Blockchain Analysis** to identify malicious Ethereum addresses before you interact with them. Think of it as an AI-powered bodyguard for your crypto wallet.

### The Problem

Crypto scams cost users **billions of dollars** annually through:
- 🎣 Phishing attacks
- 💸  Wallet drainers
- 🎭 Rug pulls
- 🤖 Bot-operated scams

### Our Solution

ChainML Guard analyzes Ethereum addresses in real-time using:
- ✅ **3 Advanced ML Models** (MLP Neural Network, Random Forest, Logistic Regression)
- ✅ **Real-time Blockchain Data** from Etherscan API
- ✅ **Explainable AI** - Know WHY an address is flagged
- ✅ **99% Accuracy** - Validated through rigorous testing

---

## ✨ Key Features

### 🤖 AI-Powered Detection
- **3 Machine Learning Models**:
  - **MLP Neural Network**: Deep learning for pattern recognition
  - **Random Forest**: Best performer (99.01% F1 score, 0.9993 ROC-AUC)
  - **Logistic Regression**: Fast baseline for comparison
- **Real-time Prediction**: Get results in seconds
- **Continuous Learning**: Models improve over time

### 🔍 Blockchain Analysis
- Analyzes 3 key features:
  - **Balance**: Wallet's ETH holdings
  - **Transaction Count**: Number of transactions
  - **Wallet Age**: Days since first transaction
- **Live Data**: Direct integration with Etherscan API
- **Rate Limit Handling**: Intelligent API management

### 🛡️ Security & Trust
- **Explainable Results**: See exactly why an address is flagged
- **Risk Scoring**: 0-100% fraud probability
- **Data-Driven Alerts**: Thresholds based on training data
- **No Data Leakage**: Validated with label shuffle tests

### 🌐 User-Friendly Interface
- **Web Dashboard**: Modern Flask-based UI
- **MetaMask Integration**: (Coming soon)
- **Transaction History**: Track your analysis
- **Visual Indicators**: Clear risk warnings

---

## 🔍 How It Works

```
1. User submits Ethereum address
        ↓
2. Fetch real-time data from Etherscan
   (balance, transactions, age)
        ↓
3. Preprocess with StandardScaler
        ↓
4. ML Model predicts fraud probability
        ↓
5. Generate explanation with reasons
        ↓
6. Display result + risk score + warnings
```

### Example Analysis

**Input**: `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`

**Output**:
- ⚠️ **Risk Score**: 76.79%
- 🚨 **Status**: DANGER - Fraud Detected
- 📊 **Stats**: Balance: 0.00000000001 ETH, Transactions: 3, Age: 328 days
- 💡 **Reasons**: 
  - Very new wallet
  - High activity for its age
  - Unusually low balance

---

## 📋 Prerequisites

Before you begin, ensure you have:

### Required
- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
  - Alternative: Python 3.11+ (for local development)
- **Etherscan API Key** - [Get free key](https://etherscan.io/apis)
  - Register at Etherscan
  - Verify your email
  - Generate API key in your account settings

### Optional
- **MetaMask** - Browser extension for wallet integration
- **Ganache** - Local blockchain for testing smart contracts
- **Truffle** - Smart contract development framework

---

## 🚀 Quick Start

### Step 1: Clone the Repository

```bash
git clone https://github.com/ouiamerehouni-lang/ChainML-Guard.git
cd ChainML-Guard
```

### Step 2: Configure Environment

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` and add your Etherscan API key:
```bash
# .env file
ETHERSCAN_API_KEY=your_actual_api_key_here
```

> 💡 **Get Your API Key**: Visit [https://etherscan.io/apis](https://etherscan.io/apis) to create a free account and generate your key.

### Step 3: Build Docker Image

```bash
docker build -t chainml-guard .
```

This builds the Docker image with all dependencies.

### Step 4: Run the Application

```bash
docker run -p 5000:5000 -v $(pwd):/app --env-file .env chainml-guard
```

**What this does:**
- `-p 5000:5000`: Maps port 5000 (container) to 5000 (your machine)
- `-v $(pwd):/app`: Mounts current directory for live code reload
- `--env-file .env`: Loads environment variables from .env file
- `chainml-guard`: The image name we built

### Step 5: Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

You should see the ChainML Guard interface! 🎉

---

## 📖 Usage Guide

### Using the Web Interface

1. **Analyze an Address**
   ```
   http://localhost:5000
   ```
   - Enter Ethereum address (e.g., `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`)
   - Click **"Analyze Address"**
   - View results in real-time

2. **Interpret Results**
   - 🟢 **Safe** (< 50%): Low fraud risk
   - 🔴 **Danger** (≥ 50%): High fraud risk - Avoid transaction!
   - View detailed reasons and statistics

3. **View History**
   ```
   http://localhost:5000/dashboard
   ```
   - See all your previous analyses
   - Track patterns over time

### Using Docker Compose (Alternative)

If you prefer Docker Compose:

```bash
# Start application
docker-compose up

# Run in background
docker-compose up -d

# Stop application
docker-compose down
```

### Training Models

**Train Logistic Regression:**
```bash
docker run --rm -v $(pwd):/app --env-file .env chainml-guard python training/train_logreg.py
```

**Train Random Forest:**
```bash
docker run --rm -v $(pwd):/app --env-file .env chainml-guard python training/train_rf.py
```

**Train MLP (Neural Network):**
```bash
docker run --rm -v $(pwd):/app --env-file .env chainml-guard python train_model.py
```

### Model Evaluation

**Compare all models:**
```bash
docker run --rm -v $(pwd):/app --env-file .env chainml-guard python experiments/evaluate_models.py
```

**Comprehensive robustness testing** (5-fold CV + repeated splits):
```bash
docker run --rm -v $(pwd):/app --env-file .env chainml-guard python experiments/robust_evaluation.py
```
⏱️ *Runtime: ~15-25 minutes (trains 45 models)*

**View results:**
```bash
# Quick comparison
cat results/metrics.csv

# Detailed cross-validation metrics
cat results/robust_eval/cv_5fold_summary.csv

# Repeated splits metrics
cat results/robust_eval/repeated_splits_summary.csv
```

---

## 🔌 API Reference

### POST `/analyze`

Analyze an Ethereum address for fraud.

**Request:**
```javascript
POST http://localhost:5000/analyze
Content-Type: application/json

{
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "amount": "1.0"  // Optional: transaction amount in ETH
}
```

**Response:**
```javascript
{
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "risk_score": 76.79,
  "status": "DANGER: Fraud detected",
  "confidence": "high",
  "balance": 0.00000000001,
  "transactions": 3,
  "age_days": 328,
  "reasons": [
    "Very new wallet",
    "High activity for its age",
    "Unusually low balance"
  ],
  "timestamp": "2026-03-11T10:30:45Z"
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid address format
- `429`: Rate limit exceeded (Etherscan API)
- `500`: Server error

### GET `/dashboard`

View analysis history.

**Response:** HTML dashboard with all previous analyses

---

## 📊 Model Performance

### Production Model: Random Forest

| Metric | 5-Fold CV | 10 Repeated Splits |
|--------|-----------|-------------------|
| **Accuracy** | 98.89% ± 1.04% | 98.75% ± 1.15% |
| **Precision** | 98.56% ± 1.91% | 99.02% ± 1.62% |
| **Recall** | 99.50% ± 1.00% | 98.75% ± 1.25% |
| **F1 Score** | 99.01% ± 0.92% | 98.88% ± 1.03% |
| **ROC-AUC** | 0.9993 ± 0.0014 | **0.9996 ± 0.0005** |

### Model Comparison

| Model | F1 Score | ROC-AUC | Best For |
|-------|----------|---------|----------|
| **Random Forest** | **99.01%** | **0.9993** | Production (best overall) |
| MLP Neural Net | 97.55% | 0.9967 | Complex patterns |
| Logistic Regression | 97.08% | 0.9973 | Fast inference |

### Dataset

- **Size**: 360 Ethereum addresses
- **Split**: 80% train (288), 20% test (72)
- **Source**: ethereum-lists (darklist + lightlist)
- **Labels**: 
  - 44.4% legitimate (160 addresses)
  - 55.6% fraudulent (200 addresses)
- **Validation**: 5-fold cross-validation + 10 repeated random splits
- **Data Leakage Check**: ✅ Passed (label shuffle test ~50% accuracy)

---

## 📁 Project Structure

```
ChainML-Guard/
│
├── 📱 Web Application
│   ├── app.py                          # Flask server
│   ├── templates/
│   │   ├── index.html                  # Main interface
│   │   └── dashboard.html              # Analysis history
│   └── static/                         # (CSS, JS, images)
│
├── 🤖 Machine Learning
│   ├── models/
│   │   ├── fraud_model.h5              # Trained MLP (production)
│   │   ├── scaler.pkl                  # Feature normalizer
│   │   ├── mlp/                        # MLP artifacts
│   │   ├── logreg/                     # Logistic Regression
│   │   └── rf/                         # Random Forest
│   │
│   ├── training/
│   │   ├── train_model.py              # Train MLP
│   │   ├── train_logreg.py             # Train Logistic Regression
│   │   ├── train_rf.py                 # Train Random Forest
│   │   └── setup_model_structure.py    # Organize model files
│   │
│   └── experiments/
│       ├── evaluate_models.py          # Compare all models
│       └── robust_evaluation.py        # Rigorous validation
│
├── 🔍 Data & Features
│   ├── data/
│   │   └── dataset_final.csv           # Training dataset (360 addresses)
│   ├── data_collection.py              # Etherscan API client
│   ├── fetch_safe_addresses.py         # Fetch legitimate addresses
│   └── utils/
│       └── explanations.py             # Explainable AI logic
│
├── 🔗 Blockchain (Smart Contracts)
│   ├── contracts/
│   │   └── FraudGuard.sol              # Solidity smart contract
│   ├── migrations/
│   │   └── 2_deploy_contracts.js       # Truffle deployment
│   ├── truffle-config.js               # Truffle configuration
│   └── package.json                    # Node.js dependencies
│
├── 🐳 Deployment
│   ├── Dockerfile                      # Docker image definition
│   ├── docker-compose.yml              # Multi-container setup
│   ├── requirements.txt                # Python dependencies
│   └── .env.example                    # Environment template
│
├── 📊 Results & Analysis
│   ├── results/
│   │   ├── metrics.csv                 # Model comparison
│   │   └── robust_eval/                # Validation results
│   ├── history.json                    # Analysis history
│   └── thresholds.json                 # Explanation thresholds
│
└── 📚 Documentation
    ├── README.md                       # This file
    └── .gitignore                      # Git ignore rules
```

---

## 🛠️ Development

### Local Development (Without Docker)

For faster iteration during development:

1. **Create virtual environment:**
```bash
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set environment variables:**
```bash
export ETHERSCAN_API_KEY="your_key_here"  # Windows: set ETHERSCAN_API_KEY=...
```

4. **Run Flask app:**
```bash
python app.py
```

5. **Access at:** http://localhost:5000

### Smart Contract Development

**Prerequisites**: Node.js, Truffle

1. **Install Truffle:**
```bash
npm install -g truffle
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start Ganache** (local blockchain)

4. **Compile contracts:**
```bash
truffle compile
```

5. **Deploy to local network:**
```bash
truffle migrate --network development
```

6. **Run tests:**
```bash
truffle test
```

### Running Tests

```bash
# Test data collection
docker run --rm -v $(pwd):/app --env-file .env chainml-guard python data_collection.py

# Evaluate models
docker run --rm -v $(pwd):/app --env-file .env chainml-guard python experiments/evaluate_models.py

# Full validation suite
docker run --rm -v $(pwd):/app --env-file .env chainml-guard python experiments/robust_evaluation.py
```

### Code Quality

```bash
# Format code (if using black)
black app.py

# Check linting (if using flake8)
flake8 app.py

# Type checking (if using mypy)
mypy app.py
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "Error: AI files not found"

**Solution**: Ensure model files exist
```bash
ls -lh models/fraud_model.h5 models/scaler.pkl
```
If missing, train the model:
```bash
docker run --rm -v $(pwd):/app chainml-guard python train_model.py
```

#### 2. "Rate limit reached" (Etherscan API)

**Solution**: 
- Free tier: 5 calls/second
- Wait 6 seconds between calls (handled automatically)
- Upgrade to paid plan for higher limits

#### 3. "Port 5000 already in use"

**Solution**: Use different port
```bash
docker run -p 5001:5000 -v $(pwd):/app chainml-guard
```
Then access at: http://localhost:5001

#### 4. Docker build fails

**Solution**:
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t chainml-guard .
```

#### 5. "Permission denied" errors

**Solution Linux/Mac**:
```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Or run with sudo
sudo docker run -p 5000:5000 -v $(pwd):/app chainml-guard
```

#### 6. Model predictions seem incorrect

**Solution**:
- Re-generate thresholds:
```bash
docker run --rm -v $(pwd):/app chainml-guard python scripts/compute_thresholds.py
```
- Verify dataset is up to date
- Check Etherscan API is returning valid data

### Getting Help

If you encounter issues:

1. Check [Issues](https://github.com/ouiamerehouni-lang/ChainML-Guard/issues) page
2. Search for similar problems
3. Create new issue with:
   - Error message
   - Steps to reproduce
   - Your environment (OS, Docker version, Python version)

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

- 🐛 **Report bugs** - Found a bug? Open an issue
- 💡 **Suggest features** - Have an idea? We'd love to hear it
- 📝 **Improve documentation** - Help others understand the project
- 🔧 **Submit pull requests** - Fix bugs or add features

### Contribution Process

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Test thoroughly**
   ```bash
   docker run --rm -v $(pwd):/app chainml-guard python experiments/evaluate_models.py
   ```
5. **Commit with clear message**
   ```bash
   git commit -m "feat: add amazing feature"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide for Python
- Add docstrings to functions
- Update README for new features
- Test with multiple Ethereum addresses
- Ensure Docker build succeeds

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**TL;DR** - You can:
- ✅ Use commercially
- ✅ Modify
- ✅ Distribute
- ✅ Use privately

With conditions:
- 📝 Include license and copyright notice
- ⚠️ No liability or warranty

---

## 👥 Authors

**ChainML Guard** is developed and maintained by:

- **REHOUNI Ouiame** - [@ouiamerehouni-lang](https://github.com/ouiamerehouni-lang)
  - Machine Learning Engineer
  - Project Lead
  
- **ANINI Hiba**
  - Blockchain Developer
  - Smart Contract Architecture

### Academic Affiliation

This project was developed as part of academic research in:
- 🎓 Blockchain Security
- 🤖 Machine Learning Applications
- 🔒 Fraud Detection Systems

---

## 🙏 Acknowledgments

We would like to thank:

- **ethereum-lists** - For providing curated lists of fraudulent and legitimate addresses
- **Etherscan** - For their comprehensive blockchain API
- **TensorFlow & scikit-learn communities** - For excellent ML frameworks
- **Flask community** - For the lightweight web framework
- **Open-source contributors** - For inspiring this project

### References

- [Ethereum Lists Project](https://github.com/ethereum-lists)
- [Etherscan API Documentation](https://docs.etherscan.io/)
- [TensorFlow Documentation](https://www.tensorflow.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

## 📞 Contact

Have questions or suggestions?

- 📧 Email: [Create an issue](https://github.com/ouiamerehouni-lang/ChainML-Guard/issues)
- 🐛 Bug Reports: [GitHub Issues](https://github.com/ouiamerehouni-lang/ChainML-Guard/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/ouiamerehouni-lang/ChainML-Guard/discussions)

---

## ⭐ Star History

If you find this project useful, please consider starring it on GitHub!

<div align="center">

**Made with ❤️ for the Ethereum community**

[⬆ Back to Top](#️-chainml-guard)

</div>
