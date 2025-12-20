"""
Service de recalcul local du patrimoine utilisateur.
Utilise UNIQUEMENT les prix en base de données, AUCUN appel API.
"""

from datetime import datetime
from typing import Optional, Dict, List
from app import db
from app.models.crypto_price import CryptoPrice


class LocalPortfolioService:
    """
    Service pour recalculer le patrimoine utilisateur en local.
    Lecture DB uniquement, pas d'appels API externes.
    """
    
    @classmethod
    def get_crypto_price_from_db(cls, symbol: str) -> Optional[float]:
        """
        Récupère le prix d'une crypto depuis la DB uniquement.
        
        Args:
            symbol: Symbole crypto (ex: 'bitcoin', 'ethereum')
            
        Returns:
            Prix EUR ou None si non trouvé
        """
        try:
            crypto_price = CryptoPrice.query.filter_by(symbol=symbol).first()
            return crypto_price.price_eur if crypto_price else None
        except:
            return None
    
    @classmethod
    def get_all_crypto_prices_from_db(cls) -> Dict[str, float]:
        """
        Récupère tous les prix crypto depuis la DB.
        
        Returns:
            Dict {symbol: price_eur}
        """
        try:
            prices = {}
            crypto_prices = CryptoPrice.query.all()
            
            for crypto_price in crypto_prices:
                prices[crypto_price.symbol] = crypto_price.price_eur
            
            return prices
            
        except Exception as e:
            print(f"Erreur récupération prix DB: {e}")
            return {}
    
    @classmethod
    def recalculate_user_crypto_portfolio(cls, user_profile) -> float:
        """
        Recalcule le portefeuille crypto d'un utilisateur avec les prix DB.
        
        Args:
            user_profile: Profil investisseur de l'utilisateur
            
        Returns:
            Total crypto en EUR
        """
        if not user_profile.cryptomonnaies_data:
            return 0.0
        
        total_crypto = 0.0
        now = datetime.utcnow()
        
        # Récupérer tous les prix crypto en une fois
        all_prices = cls.get_all_crypto_prices_from_db()
        
        for crypto in user_profile.cryptomonnaies_data:
            symbol = crypto.get('symbol', '').lower()
            quantity = crypto.get('quantity', 0)
            
            if symbol and quantity > 0 and symbol in all_prices:
                price_eur = all_prices[symbol]
                current_value = quantity * price_eur
                total_crypto += current_value
                
                # Enrichir les données crypto pour l'affichage
                crypto['current_price'] = price_eur
                crypto['calculated_value'] = round(current_value, 2)
                crypto['last_updated'] = now.isoformat()
        
        return total_crypto
    
    @classmethod
    def update_user_calculated_totals(cls, user_profile, save_to_db: bool = True):
        """
        Met à jour tous les totaux calculés d'un utilisateur.
        
        Args:
            user_profile: Profil investisseur
            save_to_db: Si True, sauvegarde en base
        """
        try:
            # 1. Recalcul crypto
            total_crypto = cls.recalculate_user_crypto_portfolio(user_profile)
            user_profile.calculated_total_cryptomonnaies = round(total_crypto, 2)
            
            # 2. Autres totaux patrimoniaux (liquidités, placements, etc.)
            cls._recalculate_other_totals(user_profile)
            
            # 3. Total patrimoine net
            total_actifs = (
                user_profile.calculated_total_liquidites or 0 +
                user_profile.calculated_total_placements or 0 +
                user_profile.calculated_total_immobilier_net or 0 +
                user_profile.calculated_total_cryptomonnaies or 0 +
                user_profile.calculated_total_autres_biens or 0
            )
            
            total_passifs = user_profile.calculated_total_credits_consommation or 0
            
            user_profile.calculated_total_actifs = round(total_actifs, 2)
            user_profile.calculated_patrimoine_total_net = round(total_actifs - total_passifs, 2)
            user_profile.last_calculation_date = datetime.utcnow()
            
            if save_to_db:
                # Sauvegarder les données crypto enrichies
                user_profile.set_cryptomonnaies_data(user_profile.cryptomonnaies_data)
                db.session.commit()
                
        except Exception as e:
            print(f"Erreur recalcul totaux utilisateur: {e}")
            if save_to_db:
                db.session.rollback()
    
    @classmethod
    def _recalculate_other_totals(cls, user_profile):
        """Recalcule les autres totaux patrimoniaux (non-crypto)."""
        try:
            # Liquidités
            total_liquidites = (
                (user_profile.livret_a_value or 0) +
                (user_profile.ldds_value or 0) +
                (user_profile.pel_cel_value or 0) +
                (user_profile.current_savings or 0)
            )
            
            # Ajouter liquidités personnalisées
            if user_profile.liquidites_personnalisees_data:
                for liquidite in user_profile.liquidites_personnalisees_data:
                    total_liquidites += liquidite.get('amount', 0)
            
            user_profile.calculated_total_liquidites = round(total_liquidites, 2)
            
            # Placements financiers
            total_placements = (
                (user_profile.pea_value or 0) +
                (user_profile.per_value or 0) +
                (user_profile.life_insurance_value or 0) +
                (user_profile.cto_value or 0) +
                (user_profile.pee_value or 0)
            )
            
            # Ajouter placements personnalisés
            if user_profile.placements_personnalises_data:
                for placement in user_profile.placements_personnalises_data:
                    total_placements += placement.get('amount', 0)
                    
            user_profile.calculated_total_placements = round(total_placements, 2)
            
            # Immobilier (simplifiée pour l'exemple)
            user_profile.calculated_total_immobilier_net = user_profile.immobilier_value or 0
            
            # Autres biens - calcul depuis autres_biens_data
            total_autres_biens = 0
            if user_profile.autres_biens_data:
                for bien in user_profile.autres_biens_data:
                    total_autres_biens += bien.get('valeur', 0)
            user_profile.calculated_total_autres_biens = round(total_autres_biens, 2)
            
        except Exception as e:
            print(f"Erreur recalcul autres totaux: {e}")
    
    @classmethod
    def refresh_user_portfolio_at_login_DISABLED(cls, user):
        """
        Recalcule le portefeuille utilisateur à la connexion.
        Utilise UNIQUEMENT les prix en DB, pas d'appels API.
        
        Args:
            user: Utilisateur qui se connecte
        """
        try:
            if user.investor_profile:
                print(f"🔄 Recalcul portefeuille {user.first_name} {user.last_name}")
                cls.update_user_calculated_totals(user.investor_profile, save_to_db=True)
                print(f"✅ Portefeuille recalculé")
                
        except Exception as e:
            print(f"❌ Erreur recalcul portefeuille login: {e}")
    
    @classmethod
    def get_portfolio_summary(cls, user_profile) -> Dict:
        """
        Génère un résumé du portefeuille utilisateur.
        
        Returns:
            Dict avec les totaux et détails
        """
        try:
            return {
                'crypto_total': user_profile.calculated_total_cryptomonnaies or 0,
                'liquidites_total': user_profile.calculated_total_liquidites or 0,
                'placements_total': user_profile.calculated_total_placements or 0,
                'immobilier_total': user_profile.calculated_total_immobilier_net or 0,
                'total_actifs': user_profile.calculated_total_actifs or 0,
                'total_passifs': user_profile.calculated_total_credits_consommation or 0,
                'patrimoine_net': user_profile.calculated_patrimoine_total_net or 0,
                'last_updated': user_profile.last_calculation_date
            }
            
        except Exception as e:
            print(f"Erreur génération résumé: {e}")
            return {}