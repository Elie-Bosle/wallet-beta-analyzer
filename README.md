# Beta Portfolio Analyzer

Une application web moderne pour analyser votre portefeuille DeFi et calculer votre score de volatilité basé sur le beta par rapport à ETH et BTC.

## 🚀 Fonctionnalités

- **Connexion Wallet EVM** : Support de MetaMask et autres wallets compatibles
- **Analyse Multi-Chaînes** : Ethereum, Arbitrum, Base, Optimism
- **Calcul Beta** : Analyse de la volatilité relative à ETH et BTC sur 30 jours
- **Score de Volatilité** : Score personnalisé basé sur la stabilité du portefeuille
- **Interface Moderne** : Design responsive avec animations fluides
- **Positions Top 5** : Affichage des positions ≥ $10 les plus importantes

## 📋 Prérequis

- Python 3.8+
- MetaMask ou autre wallet EVM
- Clé API Covalent (optionnelle mais recommandée)

## 🔑 Configuration des Clés API Multi-Chaînes

### Clés API Requises

Pour une détection complète sur toutes les chaînes EVM, obtenez des clés API gratuites :

#### 1. **Etherscan (Ethereum)** ✅ Configuré
- **URL :** [https://etherscan.io/apis](https://etherscan.io/apis)
- **Clé actuelle :** `9DT1SVWM863HNTGCZB4491BZJS7F2EW8FA`
- **Limite :** 5 req/sec (gratuit)

#### 2. **BSCScan (Binance Smart Chain)** ⚠️ Requis
- **URL :** [https://bscscan.com/apis](https://bscscan.com/apis)
- **Limite :** 5 req/sec (gratuit)
- **Status :** Erreur "NOTOK" - clé requise

#### 3. **Arbiscan (Arbitrum)** ⚠️ Requis
- **URL :** [https://arbiscan.io/apis](https://arbiscan.io/apis)
- **Limite :** 5 req/sec (gratuit)
- **Status :** Erreur "NOTOK" - clé requise

#### 4. **Optimistic Etherscan (Optimism)** ⚠️ Requis
- **URL :** [https://optimistic.etherscan.io/apis](https://optimistic.etherscan.io/apis)
- **Limite :** 5 req/sec (gratuit)
- **Status :** Erreur "NOTOK" - clé requise

#### 5. **Snowscan (Avalanche)** ⚠️ Requis
- **URL :** [https://snowscan.xyz/apis](https://snowscan.xyz/apis)
- **Limite :** 5 req/sec (gratuit)
- **Status :** Erreur "NOTOK" - clé requise

### Configuration du fichier .env

```env
# Clé Etherscan (Ethereum) - ✅ Configurée
ETHERSCAN_API_KEY="9DT1SVWM863HNTGCZB4491BZJS7F2EW8FA"

# Clés à obtenir (remplacez par vos vraies clés)
BSCSCAN_API_KEY="VotreCléBscScan"
ARBISCAN_API_KEY="VotreCléArbiscan"
OPTIMISM_API_KEY="VotreCléOptimism"
SNOWSCAN_API_KEY="VotreCléSnowscan"

# Clé Covalent (optionnelle)
COVALENT_KEY="cqt_rQ3TxXyv9KPQPgpY6Wdt8ytBygVp"
```

### Instructions pour obtenir les clés

1. **Allez sur chaque site d'API**
2. **Créez un compte gratuit**
3. **Générez une clé API**
4. **Ajoutez la clé dans le fichier .env**

### Test des clés

```bash
# Test complet multi-chaînes
python multi_chain_balances.py

# Test spécifique par chaîne
python test_etherscan.py
```

## 🚀 Installation et Lancement

### Option 1 : Script automatique (Recommandé)

**Sur macOS/Linux :**
```bash
./start.sh
```

**Sur Windows :**
```cmd
start.bat
```

### Option 2 : Gestion avancée

**Vérifier l'état de l'application :**
```bash
./status.sh
```

**Arrêter l'application :**
```bash
./stop.sh  # macOS/Linux
```

**Redémarrer l'application :**
```bash
./stop.sh && ./start.sh  # macOS/Linux
```

### Option 2 : Manuel

1. **Créer et activer l'environnement virtuel**
```bash
python3 -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Démarrer l'application**
```bash
python app.py
```

4. **Ouvrir votre navigateur**
```
http://localhost:8080 (ou port suivant si 8080 est occupé)
```

### Connecter votre wallet
- Cliquez sur "Connecter Wallet"
- Autorisez la connexion dans MetaMask
- Lancez l'analyse de votre portefeuille

## 📊 Comment ça marche

### 1. Récupération des Positions
- L'application scanne votre wallet sur les chaînes supportées
- Récupère toutes les positions ≥ $10
- Utilise l'API Covalent pour les données de prix

### 2. Calcul du Beta
- Récupère l'historique des prix sur 30 jours
- Calcule le beta de chaque token par rapport à ETH et BTC
- Utilise la formule : β = Covariance(asset, benchmark) / Variance(benchmark)

### 3. Score de Volatilité
- Score basé sur la proximité du beta avec 1 (stabilité)
- Score ETH : 100 - |β_ETH - 1| × 50
- Score BTC : 100 - |β_BTC - 1| × 50
- Score final : moyenne des deux scores

## 🔧 Configuration Avancée

### Variables d'Environnement
```env
COVALENT_KEY=cqt_votre_cle_api_ici
FLASK_ENV=development
FLASK_DEBUG=1
```

### Paramètres Modifiables
Dans `app.py`, vous pouvez ajuster :
- `DAYS = 30` : Période d'analyse
- `MIN_USD = 10` : Seuil minimum des positions
- `MAX_TOKENS = 5` : Nombre maximum de positions affichées

## 📱 Support des Chaînes

- **Ethereum** (Chain ID: 1)
- **Arbitrum** (Chain ID: 42161)
- **Base** (Chain ID: 8453)
- **Optimism** (Chain ID: 10)

## 🎨 Interface Utilisateur

- **Design Responsive** : Compatible mobile et desktop
- **Animations Fluides** : Transitions et effets visuels
- **Mode Sombre** : Interface moderne et élégante
- **Feedback Temps Réel** : Barre de progression et notifications

## 🔒 Sécurité

- **Pas de Stockage** : Aucune donnée n'est sauvegardée
- **Connexion Locale** : Toutes les analyses sont effectuées en temps réel
- **Validation Wallet** : Vérification de l'adresse Ethereum
- **Gestion d'Erreurs** : Messages d'erreur informatifs

## 🐛 Dépannage

### Erreurs Communes

1. **"MetaMask n'est pas installé"**
   - Installez l'extension MetaMask
   - Ou utilisez un autre wallet compatible

2. **"Aucune position ≥ 10 USD trouvée"**
   - Vérifiez que votre wallet contient des tokens
   - Assurez-vous d'être sur les bonnes chaînes
   - Testez avec le script de diagnostic

3. **"Erreur lors de l'analyse"**
   - Vérifiez votre connexion internet
   - Si vous avez une clé Covalent, vérifiez qu'elle est valide

### Outils de Diagnostic

**Test des balances d'un wallet :**
```bash
python test_wallet.py <adresse_wallet>
```

**Vérification de l'état de l'application :**
```bash
./status.sh
```

**Test API direct :**
```bash
curl http://localhost:8080/api/test-balances/<adresse_wallet>
```

### Logs de Débogage
```bash
# Activer les logs détaillés
export FLASK_DEBUG=1
python app.py
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- **Covalent** pour l'API de données blockchain
- **DefiLlama** pour les prix des tokens
- **CoinGecko** pour les données historiques
- **Tailwind CSS** pour le framework CSS
- **Ethers.js** pour l'interaction avec Ethereum

## 📞 Support

Pour toute question ou problème :
- Ouvrez une issue sur GitHub
- Consultez la documentation des APIs utilisées
- Vérifiez les logs de l'application

---

**Développé avec ❤️ pour la communauté DeFi**
