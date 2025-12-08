"""
Scheduler intégré pour les tâches automatiques.
Se lance automatiquement avec Flask.
"""

import threading
import time
from datetime import datetime
from flask import current_app

def update_crypto_prices():
    """Met à jour les prix crypto depuis Binance et recalcule les patrimoines."""
    try:
        from app.models.user import User
        from app.services.patrimoine_calculation import PatrimoineCalculationService
        from app.services.binance_price_service import BinancePriceService
        from app import db
        
        with current_app.app_context():
            print(f"🕐 Mise à jour crypto automatique (Binance) - {datetime.now().strftime('%H:%M:%S')}")
            
            # Étape 1: Mettre à jour tous les prix crypto en base depuis Binance
            print(f"📊 Mise à jour des prix crypto en base...")
            success = BinancePriceService.update_crypto_prices_in_db()
            
            if not success:
                print(f"❌ Échec mise à jour prix Binance")
                return
            
            # Étape 2: Recalculer les patrimoines de tous les utilisateurs avec crypto
            users_with_crypto = User.query.join(User.investor_profile)\
                .filter(User.investor_profile.has())\
                .filter(User.is_admin == False)\
                .all()
            
            updated_count = 0
            
            for user in users_with_crypto:
                if user.investor_profile and user.investor_profile.cryptomonnaies_data:
                    try:
                        # Recalculer et sauvegarder avec les nouveaux prix (forcer l'enrichissement pour la visualisation)
                        PatrimoineCalculationService.calculate_all_totaux(
                            user.investor_profile, 
                            save_to_db=True,
                            force_crypto_update=True  # Forcer la mise à jour pour enrichir les données
                        )
                        updated_count += 1
                        
                    except Exception as e:
                        print(f"❌ Erreur pour {user.email}: {e}")
                        continue
            
            print(f"✅ Mise à jour crypto terminée : {updated_count} profils")
            
    except Exception as e:
        print(f"❌ Erreur mise à jour crypto: {e}")

def crypto_scheduler():
    """Thread qui lance la mise à jour crypto toutes les heures."""
    while True:
        try:
            # Attendre 1 heure (3600 secondes)
            time.sleep(3600)
            update_crypto_prices()
            
        except Exception as e:
            print(f"❌ Erreur scheduler crypto: {e}")
            # En cas d'erreur, attendre 10 minutes avant de réessayer
            time.sleep(600)

def start_scheduler(app):
    """Démarre le scheduler en arrière-plan."""
    print("🚀 Démarrage du scheduler crypto (mise à jour toutes les heures)")
    
    # Lancer le thread du scheduler
    scheduler_thread = threading.Thread(target=crypto_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Première mise à jour après 5 minutes (laisser le temps à Flask de démarrer)
    def delayed_first_update():
        time.sleep(300)  # 5 minutes
        print("🎯 Première mise à jour crypto au démarrage")
        update_crypto_prices()
    
    first_update_thread = threading.Thread(target=delayed_first_update, daemon=True)
    first_update_thread.start()