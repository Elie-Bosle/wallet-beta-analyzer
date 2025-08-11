#!/usr/bin/env python3
"""
beta_portfolio_defillama.py – top 5 positions ≥ 10 USD, multichain
β (30 j) vs BTC & ETH
• Clé Covalent “cqt_…” transmise en query param ?key=
• Prix USD manquants via DefiLlama (chain:address)
• Historique 30 j : batch Covalent ; fallback CoinGecko pour Base
"""

import os, sys, time, datetime as dt, requests
import pandas as pd, numpy as np
from dotenv import load_dotenv
from tqdm import tqdm

# ───────── paramètres ─────────
DAYS        = 30
MIN_USD     = 10
MAX_TOKENS  = 5
BENCHMARKS  = {"BTC": "bitcoin", "ETH": "ethereum"}

CHAIN_MAP = {                         # chainId → nom
    1:     "Ethereum",
    42161: "Arbitrum",
    8453:  "Base",
    10:    "Optimism",
}
CHAIN_TO_LLAMA = {                   # chainId → slug DefiLlama
    1: "ethereum", 42161: "arbitrum", 8453: "base", 10: "optimism"
}

COV_BAL  = "https://api.covalenthq.com/v1/{chain}/address/{addr}/balances_v2/"
COV_HIST = ("https://api.covalenthq.com/v1/{chain}/pricing/"
            "historical_by_addresses_v2/USD/{addr_csv}/")
CGK_SIMPLE = "https://api.coingecko.com/api/v3/simple/price"
CGK_HIST   = "https://api.coingecko.com/api/v3/coins/{id}/market_chart"

load_dotenv()
COV_KEY = os.getenv("COVALENT_KEY")
if not COV_KEY:
    sys.exit("❌  Ajoute COVALENT_KEY=cqt_… dans .env ou exporte‑la")

HEAD = {"User-Agent": "beta-portfolio/1.0"}   # pas de clé dans HEAD

# ───────── helpers ─────────
def price_llama(chain_id: int, addr: str) -> float:
    plat = CHAIN_TO_LLAMA.get(chain_id)
    if not plat: return 0
    url  = f"https://coins.llama.fi/prices/current/{plat}:{addr}"
    r = requests.get(url, timeout=10)
    return r.json()["coins"].get(f"{plat}:{addr}", {}).get("price", 0) if r.ok else 0

def cgk_hist(id_, days):
    r = requests.get(CGK_HIST.format(id=id_),
                     params={"vs_currency":"usd","days":days}, timeout=30)
    r.raise_for_status()
    d = pd.DataFrame(r.json()["prices"], columns=["ts","p"])
    d["date"] = pd.to_datetime(d.ts, unit="ms").dt.date
    return d.groupby("date").p.first().pct_change().dropna()

# ───────── balances ─────────
def balances(addr: str, cid: int) -> pd.DataFrame:
    url = COV_BAL.format(chain=cid, addr=addr)
    r = requests.get(url, params={"nft":"false", "key": COV_KEY},
                     headers=HEAD, timeout=30)
    if not r.ok:
        print(f"⚠️  {CHAIN_MAP[cid]} balances HTTP {r.status_code}")
        return pd.DataFrame()

    rows=[]
    for it in r.json()["data"]["items"]:
        usd = it["quote"] or 0
        if usd == 0:                                    # calcule via DefiLlama
            raw = int(it["balance"] or 0)
            dec = int(it.get("contract_decimals") or 18)
            price = price_llama(cid, it["contract_address"].lower())
            usd   = raw / 10**dec * price
        if usd >= MIN_USD:
            rows.append({
                "addr":  it["contract_address"].lower(),
                "sym":   it["contract_ticker_symbol"],
                "usd":   usd,
                "cid":   cid,
            })
    return pd.DataFrame(rows)

# ───────── historique prix ─────────
def hist_prices(cid: int, addrs: list[str],
                start: dt.date, end: dt.date) -> pd.DataFrame:
    url = COV_HIST.format(chain=cid, addr_csv=",".join(addrs))
    r = requests.get(url, params={"from": start, "to": end, "key": COV_KEY},
                     headers=HEAD, timeout=60)
    if r.status_code == 404:
        frames=[]
        for a in addrs:
            g=requests.get(
                f"https://api.coingecko.com/api/v3/coins/ethereum/contract/{a}/market_chart",
                params={"vs_currency":"usd","days":DAYS}, timeout=30)
            if g.ok:
                df=pd.DataFrame(g.json()["prices"],columns=["ts","price"])
                df["date"]=pd.to_datetime(df.ts,unit="ms").dt.date
                df["addr"]=a
                frames.append(df)
        return pd.concat(frames) if frames else pd.DataFrame()
    r.raise_for_status()
    frames=[]
    for p in r.json()["data"]["prices"]:
        df=pd.DataFrame(p["prices"],columns=["date","price"])
        df["date"]=pd.to_datetime(df.date).dt.date
        df["addr"]=p["contract_address"].lower()
        frames.append(df)
    return pd.concat(frames)

def beta(x,y): return np.cov(x,y)[0,1]/np.var(y) if np.var(y) else 0

# ───────── main ─────────
if len(sys.argv) != 2:
    sys.exit("Usage : python beta_portfolio_defillama.py <wallet>")
WALLET = sys.argv[1].lower()

# 1) balances multichain
frames=[balances(WALLET, cid) for cid in CHAIN_MAP]
df = pd.concat(frames, ignore_index=True)
if df.empty: sys.exit("Aucune position ≥ 10 USD.")

top=(df.sort_values("usd",ascending=False)
        .head(MAX_TOKENS).reset_index(drop=True))

# 2) historiques
end, start = dt.date.today(), dt.date.today()-dt.timedelta(days=DAYS)
hist = pd.concat([hist_prices(cid,
                              top.query("cid==@cid").addr.tolist(),
                              start, end)
                  for cid in top.cid.unique()],
                 ignore_index=True)

# 3) benchmarks
bench = {k: cgk_hist(v,DAYS) for k,v in BENCHMARKS.items()}

# 4) β individuels
for k in BENCHMARKS: top[f"β_{k}"]=np.nan
for idx,row in tqdm(top.iterrows(), total=len(top), ncols=70):
    s = (hist.query("addr == @row.addr")
             .sort_values("date").price.pct_change().dropna())
    for k in BENCHMARKS:
        a=s.align(bench[k], join="inner")
        top.loc[idx,f"β_{k}"]=beta(a[0],a[1])

# 5) β portefeuille
weights = top.usd / top.usd.sum()
beta_port = {k:(weights*top[f"β_{k}"]).sum() for k in BENCHMARKS}

# 6) affichage
print("\n===== β individuels (30 j) =====")
print(top[["sym","usd","β_BTC","β_ETH"]]
      .to_string(index=False,
                 formatters={"usd":"${:,.2f}".format,
                             "β_BTC":"{:.2f}".format,
                             "β_ETH":"{:.2f}".format}))
print("\n===== β global portefeuille =====")
for k,v in beta_port.items():
    print(f"β vs {k} : {v:.2f}")
