#!/usr/bin/env python3
"""
Script pour ajouter facilement une nouvelle cryptomonnaie au système.

Usage:
    python scripts/add_new_crypto.py <symbol_binance> <crypto_id>
    
Exemple:
    python scripts/add_new_crypto.py XRPUSDT ripple
"""

import sys
import requests

def check_binance_symbol(symbol):
    """Vérifie si le symbole existe sur Binance."""
    try:
        response = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}", timeout=5)
        if response.status_code == 200:
            price_data = response.json()
            print(f"✅ {symbol} trouvé sur Binance: {price_data['price']} USD")
            return True
        else:
            print(f"❌ {symbol} non trouvé sur Binance")
            return False
    except Exception as e:
        print(f"❌ Erreur vérification Binance: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/add_new_crypto.py <SYMBOL_BINANCE> <crypto_id>")
        print("Exemple: python scripts/add_new_crypto.py XRPUSDT ripple")
        sys.exit(1)
    
    symbol_binance = sys.argv[1].upper()
    crypto_id = sys.argv[2].lower()
    
    print(f"🔄 Ajout de la crypto: {crypto_id} ({symbol_binance})")
    print()
    
    # Vérifier sur Binance
    if not check_binance_symbol(symbol_binance):
        print("❌ Symbole non valide sur Binance")
        sys.exit(1)
    
    print()
    print("📝 INSTRUCTIONS POUR AJOUTER CETTE CRYPTO:")
    print()
    print("1️⃣ Dans refresh_crypto_prices.py, ajouter:")
    print(f"   '{symbol_binance}': '{crypto_id}',")
    print()
    print("2️⃣ Dans app/services/binance_price_service.py, ajouter:")
    print(f"   '{crypto_id}': '{symbol_binance}',")
    print()
    print("3️⃣ Relancer la mise à jour:")
    print("   python refresh_crypto_prices.py")
    print()
    print("✅ La crypto sera alors disponible dans les calculs patrimoniaux")

if __name__ == "__main__":
    main()