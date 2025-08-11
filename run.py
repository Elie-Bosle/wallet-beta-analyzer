#!/usr/bin/env python3
"""
Script de lancement pour Beta Portfolio Analyzer
"""

import os
import sys
import subprocess
import platform

def main():
    print("🚀 Lancement de Beta Portfolio Analyzer...")
    
    # Vérifier si l'environnement virtuel existe
    venv_path = ".venv"
    if not os.path.exists(venv_path):
        print("📦 Création de l'environnement virtuel...")
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
    
    # Activer l'environnement virtuel et installer les dépendances
    if platform.system() == "Windows":
        activate_script = os.path.join(venv_path, "Scripts", "activate")
        python_path = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        activate_script = os.path.join(venv_path, "bin", "activate")
        python_path = os.path.join(venv_path, "bin", "python")
    
    # Installer les dépendances
    print("📦 Installation des dépendances...")
    subprocess.run([python_path, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Lancer l'application
    print("🌐 Démarrage du serveur web...")
    print("📍 L'application sera disponible sur: http://localhost:8080")
    print("🔄 Appuyez sur Ctrl+C pour arrêter le serveur")
    print("-" * 50)
    
    try:
        subprocess.run([python_path, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Arrêt du serveur...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du lancement: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
