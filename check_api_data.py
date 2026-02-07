import requests
import json

API_KEY = "A834WGSZC8GVJR4W5G5SFJMQESY2Q6XVTF"
BASE_URL = "https://api.etherscan.io/v2/api"

def check_address(address):
    print(f"\n--- Checking address: {address} ---")
    params = {"chainid": 1, "module": "account", "apikey": API_KEY, "address": address}
    
    # Balance test
    bal_res = requests.get(BASE_URL, params={**params, "action": "balance"}).json()
    balance = bal_res.get('result')
    
    # Transaction test (requesting 5 transactions for inspection)
    tx_res = requests.get(
        BASE_URL,
        params={**params, "action": "txlist", "offset": 5}
    ).json()
    txs = tx_res.get('result')

    if bal_res['status'] == '1' and tx_res['status'] == '1':
        print(f"Raw balance (Wei): {balance}")
        print(f"Number of transactions found: {len(txs)}")
        if len(txs) > 0:
            print(f"Date of first transaction: {txs[0]['timeStamp']}")
    else:
        print(
            f"API error: {bal_res.get('result') if bal_res['status'] != '1' else tx_res.get('result')}"
        )

# Test on a known address from your list
check_address("0x28C6c06298d514Db089934071355E5743bf21d60")  # Darklist
