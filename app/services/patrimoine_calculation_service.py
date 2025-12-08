"""
Service de calcul des totaux patrimoniaux.
Calcule et sauvegarde tous les sous-totaux et le total ÉPARGNE & PATRIMOINE.
"""

from app import db
from datetime import datetime


class PatrimoineCalculationService:
    """Service pour calculer tous les totaux patrimoniaux."""
    
    @classmethod
    def calculate_and_save_all_totaux(cls, investor_profile, save_to_db: bool = True):
        """
        Calcule et sauvegarde tous les totaux patrimoniaux.
        
        Args:
            investor_profile: Le profil investisseur
            save_to_db: Si True, sauvegarde en base de données
            
        Returns:
            dict: Dictionnaire avec tous les totaux calculés
        """
        try:
            totaux = {}
            
            # 1. LIQUIDITÉS
            total_liquidites = cls._calculate_total_liquidites(investor_profile)
            investor_profile.calculated_total_liquidites = total_liquidites
            totaux['liquidites'] = total_liquidites
            
            # 2. PLACEMENTS FINANCIERS  
            total_placements = cls._calculate_total_placements(investor_profile)
            investor_profile.calculated_total_placements = total_placements
            totaux['placements'] = total_placements
            
            # 3. IMMOBILIER NET (garder la valeur existante, ne pas recalculer)
            total_immobilier = investor_profile.calculated_total_immobilier_net or 0
            # Ne pas modifier la valeur existante: investor_profile.calculated_total_immobilier_net = total_immobilier
            totaux['immobilier'] = total_immobilier
            
            # 4. CRYPTOMONNAIES (garder valeur existante si calculée récemment)
            total_cryptos = cls._calculate_total_cryptomonnaies(investor_profile)
            investor_profile.calculated_total_cryptomonnaies = total_cryptos
            totaux['cryptomonnaies'] = total_cryptos
            
            # 5. AUTRES BIENS
            total_autres_biens = cls._calculate_total_autres_biens(investor_profile)
            investor_profile.calculated_total_autres_biens = total_autres_biens
            totaux['autres_biens'] = total_autres_biens
            
            # 6. TOTAL ÉPARGNE & PATRIMOINE (somme de tous les actifs)
            total_actifs = (
                total_liquidites +
                total_placements + 
                total_immobilier +
                total_cryptos +
                total_autres_biens
            )
            investor_profile.calculated_total_actifs = total_actifs
            totaux['total_actifs'] = total_actifs
            
            # 7. TOTAL CRÉDITS (passifs)
            total_credits = cls._calculate_total_credits(investor_profile)
            investor_profile.calculated_total_credits_consommation = total_credits
            totaux['total_credits'] = total_credits
            
            # 8. PATRIMOINE NET TOTAL (actifs - passifs)
            patrimoine_net = total_actifs - total_credits
            investor_profile.calculated_patrimoine_total_net = patrimoine_net
            totaux['patrimoine_net'] = patrimoine_net
            
            # Horodatage
            investor_profile.last_calculation_date = datetime.utcnow()
            
            if save_to_db:
                db.session.commit()
                
            return totaux
            
        except Exception as e:
            print(f"Erreur calcul patrimoine: {e}")
            if save_to_db:
                db.session.rollback()
            return None
    
    @classmethod
    def _calculate_total_liquidites(cls, profile):
        """Calcule le total des liquidités."""
        total = 0
        
        # Comptes épargne classiques
        total += profile.livret_a_value or 0
        total += profile.ldds_value or 0
        total += profile.pel_cel_value or 0
        total += profile.current_savings or 0
        
        # Liquidités personnalisées
        if profile.liquidites_personnalisees_data:
            for liquidite in profile.liquidites_personnalisees_data:
                total += liquidite.get('amount', 0)
                
        return round(total, 2)
    
    @classmethod
    def _calculate_total_placements(cls, profile):
        """Calcule le total des placements financiers."""
        total = 0
        
        # Placements classiques
        total += profile.pea_value or 0
        total += profile.per_value or 0
        total += profile.life_insurance_value or 0
        total += profile.cto_value or 0
        total += profile.pee_value or 0
        
        # Placements personnalisés
        if profile.placements_personnalises_data:
            for placement in profile.placements_personnalises_data:
                total += placement.get('amount', 0)
                
        return round(total, 2)
    
    @classmethod
    def _calculate_total_immobilier(cls, profile):
        """Utilise la valeur immobilier net déjà calculée en base de données."""
        # Utiliser la valeur déjà calculée et stockée en base
        return profile.calculated_total_immobilier_net or 0
    
    @classmethod
    def _calculate_total_cryptomonnaies(cls, profile):
        """Calcule le total des cryptomonnaies."""
        # Garder la valeur déjà calculée si elle existe et est récente
        if profile.calculated_total_cryptomonnaies:
            return profile.calculated_total_cryptomonnaies
            
        # Sinon calculer depuis les données crypto
        total = 0
        if profile.cryptomonnaies_data:
            for crypto in profile.cryptomonnaies_data:
                if 'calculated_value' in crypto:
                    total += crypto['calculated_value']
                    
        return round(total, 2)
    
    @classmethod
    def _calculate_total_autres_biens(cls, profile):
        """Calcule le total des autres biens."""
        total = 0
        
        if profile.autres_biens_data:
            for bien in profile.autres_biens_data:
                total += bien.get('valeur', 0)
                
        return round(total, 2)
    
    @classmethod
    def _calculate_total_credits(cls, profile):
        """Calcule le total des crédits (hors immobilier)."""
        total = 0
        
        if profile.credits_data:
            for credit in profile.credits_data:
                total += credit.get('montant_restant', credit.get('montant_initial', 0))
                
        return round(total, 2)