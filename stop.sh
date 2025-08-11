#!/bin/bash

echo "🛑 Arrêt de Beta Portfolio Analyzer..."

# Trouver et arrêter les processus Python qui utilisent le port 8080
if lsof -ti:8080 > /dev/null 2>&1; then
    echo "📍 Arrêt des processus sur le port 8080..."
    lsof -ti:8080 | xargs kill -9
    echo "✅ Processus arrêtés"
else
    echo "ℹ️  Aucun processus trouvé sur le port 8080"
fi

# Arrêter tous les processus Python liés à l'application
echo "🔍 Recherche d'autres processus de l'application..."
pids=$(ps aux | grep "python.*app.py" | grep -v grep | awk '{print $2}')

if [ ! -z "$pids" ]; then
    echo "📍 Arrêt des processus Python de l'application..."
    echo $pids | xargs kill -9
    echo "✅ Tous les processus arrêtés"
else
    echo "ℹ️  Aucun processus de l'application trouvé"
fi

echo "🎉 Application arrêtée avec succès"
