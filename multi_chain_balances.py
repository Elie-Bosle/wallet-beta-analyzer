#!/usr/bin/env python3
"""
Détection automatique des tokens sur toutes les chaînes EVM via APIs Etherscan
"""

import requests
import os
from dotenv import load_dotenv
from web3 import Web3
import time

# Charger les variables d'environnement
load_dotenv()

# Configuration des APIs Etherscan
ETHERSCAN_APIS = {
    "Ethereum": {
        "url": "https://api.etherscan.io/api",
        "key": os.getenv("ETHERSCAN_API_KEY"),
        "chain_id": 1
    },
    "BSC": {
        "url": "https://api.bscscan.com/api",
        "key": os.getenv("BSCSCAN_API_KEY"),
        "chain_id": 56
    },
    "Arbitrum": {
        "url": "https://api.arbiscan.io/api",
        "key": os.getenv("ARBISCAN_API_KEY"),
        "chain_id": 42161
    },
    "Optimism": {
        "url": "https://api-optimistic.etherscan.io/api",
        "key": os.getenv("OPTIMISM_API_KEY"),
        "chain_id": 10
    },
    "Avalanche": {
        "url": "https://api.snowscan.xyz/api",
        "key": os.getenv("SNOWSCAN_API_KEY"),
        "chain_id": 43114
    }
}

# RPC endpoints pour vérification des balances
RPC_ENDPOINTS = {
    1: "https://eth.llamarpc.com",
    56: "https://bsc.llamarpc.com",
    42161: "https://arbitrum.llamarpc.com",
    10: "https://optimism.llamarpc.com",
    43114: "https://avalanche.llamarpc.com"
}

def get_token_price(chain_id, token_addr):
    """Obtenir le prix d'un token via DefiLlama"""
    try:
        chain_slugs = {
            1: "ethereum",
            56: "bsc",
            42161: "arbitrum",
            10: "optimism",
            43114: "avalanche"
        }
        
        chain_slug = chain_slugs.get(chain_id)
        if not chain_slug:
            return 0
            
        url = f"https://coins.llama.fi/prices/current/{chain_slug}:{token_addr}"
        response = requests.get(url, timeout=10)
        
        if response.ok:
            data = response.json()
            return data.get("coins", {}).get(f"{chain_slug}:{token_addr}", {}).get("price", 0)
    except:
        pass
    return 0

