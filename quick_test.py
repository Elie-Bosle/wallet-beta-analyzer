#!/usr/bin/env python3
"""
Test rapide de l'application
"""

import requests
import time

def test_app():
    print("🧪 Test rapide de l'application...")
    
    # Test 1: Vérifier que l'app répond
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        if response.status_code == 200:
            print("✅ Application accessible sur http://localhost:8080")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Impossible de se connecter à l'application: {e}")
        return False
    
    # Test 2: Test de l'API d'analyse
    try:
        test_wallet = "0x1c633eb00291398589718daa3938a6bd4f71949c"
        response = requests.post("http://localhost:8080/api/analyze", 
                               json={"wallet_address": test_wallet},
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            analysis_id = data.get("analysis_id")
            print(f"✅ Analyse démarrée avec ID: {analysis_id}")
            
            # Attendre les résultats
            print("⏳ Attente des résultats...")
            for i in range(30):  # Max 30 secondes
                time.sleep(1)
                status_response = requests.get(f"http://localhost:8080/api/status/{analysis_id}")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data.get("status") == "completed":
                        result = status_data.get("result", {})
                        print(f"✅ Analyse terminée!")
                        print(f"   💰 Valeur totale: ${result.get('total_value', 0):.2f}")
                        print(f"   🎯 Score: {result.get('score', {}).get('score', 0):.1f}/100")
                        print(f"   🪙 Tokens: {result.get('token_count', 0)}")
                        return True
                    elif status_data.get("status") == "error":
                        print(f"❌ Erreur d'analyse: {status_data.get('error')}")
                        return False
            
            print("❌ Timeout - L'analyse prend trop de temps")
            return False
            
        else:
            print(f"❌ Erreur API: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test API: {e}")
        return False

if __name__ == "__main__":
    success = test_app()
    if success:
        print("\n🎉 Tous les tests sont passés ! L'application fonctionne correctement.")
        print("🌐 Ouvrez http://localhost:8080 dans votre navigateur")
    else:
        print("\n❌ Certains tests ont échoué. Vérifiez les logs.")
