from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sys
import time
import datetime as dt
import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from tqdm import tqdm
import json
from web3 import Web3
from eth_account import Account
import threading
import queue
import uuid

app = Flask(__name__)
CORS(app)

# Configuration
load_dotenv()
COV_KEY = os.getenv("COVALENT_KEY")

# Paramètres
DAYS = 30
MIN_USD = 10
MAX_TOKENS = 5
BENCHMARKS = {"BTC": "bitcoin", "ETH": "ethereum"}

CHAIN_MAP = {
    1: "Ethereum",
    42161: "Arbitrum", 
    8453: "Base",
    10: "Optimism",
}

CHAIN_TO_LLAMA = {
    1: "ethereum", 42161: "arbitrum", 8453: "base", 10: "optimism"
}

COV_BAL = "https://api.covalenthq.com/v1/{chain}/address/{addr}/balances_v2/"
COV_HIST = ("https://api.covalenthq.com/v1/{chain}/pricing/"
            "historical_by_addresses_v2/USD/{addr_csv}/")
CGK_SIMPLE = "https://api.coingecko.com/api/v3/simple/price"
CGK_HIST = "https://api.coingecko.com/api/v3/coins/{id}/market_chart"

HEAD = {"User-Agent": "beta-portfolio/1.0"}

# Stockage des résultats en cours
active_analyses = {}

import os
from dotenv import load_dotenv
load_dotenv()

# Configuration des APIs Etherscan multi-chaînes avec la nouvelle API v2
ETHERSCAN_APIS = {
    "Ethereum": {
        "url": "https://api.etherscan.io/v2/api",
        "key": "MBN5B4IPQP3JNTRPS97Z7XCZNVNTNWA655",
        "chain_id": 1
    },
    "BSC": {
        "url": "https://api.etherscan.io/v2/api",
        "key": "MBN5B4IPQP3JNTRPS97Z7XCZNVNTNWA655",
        "chain_id": 56
    },
    "Arbitrum": {
        "url": "https://api.etherscan.io/v2/api",
        "key": "MBN5B4IPQP3JNTRPS97Z7XCZNVNTNWA655",
        "chain_id": 42161
    },
    "Optimism": {
        "url": "https://api.etherscan.io/v2/api",
        "key": "MBN5B4IPQP3JNTRPS97Z7XCZNVNTNWA655",
        "chain_id": 10
    },
    "Avalanche": {
        "url": "https://api.etherscan.io/v2/api",
        "key": "MBN5B4IPQP3JNTRPS97Z7XCZNVNTNWA655",
        "chain_id": 43114
    },
    "Base": {
        "url": "https://api.etherscan.io/v2/api",
        "key": "MBN5B4IPQP3JNTRPS97Z7XCZNVNTNWA655",
        "chain_id": 8453
    }
}

# RPC endpoints pour vérification des balances
RPC_ENDPOINTS = {
    1: "https://eth.llamarpc.com",
    56: "https://bsc.llamarpc.com",
    42161: "https://arbitrum.llamarpc.com",
    10: "https://optimism.llamarpc.com",
    43114: "https://avalanche.llamarpc.com",
    8453: "https://base.llamarpc.com"
}

def price_llama(chain_id: int, addr: str) -> float:
    """Récupère le prix via DefiLlama"""
    plat = CHAIN_TO_LLAMA.get(chain_id)
    if not plat: 
        return 0
    url = f"https://coins.llama.fi/prices/current/{plat}:{addr}"
    try:
        r = requests.get(url, timeout=10)
        return r.json()["coins"].get(f"{plat}:{addr}", {}).get("price", 0) if r.ok else 0
    except:
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

