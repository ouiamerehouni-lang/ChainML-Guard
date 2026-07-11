# ChainML Guard

<div align="center">

### AI-Powered Ethereum Fraud Detection System

Protect yourself from malicious addresses before it is too late.

[Key Features](#key-features) | [Quick Start](#quick-start) | [Usage](#usage-guide) | [API](#api-reference) | [Project Structure](#project-structure)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [API Reference](#api-reference)
- [Model Performance](#model-performance)
- [Reproducing the Inference Benchmark](#reproducing-the-inference-benchmark)
- [Project Structure](#project-structure)

---

## Overview

**ChainML Guard** is an intelligent fraud detection system that combines machine learning with real-time blockchain analysis to identify suspicious Ethereum addresses before interaction.

### The Problem

Crypto scams cost users billions of dollars every year through:
- Phishing attacks
- Wallet drainers
- Rug pulls
- Bot-operated scams

### The Solution

ChainML Guard analyzes Ethereum addresses in real time using:
- A deployed MLP Neural Network for application inference
- Benchmark comparison models (Random Forest and Logistic Regression)
- Live blockchain signals from the Etherscan API
- Explainable AI outputs that show why an address is flagged
- High-accuracy model evaluation and validation

---

## Key Features

### AI-Powered Detection
- Application model:
  - MLP Neural Network: deployed model for fraud screening in the application
- Benchmark models:
  - Random Forest: strongest benchmark performance in evaluation
  - Logistic Regression: fast baseline for comparison
- Real-time prediction in seconds
- Model comparison workflow for iterative improvement

### Blockchain Analysis
- Uses three main features:
  - Balance
  - Transaction count
  - Wallet age
- Pulls data directly from Etherscan
- Includes handling for API usage constraints

### Security and Trust
- Explainable prediction output
- Risk scoring from 0 to 100
- Threshold-driven alerting
- Data-leakage validation via label-shuffle testing

### User Experience
- Flask web interface
- Analysis history dashboard
- Clear risk messaging for decision support

---

## How It Works

```text
1. User submits Ethereum address
2. System fetches live data from Etherscan (balance, transactions, age)
3. Features are preprocessed using StandardScaler
4. MLP model computes fraud probability
5. Explanation layer generates reason codes
6. UI returns risk score, status, and supporting details
````

---

## Prerequisites

Before running the project, make sure you have:

### Required

* Python 3.11+
* Etherscan API key ([create one here](https://etherscan.io/apis))

### Optional

* Docker (for containerized workflows)
* Node.js + Truffle + Ganache (for smart contract workflows)

---

## Quick Start

### Option 1: Run locally with Python

#### 1. Clone the repository

```bash
git clone https://github.com/ouiamerehouni-lang/ChainML-Guard.git
cd ChainML-Guard
```

#### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add:

```bash
ETHERSCAN_API_KEY=your_actual_api_key_here
```

#### 3. Create a virtual environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

#### 4. Install dependencies

```bash
pip install -r requirements.txt
```

#### 5. Run the application

```bash
python app.py
```

Open:

```text
http://localhost:5000
```

---

### Option 2: Run with Docker

#### 1. Clone the repository

```bash
git clone https://github.com/ouiamerehouni-lang/ChainML-Guard.git
cd ChainML-Guard
```

#### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add:

```bash
ETHERSCAN_API_KEY=your_actual_api_key_here
```

#### 3. Build the Docker image

```bash
docker build -t chainml-guard .
```

#### 4. Run the container

```bash
docker run --rm --env-file .env -p 5000:5000 chainml-guard
```

Open:

```text
http://localhost:5000
```

---

## Usage Guide

### Web Interface

1. Open `http://localhost:5000`.
2. Enter an Ethereum address (for example `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`).
3. Click `Analyze Address`.
4. Review risk score, status, and explanation details.

### Dashboard

Open `http://localhost:5000/dashboard` to review analysis history.

### Training Models

Train Logistic Regression:

```bash
python training/train_logreg.py
```

Train Random Forest:

```bash
python training/train_rf.py
```

Train MLP:

```bash
python train_model.py
```

### Evaluation

Compare models:

```bash
python experiments/evaluate_models.py
```

Run robustness evaluation:

```bash
python experiments/robust_evaluation.py
```

### Docker: Evaluation Commands

Compare models:

```bash
docker run --rm --env-file .env chainml-guard python experiments/evaluate_models.py
```

Run robustness evaluation:

```bash
docker run --rm --env-file .env chainml-guard python experiments/robust_evaluation.py
```

---

## API Reference

### POST `/analyze`

Analyze an Ethereum address for fraud.

Request:

```javascript
POST http://localhost:5000/analyze
Content-Type: application/json

{
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "amount": "1.0"
}
```

Response:

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

Status codes:

* `200`: success
* `400`: invalid address format
* `429`: rate limit exceeded
* `500`: server error

### GET `/dashboard`

Returns the analysis history dashboard.

---

## Model Performance

### Deployed Application Model: MLP Neural Network

The application uses the MLP model for fraud screening in the live workflow.

### Benchmark Results

| Model               | 5-Fold CV F1 | 10 Repeated Splits F1 | 5-Fold CV ROC-AUC | 10 Repeated Splits ROC-AUC | Role                       |
| ------------------- | ------------ | --------------------- | ----------------- | -------------------------- | -------------------------- |
| MLP Neural Net      | 97.55%       | 98.17%                | 0.9967            | 0.9982                     | Deployed application model |
| Random Forest       | 99.01%       | 98.88%                | 0.9993            | 0.9996                     | Strongest benchmark        |
| Logistic Regression | 97.08%       | 97.22%                | 0.9973            | 0.9986                     | Fast baseline              |

### Dataset

* Size: 360 Ethereum addresses
* Split: 80% train (288), 20% test (72)
* Source: ethereum-lists (darklist + lightlist)
* Labels:

  * 44.4% legitimate (160)
  * 55.6% fraudulent (200)
* Validation: 5-fold cross-validation and repeated random splits
* Data leakage check: passed (label shuffle test near random baseline)

---

## Reproducing the Inference Benchmark

To verify the inference latency measurements reported in the paper, run the benchmark script:

### Quick Start

```bash
docker run --rm -v $(pwd):/app --env-file .env chainml-guard python experiments/benchmark_inference.py
```

### What is Measured

The benchmark measures **local computational cost only** (CPU inference):
- Feature preprocessing: ~0.3 ms
- MLP model inference: ~39 ms (dominates total time)
- Reason summary generation: ~0.01 ms
- **Total per address: ~39 ms** (no network or Etherscan latency)

### Results

Results are saved to **`results/bench_compute_only.json`** with:
- Raw timing measurements (50 trials per component)
- Summary statistics (mean, median, std dev, min, max)
- Environment details (Python version, TensorFlow version, CPU-only flag, timestamp)
- Throughput estimate (~25 predictions per second)

### Details

For complete documentation, see [`docs/INFERENCE_BENCHMARK.md`](docs/INFERENCE_BENCHMARK.md).

---

## Project Structure

```text
ChainML-Guard/
|
|-- Web Application
|   |-- app.py                          # Flask server
|   |-- templates/
|   |   |-- index.html                  # Main interface
|   |   `-- dashboard.html              # Analysis history
|   `-- static/                         # CSS, JS, images
|
|-- Machine Learning
|   |-- models/
|   |   |-- fraud_model.h5              # Trained MLP
|   |   |-- scaler.pkl                  # Feature normalizer
|   |   |-- mlp/                        # MLP artifacts
|   |   |-- logreg/                     # Logistic Regression
|   |   `-- rf/                         # Random Forest
|   |
|   |-- training/
|   |   |-- train_model.py              # Train MLP
|   |   |-- train_logreg.py             # Train Logistic Regression
|   |   |-- train_rf.py                 # Train Random Forest
|   |   `-- setup_model_structure.py    # Organize model files
|   |
|   `-- experiments/
|       |-- evaluate_models.py          # Compare models
|       `-- robust_evaluation.py        # Validation tests
|
|-- Data and Features
|   |-- data/
|   |   `-- dataset_final.csv           # Training dataset
|   |-- data_collection.py              # Etherscan API client
|   |-- fetch_safe_addresses.py         # Fetch legitimate addresses
|   `-- utils/
|       `-- explanations.py             # Explanation logic
|
`-- Blockchain
    |-- contracts/
    |   `-- FraudGuard.sol              # Smart contract
    |-- migrations/
    |   `-- 2_deploy_contracts.js       # Truffle deployment script
    |-- truffle-config.js               # Truffle configuration
    `-- package.json                    # Node.js dependencies
```
