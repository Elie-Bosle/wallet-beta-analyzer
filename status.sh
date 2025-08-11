#!/bin/bash

echo "🔍 Diagnostic de Beta Portfolio Analyzer"
echo "========================================"

# Vérifier si l'environnement virtuel existe
if [ -d ".venv" ]; then
    echo "✅ Environnement virtuel trouvé"
else
    echo "❌ Environnement virtuel manquant"
fi

# Vérifier les processus Python
echo ""
echo "🐍 Processus Python :"
python_processes=$(ps aux | grep "python.*app.py" | grep -v grep)
if [ ! -z "$python_processes" ]; then
    echo "✅ Application en cours d'exécution :"
    echo "$python_processes"
else
    echo "❌ Aucune application en cours d'exécution"
fi

# Vérifier les ports utilisés
echo ""
echo "🌐 Ports utilisés :"
for port in 8080 8081 8082 8083 8084; do
    if lsof -ti:$port > /dev/null 2>&1; then
        echo "📍 Port $port : OCCUPÉ"
        lsof -i:$port
    else
        echo "📍 Port $port : LIBRE"
    fi
done

# Vérifier les dépendances
echo ""
echo "📦 Dépendances :"
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt trouvé"
    if [ -d ".venv" ]; then
        echo "🔍 Vérification des packages installés..."
        source .venv/bin/activate
        pip list | grep -E "(flask|web3|pandas|numpy)" || echo "⚠️  Certaines dépendances manquent"
    fi
else
    echo "❌ requirements.txt manquant"
fi

# Test de connectivité
echo ""
echo "🌐 Test de connectivité :"
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "✅ Application accessible sur http://localhost:8080"
elif curl -s http://localhost:8081 > /dev/null 2>&1; then
    echo "✅ Application accessible sur http://localhost:8081"
elif curl -s http://localhost:8082 > /dev/null 2>&1; then
    echo "✅ Application accessible sur http://localhost:8082"
else
    echo "❌ Application non accessible"
fi

echo ""
echo "🎯 Actions recommandées :"
echo "  - Pour démarrer : ./start.sh"
echo "  - Pour arrêter : ./stop.sh"
echo "  - Pour redémarrer : ./stop.sh && ./start.sh"
