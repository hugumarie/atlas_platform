#!/usr/bin/env python3
"""
Fix crypto simple et direct - Récupération et affichage des prix live
"""

from app import create_app
from app.models.user import User
from app.services.binance_price_service import BinancePriceService

def fix_crypto_live_prices():
    """Fix simple : récupérer et afficher les prix live pour l'utilisateur."""
    
    app = create_app()
    with app.app_context():
        
        print("🚀 FIX CRYPTO SIMPLE ET DIRECT")
        print("=" * 40)
        
        # 1. Identifier l'utilisateur et ses cryptos
        user = User.query.filter_by(email='test.client@gmail.com').first()
        
        if not user or not user.investor_profile:
            print("❌ Utilisateur non trouvé")
            return
            
        cryptos_data = user.investor_profile.cryptomonnaies_data or []
        if not cryptos_data:
            print("❌ Aucune crypto trouvée pour cet utilisateur")
            return
            
        print(f"👤 Utilisateur: {user.first_name} {user.last_name}")
        print(f"📊 Nombre de cryptos: {len(cryptos_data)}")
        
        # 2. Récupérer les prix live depuis Binance
        print("\n💰 RÉCUPÉRATION PRIX LIVE BINANCE")
        print("-" * 35)
        
        # Méthode directe sans base de données
        binance_prices = BinancePriceService.fetch_all_prices()
        
        if not binance_prices:
            print("❌ Impossible de récupérer les prix Binance")
            return
            
        # 3. Calculer et afficher pour chaque crypto de l'utilisateur
        print("\n📈 CALCULS CRYPTO UTILISATEUR")
        print("-" * 30)
        
        total_portfolio = 0
        new_crypto_data = []
        
        for crypto in cryptos_data:
            symbol = crypto.get('symbol', '').lower()
            quantity = crypto.get('quantity', 0)
            
            if symbol in binance_prices:
                live_price = binance_prices[symbol]
                live_value = quantity * live_price
                total_portfolio += live_value
                
                print(f"🪙 {symbol.upper()}:")
                print(f"   Quantité: {quantity}")
                print(f"   Prix live: €{live_price:.2f}")
                print(f"   Valeur: €{live_value:.2f}")
                print()
                
                # Créer la nouvelle donnée enrichie
                new_crypto_data.append({
                    'symbol': symbol,
                    'quantity': quantity,
                    'current_price': live_price,
                    'calculated_value': round(live_value, 2)
                })
            else:
                print(f"⚠️ Prix non trouvé pour {symbol}")
                
        print(f"💳 TOTAL PORTFOLIO: €{total_portfolio:.2f}")
        
        # 4. Sauvegarder les nouvelles données enrichies
        print("\n💾 SAUVEGARDE DES DONNÉES ENRICHIES")
        print("-" * 35)
        
        try:
            # Mettre à jour les données crypto avec les prix live (utiliser la méthode setter)
            user.investor_profile.set_cryptomonnaies_data(new_crypto_data)
            user.investor_profile.calculated_total_cryptomonnaies = round(total_portfolio, 2)
            user.investor_profile.last_calculation_date = datetime.utcnow()
            
            # Sauvegarder
            db.session.commit()
            print("✅ Données sauvegardées avec succès")
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            db.session.rollback()
            
        return new_crypto_data, total_portfolio

if __name__ == '__main__':
    from datetime import datetime
    from app import db
    
    fix_crypto_live_prices()