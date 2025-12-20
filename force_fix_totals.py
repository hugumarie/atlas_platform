#!/usr/bin/env python3
"""
Force la correction des totaux en base MAINTENANT.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.investor_profile import InvestorProfile

def force_fix_totals():
    """Force la correction des totaux."""
    app = create_app()
    
    with app.app_context():
        try:
            profile = InvestorProfile.query.first()
            if profile:
                print(f"🔧 CORRECTION FORCÉE DES TOTAUX EN BASE:")
                
                # Calculer les vrais totaux depuis les données individuelles
                total_liquidites = (profile.livret_a_value or 0)
                if profile.liquidites_personnalisees_json:
                    for liq in profile.liquidites_personnalisees_json:
                        total_liquidites += liq.get('amount', 0)
                
                total_placements = (
                    (profile.pea_value or 0) + 
                    (profile.cto_value or 0) + 
                    (profile.life_insurance_value or 0) + 
                    (profile.per_value or 0) + 
                    (profile.pee_value or 0) + 
                    (profile.scpi_value or 0) + 
                    (profile.private_equity_value or 0)
                )
                
                if profile.placements_personnalises_json:
                    for plc in profile.placements_personnalises_json:
                        total_placements += plc.get('amount', 0)
                
                total_autres_biens = 0
                if profile.autres_biens_data_json:
                    for bien in profile.autres_biens_data_json:
                        total_autres_biens += bien.get('valeur', 0)
                
                total_crypto = profile.calculated_total_cryptomonnaies or 0
                total_immobilier = profile.calculated_total_immobilier_net or 0
                
                total_actifs = total_liquidites + total_placements + total_autres_biens + total_crypto + total_immobilier
                total_dettes = profile.calculated_total_credits_consommation or 0
                patrimoine_net = total_actifs - total_dettes
                
                # Mise à jour directe en base
                profile.calculated_total_liquidites = total_liquidites
                profile.calculated_total_placements = total_placements
                profile.calculated_total_autres_biens = total_autres_biens
                profile.calculated_total_actifs = total_actifs
                profile.calculated_patrimoine_total_net = patrimoine_net
                
                db.session.commit()
                
                print(f"✅ TOTAUX CORRIGÉS EN BASE:")
                print(f"  - Total Liquidités: {total_liquidites}€")
                print(f"  - Total Placements: {total_placements}€")
                print(f"  - Total Autres Biens: {total_autres_biens}€")
                print(f"  - Total Actifs: {total_actifs}€")
                print(f"  - Patrimoine Net: {patrimoine_net}€")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    force_fix_totals()