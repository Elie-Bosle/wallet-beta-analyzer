#!/bin/bash

echo "🚀 Lancement de Beta Portfolio Analyzer..."

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d ".venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv .venv
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source .venv/bin/activate

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# Vérifier et libérer le port si nécessaire
echo "🔍 Vérification des ports..."
if lsof -ti:8080 > /dev/null 2>&1; then
    echo "⚠️  Port 8080 occupé, libération en cours..."
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Lancer l'application
echo "🌐 Démarrage du serveur web..."
echo "📍 L'application sera disponible sur: http://localhost:8080 (ou port suivant)"
echo "🔄 Appuyez sur Ctrl+C pour arrêter le serveur"
echo "----------------------------------------"

python app.py
