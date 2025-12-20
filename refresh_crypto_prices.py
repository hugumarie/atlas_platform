#!/usr/bin/env python3
"""
Script de rafraîchissement des prix crypto pour Atlas.
Utilise le BinancePriceService pour les 50 cryptos supportés.

Usage: python refresh_crypto_prices.py
Ou depuis start_atlas.sh (recommandé)
"""

import sys
import os
from datetime import datetime, timedelta

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.services.binance_price_service import BinancePriceService
from app.models.crypto_price import CryptoPrice


class PeriodicCryptoPriceRefresh:
    """Service pour refresh périodique des prix crypto via le BinancePriceService."""
    
    @classmethod
    def run_refresh(cls) -> bool:
        """Point d'entrée principal pour le refresh périodique."""
        print("🚀 REFRESH PRIX CRYPTO ATLAS")
        print("=" * 50)
        print(f"⏰ Démarré: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Utiliser le service Binance centralisé pour tous les 50 cryptos
            print("🔄 Utilisation du BinancePriceService pour les Top 50 cryptos...")
            
            success = BinancePriceService.update_crypto_prices_in_db()
            
            if success:
                # Vérifier les résultats
                total_count = CryptoPrice.query.count()
                recent_count = CryptoPrice.query.filter(
                    CryptoPrice.updated_at >= datetime.utcnow() - timedelta(minutes=5)
                ).count()
                
                print(f"\n✅ REFRESH TERMINÉ AVEC SUCCÈS!")
                print(f"📊 Total cryptos en base: {total_count}")
                print(f"🔄 Prix mis à jour: {recent_count}")
                
                # Test de quelques cryptos principaux
                test_symbols = ['bitcoin', 'ethereum', 'tether', 'binancecoin', 'solana']
                working_count = 0
                
                print(f"\n💰 Vérification Top 5:")
                for symbol in test_symbols:
                    crypto = CryptoPrice.query.filter_by(symbol=symbol).first()
                    if crypto:
                        age = (datetime.utcnow() - crypto.updated_at).total_seconds() / 60
                        print(f"   ✅ {symbol}: €{crypto.price_eur:.2f} (âge: {age:.1f}min)")
                        working_count += 1
                    else:
                        print(f"   ❌ {symbol}: Non trouvé")
                
                success_rate = (working_count / len(test_symbols)) * 100
                print(f"\n📈 Succès: {success_rate:.0f}% ({working_count}/{len(test_symbols)})")
                
                return True
            else:
                print(f"\n❌ ÉCHEC du refresh des prix crypto")
                return False
                
        except Exception as e:
            print(f"\n💥 ERREUR CRITIQUE: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Point d'entrée du script."""
    print("🎯 Atlas Crypto Refresh - Compatible Top 50")
    
    app = create_app()
    
    with app.app_context():
        success = PeriodicCryptoPriceRefresh.run_refresh()
        
        if success:
            print(f"\n🔚 Refresh terminé avec succès")
            print(f"🚀 Atlas peut maintenant être démarré avec les prix crypto à jour")
            exit(0)
        else:
            print(f"\n🔚 Refresh terminé avec des erreurs")
            print(f"⚠️ Atlas peut démarrer mais les prix crypto peuvent être obsolètes")
            exit(1)


if __name__ == '__main__':
    main()