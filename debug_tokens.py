#!/usr/bin/env python3
"""
Script de debug pour voir tous les tokens d'un wallet
"""

import requests
import os
from dotenv import load_dotenv
from web3 import Web3

# Charger les variables d'environnement
load_dotenv()

def debug_wallet_tokens():
    """Debug des tokens d'un wallet"""
    wallet_address = "0x1c633eb00291398589718daa3938a6bd4f71949c"
    
    # Récupérer la clé Etherscan
    etherscan_key = os.getenv("ETHERSCAN_API_KEY")
    if not etherscan_key:
        print("❌ Clé Etherscan non trouvée")
        return
    
    print(f"🔑 Clé Etherscan: {etherscan_key[:10]}...")
    print(f"👛 Wallet: {wallet_address}")
    print("=" * 60)
    
    # 1. Test Etherscan API
    try:
        url = "https://api.etherscan.io/api"
        params = {
            "module": "account",
            "action": "tokentx",
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
                
                # 2. Vérifier les balances actuels via Web3
                w3 = Web3(Web3.HTTPProvider("https://eth.llamarpc.com"))
                if w3.is_connected():
                    print("🔍 Vérification des balances actuels via Web3...")
                    print()
                    
                    abi = [{"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]
                    
                    for token_addr, token_info in token_balances.items():
                        try:
                            contract = w3.eth.contract(
                                address=Web3.to_checksum_address(token_addr),
                                abi=abi
                            )
                            current_balance = contract.functions.balanceOf(Web3.to_checksum_address(wallet_address)).call()
                            
                            balance_human = token_info["net_balance"] / 10**token_info["decimals"]
                            current_balance_human = current_balance / 10**token_info["decimals"]
                            
                            print(f"  🪙 {token_info['symbol']} ({token_info['name']})")
                            print(f"     Adresse: {token_addr}")
                            print(f"     Balance calculé: {balance_human:,.6f}")
                            print(f"     Balance actuel: {current_balance_human:,.6f}")
                            print(f"     Décimales: {token_info['decimals']}")
                            print()
                            
                        except Exception as e:
                            print(f"  ❌ Erreur pour {token_info['symbol']}: {e}")
                            print()
                else:
                    print("❌ Impossible de se connecter à Web3")
            else:
                print(f"❌ Erreur Etherscan: {data.get('message')}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    debug_wallet_tokens()
