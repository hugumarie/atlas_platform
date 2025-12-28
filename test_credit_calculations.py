#!/usr/bin/env python3
"""
Script de test pour valider les nouveaux calculs de crédit immobilier.
"""

import sys
import os
from datetime import date, datetime

# Ajouter le path de l'application
sys.path.insert(0, '/Users/huguesmarie/Documents/Jepargne digital')

from app.services.credit_calculation import CreditCalculationService

def test_credit_example():
    """Test avec l'exemple de l'interface"""
    
    print("🧪 Test des calculs de crédit immobilier")
    print("=" * 50)
    
    # Données de l'exemple
    principal = 215000.0  # Montant emprunté 
    annual_rate = 3.35    # Taux TAEG (%)
    duration_years = 25   # Durée (années)
    start_date = date(2024, 10, 1)  # octobre 2024
    current_date = date(2024, 12, 28)  # aujourd'hui
    
    print(f"💰 Montant emprunté: {principal:,.0f} €")
    print(f"📊 Taux TAEG: {annual_rate}%")
    print(f"📅 Durée: {duration_years} années")
    print(f"🗓️  Date de début: {start_date.strftime('%B %Y')}")
    print(f"🗓️  Date actuelle: {current_date.strftime('%B %Y')}")
    print()
    
    # Calculs
    duration_months = duration_years * 12
    
    # 1. Mensualité
    monthly_payment = CreditCalculationService.calculate_monthly_payment(
        principal, annual_rate, duration_months
    )
    print(f"💳 Mensualités: {monthly_payment:.0f} €/mois")
    
    # 2. Capital restant 
    remaining_capital = CreditCalculationService.calculate_remaining_capital(
        principal, annual_rate, duration_months, start_date, current_date
    )
    print(f"📉 Capital restant à rembourser: {remaining_capital:,.0f} €")
    
    # 3. Capital remboursé
    capital_repaid = principal - remaining_capital
    print(f"📈 Capital remboursé: {capital_repaid:,.0f} €")
    
    # 4. Coût total du crédit
    total_cost = (monthly_payment * duration_months) - principal
    print(f"💸 Coût global du crédit: {total_cost:,.0f} €")
    
    # 5. Mois écoulés
    months_elapsed = CreditCalculationService._calculate_months_elapsed(start_date, current_date)
    print(f"📆 Mois écoulés: {months_elapsed}")
    
    # 6. Valeur nette du bien (exemple valeur 250,000€)
    property_value = 250000.0
    net_value = property_value - remaining_capital
    print(f"🏠 Valeur nette du bien: {net_value:,.0f}€")
    
    print()
    print("✅ Test des nouveaux calculs terminé !")

if __name__ == "__main__":
    test_credit_example()