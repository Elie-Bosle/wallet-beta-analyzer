# 🚀 Démonstration - Beta Portfolio Analyzer

## 📋 Vue d'ensemble

Beta Portfolio Analyzer est une application web moderne qui permet d'analyser votre portefeuille DeFi et de calculer votre score de volatilité basé sur le beta par rapport à ETH et BTC.

## 🎯 Fonctionnalités Principales

### 1. Connexion Wallet EVM
- Support de MetaMask et autres wallets compatibles
- Connexion sécurisée et validation d'adresse
- Interface intuitive avec feedback visuel

### 2. Analyse Multi-Chaînes
- **Ethereum** (Chain ID: 1)
- **Arbitrum** (Chain ID: 42161)
- **Base** (Chain ID: 8453)
- **Optimism** (Chain ID: 10)

### 3. Calcul Beta Avancé
- Analyse sur 30 jours
- Beta par rapport à ETH et BTC
- Calcul de la volatilité relative
- Score de stabilité personnalisé

## 🎨 Interface Utilisateur

### Page d'Accueil
```
┌─────────────────────────────────────────────────────────┐
│                    Beta Portfolio Analyzer              │
│                                                         │
│  Analysez votre portefeuille DeFi et obtenez votre     │
│  score de volatilité basé sur le beta par rapport à    │
│  ETH et BTC                                            │
└─────────────────────────────────────────────────────────┘
```

### Section Connexion Wallet
```
┌─────────────────────────────────────────────────────────┐
│                    Connexion Wallet                     │
│                                                         │
│  [🔌 Connecter Wallet]                                 │
│                                                         │
│  ✅ Wallet connecté                                     │
│     0x1234...5678                                      │
└─────────────────────────────────────────────────────────┘
```

### Section Analyse
```
┌─────────────────────────────────────────────────────────┐
│                  Analyse du Portefeuille               │
│                                                         │
│  [▶️ Lancer l'Analyse]                                 │
│                                                         │
│  ████████████████████████████████████████████████████  │
│  Analyse en cours... 85%                                │
└─────────────────────────────────────────────────────────┘
```

### Résultats
```
┌─────────────────────────────────────────────────────────┐
│                        Scores                          │
│                                                         │
│  ⭐ Score Global: 78.5                                 │
│  🟢 Score ETH: 82.3                                    │
│  🟠 Score BTC: 74.7                                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    Valeurs Beta                        │
│                                                         │
│  🟢 Beta vs ETH: 0.85                                  │
│  🟠 Beta vs BTC: 1.23                                  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    Top Positions                       │
│                                                         │
│  Token    │ Chaîne   │ Valeur USD │ β ETH │ β BTC     │
│  USDC     │ Ethereum │ $1,250.00  │ 0.02  │ 0.01      │
│  WETH     │ Ethereum │ $850.00    │ 1.05  │ 0.95      │
│  UNI      │ Ethereum │ $320.00    │ 1.15  │ 1.08      │
└─────────────────────────────────────────────────────────┘
```

## 🔧 Utilisation

### 1. Lancement de l'Application
```bash
# Option 1: Script automatique (recommandé)
./start.sh

# Option 2: Manuel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### 2. Accès à l'Application
- Ouvrez votre navigateur
- Allez sur `http://localhost:8080`
- L'interface s'affiche automatiquement

### 3. Connexion Wallet
- Cliquez sur "Connecter Wallet"
- Autorisez la connexion dans MetaMask
- Vérifiez que l'adresse s'affiche correctement

### 4. Lancement de l'Analyse
- Cliquez sur "Lancer l'Analyse"
- Suivez la progression en temps réel
- Attendez les résultats (30-60 secondes)

### 5. Interprétation des Résultats

#### Score Global
- **90-100** : Portefeuille très stable
- **70-89** : Portefeuille stable
- **50-69** : Volatilité modérée
- **0-49** : Portefeuille volatil

#### Beta Values
- **β = 1.0** : Même volatilité que le benchmark
- **β > 1.0** : Plus volatil que le benchmark
- **β < 1.0** : Moins volatil que le benchmark

## 📊 Exemples de Résultats

### Portefeuille Stable (Score: 85)
```
Positions:
- USDC: $2,000 (β ETH: 0.01, β BTC: 0.01)
- WETH: $1,500 (β ETH: 1.02, β BTC: 0.98)
- DAI: $800 (β ETH: 0.02, β BTC: 0.01)

Score Global: 85.2
Score ETH: 87.1
Score BTC: 83.3
```

### Portefeuille Volatil (Score: 35)
```
Positions:
- PEPE: $1,000 (β ETH: 2.5, β BTC: 2.8)
- SHIB: $800 (β ETH: 1.8, β BTC: 2.1)
- DOGE: $600 (β ETH: 1.6, β BTC: 1.9)

Score Global: 35.4
Score ETH: 38.2
Score BTC: 32.6
```

## 🔒 Sécurité

- **Aucune donnée stockée** : Toutes les analyses sont en temps réel
- **Validation d'adresse** : Vérification de l'adresse Ethereum
- **Connexion locale** : Pas de transmission de données sensibles
- **Gestion d'erreurs** : Messages informatifs en cas de problème

## 🐛 Dépannage

### Erreurs Communes

1. **"MetaMask n'est pas installé"**
   - Installez l'extension MetaMask
   - Ou utilisez un autre wallet compatible

2. **"Aucune position ≥ 10 USD trouvée"**
   - Vérifiez que votre wallet contient des tokens
   - Assurez-vous d'être sur les bonnes chaînes

3. **"Erreur lors de l'analyse"**
   - Vérifiez votre connexion internet
   - Si vous avez une clé Covalent, vérifiez qu'elle est valide

### Logs de Débogage
```bash
# Activer les logs détaillés
export FLASK_DEBUG=1
python app.py
```

## 🎯 Cas d'Usage

### 1. Analyse de Portefeuille Personnel
- Vérifier la stabilité de vos investissements
- Comparer la volatilité par rapport aux benchmarks
- Optimiser l'allocation de vos actifs

### 2. Recherche et Analyse
- Étudier la corrélation entre différents tokens
- Analyser l'impact des événements de marché
- Comparer les performances sur différentes chaînes

### 3. Gestion de Risque
- Identifier les positions les plus volatiles
- Équilibrer le portefeuille pour réduire les risques
- Surveiller les changements de volatilité

## 🚀 Améliorations Futures

- [ ] Support de plus de chaînes (Polygon, BSC, etc.)
- [ ] Analyse historique des scores
- [ ] Alertes de volatilité
- [ ] Export des données
- [ ] Comparaison entre portefeuilles
- [ ] Intégration avec des DEX pour le trading

---

**Développé avec ❤️ pour la communauté DeFi**
