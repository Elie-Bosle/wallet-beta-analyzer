#!/usr/bin/env python3
"""
Script de test pour vérifier les balances d'un wallet
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import balances, CHAIN_MAP

def test_wallet(wallet_address):
    """Teste les balances d'un wallet sur toutes les chaînes"""
    print(f"🔍 Test des balances pour: {wallet_address}")
    print("=" * 50)
    
    total_positions = 0
    total_value = 0
    
    for cid, chain_name in CHAIN_MAP.items():
        print(f"\n📊 {chain_name} (Chain ID: {cid}):")
        try:
            df = balances(wallet_address, cid)
            if not df.empty:
                print(f"  ✅ {len(df)} positions trouvées")
                for _, row in df.iterrows():
                    print(f"    - {row['sym']}: ${row['usd']:.2f}")
                total_positions += len(df)
                total_value += df.usd.sum()
            else:
                print("  ❌ Aucune position trouvée")
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
    
    print("\n" + "=" * 50)
    print(f"📈 Résumé:")
    print(f"  - Total positions: {total_positions}")
    print(f"  - Valeur totale: ${total_value:.2f}")
    
    if total_positions == 0:
        print("\n⚠️  Aucune position trouvée. Vérifiez:")
        print("  - L'adresse du wallet est correcte")
        print("  - Le wallet contient des tokens")
        print("  - Les tokens valent ≥ $10")
        print("  - La clé Covalent est configurée (optionnel)")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_wallet.py <wallet_address>")
        print("Exemple: python test_wallet.py 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6")
        sys.exit(1)
    
    wallet_address = sys.argv[1].lower()
    test_wallet(wallet_address)
