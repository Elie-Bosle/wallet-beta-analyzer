#!/usr/bin/env python3
"""
Test de l'API v2 Etherscan pour voir les tokens retournés
"""

import requests
import json

def test_api_v2():
    wallet = "0x1c633eb00291398589718daa3938a6bd4f71949c"
    api_key = "MBN5B4IPQP3JNTRPS97Z7XCZNVNTNWA655"
    
    chains = {
        "Ethereum": 1,
        "Arbitrum": 42161,
        "Base": 8453,
        "Optimism": 10
    }
    
    for chain_name, chain_id in chains.items():
        print(f"\n🔍 Test {chain_name} (Chain ID: {chain_id})")
        print("=" * 50)
        
        params = {
            "chainid": chain_id,
            "module": "account",
            "action": "addresstokenbalance",
            "address": wallet,
            "page": 1,
            "offset": 100,
            "apikey": api_key
        }
        
        try:
            response = requests.get("https://api.etherscan.io/v2/api", params=params, timeout=15)
            
            if response.ok:
                data = response.json()
                print(f"Status: {data.get('status')}")
                print(f"Message: {data.get('message', 'N/A')}")
                
                if data.get("status") == "1":
                    tokens = data.get("result", [])
                    print(f"Nombre de tokens: {len(tokens)}")
                    
                    if tokens:
                        print("\nPremiers tokens:")
                        for i, token in enumerate(tokens[:5]):  # Afficher les 5 premiers
                            print(f"  {i+1}. {token.get('symbol', 'UNKNOWN')} ({token.get('contractAddress', 'N/A')})")
                            print(f"     Balance: {token.get('balance', '0')}")
                            print(f"     Decimals: {token.get('decimals', '18')}")
                            print()
                    else:
                        print("Aucun token trouvé")
                else:
                    print(f"Erreur: {data}")
            else:
                print(f"Erreur HTTP: {response.status_code}")
                print(f"Réponse: {response.text}")
                
        except Exception as e:
            print(f"Erreur: {e}")

if __name__ == "__main__":
    test_api_v2()
