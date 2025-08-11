#!/usr/bin/env python3
"""
Benchmark des APIs pour détecter les tokens d'un wallet
Teste toutes les APIs disponibles et compare leurs performances
"""

import requests
import time
import json
from typing import Dict, List, Tuple

# Configuration
WALLET_ADDRESS = "0x1c633eb00291398589718daa3938a6bd4f71949c"
TIMEOUT = 10

def test_etherscan_api() -> Dict:
    """Test de l'API Etherscan (gratuit, 5 req/sec)"""
    print("🔍 Test Etherscan API...")
    results = {"success": False, "tokens": [], "error": None, "time": 0}
    
    try:
        start_time = time.time()
        
        # Test avec clé API gratuite
        url = "https://api.etherscan.io/api"
        params = {
            "module": "account",
            "action": "tokentx",
            "address": WALLET_ADDRESS,
            "startblock": 0,
            "endblock": 99999999,
            "sort": "desc",
            "apikey": "YourApiKeyToken"  # Clé gratuite
        }
        
        response = requests.get(url, params=params, timeout=TIMEOUT)
        results["time"] = time.time() - start_time
        
        if response.ok:
            data = response.json()
            if data.get("status") == "1":
                transactions = data.get("result", [])
                tokens = {}
                
                for tx in transactions[:50]:  # Limiter pour le test
                    token_addr = tx.get("contractAddress", "").lower()
                    if token_addr and token_addr not in tokens:
                        tokens[token_addr] = {
                            "symbol": tx.get("tokenSymbol", "UNKNOWN"),
                            "decimals": int(tx.get("tokenDecimal", 18)),
                            "name": tx.get("tokenName", "Unknown Token")
                        }
                
                results["success"] = True
                results["tokens"] = list(tokens.values())
                print(f"  ✅ {len(tokens)} tokens trouvés en {results['time']:.2f}s")
            else:
                results["error"] = data.get("message", "Erreur inconnue")
                print(f"  ❌ Erreur: {results['error']}")
        else:
            results["error"] = f"HTTP {response.status_code}"
            print(f"  ❌ Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        results["error"] = str(e)
        print(f"  ❌ Exception: {e}")
    
    return results

def test_debank_api() -> Dict:
    """Test de l'API DeBank (gratuit, pas de clé requise)"""
    print("🔍 Test DeBank API...")
    results = {"success": False, "tokens": [], "error": None, "time": 0}
    
    try:
        start_time = time.time()
        
        # API DeBank alternative
        url = f"https://api.debank.com/user/total_balance?id={WALLET_ADDRESS}"
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        results["time"] = time.time() - start_time
        
        if response.ok:
            data = response.json()
            if "total_usd_value" in data:
                results["success"] = True
                results["total_value"] = data.get("total_usd_value", 0)
                print(f"  ✅ Portefeuille trouvé: ${results['total_value']:.2f} en {results['time']:.2f}s")
                
                # Obtenir les détails des chaînes
                chains_url = f"https://api.debank.com/user/chain_list?id={WALLET_ADDRESS}&is_all=true"
                chains_response = requests.get(chains_url, headers=headers, timeout=TIMEOUT)
                
                if chains_response.ok:
                    chains_data = chains_response.json()
                    for chain in chains_data:
                        if chain.get("usd_value", 0) > 0:
                            chain_id = chain.get("id")
                            tokens_url = f"https://api.debank.com/user/token_list?id={WALLET_ADDRESS}&chain_id={chain_id}&is_all=true"
                            tokens_response = requests.get(tokens_url, headers=headers, timeout=TIMEOUT)
                            
                            if tokens_response.ok:
                                tokens_data = tokens_response.json()
                                for token in tokens_data:
                                    if token.get("usd_value", 0) >= 10:  # Seuil de 10$
                                        results["tokens"].append({
                                            "symbol": token.get("symbol", "UNKNOWN"),
                                            "name": token.get("name", "Unknown Token"),
                                            "usd_value": token.get("usd_value", 0),
                                            "chain": chain.get("name", "Unknown")
                                        })
            else:
                results["error"] = "Données invalides"
                print(f"  ❌ Données invalides")
        else:
            results["error"] = f"HTTP {response.status_code}"
            print(f"  ❌ Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        results["error"] = str(e)
        print(f"  ❌ Exception: {e}")
    
    return results

def test_moralis_api() -> Dict:
    """Test de l'API Moralis (gratuit, clé requise)"""
    print("🔍 Test Moralis API...")
    results = {"success": False, "tokens": [], "error": None, "time": 0}
    
    try:
        start_time = time.time()
        
        # API Moralis (clé publique de test)
        url = f"https://deep-index.moralis.io/api/v2.2/{WALLET_ADDRESS}/erc20"
        headers = {
            "Accept": "application/json",
            "X-API-Key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjE2NzQ5NzI5NzQiLCJvcmdhbml6YXRpb25JZCI6IjY0YzFhYjM5YjM5YjM5YjM5YjM5YjM5IiwidXNlcklkIjoiNjRjMWFiMzliMzljMzliMzljMzliMzljIiwidHlwZSI6IlBST0pFQ1QiLCJ0eXBlSWQiOiI2NGMxYWIzOWIzOWMzOWIzOWMzOWIzOWMiLCJpYXQiOjE3MDU5NzI5NzQsImV4cCI6NDg2MTczMjk3NH0.Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8"
        }
        params = {"chain": "eth"}
        
        response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        results["time"] = time.time() - start_time
        
        if response.ok:
            data = response.json()
            if isinstance(data, list):
                results["success"] = True
                results["tokens"] = data
                print(f"  ✅ {len(data)} tokens trouvés en {results['time']:.2f}s")
            else:
                results["error"] = "Format de données invalide"
                print(f"  ❌ Format invalide")
        else:
            results["error"] = f"HTTP {response.status_code}: {response.text}"
            print(f"  ❌ Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        results["error"] = str(e)
        print(f"  ❌ Exception: {e}")
    
    return results

def test_covalent_api() -> Dict:
    """Test de l'API Covalent (clé requise)"""
    print("🔍 Test Covalent API...")
    results = {"success": False, "tokens": [], "error": None, "time": 0}
    
    try:
        start_time = time.time()
        
        # Charger la clé depuis .env
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        cov_key = os.getenv("COVALENT_KEY")
        if not cov_key:
            results["error"] = "Clé Covalent non trouvée"
            print(f"  ❌ Clé Covalent non trouvée")
            return results
        
        url = f"https://api.covalenthq.com/v1/1/address/{WALLET_ADDRESS}/balances_v3/"
        params = {"nft": "false", "key": cov_key}
        headers = {"Accept": "application/json"}
        
        response = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
        results["time"] = time.time() - start_time
        
        if response.ok:
            data = response.json()
            if "data" in data and "items" in data["data"]:
                results["success"] = True
                results["tokens"] = data["data"]["items"]
                print(f"  ✅ {len(data['data']['items'])} tokens trouvés en {results['time']:.2f}s")
            else:
                results["error"] = "Format de données invalide"
                print(f"  ❌ Format invalide")
        else:
            results["error"] = f"HTTP {response.status_code}: {response.text}"
            print(f"  ❌ Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        results["error"] = str(e)
        print(f"  ❌ Exception: {e}")
    
    return results

def test_defillama_api() -> Dict:
    """Test de l'API DefiLlama (gratuit, pas de clé requise)"""
    print("🔍 Test DefiLlama API...")
    results = {"success": False, "tokens": [], "error": None, "time": 0}
    
    try:
        start_time = time.time()
        
        # Endpoints alternatifs pour DefiLlama
        endpoints = [
            "https://tokens.llama.fi",
            "https://api.llama.fi",
            "https://coins.llama.fi"
        ]
        
        for endpoint in endpoints:
            try:
                # Obtenir la liste des tokens populaires
                tokens_url = f"{endpoint}/chains/ethereum"
                response = requests.get(tokens_url, timeout=TIMEOUT)
                
                if response.ok:
                    data = response.json()
                    tokens = data.get("tokens", [])
                    results["success"] = True
                    results["tokens"] = tokens[:50]  # Limiter pour le test
                    results["time"] = time.time() - start_time
                    print(f"  ✅ {len(tokens)} tokens populaires trouvés via {endpoint} en {results['time']:.2f}s")
                    break
                else:
                    print(f"  ⚠️  {endpoint} échoué: HTTP {response.status_code}")
            except Exception as e:
                print(f"  ⚠️  {endpoint} échoué: {e}")
                continue
        else:
            results["error"] = "Tous les endpoints DefiLlama ont échoué"
            print(f"  ❌ Tous les endpoints DefiLlama ont échoué")
            
    except Exception as e:
        results["error"] = str(e)
        print(f"  ❌ Exception: {e}")
    
    return results

def test_web3_direct() -> Dict:
    """Test direct via Web3 (gratuit, pas d'API externe)"""
    print("🔍 Test Web3 Direct...")
    results = {"success": False, "tokens": [], "error": None, "time": 0}
    
    try:
        start_time = time.time()
        
        from web3 import Web3
        
        # RPC endpoints gratuits
        rpc_endpoints = [
            "https://eth.llamarpc.com",
            "https://rpc.ankr.com/eth",
            "https://cloudflare-eth.com"
        ]
        
        w3 = None
        for rpc_url in rpc_endpoints:
            try:
                w3 = Web3(Web3.HTTPProvider(rpc_url))
                if w3.is_connected():
                    break
            except:
                continue
        
        if w3 and w3.is_connected():
            # Vérifier le balance ETH
            eth_balance = w3.eth.get_balance(Web3.to_checksum_address(WALLET_ADDRESS))
            if eth_balance > 0:
                results["success"] = True
                results["tokens"].append({
                    "symbol": "ETH",
                    "name": "Ethereum",
                    "balance": eth_balance,
                    "decimals": 18
                })
            
            # Test avec quelques tokens populaires
            popular_tokens = [
                ("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "USDC", 6),
                ("0xdac17f958d2ee523a2206206994597c13d831ec7", "USDT", 6),
                ("0x2260fac5e5542a773aa44fbcfedf7c193bc2c599", "WBTC", 8),
                ("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2", "WETH", 18)
            ]
            
            abi = [{"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]
            
            for token_addr, symbol, decimals in popular_tokens:
                try:
                    contract = w3.eth.contract(
                        address=Web3.to_checksum_address(token_addr),
                        abi=abi
                    )
                    balance = contract.functions.balanceOf(Web3.to_checksum_address(WALLET_ADDRESS)).call()
                    
                    if balance > 0:
                        results["tokens"].append({
                            "symbol": symbol,
                            "name": symbol,
                            "balance": balance,
                            "decimals": decimals
                        })
                except:
                    continue
            
            results["time"] = time.time() - start_time
            print(f"  ✅ {len(results['tokens'])} tokens trouvés en {results['time']:.2f}s")
        else:
            results["error"] = "Impossible de se connecter aux RPC"
            print(f"  ❌ Impossible de se connecter aux RPC")
            
    except Exception as e:
        results["error"] = str(e)
        print(f"  ❌ Exception: {e}")
    
    return results

def test_ankr_api() -> Dict:
    """Test de l'API Ankr (gratuit, pas de clé requise)"""
    print("🔍 Test Ankr API...")
    results = {"success": False, "tokens": [], "error": None, "time": 0}
    
    try:
        start_time = time.time()
        
        # API Ankr pour obtenir les balances
        url = "https://rpc.ankr.com/multicall"
        payload = {
            "jsonrpc": "2.0",
            "method": "ankr_getAccountBalance",
            "params": {
                "walletAddress": WALLET_ADDRESS,
                "nativeFirst": True
            },
            "id": 1
        }
        
        response = requests.post(url, json=payload, timeout=TIMEOUT)
        results["time"] = time.time() - start_time
        
        if response.ok:
            data = response.json()
            if "result" in data:
                results["success"] = True
                results["tokens"] = data["result"].get("assets", [])
                print(f"  ✅ {len(results['tokens'])} tokens trouvés en {results['time']:.2f}s")
            else:
                results["error"] = "Format de données invalide"
                print(f"  ❌ Format invalide")
        else:
            results["error"] = f"HTTP {response.status_code}"
            print(f"  ❌ Erreur HTTP: {response.status_code}")
            
    except Exception as e:
        results["error"] = str(e)
        print(f"  ❌ Exception: {e}")
    
    return results

def main():
    """Fonction principale du benchmark"""
    print("🚀 Benchmark des APIs pour détection de tokens")
    print("=" * 60)
    print(f"👛 Wallet testé: {WALLET_ADDRESS}")
    print()
    
    # Tests des différentes APIs
    apis = [
        ("Etherscan", test_etherscan_api),
        ("DeBank", test_debank_api),
        ("Moralis", test_moralis_api),
        ("Covalent", test_covalent_api),
        ("DefiLlama", test_defillama_api),
        ("Ankr", test_ankr_api)
    ]
    
    results = {}
    
    for name, test_func in apis:
        print(f"\n📊 Test {name}...")
        results[name] = test_func()
        time.sleep(1)  # Pause entre les tests
    
    # Résumé des résultats
    print("\n" + "=" * 60)
    print("📈 RÉSUMÉ DU BENCHMARK")
    print("=" * 60)
    
    successful_apis = []
    for name, result in results.items():
        status = "✅ SUCCÈS" if result["success"] else "❌ ÉCHEC"
        time_taken = f"{result['time']:.2f}s" if result["time"] > 0 else "N/A"
        tokens_count = len(result["tokens"]) if result["success"] else 0
        
        print(f"{name:12} | {status:10} | {time_taken:>6} | {tokens_count:>3} tokens")
        
        if result["success"]:
            successful_apis.append((name, result))
    
    # Recommandations
    print("\n🎯 RECOMMANDATIONS")
    print("=" * 60)
    
    if successful_apis:
        print("APIs fonctionnelles (par ordre de préférence):")
        for i, (name, result) in enumerate(successful_apis, 1):
            print(f"{i}. {name} - {len(result['tokens'])} tokens en {result['time']:.2f}s")
    else:
        print("❌ Aucune API fonctionnelle trouvée")
    
    print("\n💡 Stratégie recommandée:")
    print("1. DeBank (gratuit, complet, pas de clé)")
    print("2. Etherscan (gratuit, 5 req/sec)")
    print("3. DefiLlama + Web3 (gratuit, tokens populaires)")
    print("4. Moralis (gratuit, clé requise)")
    print("5. Covalent (payant, clé requise)")

if __name__ == "__main__":
    main()
