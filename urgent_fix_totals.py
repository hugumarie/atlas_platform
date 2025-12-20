#!/usr/bin/env python3
"""
CORRECTION URGENTE - Forcer les totaux corrects en base de données
"""
import sys
import os

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app, db
    from app.models.investor_profile import InvestorProfile
    from app.services.patrimoine_calculation import PatrimoineCalculationService
    
    def urgent_fix():
        app = create_app()
        
        with app.app_context():
            try:
                # Récupérer le premier profil
                profile = InvestorProfile.query.first()
                if not profile:
                    print("❌ Aucun profil trouvé")
                    return
                
                print("🔧 CORRECTION URGENTE des totaux en base")
                print(f"📋 Profil ID: {profile.id}")
                
                # Afficher les valeurs actuelles
                print(f"\n📊 AVANT CORRECTION:")
                print(f"  - Liquidités DB: {profile.calculated_total_liquidites}€")
                print(f"  - Placements DB: {profile.calculated_total_placements}€") 
                print(f"  - Autres biens DB: {profile.calculated_total_autres_biens}€")
                print(f"  - Total actifs DB: {profile.calculated_total_actifs}€")
                
                # Calculer les vrais totaux avec le service
                print(f"\n🧮 CALCUL AVEC SERVICE...")
                totaux = PatrimoineCalculationService.calculate_all_totaux(profile, save_to_db=True)
                
                print(f"\n✅ TOTAUX CALCULÉS:")
                for cle, valeur in totaux.items():
                    print(f"  - {cle}: {valeur}€")
                
                # Vérifier la sauvegarde
                db.session.refresh(profile)
                print(f"\n📊 VÉRIFICATION FINALE:")
                print(f"  - Liquidités DB: {profile.calculated_total_liquidites}€")
                print(f"  - Placements DB: {profile.calculated_total_placements}€")
                print(f"  - Autres biens DB: {profile.calculated_total_autres_biens}€") 
                print(f"  - Total actifs DB: {profile.calculated_total_actifs}€")
                print(f"  - Patrimoine net DB: {profile.calculated_patrimoine_total_net}€")
                
                print(f"\n🎯 CORRECTION TERMINÉE!")
                
            except Exception as e:
                print(f"❌ ERREUR: {e}")
                import traceback
                traceback.print_exc()
    
    if __name__ == "__main__":
        urgent_fix()
        
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Essayez de démarrer l'application Flask d'abord")
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()