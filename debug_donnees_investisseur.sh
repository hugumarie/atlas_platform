#!/bin/bash

echo "🐛 Debug route donnees-investisseur"
echo "==================================="

echo "🧪 Test de la route problématique..."
ssh dokku@167.172.108.93 "run atlas python -c '
from app import create_app
from app.models.user import User
from app.models.investor_profile import InvestorProfile

app = create_app()
with app.app_context():
    print(\"📊 Diagnostic des profils utilisateurs...\")
    
    # Compter les utilisateurs avec/sans profils
    total_users = User.query.count()
    users_with_profiles = User.query.join(InvestorProfile).count()
    users_without_profiles = total_users - users_with_profiles
    
    print(f\"Total utilisateurs: {total_users}\")
    print(f\"Avec profils: {users_with_profiles}\")
    print(f\"Sans profils: {users_without_profiles}\")
    
    # Test des imports
    try:
        from app.services.patrimony_calculation_engine import PatrimonyCalculationEngine
        print(\"✅ PatrimonyCalculationEngine importé\")
    except Exception as e:
        print(f\"❌ Erreur import PatrimonyCalculationEngine: {e}\")
    
    try:
        from app.services.credit_calculation import CreditCalculationService
        print(\"✅ CreditCalculationService importé\")
    except Exception as e:
        print(f\"❌ Erreur import CreditCalculationService: {e}\")
    
    # Test création profil vide
    try:
        test_profile = InvestorProfile(
            user_id=999999,  # ID fictif
            monthly_net_income=0.0,
            current_savings=0.0,
            monthly_savings_capacity=0.0,
            risk_tolerance=\"conservateur\",
            investment_experience=\"debutant\", 
            investment_goals=\"constitution_epargne\",
            investment_horizon=\"court terme\"
        )
        print(\"✅ Création profil vide OK\")
    except Exception as e:
        print(f\"❌ Erreur création profil: {e}\")
        
    # Test des utilisateurs récents sans profil
    users_no_profile = User.query.filter(~User.id.in_(
        app.session.query(InvestorProfile.user_id)
    )).limit(3).all()
    
    for user in users_no_profile:
        print(f\"Utilisateur sans profil: {user.email} (ID: {user.id})\")
'"

echo ""
echo "💡 Si tout semble normal, le problème peut être:"
echo "1. Erreur dans le template investor_data.html"
echo "2. Problème avec les calculs sur un profil spécifique"
echo "3. Erreur JavaScript côté client"