def get_balance_via_web3(chain_id, wallet_addr, token_addr, decimals):
    """Obtenir le balance actuel via Web3"""
    try:
        rpc_url = RPC_ENDPOINTS.get(chain_id)
        if not rpc_url:
            return 0
            
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            return 0
            
        abi = [{"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]
        
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(token_addr),
            abi=abi
        )
        balance = contract.functions.balanceOf(Web3.to_checksum_address(wallet_addr)).call()
        return balance
    except:
        return 0

def get_native_balance(chain_id, wallet_addr):
    """Obtenir le balance natif (ETH, BNB, etc.)"""
    try:
        rpc_url = RPC_ENDPOINTS.get(chain_id)
        if not rpc_url:
            return 0
            
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            return 0
            
        balance = w3.eth.get_balance(Web3.to_checksum_address(wallet_addr))
        return balance
    except:
        return 0

def scan_chain_tokens(chain_name, api_config, wallet_addr):
    """Scanner les tokens d'une chaîne via son API Etherscan"""
    print(f"🔍 Analyse de {chain_name}...")
    
    results = []
    
    # 1. Vérifier le balance natif
    try:
        native_balance = get_native_balance(api_config["chain_id"], wallet_addr)
        if native_balance > 0:
            # Obtenir le prix du token natif
            native_price = get_token_price(api_config["chain_id"], "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
            if native_price > 0:
                native_value = native_balance / 10**18 * native_price
                if native_value >= 10:  # Seuil de 10$
                    results.append({
                        "chain": chain_name,
                        "symbol": "ETH" if chain_name == "Ethereum" else f"Native-{chain_name}",
                        "address": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
                        "balance": native_balance,
                        "decimals": 18,
                        "price": native_price,
                        "usd_value": native_value
                    })
                    print(f"  ✅ Native: ${native_value:.2f}")
    except Exception as e:
        print(f"  ❌ Erreur balance natif: {e}")
    
    # 2. Scanner les tokens ERC20 via l'API
    if api_config["key"]:
        try:
            params = {
                "module": "account",
                "action": "tokentx",
                "address": wallet_addr,
                "startblock": 0,
                "endblock": 99999999,
                "sort": "desc",
                "apikey": api_config["key"]
            }
            
            response = requests.get(api_config["url"], params=params, timeout=15)
            
            if response.ok:
                data = response.json()
                if data.get("status") == "1":
                    transactions = data.get("result", [])
                    
                    # Grouper par token et calculer le balance net
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
                            # Calculer le balance net (entrées - sorties)
                            value = int(tx.get("value", "0"))
                            if tx.get("to", "").lower() == wallet_addr.lower():
                                # Réception
                                token_balances[token_addr]["net_balance"] += value
                            elif tx.get("from", "").lower() == wallet_addr.lower():
                                # Envoi
                                token_balances[token_addr]["net_balance"] -= value
                    
                    print(f"  📊 {len(token_balances)} tokens uniques trouvés")
                    
                    # Vérifier chaque token avec balance positif
                    for token_addr, token_info in token_balances.items():
                        if token_info["net_balance"] > 0:
                            try:
                                # Vérifier le balance actuel via Web3
                                current_balance = get_balance_via_web3(
                                    api_config["chain_id"], 
                                    wallet_addr, 
                                    token_addr, 
                                    token_info["decimals"]
                                )
                                
                                if current_balance > 0:
                                    # Obtenir le prix
                                    price = get_token_price(api_config["chain_id"], token_addr)
                                    if price > 0:
                                        usd_value = current_balance / 10**token_info["decimals"] * price
                                        if usd_value >= 10:  # Seuil de 10$
                                            results.append({
                                                "chain": chain_name,
                                                "symbol": token_info["symbol"],
                                                "address": token_addr,
                                                "balance": current_balance,
                                                "decimals": token_info["decimals"],
                                                "price": price,
                                                "usd_value": usd_value
                                            })
                                            print(f"  ✅ {token_info['symbol']}: ${usd_value:.2f}")
                                            
                            except Exception as e:
                                continue
                else:
                    print(f"  ⚠️  Erreur API: {data.get('message', 'Erreur inconnue')}")
            else:
                print(f"  ❌ Erreur HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Erreur API: {e}")
    else:
        print(f"  ⚠️  Pas de clé API pour {chain_name}")
    
    return results

def main():
    """Fonction principale"""
    wallet_address = "0x1c633eb00291398589718daa3938a6bd4f71949c"
    
    print("🚀 Détection Multi-Chaînes via APIs Etherscan")
    print("=" * 60)
    print(f"👛 Wallet: {wallet_address}")
    print()
    
    all_results = []
    total_value = 0
    
    # Scanner chaque chaîne
    for chain_name, api_config in ETHERSCAN_APIS.items():
        try:
            results = scan_chain_tokens(chain_name, api_config, wallet_address)
            all_results.extend(results)
            
            # Calculer la valeur totale pour cette chaîne
            chain_value = sum(r["usd_value"] for r in results)
            if chain_value > 0:
                print(f"  💰 Valeur totale {chain_name}: ${chain_value:.2f}")
            print()
            
            total_value += chain_value
            
            # Pause entre les requêtes pour éviter le rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Erreur pour {chain_name}: {e}")
            print()
    
    # Résumé final
    print("=" * 60)
    print("📈 RÉSUMÉ FINAL")
    print("=" * 60)
    
    if all_results:
        print(f"🎯 {len(all_results)} positions trouvées")
        print(f"💰 Valeur totale: ${total_value:.2f}")
        print()
        
        # Grouper par chaîne
        by_chain = {}
        for result in all_results:
            chain = result["chain"]
            if chain not in by_chain:
                by_chain[chain] = []
            by_chain[chain].append(result)
        
        for chain, tokens in by_chain.items():
            chain_value = sum(t["usd_value"] for t in tokens)
            print(f"📊 {chain}: {len(tokens)} tokens (${chain_value:.2f})")
            for token in tokens:
                print(f"  - {token['symbol']}: ${token['usd_value']:.2f}")
            print()
    else:
        print("❌ Aucune position trouvée")

if __name__ == "__main__":
    main()
