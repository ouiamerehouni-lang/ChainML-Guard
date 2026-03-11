import json
import pandas as pd
import requests
import time
import os

# CONFIGURATION
API_KEY = os.getenv('ETHERSCAN_API_KEY')
if not API_KEY:
    raise ValueError("ETHERSCAN_API_KEY environment variable not set. Please create a .env file or set the variable.")
BASE_URL = "https://api.etherscan.io/v2/api"

def get_address_features(address):
    """Fetches real blockchain data from Etherscan with rate limit handling"""
    print(f"Analyzing address: {address}...")
    try:
        params_base = {"chainid": 1, "apikey": API_KEY}

        # 1. Fetch balance
        bal_params = {
            **params_base,
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest"
        }
        res_bal = requests.get(BASE_URL, params=bal_params).json()
        
        # Rate limit handling (Required for the free API)
        if res_bal.get('status') != '1' and "Max rate limit" in str(res_bal.get('result', '')):
            print("⏳ Rate limit reached, pausing for 6s...")
            time.sleep(6)
            res_bal = requests.get(BASE_URL, params=bal_params).json()

        balance = float(res_bal.get('result', 0)) / 10**18

        # 2. Fetch transaction history
        tx_params = {
            **params_base,
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": 0,
            "endblock": 99999999,
            "page": 1,
            "offset": 20,
            "sort": "asc"
        }
        res_tx = requests.get(BASE_URL, params=tx_params).json()
        
        # Second rate limit check for the second API call
        if res_tx.get('status') != '1' and "Max rate limit" in str(res_tx.get('result', '')):
            time.sleep(6)
            res_tx = requests.get(BASE_URL, params=tx_params).json()

        txs = res_tx.get('result', [])
        tx_count = len(txs) if isinstance(txs, list) else 0
        
        if tx_count > 0:
            first_tx = int(txs[0]['timeStamp'])
            age_days = (time.time() - first_tx) / 86400
        else:
            age_days = 0

        return [balance, tx_count, age_days]

    except Exception as e:
        print(f" Error on {address}: {e}")
        return None

def get_blockchain_data(address, label):
    """Wraps features with their label (0=Legitimate, 1=Fraud)"""
    features = get_address_features(address)
    if features:
        return {
            "address": address,
            "balance": features[0],
            "tx_count": features[1],
            "age_days": features[2],
            "is_fraud": label
        }
    return None

# SCRIPT EXECUTION FOR DATA COLLECTION
if __name__ == "__main__":
    if not os.path.exists('data'):
        os.makedirs('data')

    # Load JSON files
    try:
        with open('src/addresses/addresses-darklist.json') as f:
            dark_list = json.load(f)
        with open('src/addresses/addresses-lightlist.json') as f:
            light_list = json.load(f)
    except FileNotFoundError:
        print(" Critical error: JSON files not found. Check the src/addresses/ directory.")
        exit()

    dataset = []

    # 1. Fraud collection (200 addresses)
    print("\n---  Collecting Darklist (Fraud) data... ---")
    for item in dark_list[:200]:
        data = get_blockchain_data(item['address'], 1)
        if data:
            dataset.append(data)
        time.sleep(0.7)  # Increased delay to avoid IP banning

    # 2. Legitimate collection (200 addresses for perfect 1:1 balance)
    print("\n---  Collecting Lightlist (Legitimate) data... ---")
    for item in light_list[:200]:
        data = get_blockchain_data(item['address'], 0)
        if data:
            dataset.append(data)
        time.sleep(0.7)

    # Save to final CSV file
    if dataset:
        df = pd.DataFrame(dataset)
        # Shuffle data so the AI does not read all frauds sequentially
        df = df.sample(frac=1).reset_index(drop=True)
        df.to_csv('data/dataset_final.csv', index=False)
        
        print("\n" + "="*40)
        print(f" Final dataset generated: data/dataset_final.csv")
        print(f" Total addresses: {len(df)}")
        print(f" Frauds: {len(df[df['is_fraud'] == 1])}")
        print(f" Legitimate: {len(df[df['is_fraud'] == 0])}")
        print("="*40)
    else:
        print(" Failure: No data could be collected.")