def scan_chain_via_etherscan(chain_name, api_config, wallet_addr):
    """Scanner une chaîne via l'API addresstokenbalance"""
    results = []
    
    # 1. Vérifier le balance natif
    try:
        native_balance = get_native_balance(api_config["chain_id"], wallet_addr)
        if native_balance > 0:
            # Obtenir le prix du token natif
            native_price = price_llama(api_config["chain_id"], "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
            if native_price > 0:
                native_value = native_balance / 10**18 * native_price
                # Prendre tous les montants en compte
                results.append({
                    "addr": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
                    "sym": "ETH" if chain_name == "Ethereum" else f"Native-{chain_name}",
                    "usd": native_value,
                    "cid": api_config["chain_id"],
                    "chain": chain_name
                })
                print(f"  ✅ Native: ${native_value:.2f}")
    except Exception as e:
        print(f"  ❌ Erreur balance natif: {e}")
    
    # 2. Obtenir les tokens ERC20 via addresstokenbalance
    try:
        params = {
            "chainid": api_config["chain_id"],
            "module": "account",
            "action": "addresstokenbalance",
            "address": wallet_addr,
            "page": 1,
            "offset": 100,
            "apikey": api_config["key"]
        }
        
        response = requests.get(api_config["url"], params=params, timeout=15)
        
        if response.ok:
            data = response.json()
            if data.get("status") == "1":
                tokens = data.get("result", [])
                print(f"  📊 {len(tokens)} tokens trouvés via {chain_name}")
                
                for token in tokens:
                    try:
                        token_addr = token.get("TokenAddress", "").lower()
                        symbol = token.get("TokenSymbol", "UNKNOWN")
                        quantity = int(token.get("TokenQuantity", "0"))
                        divisor = int(token.get("TokenDivisor", "18"))
                        
                        if quantity > 0:
                            # Obtenir le prix
                            price = price_llama(api_config["chain_id"], token_addr)
                            if price > 0:
                                usd_value = quantity / 10**divisor * price
                                # Prendre tous les montants en compte
                                results.append({
                                    "addr": token_addr,
                                    "sym": symbol,
                                    "usd": usd_value,
                                    "cid": api_config["chain_id"],
                                    "chain": chain_name
                                })
                                print(f"  ✅ {symbol}: ${usd_value:.2f}")
                            else:
                                print(f"  ❌ {symbol}: Prix non trouvé")
                                
                    except Exception as e:
                        print(f"  ❌ Erreur token: {e}")
                        continue
            else:
                print(f"  ⚠️  Erreur {chain_name}: {data.get('message', 'Erreur inconnue')}")
        else:
            print(f"  ❌ Erreur {chain_name}: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Erreur {chain_name}: {e}")
    
    return results

def balances(addr: str, cid: int) -> pd.DataFrame:
    """Récupère les balances d'un wallet sur une chaîne - Solution Multi-Chaînes"""
    rows = []
    
    # Mapper les chain IDs vers les noms
    chain_id_to_name = {
        1: "Ethereum",
        56: "BSC", 
        42161: "Arbitrum",
        10: "Optimism",
        43114: "Avalanche",
        8453: "Base"
    }
    
    chain_name = chain_id_to_name.get(cid)
    
    if chain_name and chain_name in ETHERSCAN_APIS:
        # Utiliser l'API Etherscan pour cette chaîne
        api_config = ETHERSCAN_APIS[chain_name]
        print(f"🔍 Analyse de {chain_name} via API Etherscan...")
        results = scan_chain_via_etherscan(chain_name, api_config, addr)
        rows.extend(results)
    else:
        # Fallback vers la méthode originale pour les autres chaînes
        print(f"🔍 Analyse de {CHAIN_MAP.get(cid, f'Chain {cid}')} via Web3...")
        
        # RPC endpoints avec fallbacks
        rpc_endpoints = {
            1: ["https://eth.llamarpc.com", "https://rpc.ankr.com/eth", "https://cloudflare-eth.com"],
            42161: ["https://arbitrum.llamarpc.com", "https://rpc.ankr.com/arbitrum"], 
            8453: ["https://base.llamarpc.com", "https://rpc.ankr.com/base"],
            10: ["https://optimism.llamarpc.com", "https://rpc.ankr.com/optimism"]
        }
        
        rpc_urls = rpc_endpoints.get(cid, [])
        if rpc_urls:
            w3 = None
            for rpc_url in rpc_urls:
                try:
                    from web3 import Web3
                    w3 = Web3(Web3.HTTPProvider(rpc_url))
                    if w3.is_connected():
                        break
                except:
                    continue
            
            if w3 and w3.is_connected():
                # Balance ETH natif
                try:
                    eth_balance = w3.eth.get_balance(Web3.to_checksum_address(addr))
                    if eth_balance > 0:
                        eth_price = price_llama(cid, "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
                        if eth_price > 0:
                            eth_value = eth_balance / 10**18 * eth_price
                            # Prendre tous les montants en compte
                            rows.append({
                                "addr": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
                                "sym": "ETH" if cid == 1 else f"ETH-{CHAIN_MAP[cid]}",
                                "usd": eth_value,
                                "cid": cid,
                                "chain": CHAIN_MAP.get(cid, f"Chain {cid}")
                            })
                            print(f"  ✅ ETH: ${eth_value:.2f}")
                except Exception as e:
                    print(f"  ❌ Erreur ETH: {e}")
    
    return pd.DataFrame(rows)

def cgk_hist(id_, days):
    """Récupère l'historique des prix via CoinGecko"""
    try:
        r = requests.get(CGK_HIST.format(id=id_),
                        params={"vs_currency":"usd","days":days}, timeout=30)
        r.raise_for_status()
        d = pd.DataFrame(r.json()["prices"], columns=["ts","p"])
        d["date"] = pd.to_datetime(d.ts, unit="ms").dt.date
        return d.groupby("date").p.first().pct_change().dropna()
    except:
        return pd.Series()

def hist_prices(cid: int, addrs: list[str], start: dt.date, end: dt.date) -> pd.DataFrame:
    """Récupère l'historique des prix"""
    if not COV_KEY:
        return pd.DataFrame()
        
    url = COV_HIST.format(chain=cid, addr_csv=",".join(addrs))
    try:
        r = requests.get(url, params={"from": start, "to": end, "key": COV_KEY},
                        headers=HEAD, timeout=60)
        if r.status_code == 404:
            frames = []
            for a in addrs:
                try:
                    g = requests.get(
                        f"https://api.coingecko.com/api/v3/coins/ethereum/contract/{a}/market_chart",
                        params={"vs_currency":"usd","days":DAYS}, timeout=30)
                    if g.ok:
                        df = pd.DataFrame(g.json()["prices"], columns=["ts","price"])
                        df["date"] = pd.to_datetime(df.ts, unit="ms").dt.date
                        df["addr"] = a
                        frames.append(df)
                except:
                    continue
            return pd.concat(frames) if frames else pd.DataFrame()
        r.raise_for_status()
        frames = []
        for p in r.json()["data"]["prices"]:
            df = pd.DataFrame(p["prices"], columns=["date","price"])
            df["date"] = pd.to_datetime(df.date).dt.date
            df["addr"] = p["contract_address"].lower()
            frames.append(df)
        return pd.concat(frames)
    except:
        return pd.DataFrame()

def beta(x, y): 
    """Calcule le beta entre deux séries"""
    return np.cov(x, y)[0,1]/np.var(y) if np.var(y) else 0

def calculate_beta_score(wallet_address: str, analysis_id: str):
    """Calcule le beta score pour un wallet"""
    try:
        active_analyses[analysis_id] = {"status": "processing", "progress": 0}
        
        # 1) Récupération des balances multichain
        active_analyses[analysis_id]["progress"] = 10
        frames = [balances(wallet_address, cid) for cid in CHAIN_MAP]
        df = pd.concat(frames, ignore_index=True)
        
        if df.empty:
            # Essayer de diagnostiquer le problème
            debug_info = []
            for cid in CHAIN_MAP:
                try:
                    test_df = balances(wallet_address, cid)
                    debug_info.append(f"{CHAIN_MAP[cid]}: {len(test_df)} positions trouvées")
                except Exception as e:
                    debug_info.append(f"{CHAIN_MAP[cid]}: Erreur - {str(e)}")
            
            active_analyses[analysis_id] = {
                "status": "error", 
                "message": f"Aucune position ≥ 10 USD trouvée. Debug: {'; '.join(debug_info)}"
            }
            return
            
        active_analyses[analysis_id]["progress"] = 30
        
        # Top positions
        top = (df.sort_values("usd", ascending=False)
               .head(MAX_TOKENS).reset_index(drop=True))
        
        # 2) Historiques des prix
        active_analyses[analysis_id]["progress"] = 50
        end, start = dt.date.today(), dt.date.today() - dt.timedelta(days=DAYS)
        hist = pd.concat([hist_prices(cid,
                                    top.query("cid==@cid").addr.tolist(),
                                    start, end)
                         for cid in top.cid.unique()],
                        ignore_index=True)
        
        # 3) Benchmarks
        active_analyses[analysis_id]["progress"] = 70
        bench = {k: cgk_hist(v, DAYS) for k, v in BENCHMARKS.items()}
        
        # 4) Beta individuels
        active_analyses[analysis_id]["progress"] = 85
        for k in BENCHMARKS: 
            top[f"β_{k}"] = np.nan
            
        for idx, row in top.iterrows():
            s = (hist.query("addr == @row.addr")
                    .sort_values("date").price.pct_change().dropna())
            for k in BENCHMARKS:
                a = s.align(bench[k], join="inner")
                top.loc[idx, f"β_{k}"] = beta(a[0], a[1])
        
        # 5) Beta portefeuille
        active_analyses[analysis_id]["progress"] = 95
        weights = top.usd / top.usd.sum()
        beta_port = {k: (weights * top[f"β_{k}"]).sum() for k in BENCHMARKS}
        
        # 6) Calcul du score final
        beta_eth = beta_port.get("ETH", 0)
        beta_btc = beta_port.get("BTC", 0)
        
        # Score basé sur la volatilité relative (beta plus proche de 1 = plus stable)
        score_eth = max(0, 100 - abs(beta_eth - 1) * 50)
        score_btc = max(0, 100 - abs(beta_btc - 1) * 50)
        final_score = (score_eth + score_btc) / 2
        
        # Préparation des résultats
        results = {
            "status": "completed",
            "wallet": wallet_address,
            "total_value": float(top.usd.sum()),
            "positions": top.to_dict('records'),
            "portfolio_betas": beta_port,
            "score": round(final_score, 2),
            "score_breakdown": {
                "eth_score": round(score_eth, 2),
                "btc_score": round(score_btc, 2)
            }
        }
        
        active_analyses[analysis_id] = results
        
    except Exception as e:
        active_analyses[analysis_id] = {
            "status": "error",
            "message": str(e)
        }

def calculate_beta(token_returns, benchmark_returns):
    """Calcule le beta d'un token par rapport à un benchmark"""
    if len(token_returns) < 30 or len(benchmark_returns) < 30:
        return 1.0  # Beta par défaut si pas assez de données
    
    try:
        # Calculer la covariance et la variance
        covariance = np.cov(token_returns, benchmark_returns)[0, 1]
        variance = np.var(benchmark_returns)
        
        if variance == 0:
            return 1.0
        
        beta = covariance / variance
        return beta
    except:
        return 1.0

def calculate_wallet_score(tokens_df):
    """Calcule le score du wallet basé sur la volatilité des tokens"""
    if tokens_df.empty:
        return {"score": 0, "details": "Aucun token trouvé"}
    
    total_value = tokens_df['usd'].sum()
    scores = []
    
    # Définir les tokens stables (stablecoins et tokens majeurs)
    stable_tokens = {
        'USDC', 'USDT', 'DAI', 'BUSD', 'FRAX', 'TUSD', 'USDP', 'GUSD', 'LUSD', 'sUSD',
        'ETH', 'WETH', 'ezETH', 'rWETH', 'aBasWETH', 'sezETH', 'sWETH-wstETH'
    }
    
    # Définir les tokens volatils (meme, degen, etc.)
    volatile_tokens = {
        'PEPE', 'DOGE', 'SHIB', 'FLOKI', 'BONK', 'WIF', 'BOME', 'DEGEN', 'MOON', 'SAFE',
        'APE', 'GALA', 'CHZ', 'HOT', 'BTT', 'WIN', 'TRX', 'ADA', 'DOT', 'LINK'
    }
    
    for _, token in tokens_df.iterrows():
        symbol = token['sym'].upper()
        value = token['usd']
        weight = value / total_value if total_value > 0 else 0
        
        # Calculer le score basé sur le type de token
        if symbol in stable_tokens:
            # Tokens stables : score élevé (80-100)
            score = 90 + (value / 1000) * 10  # Bonus pour les gros montants
            score = min(100, score)
        elif symbol in volatile_tokens:
            # Tokens volatils : score faible (20-50)
            score = 30 + (value / 1000) * 20  # Légère amélioration pour les gros montants
            score = min(50, score)
        else:
            # Tokens normaux : score moyen (40-80)
            # Basé sur la valeur relative dans le portfolio
            if value > 1000:
                score = 70  # Gros montant = plus stable
            elif value > 100:
                score = 60  # Montant moyen
            elif value > 10:
                score = 50  # Petit montant
            else:
                score = 40  # Très petit montant
        
        weighted_score = score * weight
        
        scores.append({
            'token': token['sym'],
            'value': value,
            'score': score,
            'weight': weight,
            'weighted_score': weighted_score,
            'type': 'stable' if symbol in stable_tokens else 'volatile' if symbol in volatile_tokens else 'normal'
        })
        
        print(f"  📊 {token['sym']}: ${value:.2f} | Score = {score:.1f} | Type = {scores[-1]['type']}")
    
    if scores:
        total_score = sum(s['weighted_score'] for s in scores)
        
        # Ajuster le score final basé sur la diversification
        unique_tokens = len(scores)
        if unique_tokens > 10:
            total_score += 5  # Bonus pour la diversification
        elif unique_tokens < 3:
            total_score -= 10  # Pénalité pour la concentration
        
        # Limiter le score entre 0 et 100
        total_score = max(0, min(100, total_score))
        
        return {
            "score": total_score,
            "total_value": total_value,
            "details": scores,
            "token_count": unique_tokens
        }
    else:
        return {"score": 50, "details": "Calcul impossible, score par défaut"}

def analyze_wallet(wallet_address):
    """Analyse complète d'un wallet : tokens + beta + score"""
    print(f"🔍 Analyse complète du wallet: {wallet_address}")
    print("=" * 60)
    
    all_tokens = []
    
    # Scanner toutes les chaînes
    for chain_name, api_config in ETHERSCAN_APIS.items():
        try:
            results = scan_chain_via_etherscan(chain_name, api_config, wallet_address)
            all_tokens.extend(results)
        except Exception as e:
            print(f"❌ Erreur pour {chain_name}: {e}")
    
    if not all_tokens:
        return {"error": "Aucun token trouvé"}
    
    # Créer le DataFrame
    tokens_df = pd.DataFrame(all_tokens)
    
    print("\n" + "=" * 60)
    print("📈 CALCUL DU SCORE")
    print("=" * 60)
    
    # Calculer le score
    score_result = calculate_wallet_score(tokens_df)
    
    return {
        "tokens": tokens_df.to_dict('records'),
        "total_value": tokens_df['usd'].sum(),
        "score": score_result
    }

@app.route('/')
def index():
    """Page principale"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_wallet_api():
    """API pour analyser un wallet"""
    data = request.get_json()
    wallet_address = data.get('wallet_address')
    
    if not wallet_address:
        return jsonify({"error": "Adresse wallet requise"}), 400
    
    # Générer un ID unique pour cette analyse
    analysis_id = str(uuid.uuid4())
    
    # Démarrer l'analyse en arrière-plan
    def run_analysis():
        try:
            result = analyze_wallet(wallet_address)
            active_analyses[analysis_id] = {
                "status": "completed",
                "result": result,
                "timestamp": time.time()
            }
        except Exception as e:
            active_analyses[analysis_id] = {
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }
    
    # Lancer l'analyse dans un thread séparé
    thread = threading.Thread(target=run_analysis)
    thread.start()
    
    # Initialiser le statut
    active_analyses[analysis_id] = {
        "status": "running",
        "timestamp": time.time()
    }
    
    return jsonify({
        "analysis_id": analysis_id,
        "status": "started"
    })

@app.route('/api/status/<analysis_id>')
def get_analysis_status(analysis_id):
    """Obtenir le statut d'une analyse"""
    if analysis_id not in active_analyses:
        return jsonify({"error": "Analyse non trouvée"}), 404
    
    analysis = active_analyses[analysis_id]
    
    if analysis["status"] == "completed":
        result = analysis["result"]
        return jsonify({
            "status": "completed",
            "result": {
                "tokens": result["tokens"],
                "total_value": result["total_value"],
                "score": result["score"],
                "token_count": result["score"].get("token_count", 0)
            }
        })
    elif analysis["status"] == "error":
        return jsonify({
            "status": "error",
            "error": analysis["error"]
        })
    else:
        return jsonify({
            "status": "running"
        })

@app.route('/api/chains')
def get_chains():
    """API pour récupérer les chaînes supportées"""
    return jsonify(CHAIN_MAP)

@app.route('/api/test-balances/<wallet_address>')
def test_balances(wallet_address):
    """API de test pour vérifier les balances d'un wallet"""
    try:
        results = {}
        for cid, chain_name in CHAIN_MAP.items():
            try:
                df = balances(wallet_address, cid)
                results[chain_name] = {
                    "positions_count": len(df),
                    "total_value": float(df.usd.sum()) if not df.empty else 0,
                    "positions": df.to_dict('records') if not df.empty else []
                }
            except Exception as e:
                results[chain_name] = {
                    "error": str(e),
                    "positions_count": 0,
                    "total_value": 0,
                    "positions": []
                }
        
        return jsonify({
            "wallet": wallet_address,
            "results": results,
            "covalent_key_available": bool(COV_KEY)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def find_free_port(start_port=8080, max_attempts=10):
    """Trouve un port libre à partir du port de départ"""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

if __name__ == '__main__':
    if not COV_KEY:
        print("⚠️  COVALENT_KEY non trouvée dans .env")
        print("   L'analyse des balances sera limitée")
    
    # Trouver un port libre
    port = find_free_port()
    if port is None:
        print("❌ Impossible de trouver un port libre")
        sys.exit(1)
    
    print(f"🌐 Démarrage sur le port {port}")
    print(f"📍 URL: http://localhost:{port}")
    
    app.run(debug=True, host='0.0.0.0', port=port)

