"""
Service centralisé pour le calcul et la sauvegarde de tous les totaux patrimoniaux.
Gère les liquidités, placements, immobilier, cryptos, autres biens et patrimoine net.
"""

from typing import Dict, List, Optional
from datetime import datetime, date
from app import db
from app.models.investor_profile import InvestorProfile
from app.services.credit_calculation import CreditCalculationService
from app.services.binance_price_service import BinancePriceService


class PatrimoineCalculationService:
    """
    Service centralisé pour tous les calculs patrimoniaux.
    Sauvegarde tous les totaux calculés en base de données.
    """
    
    # Le service crypto est maintenant géré par BinancePriceService
    
    @classmethod
    def calculate_all_totaux(cls, investor_profile: InvestorProfile, save_to_db: bool = True, force_crypto_update: bool = False) -> Dict:
        """
        Calcule tous les totaux patrimoniaux et les sauvegarde en base.
        
        Args:
            investor_profile: Profil investisseur
            save_to_db: Si True, sauvegarde les résultats en base
            force_crypto_update: Si True, force la mise à jour des prix crypto via API
            
        Returns:
            Dict: Tous les totaux calculés
        """
        try:
            results = {}
            
            # 1. Calcul des liquidités
            results['total_liquidites'] = cls._calculate_total_liquidites(investor_profile)
            
            # 2. Calcul des placements financiers
            results['total_placements'] = cls._calculate_total_placements(investor_profile)
            
            # 3. Calcul de l'immobilier net
            results['total_immobilier_net'] = cls._calculate_total_immobilier_net(investor_profile)
            
            # 4. Calcul des cryptomonnaies (avec ou sans mise à jour API)
            if force_crypto_update:
                results['total_cryptomonnaies'] = cls._calculate_total_cryptomonnaies(investor_profile)
                # Sauvegarder immédiatement les données enrichies
                if save_to_db:
                    cls._save_crypto_data_to_db(investor_profile)
            else:
                # Utiliser les valeurs déjà en base ou calculer sans API
                results['total_cryptomonnaies'] = cls._calculate_total_cryptomonnaies_cached(investor_profile)
            
            # 5. Calcul des autres biens
            results['total_autres_biens'] = cls._calculate_total_autres_biens(investor_profile)
            
            # 6. Calcul des crédits de consommation
            results['total_credits_consommation'] = cls._calculate_total_credits_consommation(investor_profile)
            
            # 7. Calcul du patrimoine total net
            total_actifs = (
                results['total_liquidites'] +
                results['total_placements'] +
                results['total_immobilier_net'] +
                results['total_cryptomonnaies'] +
                results['total_autres_biens']
            )
            
            results['total_actifs'] = total_actifs
            results['patrimoine_total_net'] = total_actifs - results['total_credits_consommation']
            
            # Sauvegarde en base de données
            if save_to_db:
                cls._save_totaux_to_db(investor_profile, results)
            
            return results
            
        except Exception as e:
            print(f"Erreur lors du calcul des totaux: {e}")
            return cls._get_default_totaux()
    
    @classmethod
    def _calculate_total_liquidites(cls, investor_profile: InvestorProfile) -> float:
        """Calcule le total des liquidités."""
        total = 0.0
        
        # Liquidités standards - vérifier que les attributs existent
        if hasattr(investor_profile, 'has_livret_a') and investor_profile.has_livret_a and hasattr(investor_profile, 'livret_a_value') and investor_profile.livret_a_value:
            total += investor_profile.livret_a_value
            
        if hasattr(investor_profile, 'has_ldds') and investor_profile.has_ldds and hasattr(investor_profile, 'ldds_value') and investor_profile.ldds_value:
            total += investor_profile.ldds_value
            
        if hasattr(investor_profile, 'has_pel_cel') and investor_profile.has_pel_cel and hasattr(investor_profile, 'pel_cel_value') and investor_profile.pel_cel_value:
            total += investor_profile.pel_cel_value
            
        if hasattr(investor_profile, 'has_autres_livrets') and investor_profile.has_autres_livrets and hasattr(investor_profile, 'autres_livrets_value') and investor_profile.autres_livrets_value:
            total += investor_profile.autres_livrets_value
        
        # Liquidités personnalisées
        if investor_profile.liquidites_personnalisees_data:
            for liquidite in investor_profile.liquidites_personnalisees_data:
                total += liquidite.get('amount', 0)
        
        return round(total, 2)
    
    @classmethod
    def _calculate_total_placements(cls, investor_profile: InvestorProfile) -> float:
        """Calcule le total des placements financiers."""
        total = 0.0
        
        # Placements standards - vérifier que les attributs existent
        if hasattr(investor_profile, 'has_pea') and investor_profile.has_pea and hasattr(investor_profile, 'pea_value') and investor_profile.pea_value:
            total += investor_profile.pea_value
            
        if hasattr(investor_profile, 'has_per') and investor_profile.has_per and hasattr(investor_profile, 'per_value') and investor_profile.per_value:
            total += investor_profile.per_value
            
        if hasattr(investor_profile, 'has_life_insurance') and investor_profile.has_life_insurance and hasattr(investor_profile, 'life_insurance_value') and investor_profile.life_insurance_value:
            total += investor_profile.life_insurance_value
            
        if hasattr(investor_profile, 'has_pee') and investor_profile.has_pee and hasattr(investor_profile, 'pee_value') and investor_profile.pee_value:
            total += investor_profile.pee_value
            
        if hasattr(investor_profile, 'has_scpi') and investor_profile.has_scpi and hasattr(investor_profile, 'scpi_value') and investor_profile.scpi_value:
            total += investor_profile.scpi_value
            
        if hasattr(investor_profile, 'has_cto') and investor_profile.has_cto and hasattr(investor_profile, 'cto_value') and investor_profile.cto_value:
            total += investor_profile.cto_value
            
        if hasattr(investor_profile, 'has_private_equity') and investor_profile.has_private_equity and hasattr(investor_profile, 'private_equity_value') and investor_profile.private_equity_value:
            total += investor_profile.private_equity_value
            
        if hasattr(investor_profile, 'has_crowdfunding') and investor_profile.has_crowdfunding and hasattr(investor_profile, 'crowdfunding_value') and investor_profile.crowdfunding_value:
            total += investor_profile.crowdfunding_value
        
        # Placements personnalisés
        if investor_profile.placements_personnalises_data:
            for placement in investor_profile.placements_personnalises_data:
                total += placement.get('amount', 0)
        
        return round(total, 2)
    
    @classmethod
    def _calculate_total_immobilier_net(cls, investor_profile: InvestorProfile) -> float:
        """Calcule le total de l'immobilier net (valeur - crédits immobiliers)."""
        total = 0.0
        
        if investor_profile.immobilier_data:
            for bien in investor_profile.immobilier_data:
                valeur = bien.get('valeur', 0)
                
                # Soustraction du crédit immobilier s'il existe
                if bien.get('has_credit', False):
                    # Récupération des données de crédit immobilier
                    credit_initial = bien.get('credit_montant', 0)
                    credit_taux = bien.get('credit_tag', 0)  # Dans immobilier_data c'est 'credit_tag' pas 'credit_taux'
                    credit_duree_annees = bien.get('credit_duree', 0)  # En années
                    credit_duree_mois = credit_duree_annees * 12 if credit_duree_annees else 0
                    credit_date_debut = bien.get('credit_date', '')  # Dans immobilier_data c'est 'credit_date'
                    
                    if all([credit_initial, credit_duree_mois, credit_date_debut]):
                        try:
                            # Parse de la date (format 2025-10)
                            if isinstance(credit_date_debut, str) and len(credit_date_debut) == 7:
                                year, month = credit_date_debut.split('-')
                                start_date = date(int(year), int(month), 1)
                            elif isinstance(credit_date_debut, str):
                                start_date = datetime.strptime(credit_date_debut, '%Y-%m-%d').date()
                            else:
                                start_date = credit_date_debut
                            
                            # Calcul dynamique pour tous les cas
                            capital_restant = CreditCalculationService.calculate_remaining_capital(
                                credit_initial, credit_taux, credit_duree_mois, start_date
                            )
                            valeur_nette = valeur - capital_restant
                        except Exception as e:
                            print(f"Erreur calcul crédit immobilier: {e}")
                            # En cas d'erreur, utiliser le montant initial
                            valeur_nette = valeur - credit_initial
                    else:
                        valeur_nette = valeur - credit_initial
                else:
                    valeur_nette = valeur
                
                total += valeur_nette
        
        return round(total, 2)
    
    @classmethod
    def _calculate_total_cryptomonnaies(cls, investor_profile: InvestorProfile) -> float:
        """
        Calcule le total des cryptomonnaies avec les prix depuis Binance/DB.
        """
        if not investor_profile.cryptomonnaies_data:
            return 0.0
        
        try:
            # Récupérer les symboles nécessaires
            symbols_needed = []
            for crypto in investor_profile.cryptomonnaies_data:
                symbol = crypto.get('symbol', '').lower()
                if symbol:
                    symbols_needed.append(symbol)
            
            if not symbols_needed:
                return 0.0
            
            # Récupérer les prix depuis Binance/DB avec mise à jour forcée
            print(f"🔄 Récupération des prix crypto via Binance...")
            prices = BinancePriceService.get_crypto_prices_for_symbols(
                symbols_needed, 
                force_update=True
            )
            
            total = 0.0
            for crypto in investor_profile.cryptomonnaies_data:
                symbol = crypto.get('symbol', '').lower()
                quantity = crypto.get('quantity', 0)
                
                if symbol in prices:
                    current_price = prices[symbol]
                    value = quantity * current_price
                    total += value
                    
                    # Stocker les valeurs calculées dans les données crypto
                    crypto['calculated_value'] = round(value, 2)
                    crypto['current_price'] = current_price
                    print(f"💰 {symbol}: {quantity} x €{current_price:.2f} = €{round(value, 2)}")
                else:
                    print(f"⚠️ Prix indisponible pour {symbol}")
                    # Garder les anciennes valeurs si disponibles
                    if 'calculated_value' not in crypto:
                        crypto['calculated_value'] = 0.0
                        crypto['current_price'] = 0.0
            
            print(f"🎯 Total crypto: €{round(total, 2)}")
            return round(total, 2)
            
        except Exception as e:
            print(f"❌ Erreur calcul crypto Binance: {e}")
            # En cas d'erreur, garder les anciennes valeurs si disponibles
            total = 0.0
            for crypto in investor_profile.cryptomonnaies_data:
                if 'calculated_value' in crypto:
                    total += crypto.get('calculated_value', 0)
                else:
                    crypto['calculated_value'] = 0.0
                    crypto['current_price'] = 0.0
            
            return round(total, 2)
    
    @classmethod
    def _calculate_total_cryptomonnaies_cached(cls, investor_profile: InvestorProfile) -> float:
        """
        Utilise les prix depuis la DB (sans appel API Binance).
        Pour le mode visualisation - utilise des prix récents en cache.
        """
        if not investor_profile.cryptomonnaies_data:
            return 0.0
        
        try:
            # Récupérer les symboles nécessaires
            symbols_needed = []
            for crypto in investor_profile.cryptomonnaies_data:
                symbol = crypto.get('symbol', '').lower()
                if symbol:
                    symbols_needed.append(symbol)
            
            if not symbols_needed:
                return 0.0
            
            # Récupérer les prix depuis la DB SEULEMENT (sans appel API)
            print(f"📊 Utilisation des prix crypto en cache...")
            prices = BinancePriceService.get_crypto_prices_for_symbols(
                symbols_needed, 
                force_update=False  # Pas de mise à jour forcée
            )
            
            total = 0.0
            for crypto in investor_profile.cryptomonnaies_data:
                symbol = crypto.get('symbol', '').lower()
                quantity = crypto.get('quantity', 0)
                
                if symbol in prices:
                    current_price = prices[symbol]
                    value = quantity * current_price
                    total += value
                    
                    # Mettre à jour les valeurs pour l'affichage
                    crypto['calculated_value'] = round(value, 2)
                    crypto['current_price'] = current_price
                else:
                    # Essayer de garder les anciennes valeurs si disponibles
                    if 'calculated_value' in crypto:
                        total += crypto.get('calculated_value', 0)
                    else:
                        # Sinon utiliser le total sauvegardé comme fallback
                        if hasattr(investor_profile, 'calculated_total_cryptomonnaies'):
                            return investor_profile.calculated_total_cryptomonnaies or 0.0
            
            print(f"📊 Total crypto (cache): €{round(total, 2)}")
            return round(total, 2)
            
        except Exception as e:
            print(f"❌ Erreur calcul crypto cache: {e}")
            # Fallback sur le total sauvegardé
            if hasattr(investor_profile, 'calculated_total_cryptomonnaies'):
                return investor_profile.calculated_total_cryptomonnaies or 0.0
            return 0.0
    
    @classmethod
    def _calculate_total_autres_biens(cls, investor_profile: InvestorProfile) -> float:
        """Calcule le total des autres biens."""
        total = 0.0
        
        # Autres biens standard
        if hasattr(investor_profile, 'has_autres_biens') and investor_profile.has_autres_biens and hasattr(investor_profile, 'autres_biens_value') and investor_profile.autres_biens_value:
            total += investor_profile.autres_biens_value
        
        # Autres biens détaillés
        if investor_profile.autres_biens_data:
            for bien in investor_profile.autres_biens_data:
                total += bien.get('valeur', 0)
        
        return round(total, 2)
    
    @classmethod
    def _calculate_total_credits_consommation(cls, investor_profile: InvestorProfile) -> float:
        """Calcule le total des crédits de consommation restants."""
        total = 0.0
        
        if hasattr(investor_profile, 'credits_data') and investor_profile.credits_data:
            for credit in investor_profile.credits_data:
                # Calcul du capital restant précis - adapter aux différentes structures
                montant_initial = credit.get('montant_initial', 0)
                taux_interet = credit.get('taux', 0)  # Dans credits_data c'est 'taux' pas 'taux_interet'
                duree_annees = credit.get('duree', 0)  # Dans credits_data c'est en années
                duree_mois = duree_annees * 12 if duree_annees else 0
                date_debut_str = credit.get('date_depart', '')
                
                if all([montant_initial, duree_mois, date_debut_str]):
                    try:
                        # Parse de la date de début (format 2025-10 ou 2025-01)
                        if '/' in date_debut_str:
                            month, year = date_debut_str.split('/')
                            start_date = date(int(year), int(month), 1)
                        elif len(date_debut_str) == 7 and '-' in date_debut_str:
                            year, month = date_debut_str.split('-')
                            start_date = date(int(year), int(month), 1)
                        else:
                            start_date = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
                        
                        # Calcul du capital restant
                        capital_restant = CreditCalculationService.calculate_remaining_capital(
                            montant_initial, taux_interet, duree_mois, start_date
                        )
                        
                        # Mise à jour du crédit avec les valeurs calculées
                        mensualite = CreditCalculationService.calculate_monthly_payment(
                            montant_initial, taux_interet, duree_mois
                        )
                        
                        credit['capital_restant'] = capital_restant
                        credit['mensualite'] = mensualite
                        
                        total += capital_restant
                        
                    except Exception as e:
                        print(f"Erreur calcul crédit consommation: {e}")
                        # En cas d'erreur, utiliser le montant initial
                        total += montant_initial
                else:
                    # Données incomplètes, utiliser le montant initial
                    total += montant_initial
        
        return round(total, 2)
    
    # Ancienne méthode CoinGecko supprimée - remplacée par BinancePriceService
    
    @classmethod
    def _save_crypto_data_to_db(cls, investor_profile: InvestorProfile):
        """Sauvegarde les données crypto enrichies en base de données."""
        try:
            if investor_profile.cryptomonnaies_data:
                # Vérifier qu'on a bien des données enrichies
                enriched_count = sum(1 for c in investor_profile.cryptomonnaies_data if 'calculated_value' in c)
                print(f"💾 Sauvegarde crypto: {enriched_count}/{len(investor_profile.cryptomonnaies_data)} enrichies")
                
                if enriched_count == 0:
                    print(f"⚠️ Aucune donnée enrichie à sauver")
                    return
                
                # Méthode robuste : forcer avec UPDATE SQL direct dans une nouvelle transaction
                import json
                from sqlalchemy import text
                
                json_data = json.dumps(investor_profile.cryptomonnaies_data)
                print(f"📝 JSON à sauver: {json_data[:100]}...")
                
                # Utiliser une transaction séparée pour être sûr
                connection = db.engine.connect()
                trans = connection.begin()
                try:
                    connection.execute(
                        text("UPDATE investor_profiles SET cryptomonnaies_data_json = :data WHERE id = :id"),
                        {'data': json_data, 'id': investor_profile.id}
                    )
                    trans.commit()
                    print(f"✅ Sauvegarde crypto réussie avec transaction séparée")
                except Exception as ex:
                    trans.rollback()
                    raise ex
                finally:
                    connection.close()
                
        except Exception as e:
            print(f"❌ Erreur sauvegarde crypto data: {e}")
            import traceback
            traceback.print_exc()
    
    @classmethod
    def _save_totaux_to_db(cls, investor_profile: InvestorProfile, totaux: Dict):
        """Sauvegarde tous les totaux calculés en base de données."""
        try:
            # Sauvegarde des totaux principaux
            investor_profile.calculated_total_liquidites = totaux['total_liquidites']
            investor_profile.calculated_total_placements = totaux['total_placements']
            investor_profile.calculated_total_immobilier_net = totaux['total_immobilier_net']
            investor_profile.calculated_total_cryptomonnaies = totaux['total_cryptomonnaies']
            investor_profile.calculated_total_autres_biens = totaux['total_autres_biens']
            investor_profile.calculated_total_credits_consommation = totaux['total_credits_consommation']
            investor_profile.calculated_total_actifs = totaux['total_actifs']
            investor_profile.calculated_patrimoine_total_net = totaux['patrimoine_total_net']
            investor_profile.last_calculation_date = datetime.utcnow()
            
            # Commit des changements
            db.session.commit()
            
            # Totaux sauvegardés silencieusement
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des totaux: {e}")
            db.session.rollback()
    
    @classmethod
    def _get_default_totaux(cls) -> Dict:
        """Retourne des totaux par défaut en cas d'erreur."""
        return {
            'total_liquidites': 0.0,
            'total_placements': 0.0,
            'total_immobilier_net': 0.0,
            'total_cryptomonnaies': 0.0,
            'total_autres_biens': 0.0,
            'total_credits_consommation': 0.0,
            'total_actifs': 0.0,
            'patrimoine_total_net': 0.0
        }
    
    @classmethod
    def update_all_users_patrimoine(cls):
        """Met à jour les calculs patrimoniaux pour tous les utilisateurs."""
        try:
            profiles = InvestorProfile.query.all()
            
            for profile in profiles:
                print(f"Mise à jour du patrimoine pour l'utilisateur {profile.user_id}")
                cls.calculate_all_totaux(profile, save_to_db=True)
            
            print(f"Mise à jour terminée pour {len(profiles)} profils")
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour globale: {e}")