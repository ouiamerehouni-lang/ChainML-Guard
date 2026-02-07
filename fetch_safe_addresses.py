import requests
import time
import json

API_KEY = "A834WGSZC8GVJR4W5G5SFJMQESY2Q6XVTF"
BASE_URL = "https://api.etherscan.io/v2/api"

def get_recent_safe_addresses(limit=160):
    safe_addresses = []
    
    params_block = {
        "chainid": 1,
        "module": "proxy",
        "action": "eth_blockNumber",
        "apikey": API_KEY
    }
    res = requests.get(BASE_URL, params=params_block).json()
    last_block = int(res['result'], 16)
    
    print(f" Analysis starting from block: {last_block}")

    current_block = last_block
    while len(safe_addresses) < limit:
        params_tx = {
            "chainid": 1,
            "module": "proxy",
            "action": "eth_getBlockByNumber",
            "tag": hex(current_block),
            "boolean": "true",
            "apikey": API_KEY
        }
        
        block_data = requests.get(BASE_URL, params=params_tx).json()
        transactions = block_data.get('result', {}).get('transactions', [])
        
        for tx in transactions:
            addr = tx.get('from')
            if addr and addr not in safe_addresses:
                safe_addresses.append(addr)
            
            if len(safe_addresses) >= limit:
                break
            
        print(f" {len(safe_addresses)} addresses collected...")
        current_block -= 1
        time.sleep(0.2)

    formatted_list = [
        {"address": a, "comment": "Auto-collected Safe Address"}
        for a in safe_addresses
    ]
    
    with open('src/addresses/addresses-lightlist.json', 'w') as f:
        json.dump(formatted_list, f, indent=4)
    
    print("\n Done! 160 safe addresses saved in 'src/addresses/addresses-lightlist.json'")

if __name__ == "__main__":
    get_recent_safe_addresses(160)
