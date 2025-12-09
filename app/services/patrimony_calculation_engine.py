"""
Service central de calcul patrimonial - PatrimonyCalculationEngine
Gère TOUS les calculs de totaux avec sauvegarde automatique en base de données.

Formules:
- TOTAL ÉPARGNE & PATRIMOINE = Liquidités + Placements + Immobilier Net + Cryptos + Autres Biens  
- PATRIMOINE TOTAL NET = TOTAL ÉPARGNE & PATRIMOINE - Crédits
"""

from app import db
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
import traceback
from app.services.credit_calculation import CreditCalculationService


class PatrimonyCalculationEngine:
    """Service central pour tous les calculs patrimoniaux."""
    
    @classmethod
    def calculate_and_save_all(cls, investor_profile, force_recalculate=False, save_to_db=True):
        """
        Calcule et sauvegarde TOUS les totaux patrimoniaux.
        
        Args:
            investor_profile: Le profil investisseur
            force_recalculate: Si True, force le recalcul même si les valeurs existent
            save_to_db: Si True, sauvegarde en base de données
            
        Returns:
            dict: Tous les totaux calculés
        """
        try:
            results = {}
            
            
            # 1. LIQUIDITÉS
            total_liquidites = cls._calculate_liquidites(investor_profile)
            investor_profile.calculated_total_liquidites = total_liquidites
            results['liquidites'] = float(total_liquidites)
            
            # 2. PLACEMENTS FINANCIERS
            total_placements = cls._calculate_placements_financiers(investor_profile)
            investor_profile.calculated_total_placements = total_placements
            results['placements_financiers'] = float(total_placements)
            
            # 3. PATRIMOINE IMMOBILIER NET - calculer correctement avec capital restant
            patrimoine_immobilier_net = cls._calculate_patrimoine_immobilier_net_correct(investor_profile)
            investor_profile.calculated_total_immobilier_net = patrimoine_immobilier_net
            results['patrimoine_immobilier_net'] = float(patrimoine_immobilier_net)
            
            # 4. TOTAL CRYPTOMONNAIES
            total_cryptos = cls._calculate_total_cryptomonnaies(investor_profile)
            investor_profile.calculated_total_cryptomonnaies = total_cryptos
            results['total_cryptomonnaies'] = float(total_cryptos)
            
            # 5. TOTAL AUTRES BIENS
            total_autres_biens = cls._calculate_total_autres_biens(investor_profile)
            investor_profile.calculated_total_autres_biens = total_autres_biens
            results['total_autres_biens'] = float(total_autres_biens)
            
            # 6. TOTAL ÉPARGNE & PATRIMOINE (FORMULE PRINCIPALE)
            total_epargne_patrimoine = (
                total_liquidites +
                total_placements +
                patrimoine_immobilier_net +
                total_cryptos +
                total_autres_biens
            )
            investor_profile.calculated_total_actifs = total_epargne_patrimoine
            results['total_epargne_patrimoine'] = float(total_epargne_patrimoine)
            
            # 7. MONTANT CRÉDITS À REMBOURSER
            total_credits = cls._calculate_total_credits(investor_profile)
            investor_profile.calculated_total_credits_consommation = total_credits
            results['total_credits'] = float(total_credits)
            
            # 8. PATRIMOINE TOTAL NET (FORMULE FINALE)
            patrimoine_total_net = total_epargne_patrimoine - total_credits
            investor_profile.calculated_patrimoine_total_net = patrimoine_total_net
            results['patrimoine_total_net'] = float(patrimoine_total_net)
            
            # Horodatage
            investor_profile.last_calculation_date = datetime.utcnow()
            
            if save_to_db:
                db.session.commit()
            
            return results
            
        except Exception as e:
            if save_to_db:
                db.session.rollback()
            return None
    
    @classmethod
    def _calculate_liquidites(cls, profile):
        """Calcule Total Liquidités."""
        total = Decimal('0')
        
        # Comptes épargne réglementés
        total += Decimal(str(profile.livret_a_value or 0))
        total += Decimal(str(profile.ldds_value or 0))
        total += Decimal(str(profile.pel_cel_value or 0))
        
        # Épargne courante
        total += Decimal(str(profile.current_savings or 0))
        
        # Liquidités personnalisées
        if profile.liquidites_personnalisees_data:
            for liquidite in profile.liquidites_personnalisees_data:
                montant = liquidite.get('amount', 0)
                total += Decimal(str(montant))
        
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @classmethod
    def _calculate_placements_financiers(cls, profile):
        """Calcule Total Placements Financiers."""
        total = Decimal('0')
        
        # Placements réglementés
        total += Decimal(str(profile.pea_value or 0))
        total += Decimal(str(profile.per_value or 0))
        total += Decimal(str(profile.life_insurance_value or 0))
        total += Decimal(str(profile.cto_value or 0))
        total += Decimal(str(profile.pee_value or 0))
        
        # Placements personnalisés
        if profile.placements_personnalises_data:
            for placement in profile.placements_personnalises_data:
                montant = placement.get('amount', 0)
                total += Decimal(str(montant))
        
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @classmethod
    def _calculate_patrimoine_immobilier_net(cls, profile):
        """Calcule Patrimoine Immobilier Net (valeur - crédits immobiliers)."""
        valeur_totale = Decimal('0')
        credits_immobiliers = Decimal('0')
        
        if profile.immobilier_data:
            for bien in profile.immobilier_data:
                # Valeur du bien
                valeur_bien = Decimal(str(bien.get('valeur', 0)))
                valeur_totale += valeur_bien
                
                # Crédit associé au bien
                if bien.get('has_credit', False):
                    montant_credit = Decimal(str(bien.get('credit_montant', 0)))
                    credits_immobiliers += montant_credit
        else:
            # Fallback sur valeur simple
            valeur_totale = Decimal(str(profile.immobilier_value or 0))
        
        patrimoine_net = valeur_totale - credits_immobiliers
        return patrimoine_net.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @classmethod
    def _calculate_patrimoine_immobilier_net_correct(cls, profile):
        """
        Calcule Patrimoine Immobilier Net avec le capital restant RÉEL des crédits.
        
        Utilise CreditCalculationService pour calculer le capital restant après 
        déduction des mensualités déjà payées.
        """
        valeur_totale = Decimal('0')
        capital_restant_total = Decimal('0')
        
        
        if profile.immobilier_data:
            for i, bien in enumerate(profile.immobilier_data):
                # Valeur du bien
                valeur_bien = Decimal(str(bien.get('valeur', 0)))
                valeur_totale += valeur_bien
                
                # Si le bien a un crédit associé
                if bien.get('has_credit', False):
                    montant_initial = float(bien.get('credit_montant', 0))
                    taux_interet = float(bien.get('credit_taeg', 0))  # Utiliser credit_taeg au lieu de credit_taux
                    duree_annees = int(bien.get('credit_duree', 0))  # En années dans la base
                    duree_mois = duree_annees * 12  # Conversion en mois
                    
                    # Parse de la date de début du crédit
                    date_debut_str = bien.get('credit_date', '')  # Utiliser credit_date
                    try:
                        # Essayer différents formats de date
                        if date_debut_str:
                            if '-' in date_debut_str and len(date_debut_str) >= 7:
                                # Format YYYY-MM ou YYYY-MM-DD
                                date_debut = datetime.strptime(date_debut_str[:7] + '-01', '%Y-%m-%d').date()
                            elif '/' in date_debut_str:
                                # Format MM/YYYY
                                parts = date_debut_str.split('/')
                                if len(parts) == 2:
                                    month, year = parts
                                    date_debut = datetime.strptime(f'{year}-{month.zfill(2)}-01', '%Y-%m-%d').date()
                                else:
                                    date_debut = date.today()
                            else:
                                date_debut = date.today()
                        else:
                            date_debut = date.today()
                    except (ValueError, TypeError):
                        date_debut = date.today()
                    
                    # Calcul du capital restant avec service existant
                    if montant_initial > 0 and duree_mois > 0:
                        capital_restant_reel = CreditCalculationService.calculate_remaining_capital(
                            principal=montant_initial,
                            annual_rate=taux_interet,
                            duration_months=duree_mois,
                            start_date=date_debut,
                            current_date=date.today()
                        )
                        
                        capital_restant_total += Decimal(str(capital_restant_reel))
        else:
            # Fallback sur valeur simple
            valeur_totale = Decimal(str(profile.immobilier_value or 0))
        
        # Calcul final
        patrimoine_net = valeur_totale - capital_restant_total
        
        return patrimoine_net.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @classmethod 
    def _calculate_total_cryptomonnaies(cls, profile):
        """Calcule Total Cryptomonnaies avec prix en base de données."""
        total = Decimal('0')
        
        if profile.cryptomonnaies_data:
            # Récupérer les prix depuis la base de données
            prix_cryptos = cls._get_crypto_prices_from_db()
            
            # Travailler sur une copie modifiable
            cryptos_updated = []
            for crypto in profile.cryptomonnaies_data:
                # Créer une copie de la crypto
                crypto_copy = dict(crypto)
                symbol = crypto_copy.get('symbol', '').lower()
                quantity = Decimal(str(crypto_copy.get('quantity', 0)))
                
                if quantity > 0 and symbol in prix_cryptos:
                    price_eur = Decimal(str(prix_cryptos[symbol]))
                    valeur_calculee = quantity * price_eur
                    
                    # Mettre à jour la copie avec la valeur calculée
                    crypto_copy['current_price'] = float(price_eur)
                    crypto_copy['calculated_value'] = float(valeur_calculee)
                    crypto_copy['last_updated'] = datetime.utcnow().isoformat()
                    
                    total += valeur_calculee
                
                cryptos_updated.append(crypto_copy)
            
            # Sauvegarder immédiatement les cryptos mises à jour
            profile.set_cryptomonnaies_data(cryptos_updated)
        
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @classmethod
    def _get_crypto_prices_from_db(cls):
        """Récupère les prix crypto depuis la base de données."""
        try:
            from app.models.crypto_price import CryptoPrice
            
            prix_cryptos = {}
            crypto_prices = CryptoPrice.query.all()
            
            # Mapping des symboles
            symbol_mapping = {
                'bitcoin': ['btc', 'bitcoin'],
                'ethereum': ['eth', 'ethereum'], 
                'binancecoin': ['bnb', 'binancecoin'],
                'solana': ['sol', 'solana'],
                'cardano': ['ada', 'cardano'],
                'ripple': ['xrp', 'ripple'],
                'polkadot': ['dot', 'polkadot'],
                'chainlink': ['link', 'chainlink'],
                'litecoin': ['ltc', 'litecoin'],
                'avalanche-2': ['avax', 'avalanche-2'],
                'matic-network': ['matic', 'matic-network'],
                'cosmos': ['atom', 'cosmos'],
                'uniswap': ['uni', 'uniswap'],
                'tether': ['usdt', 'tether'],
                'usd-coin': ['usdc', 'usd-coin']
            }
            
            for crypto_price in crypto_prices:
                crypto_id = crypto_price.symbol
                price_eur = crypto_price.price_eur
                
                # Ajouter tous les alias possibles pour cette crypto
                if crypto_id in symbol_mapping:
                    for alias in symbol_mapping[crypto_id]:
                        prix_cryptos[alias] = price_eur
                        
            return prix_cryptos
            
        except Exception as e:
            return {}
    
    @classmethod
    def _calculate_total_autres_biens(cls, profile):
        """Calcule Total Autres Biens."""
        total = Decimal('0')
        
        if profile.autres_biens_data:
            for bien in profile.autres_biens_data:
                valeur = bien.get('valeur', 0)
                total += Decimal(str(valeur))
        
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @classmethod
    def _calculate_total_credits(cls, profile):
        """Calcule Total Crédits à rembourser (hors immobilier)."""
        total = Decimal('0')
        
        if profile.credits_data:
            for credit in profile.credits_data:
                montant_restant = credit.get('montant_restant', credit.get('montant_initial', 0))
                total += Decimal(str(montant_restant))
        
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @classmethod
    def refresh_user_totals(cls, user):
        """
        Point d'entrée principal pour rafraîchir tous les totaux d'un utilisateur.
        """
        if user and user.investor_profile:
            return cls.calculate_and_save_all(
                user.investor_profile, 
                force_recalculate=True,
                save_to_db=True
            )
        return None
    
