# 🚀 Tutorial: Wallet Beta Analyzer

## 📋 Overview

This application analyzes your EVM wallet to:
- 🔍 Automatically detect all your tokens across 6 chains
- 📊 Calculate a stability score based on volatility
- 💰 Display total value and distribution by chain
- 🎯 Provide recommendations on diversification

## 🛠️ Installation and Launch

### Prerequisites
- Python 3.8+
- Node.js (optional, for scripts)
- Internet connection

### 1. Clone the project
```bash
git clone <your-repo>
cd wallet-beta-dual
```

### 2. API Key Configuration
Create a `.env` file in the project root:
```env
# Etherscan key (required)
ETHERSCAN_API_KEY="MBN5B4IPQP3JNTRPS97Z7XCZNVNTNWA655"

# Optional keys for other chains
BSCSCAN_API_KEY="YourBscScanKey"
ARBISCAN_API_KEY="YourArbiscanKey"
OPTIMISM_API_KEY="YourOptimismKey"
SNOWSCAN_API_KEY="YourSnowscanKey"
```

### 3. Install dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Launch the application

#### Option A: Automatic script (Recommended)
```bash
# On macOS/Linux:
./start.sh

# On Windows:
start.bat
```

#### Option B: Manual launch
```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Launch application
python app.py
```

### 5. Access the application
Open your browser and go to:
```
http://localhost:8080
```

## 🎯 Usage

### 1. Enter Wallet Address
- **Option A: Manual entry**
  - Type your wallet address in the field
  - Address must start with `0x` and be 42 characters long
  - Press Enter or click "Validate Address"

- **Option B: Paste from clipboard**
  - Copy address from your wallet or explorer
  - Click the 📋 (Paste) button
  - Address will be automatically validated

### 2. Address Validation
- Application automatically checks address format
- If address is valid, "Validate Address" button becomes active
- Click to confirm and proceed to analysis

### 3. Launch Analysis
- Click "Analyze Portfolio"
- Application will automatically scan:
  - ✅ Ethereum
  - ✅ Arbitrum  
  - ✅ Base
  - ✅ Optimism
  - ✅ BSC
  - ✅ Avalanche

### 4. Interpret Results

#### Portfolio Score
- 🟢 **80-100** : Excellent - Very stable portfolio
- 🟡 **60-79** : Good - Moderately stable portfolio  
- 🟠 **40-59** : Average - Volatile portfolio
- 🔴 **0-39** : Risky - Very volatile portfolio

#### Token Types
- **Stable** : USDC, USDT, ETH, WETH (High score)
- **Normal** : Standard tokens (Medium score)
- **Volatile** : Meme coins, DeFi tokens (Low score)

## 🔧 Advanced Features

### Command Line Testing
```bash
# Complete wallet test
python test_complete_analysis.py

# Specific test
python test_wallet.py 0x1c633eb00291398589718daa3938a6bd4f71949c
```

### Useful Scripts
```bash
# Stop application
./stop.sh

# Check status
./status.sh

# Clean processes
pkill -f "python app.py"
```

## 🐛 Troubleshooting

### Port Issues
If port 8080 is occupied:
```bash
# Find process
lsof -i :8080

# Kill process
kill -9 <PID>
```

### Dependency Errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### API Errors
- Check your Etherscan key in `.env`
- Ensure you have internet connection
- Check API limits (5 req/sec)

### Undetected Tokens
- API may not detect very recent tokens
- Some tokens may have unavailable prices
- Verify wallet address is correct

## 📊 Supported Chains

| Chain | Status | API |
|-------|--------|-----|
| Ethereum | ✅ | Etherscan |
| Arbitrum | ✅ | Etherscan |
| Base | ✅ | Etherscan |
| Optimism | ✅ | Etherscan |
| BSC | ✅ | Etherscan |
| Avalanche | ✅ | Etherscan |

## 🔒 Security

- ✅ No private keys stored
- ✅ Only public addresses used
- ✅ Secure MetaMask connection
- ✅ No personal data collected

## 📈 Future Improvements

- [ ] Support for more chains
- [ ] Analysis history
- [ ] Volatility alerts
- [ ] Data export
- [ ] Public API

## 🆘 Support

If you encounter issues:
1. Check console logs
2. Test with a simple wallet
3. Verify internet connection
4. Check GitHub issues

---

**🎉 Your wallet analyzer is ready!**
