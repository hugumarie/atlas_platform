#!/usr/bin/env python3
"""
Script final pour corriger définitivement la visualisation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.investor_profile import InvestorProfile
from app.services.patrimoine_calculation import PatrimoineCalculationService

def final_fix():
    """Correction finale avec le service de calcul."""
    app = create_app()
    
    with app.app_context():
        try:
            profile = InvestorProfile.query.first()
            if profile:
                print(f"🔧 CORRECTION FINALE:")
                
                # Utiliser le service de calcul complet
                totaux = PatrimoineCalculationService.calculate_all_totaux(profile, save_to_db=True)
                
                print(f"✅ TOTAUX CALCULÉS ET SAUVÉS:")
                for key, value in totaux.items():
                    print(f"  - {key}: {value}€")
                
                # Vérification finale
                db.session.refresh(profile)
                print(f"\n📊 VÉRIFICATION EN BASE:")
                print(f"  - Liquidités: {profile.calculated_total_liquidites}€")
                print(f"  - Placements: {profile.calculated_total_placements}€")
                print(f"  - Autres biens: {profile.calculated_total_autres_biens}€")
                print(f"  - Total actifs: {profile.calculated_total_actifs}€")
                print(f"  - Patrimoine net: {profile.calculated_patrimoine_total_net}€")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    final_fix()