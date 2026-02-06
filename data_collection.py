import json
import pandas as pd
import requests
import time
import os

# --- CONFIGURATION ---
API_KEY = "A834WGSZC8GVJR4W5G5SFJMQESY2Q6XVTF" 
BASE_URL = "https://api.etherscan.io/v2/api"

def get_address_features(address):
    """Récupère les données réelles via Etherscan avec gestion de rate limit"""
    print(f"Analyse de l'adresse : {address}...")
    try:
        params_base = {"chainid": 1, "apikey": API_KEY}

        # 1. Récupérer le solde
        bal_params = {**params_base, "module": "account", "action": "balance", "address": address, "tag": "latest"}
        res_bal = requests.get(BASE_URL, params=bal_params).json()
        
        # Gestion du Rate Limit (Indispensable pour l'API gratuite)
        if res_bal.get('status') != '1' and "Max rate limit" in str(res_bal.get('result', '')):
            print("⏳ Rate limit atteint, pause de 6s...")
            time.sleep(6)
            res_bal = requests.get(BASE_URL, params=bal_params).json()

        balance = float(res_bal.get('result', 0)) / 10**18

        # 2. Récupérer l'historique des transactions
        tx_params = {**params_base, "module": "account", "action": "txlist", "address": address, 
                     "startblock": 0, "endblock": 99999999, "page": 1, "offset": 20, "sort": "asc"}
        res_tx = requests.get(BASE_URL, params=tx_params).json()
        
        # Deuxième vérification de Rate Limit pour le deuxième appel API
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
        print(f" Erreur sur {address}: {e}")
        return None

def get_blockchain_data(address, label):
    """Encapsule les features avec leur label (0=Sain, 1=Fraude)"""
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

# --- EXÉCUTION DU SCRIPT DE COLLECTE ---
if __name__ == "__main__":
    if not os.path.exists('data'):
        os.makedirs('data')

    # Chargement des fichiers JSON
    try:
        with open('src/addresses/addresses-darklist.json') as f:
            dark_list = json.load(f)
        with open('src/addresses/addresses-lightlist.json') as f:
            light_list = json.load(f)
    except FileNotFoundError:
        print(" Erreur critique : Fichiers JSON introuvables. Vérifiez le dossier src/addresses/")
        exit()

    dataset = []

    # 1. Collecte des Fraudes (200 adresses)
    print("\n---  Collecte Darklist (Fraudes) en cours... ---")
    for item in dark_list[:200]:
        data = get_blockchain_data(item['address'], 1)
        if data: 
            dataset.append(data)
        time.sleep(0.7) # Délai augmenté pour éviter le bannissement d'IP

    # 2. Collecte des Sains (200 adresses pour l'équilibre parfait 1:1)
    print("\n---  Collecte Lightlist (Sains) en cours... ---")
    for item in light_list[:200]:
        data = get_blockchain_data(item['address'], 0)
        if data: 
            dataset.append(data)
        time.sleep(0.7)

    # Sauvegarde dans le fichier CSV final
    if dataset:
        df = pd.DataFrame(dataset)
        # On mélange les données pour que l'IA ne lise pas toutes les fraudes d'un coup
        df = df.sample(frac=1).reset_index(drop=True) 
        df.to_csv('data/dataset_final.csv', index=False)
        
        print("\n" + "="*40)
        print(f" Dataset final généré : data/dataset_final.csv")
        print(f" Total adresses : {len(df)}")
        print(f" Fraudes : {len(df[df['is_fraud']==1])}")
        print(f" Sains : {len(df[df['is_fraud']==0])}")
        print("="*40)
    else:
        print(" Échec : Aucune donnée n'a pu être collectée.")