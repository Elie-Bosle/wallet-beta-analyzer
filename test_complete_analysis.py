#!/usr/bin/env python3
"""
Test de l'analyse complète : tokens + beta + score
"""

from app import analyze_wallet

def main():
    wallet_address = "0x1c633eb00291398589718daa3938a6bd4f71949c"  # Votre wallet original
    
    print("🚀 ANALYSE COMPLÈTE DU WALLET")
    print("=" * 60)
    
    result = analyze_wallet(wallet_address)
    
    if "error" in result:
        print(f"❌ Erreur: {result['error']}")
        return
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS FINAUX")
    print("=" * 60)
    
    print(f"💰 Valeur totale: ${result['total_value']:.2f}")
    print(f"🎯 Score du wallet: {result['score']['score']:.1f}/100")
    
    if isinstance(result['score']['details'], list):
        print(f"\n📈 Détails par token:")
        for detail in result['score']['details']:
            print(f"  - {detail['token']}: Beta ETH = {detail['beta_eth']:.3f}, Score = {detail['score_eth']:.1f}")
    
    print(f"\n🎯 Interprétation du score:")
    score = result['score']['score']
    if score >= 80:
        print("  🟢 Excellent: Portfolio très stable")
    elif score >= 60:
        print("  🟡 Bon: Portfolio modérément stable")
    elif score >= 40:
        print("  🟠 Moyen: Portfolio volatile")
    else:
        print("  🔴 Risqué: Portfolio très volatile")

if __name__ == "__main__":
    main()
