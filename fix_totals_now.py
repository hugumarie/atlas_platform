#!/usr/bin/env python3
"""
Script pour mettre à jour IMMÉDIATEMENT les totaux corrects en base.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.investor_profile import InvestorProfile

def fix_totals_now():
    """Corriger les totaux maintenant avec les bonnes valeurs."""
    app = create_app()
    
    with app.app_context():
        try:
            profile = InvestorProfile.query.first()
            if profile:
                print(f"🔧 CORRECTION IMMÉDIATE des totaux:")
                
                # Calcul direct des valeurs depuis les données réelles
                total_liquidites = (profile.livret_a_value or 0) + (profile.current_savings or 0)
                if profile.liquidites_personnalisees_data:
                    for liq in profile.liquidites_personnalisees_data:
                        total_liquidites += liq.get('amount', 0)
                
                total_placements = (profile.pea_value or 0) + (profile.cto_value or 0)
                if hasattr(profile, 'immobilier_data') and profile.immobilier_data:
                    for bien in profile.immobilier_data:
                        total_placements += bien.get('amount', 0)
                if profile.placements_personnalises_data:
                    for plc in profile.placements_personnalises_data:
                        total_placements += plc.get('amount', 0)
                
                total_autres_biens = 0
                if profile.autres_biens_data:
                    for bien in profile.autres_biens_data:
                        total_autres_biens += bien.get('valeur', 0)
                
                total_crypto = profile.calculated_total_cryptomonnaies or 0
                total_immobilier = profile.calculated_total_immobilier_net or 0
                
                total_actifs_correct = total_liquidites + total_placements + total_autres_biens + total_crypto + total_immobilier
                total_dettes_correct = profile.calculated_total_credits_consommation or 0
                patrimoine_net_correct = total_actifs_correct - total_dettes_correct
                
                # Mise à jour directe en base
                profile.calculated_total_liquidites = total_liquidites
                profile.calculated_total_placements = total_placements
                profile.calculated_total_autres_biens = total_autres_biens
                profile.calculated_total_actifs = total_actifs_correct
                profile.calculated_patrimoine_total_net = patrimoine_net_correct
                profile.calculated_total_credits_consommation = total_dettes_correct
                
                db.session.commit()
                
                print(f"✅ TOTAUX CORRIGÉS:")
                print(f"  - Total Liquidités: {total_liquidites}€")
                print(f"  - Total Placements: {total_placements}€") 
                print(f"  - Total Autres Biens: {total_autres_biens}€")
                print(f"  - Total Actifs: {total_actifs_correct}€")
                print(f"  - Patrimoine Net: {patrimoine_net_correct}€")
                print(f"  - Total Dettes: {total_dettes_correct}€")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    fix_totals_now()