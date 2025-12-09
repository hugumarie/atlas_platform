#!/usr/bin/env python3
"""
Script de rafraîchissement périodique des prix crypto.
À lancer via cron toutes les 5-10 minutes.

Usage: python refresh_crypto_prices.py
Ou: flask refresh-crypto-prices (si ajouté comme commande Flask)
"""

import sys
import os
import requests
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.crypto_price import CryptoPrice


class PeriodicCryptoPriceRefresh:
    """Service pour refresh périodique des prix crypto via cron."""
    
    BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
    EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest/USD"
    
    # Mapping complet des cryptos supportées - SYNCHRONISÉ avec BinancePriceService
    SUPPORTED_CRYPTOS = {
        'BTCUSDT': 'bitcoin',
        'ETHUSDT': 'ethereum', 
        'BNBUSDT': 'binancecoin',
        'SOLUSDT': 'solana',
        'ADAUSDT': 'cardano',
        'DOTUSDT': 'polkadot',
        'MATICUSDT': 'matic-network',
        'LINKUSDT': 'chainlink',
        'AVAXUSDT': 'avalanche-2',
        'ATOMUSDT': 'cosmos',
        'XLMUSDT': 'stellar',
        'VETUSDT': 'vechain',
        'ALGOUSDT': 'algorand',
        'HBARUSDT': 'hedera-hashgraph',
        'LTCUSDT': 'litecoin',
        'UNIUSDT': 'uniswap',
        'USDTUSDT': 'tether',
        'USDCUSDT': 'usd-coin',
        # Ajout facile de nouvelles cryptos ici
        # 'NEWTOKENUSDT': 'new-token-id',
    }
    
    @classmethod
    def get_usd_to_eur_rate(cls) -> float:
        """Récupère le taux USD->EUR."""
        try:
            print("🔄 Récupération du taux USD->EUR...")
            response = requests.get(cls.EXCHANGE_RATE_API, timeout=5)
            response.raise_for_status()
            rate = response.json()['rates']['EUR']
            print(f"💱 Taux USD->EUR: {rate:.4f}")
            return rate
        except Exception as e:
            print(f"⚠️ Erreur taux de change, utilisation fallback: {e}")
            return 0.92  # Fallback
    
    @classmethod
    def fetch_all_binance_prices(cls) -> dict:
        """Récupère TOUS les prix depuis Binance en un appel."""
        try:
            print("🔄 Récupération des prix depuis Binance...")
            response = requests.get(cls.BINANCE_API_URL, timeout=10)
            response.raise_for_status()
            
            all_prices = response.json()
            
            # Convertir en dict pour accès rapide
            binance_prices = {}
            for item in all_prices:
                symbol = item['symbol']
                if symbol in cls.SUPPORTED_CRYPTOS:
                    binance_prices[symbol] = float(item['price'])
            
            print(f"📊 {len(binance_prices)} prix crypto récupérés")
            return binance_prices
            
        except Exception as e:
            print(f"❌ Erreur récupération Binance: {e}")
            return {}
    
    @classmethod
    def update_database_prices(cls, binance_prices: dict, eur_rate: float) -> int:
        """Met à jour la base de données avec les nouveaux prix."""
        try:
            print("💾 Mise à jour de la base de données...")
            
            now = datetime.utcnow()
            updated_count = 0
            
            for binance_symbol, price_usd in binance_prices.items():
                our_symbol = cls.SUPPORTED_CRYPTOS[binance_symbol]
                price_eur = price_usd * eur_rate
                
                # Upsert en base
                crypto_price = CryptoPrice.query.filter_by(symbol=our_symbol).first()
                
                if crypto_price:
                    # Mise à jour
                    crypto_price.price_usd = price_usd
                    crypto_price.price_eur = price_eur
                    crypto_price.updated_at = now
                    print(f"   ✏️ MAJ {our_symbol}: ${price_usd:.2f} / €{price_eur:.2f}")
                else:
                    # Création
                    crypto_price = CryptoPrice(
                        symbol=our_symbol,
                        price_usd=price_usd,
                        price_eur=price_eur,
                        updated_at=now
                    )
                    db.session.add(crypto_price)
                    print(f"   ➕ NOUVEAU {our_symbol}: ${price_usd:.2f} / €{price_eur:.2f}")
                
                updated_count += 1
            
            db.session.commit()
            print(f"✅ {updated_count} prix mis à jour avec succès")
            return updated_count
            
        except Exception as e:
            print(f"❌ Erreur mise à jour DB: {e}")
            db.session.rollback()
            return 0
    
    @classmethod
    def run_refresh(cls) -> bool:
        """Point d'entrée principal pour le refresh périodique."""
        print("🚀 REFRESH PÉRIODIQUE DES PRIX CRYPTO")
        print("=" * 50)
        print(f"⏰ Démarré à: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 1. Récupérer les prix Binance
            binance_prices = cls.fetch_all_binance_prices()
            if not binance_prices:
                print("❌ Aucun prix récupéré, arrêt du refresh")
                return False
            
            # 2. Récupérer le taux EUR
            eur_rate = cls.get_usd_to_eur_rate()
            
            # 3. Mettre à jour la base
            updated_count = cls.update_database_prices(binance_prices, eur_rate)
            
            if updated_count > 0:
                print(f"\n🎉 REFRESH TERMINÉ AVEC SUCCÈS!")
                print(f"📊 {updated_count} prix crypto mis à jour")
                return True
            else:
                print("\n⚠️ Refresh terminé sans mise à jour")
                return False
                
        except Exception as e:
            print(f"\n💥 ERREUR CRITIQUE: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Point d'entrée du script."""
    app = create_app()
    
    with app.app_context():
        success = PeriodicCryptoPriceRefresh.run_refresh()
        
        if success:
            print("\n🔚 Script terminé avec succès")
            exit(0)
        else:
            print("\n🔚 Script terminé avec des erreurs")
            exit(1)


if __name__ == '__main__':
    main()