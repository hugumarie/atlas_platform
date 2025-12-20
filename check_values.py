#!/usr/bin/env python3
"""
Script pour vérifier les valeurs exactes en base.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.investor_profile import InvestorProfile

def check_values():
    """Vérifier les valeurs exactes en base."""
    app = create_app()
    
    with app.app_context():
        try:
            profile = InvestorProfile.query.first()
            if profile:
                print(f"📊 Valeurs exactes en base:")
                print(f"  - Total Liquidités: {profile.calculated_total_liquidites}")
                print(f"  - Total Placements: {profile.calculated_total_placements}")
                print(f"  - Total Crypto: {profile.calculated_total_cryptomonnaies}")
                print(f"  - Total Autres Biens: {profile.calculated_total_autres_biens}")
                print(f"  - Total Actifs: {profile.calculated_total_actifs}")
                
                # Calcul manuel pour vérification
                total_manuel = (profile.calculated_total_liquidites or 0) + \
                              (profile.calculated_total_placements or 0) + \
                              (profile.calculated_total_cryptomonnaies or 0) + \
                              (profile.calculated_total_autres_biens or 0)
                
                print(f"\n🧮 Calcul manuel:")
                print(f"  - {profile.calculated_total_liquidites} + {profile.calculated_total_placements} + {profile.calculated_total_cryptomonnaies} + {profile.calculated_total_autres_biens}")
                print(f"  - Total manuel = {total_manuel}")
                print(f"  - Total en base = {profile.calculated_total_actifs}")
                print(f"  - Différence = {profile.calculated_total_actifs - total_manuel}")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_values()