#!/usr/bin/env python3
"""
Script de mise à jour des prix crypto via l'API Binance.
À lancer régulièrement (cron, scheduler, etc.) pour maintenir les prix à jour.

Usage:
    python scripts/update_crypto_prices.py
"""

import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.services.binance_price_service import BinancePriceService


def main():
    """Point d'entrée principal du script."""
    
    print(f"🚀 MISE À JOUR DES PRIX CRYPTO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Créer le contexte Flask
    app = create_app()
    
    with app.app_context():
        try:
            print("📡 Récupération des prix depuis l'API Binance...")
            
            # Lancer la mise à jour
            success = BinancePriceService.update_crypto_prices_in_db()
            
            if success:
                print("✅ Succès ! Prix crypto mis à jour en base de données")
                
                # Afficher quelques exemples pour vérification
                print("\n📊 Vérification - Quelques prix récupérés :")
                important_cryptos = ['bitcoin', 'ethereum', 'binancecoin', 'solana']
                
                for crypto in important_cryptos:
                    price = BinancePriceService.get_crypto_price_from_db(crypto, max_age_minutes=1)
                    if price:
                        print(f"   💰 {crypto.upper():<12}: {price:>10,.2f}€")
                
                # Afficher le nombre total de cryptos supportés
                supported = BinancePriceService.get_supported_symbols()
                print(f"\n📈 Total cryptomonnaies supportées : {len(supported)}")
                
                print(f"\n🕐 Mise à jour terminée : {datetime.now().strftime('%H:%M:%S')}")
                return 0
                
            else:
                print("❌ Échec de la mise à jour des prix crypto")
                return 1
                
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour : {e}")
            import traceback
            traceback.print_exc()
            return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)