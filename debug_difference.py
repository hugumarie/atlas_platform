#!/usr/bin/env python3
"""
Script pour débugger la différence d'1€.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.investor_profile import InvestorProfile

def debug_difference():
    """Débugger la différence d'1€."""
    app = create_app()
    
    with app.app_context():
        try:
            profile = InvestorProfile.query.first()
            if profile:
                print(f"🔍 ANALYSE DÉTAILLÉE DES TOTAUX:")
                print(f"\n📊 Valeurs brutes en base:")
                print(f"  - calculated_total_actifs = {profile.calculated_total_actifs} (type: {type(profile.calculated_total_actifs)})")
                
                # Test des différents arrondis
                actifs_raw = profile.calculated_total_actifs or 0
                print(f"\n🧮 Tests d'arrondi sur {actifs_raw}:")
                print(f"  - round(actifs_raw, 0) = {round(actifs_raw, 0)}")
                print(f"  - int(round(actifs_raw, 0)) = {int(round(actifs_raw, 0))}")
                print(f"  - format(actifs_raw, '.0f') = {actifs_raw:.0f}")
                print(f"  - '{:,.0f}'.format(actifs_raw) = {actifs_raw:,.0f}")
                
                # Vérifier les composants individuels
                print(f"\n📋 Composants individuels:")
                print(f"  - Total Liquidités: {profile.calculated_total_liquidites}")
                print(f"  - Total Placements: {profile.calculated_total_placements}")
                print(f"  - Total Immobilier: {profile.calculated_total_immobilier_net}")
                print(f"  - Total Cryptos: {profile.calculated_total_cryptomonnaies}")
                print(f"  - Total Autres Biens: {profile.calculated_total_autres_biens}")
                
                # Calcul manuel des composants
                total_manuel = (
                    (profile.calculated_total_liquidites or 0) +
                    (profile.calculated_total_placements or 0) +
                    (profile.calculated_total_immobilier_net or 0) +
                    (profile.calculated_total_cryptomonnaies or 0) +
                    (profile.calculated_total_autres_biens or 0)
                )
                
                print(f"\n➕ Calcul manuel total:")
                print(f"  - Manuel: {total_manuel}")
                print(f"  - En base: {profile.calculated_total_actifs}")
                print(f"  - Différence: {abs(total_manuel - (profile.calculated_total_actifs or 0))}")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_difference()