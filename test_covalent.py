#!/usr/bin/env python3
"""
Script pour tester l'API Covalent directement
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

COV_KEY = os.getenv("COVALENT_KEY")
WALLET = "0x1c633eb00291398589718daa3938a6bd4f71949c"

def test_covalent_api():
    """Teste l'API Covalent directement"""
    if not COV_KEY:
        print("❌ Clé Covalent non trouvée")
        return
    
    print(f"🔑 Clé Covalent: {COV_KEY[:10]}...")
    print(f"👛 Wallet: {WALLET}")
    print("=" * 50)
    
    # Test sur Ethereum
    url = f"https://api.covalenthq.com/v1/1/address/{WALLET}/balances_v2/"
    params = {"nft": "false", "key": COV_KEY}
    headers = {"User-Agent": "beta-portfolio/1.0"}
    
    try:
        print("📡 Test API Covalent (Ethereum)...")
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.ok:
            data = response.json()
            print(f"✅ Réponse reçue")
            
            if "data" in data and "items" in data["data"]:
                items = data["data"]["items"]
                print(f"📊 {len(items)} tokens trouvés")
                
                for i, item in enumerate(items[:10]):  # Afficher les 10 premiers
                    symbol = item.get("contract_ticker_symbol", "UNKNOWN")
                    balance = item.get("balance", 0)
                    quote = item.get("quote", 0)
                    decimals = item.get("contract_decimals", 18)
                    
                    print(f"  {i+1}. {symbol}:")
                    print(f"     Balance: {balance}")
                    print(f"     Quote: ${quote}")
                    print(f"     Decimals: {decimals}")
                    
                    if quote and quote >= 10:
                        print(f"     ✅ ≥ $10")
                    else:
                        print(f"     ❌ < $10")
            else:
                print("❌ Pas de données dans la réponse")
                print(f"Réponse: {data}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_covalent_api()
