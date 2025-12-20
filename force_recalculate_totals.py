#!/usr/bin/env python3
"""
Script pour forcer le recalcul des totaux patrimoniaux.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.investor_profile import InvestorProfile
from app.services.patrimoine_calculation import PatrimoineCalculationService

def force_recalculate_all():
    """Force le recalcul de tous les totaux patrimoniaux."""
    app = create_app()
    
    with app.app_context():
        try:
            # Récupérer tous les profils
            profiles = InvestorProfile.query.all()
            print(f"🔄 Recalcul forcé des totaux pour {len(profiles)} profil(s)")
            
            for profile in profiles:
                print(f"\n📊 Profil utilisateur ID: {profile.user_id}")
                print(f"  - Avant: Total Liquidités = {profile.calculated_total_liquidites}€")
                print(f"  - Avant: Total Placements = {profile.calculated_total_placements}€")
                print(f"  - Avant: Total Autres Biens = {profile.calculated_total_autres_biens}€")
                print(f"  - Avant: Total Actifs = {profile.calculated_total_actifs}€")
                print(f"  - Avant: Patrimoine Net = {profile.calculated_patrimoine_total_net}€")
                
                # Forcer le recalcul
                totaux = PatrimoineCalculationService.calculate_all_totaux(profile, save_to_db=True)
                
                print(f"  - Après: Total Liquidités = {totaux['total_liquidites']}€")
                print(f"  - Après: Total Placements = {totaux['total_placements']}€")
                print(f"  - Après: Total Autres Biens = {totaux['total_autres_biens']}€")
                print(f"  - Après: Total Actifs = {totaux['total_actifs']}€")
                print(f"  - Après: Patrimoine Net = {totaux['patrimoine_total_net']}€")
                
            print(f"\n✅ Recalcul terminé pour tous les profils")
            
        except Exception as e:
            print(f"❌ Erreur lors du recalcul: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    force_recalculate_all()