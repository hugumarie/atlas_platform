"""
Service centralisé pour les calculs de crédit.
Formules standardisées pour le calcul des mensualités et du capital restant.
"""

import math
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple


class CreditCalculationService:
    """
    Service centralisé pour tous les calculs liés aux crédits.
    Utilise les formules d'amortissement standard.
    """
    
    @staticmethod
    def calculate_monthly_payment(principal: float, annual_rate: float, duration_months: int) -> float:
        """
        Calcule la mensualité selon la formule d'amortissement standard.
        
        Formule: M = P * [r(1+r)^n] / [(1+r)^n - 1]
        où P = capital, r = taux mensuel, n = nombre de mensualités
        
        Args:
            principal (float): Montant emprunté
            annual_rate (float): Taux annuel en % (ex: 2.5 pour 2.5%)
            duration_months (int): Durée en mois
            
        Returns:
            float: Mensualité calculée
        """
        if principal <= 0 or annual_rate < 0 or duration_months <= 0:
            return 0.0
            
        # Conversion du taux annuel en taux mensuel
        monthly_rate = annual_rate / 100 / 12
        
        if monthly_rate == 0:
            # Si taux = 0%, alors mensualité = capital / nb_mois
            return principal / duration_months
        
        # Formule d'amortissement
        numerator = principal * monthly_rate * math.pow(1 + monthly_rate, duration_months)
        denominator = math.pow(1 + monthly_rate, duration_months) - 1
        
        return round(numerator / denominator, 2)
    
    @staticmethod
    def calculate_remaining_capital(principal: float, annual_rate: float, duration_months: int, 
                                  start_date: date, current_date: Optional[date] = None) -> float:
        """
        Calcule le capital restant dû selon l'amortissement.
        
        Args:
            principal (float): Montant initial emprunté
            annual_rate (float): Taux annuel en %
            duration_months (int): Durée totale en mois
            start_date (date): Date de début du crédit
            current_date (date, optional): Date actuelle (défaut: aujourd'hui)
            
        Returns:
            float: Capital restant dû
        """
        if current_date is None:
            current_date = date.today()
            
        if principal <= 0:
            return 0.0
            
        # Si le crédit n'a pas encore commencé, retourner le montant initial
        if start_date > current_date:
            return principal
        
        # Calcul du nombre de mois écoulés
        months_elapsed = CreditCalculationService._calculate_months_elapsed(start_date, current_date)
        
        if months_elapsed >= duration_months:
            return 0.0
        
        # Approche simplifiée : capital remboursé = nb mois × mensualité  
        monthly_payment = CreditCalculationService.calculate_monthly_payment(principal, annual_rate, duration_months)
        capital_repaid = monthly_payment * months_elapsed
        
        # Capital restant = capital initial - capital remboursé
        return round(max(0, principal - capital_repaid), 2)
    
    @staticmethod
    def calculate_amortization_schedule(principal: float, annual_rate: float, duration_months: int,
                                      start_date: date) -> List[Dict]:
        """
        Génère le tableau d'amortissement complet.
        
        Args:
            principal (float): Montant emprunté
            annual_rate (float): Taux annuel en %
            duration_months (int): Durée en mois
            start_date (date): Date de début
            
        Returns:
            List[Dict]: Liste des échéances avec détail amortissement/intérêts
        """
        schedule = []
        monthly_payment = CreditCalculationService.calculate_monthly_payment(principal, annual_rate, duration_months)
        monthly_rate = annual_rate / 100 / 12
        remaining_capital = principal
        
        for month in range(1, duration_months + 1):
            # Calcul des intérêts du mois
            interest_payment = remaining_capital * monthly_rate
            
            # Calcul de l'amortissement du capital
            capital_payment = monthly_payment - interest_payment
            
            # Nouveau capital restant
            remaining_capital -= capital_payment
            
            # Protection contre les valeurs négatives dues aux arrondis
            if remaining_capital < 0:
                capital_payment += remaining_capital
                remaining_capital = 0
            
            schedule.append({
                'month': month,
                'date': CreditCalculationService._add_months(start_date, month - 1),
                'monthly_payment': round(monthly_payment, 2),
                'interest_payment': round(interest_payment, 2),
                'capital_payment': round(capital_payment, 2),
                'remaining_capital': round(remaining_capital, 2)
            })
            
            if remaining_capital <= 0:
                break
        
        return schedule
    
    @staticmethod
    def calculate_total_cost(principal: float, annual_rate: float, duration_months: int) -> Dict:
        """
        Calcule le coût total du crédit.
        
        Args:
            principal (float): Montant emprunté
            annual_rate (float): Taux annuel en %
            duration_months (int): Durée en mois
            
        Returns:
            Dict: Détail du coût total (capital + intérêts)
        """
        monthly_payment = CreditCalculationService.calculate_monthly_payment(principal, annual_rate, duration_months)
        total_paid = monthly_payment * duration_months
        total_interest = total_paid - principal
        
        return {
            'principal': round(principal, 2),
            'monthly_payment': round(monthly_payment, 2),
            'total_paid': round(total_paid, 2),
            'total_interest': round(total_interest, 2),
            'effective_rate': round((total_interest / principal) * 100, 2) if principal > 0 else 0
        }
    
    @staticmethod
    def update_credit_calculations(credit_data: Dict) -> Dict:
        """
        Met à jour tous les calculs pour un crédit donné.
        
        Args:
            credit_data (Dict): Données du crédit
            
        Returns:
            Dict: Données du crédit avec calculs mis à jour
        """
        try:
            principal = float(credit_data.get('montant_initial', 0))
            annual_rate = float(credit_data.get('taux_interet', 0))
            duration_months = int(credit_data.get('duree_mois', 0))
            
            # Parse de la date de début
            start_date_str = credit_data.get('date_debut', '')
            if start_date_str:
                start_date = CreditCalculationService._parse_date(start_date_str)
            else:
                start_date = date.today()
            
            # Calculs
            monthly_payment = CreditCalculationService.calculate_monthly_payment(principal, annual_rate, duration_months)
            remaining_capital = CreditCalculationService.calculate_remaining_capital(
                principal, annual_rate, duration_months, start_date
            )
            
            # Mise à jour des données
            credit_data['mensualite'] = monthly_payment
            credit_data['capital_restant'] = remaining_capital
            credit_data['date_debut_parsed'] = start_date.isoformat()
            
            # Calculs additionnels
            months_elapsed = CreditCalculationService._calculate_months_elapsed(start_date, date.today())
            months_remaining = max(0, duration_months - months_elapsed)
            percentage_paid = ((principal - remaining_capital) / principal * 100) if principal > 0 else 0
            
            credit_data['mois_ecoules'] = months_elapsed
            credit_data['mois_restants'] = months_remaining
            credit_data['pourcentage_rembourse'] = round(percentage_paid, 1)
            
        except (ValueError, TypeError) as e:
            print(f"Erreur calcul crédit: {e}")
            # En cas d'erreur, on garde les valeurs par défaut
            credit_data['mensualite'] = credit_data.get('mensualite', 0)
            credit_data['capital_restant'] = credit_data.get('montant_initial', 0)
        
        return credit_data
    
    @staticmethod
    def _calculate_months_elapsed(start_date: date, current_date: date) -> int:
        """
        Calcule le nombre de mois écoulés entre deux dates.
        Part du principe que le remboursement se fait le 1er du mois.
        
        Args:
            start_date (date): Date de début
            current_date (date): Date actuelle
            
        Returns:
            int: Nombre de mois écoulés (inclut le mois de départ)
        """
        # Calcul classique
        months_diff = (current_date.year - start_date.year) * 12 + (current_date.month - start_date.month)
        
        # Si on est dans le mois de départ ou après, on compte ce mois
        # Exemple: crédit octobre 2025, aujourd'hui novembre 2025 -> 2 mois (octobre + novembre)
        return months_diff + 1
    
    @staticmethod
    def _add_months(base_date: date, months: int) -> date:
        """
        Ajoute un nombre de mois à une date.
        
        Args:
            base_date (date): Date de base
            months (int): Nombre de mois à ajouter
            
        Returns:
            date: Nouvelle date
        """
        month = base_date.month - 1 + months
        year = base_date.year + month // 12
        month = month % 12 + 1
        
        # Gestion du dernier jour du mois
        try:
            return base_date.replace(year=year, month=month)
        except ValueError:
            # Si le jour n'existe pas dans le nouveau mois (ex: 31 février)
            # On prend le dernier jour du mois
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            return base_date.replace(year=year, month=month, day=last_day)
    
    @staticmethod
    def _parse_date(date_str: str) -> date:
        """
        Parse une date depuis différents formats.
        
        Args:
            date_str (str): Date au format string
            
        Returns:
            date: Date parsée
        """
        try:
            # Format YYYY-MM-DD
            if '-' in date_str and len(date_str) == 10:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            # Format YYYY-MM
            elif '-' in date_str and len(date_str) == 7:
                return datetime.strptime(date_str + '-01', '%Y-%m-%d').date()
            # Format MM/YYYY
            elif '/' in date_str:
                parts = date_str.split('/')
                if len(parts) == 2:
                    month, year = parts
                    return datetime.strptime(f'{year}-{month.zfill(2)}-01', '%Y-%m-%d').date()
        except ValueError:
            pass
        
        # Par défaut, retourner aujourd'hui
        return date.today()