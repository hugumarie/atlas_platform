#!/usr/bin/env python3
"""
Script de test pour valider les nouveaux calculs des crédits de consommation.
Teste l'exemple du crédit auto avec les vraies formules d'amortissement.
"""

import sys
import os
from datetime import date, datetime

# Ajouter le path de l'application
sys.path.insert(0, '/Users/huguesmarie/Documents/Jepargne digital')

from app.services.credit_calculation import CreditCalculationService

def test_credit_auto_example():
    """Test avec l'exemple du crédit auto de l'interface"""
    
    print("🚗 TEST CRÉDIT AUTO - VALIDATION CALCULS")
    print("=" * 50)
    
    # Données du crédit auto de l'exemple
    principal = 5000.0  # Montant initial
    annual_rate = 6.5   # Taux d'intérêt (%)
    duration_years = 5  # Durée initiale (années)
    start_date = date(2025, 1, 1)  # janvier 2025
    current_date = date(2025, 12, 28)  # aujourd'hui
    
    print(f"💰 Montant initial: {principal:,.0f}€")
    print(f"📊 Taux d'intérêt: {annual_rate}%")
    print(f"📅 Durée: {duration_years} années ({duration_years * 12} mois)")
    print(f"🗓️  Date de début: {start_date.strftime('%B %Y')}")
    print(f"🗓️  Date actuelle: {current_date.strftime('%B %Y')}")
    print()
    
    # Calculs avec les nouvelles formules
    duration_months = duration_years * 12
    
    # 1. Mensualité
    monthly_payment = CreditCalculationService.calculate_monthly_payment(
        principal, annual_rate, duration_months
    )
    print(f"💳 Mensualité calculée: {monthly_payment:.2f}€")
    print(f"💳 Mensualité interface: 97.83€")
    print(f"✅ Différence mensualité: {abs(monthly_payment - 97.83):.2f}€")
    print()
    
    # 2. Capital restant avec vraie formule d'amortissement
    remaining_capital = CreditCalculationService.calculate_remaining_capital(
        principal, annual_rate, duration_months, start_date, current_date
    )
    print(f"📉 Capital restant ANCIEN (interface): 3826€")
    print(f"📉 Capital restant NOUVEAU (correct): {remaining_capital:,.0f}€")
    print(f"⚠️  Différence: {abs(remaining_capital - 3826):,.0f}€")
    print()
    
    # 3. Capital remboursé
    capital_repaid = principal - remaining_capital
    print(f"📈 Capital remboursé: {capital_repaid:,.0f}€")
    
    # 4. Coût total du crédit
    total_cost = (monthly_payment * duration_months) - principal
    print(f"💸 Coût global du crédit: {total_cost:,.0f}€")
    print()
    
    # 5. Détails supplémentaires
    months_elapsed = CreditCalculationService._calculate_months_elapsed(start_date, current_date)
    print(f"📆 Mois écoulés: {months_elapsed}")
    
    # Pourcentage remboursé
    percentage_repaid = (capital_repaid / principal) * 100
    print(f"📊 Pourcentage remboursé: {percentage_repaid:.1f}%")
    
    print()
    print("🔍 ANALYSE DES RÉSULTATS:")
    print("-" * 30)
    
    if abs(monthly_payment - 97.83) < 0.1:
        print("✅ Mensualité: CORRECTE")
    else:
        print("❌ Mensualité: DIFFÉRENTE")
    
    if remaining_capital != 3826:
        print(f"⚠️  Capital restant: CORRIGÉ (+{abs(remaining_capital - 3826):,.0f}€)")
        print(f"   → L'ancien calcul sous-estimait le capital restant")
    else:
        print("✅ Capital restant: IDENTIQUE")
    
    print()
    print("🎯 NOUVEAUX LIBELLÉS POUR L'INTERFACE:")
    print("-" * 40)
    print(f"• Capital remboursé: {capital_repaid:,.0f}€")
    print(f"• Capital restant à rembourser: {remaining_capital:,.0f}€") 
    print(f"• Coût global du crédit: {total_cost:,.0f}€")
    
    print()
    print("✅ Test des nouveaux calculs de crédit de consommation terminé !")

if __name__ == "__main__":
    test_credit_auto_example()