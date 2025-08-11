#!/usr/bin/env python3
"""
Test de l'API Etherscan pour détecter les tokens d'un wallet
"""

import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_etherscan_api():
    """Test de l'API Etherscan"""
    wallet_address = "0x1c633eb00291398589718daa3938a6bd4f71949c"
    
    # Récupérer la clé API
    etherscan_key = os.getenv("ETHERSCAN_API_KEY")
    if not etherscan_key:
        print("❌ Clé Etherscan non trouvée dans .env")
        print("💡 Obtenez une clé gratuite sur: https://etherscan.io/apis")
        print("💡 Ajoutez-la dans .env: ETHERSCAN_API_KEY=\"VotreClé\"")
        return
    
    print(f"🔑 Clé Etherscan: {etherscan_key[:10]}...")
    print(f"👛 Wallet: {wallet_address}")
    print("=" * 60)
    
    # Test de l'API Etherscan
    try:
        url = "https://api.etherscan.io/api"
        params = {
            "module": "account",
            "action": "tokentx",  # Token transactions
            "address": wallet_address,
            "startblock": 0,
            "endblock": 99999999,
            "sort": "desc",
            "apikey": etherscan_key
        }
        
        print("📡 Test API Etherscan...")
        response = requests.get(url, params=params, timeout=15)
        
        if response.ok:
            data = response.json()
            if data.get("status") == "1":
                transactions = data.get("result", [])
                print(f"✅ {len(transactions)} transactions trouvées")
                
                # Grouper par token
                token_balances = {}
                for tx in transactions:
                    token_addr = tx.get("contractAddress", "").lower()
                    if token_addr and token_addr not in token_balances:
                        token_balances[token_addr] = {
                            "symbol": tx.get("tokenSymbol", "UNKNOWN"),
                            "decimals": int(tx.get("tokenDecimal", 18)),
                            "name": tx.get("tokenName", "Unknown Token"),
                            "net_balance": 0
                        }
                    
                    if token_addr:
                        # Calculer le balance net
                        value = int(tx.get("value", "0"))
                        if tx.get("to", "").lower() == wallet_address.lower():
                            # Réception
                            token_balances[token_addr]["net_balance"] += value
                        elif tx.get("from", "").lower() == wallet_address.lower():
                            # Envoi
                            token_balances[token_addr]["net_balance"] -= value
                
                print(f"📊 {len(token_balances)} tokens uniques trouvés:")
                print()
                
                # Afficher les tokens avec balance positif
                for token_addr, token_info in token_balances.items():
                    if token_info["net_balance"] > 0:
                        balance_human = token_info["net_balance"] / 10**token_info["decimals"]
                        print(f"  ✅ {token_info['symbol']} ({token_info['name']})")
                        print(f"     Balance: {balance_human:,.6f}")
                        print(f"     Adresse: {token_addr}")
                        print()
                
            else:
                error_msg = data.get("message", "Erreur inconnue")
                print(f"❌ Erreur: {error_msg}")
                if "NOTOK" in error_msg:
                    print("💡 Vérifiez votre clé API sur https://etherscan.io/apis")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_etherscan_api()
