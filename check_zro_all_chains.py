#!/usr/bin/env python3
"""
Vérifier ZRO sur toutes les chaînes
"""

from web3 import Web3

def check_zro_all_chains():
    """Vérifier ZRO sur toutes les chaînes"""
    wallet = "0x1c633eb00291398589718daa3938a6bd4f71949c"
    zro_addr = "0x6985884c4392d348587b19cb9eaaf157f13271cd"
    
    # RPC endpoints pour chaque chaîne
    chains = {
        "Ethereum": "https://eth.llamarpc.com",
        "Arbitrum": "https://arbitrum.llamarpc.com",
        "Base": "https://base.llamarpc.com",
        "Optimism": "https://optimism.llamarpc.com",
        "Polygon": "https://polygon.llamarpc.com",
        "BSC": "https://bsc.llamarpc.com",
        "Avalanche": "https://avalanche.llamarpc.com"
    }
    
    abi = [{"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]
    
    print(f"🔍 Vérification ZRO sur toutes les chaînes")
    print(f"👛 Wallet: {wallet}")
    print(f"🪙 Token ZRO: {zro_addr}")
    print("=" * 60)
    
    for chain_name, rpc_url in chains.items():
        try:
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            if w3.is_connected():
                try:
                    contract = w3.eth.contract(
                        address=Web3.to_checksum_address(zro_addr),
                        abi=abi
                    )
                    balance = contract.functions.balanceOf(Web3.to_checksum_address(wallet)).call()
                    
                    if balance > 0:
                        balance_human = balance / 10**18
                        print(f"✅ {chain_name}: {balance_human:,.6f} ZRO")
                    else:
                        print(f"❌ {chain_name}: 0 ZRO")
                        
                except Exception as e:
                    print(f"⚠️  {chain_name}: Erreur - {e}")
            else:
                print(f"❌ {chain_name}: Impossible de se connecter")
                
        except Exception as e:
            print(f"❌ {chain_name}: Erreur de connexion - {e}")

if __name__ == "__main__":
    check_zro_all_chains()
