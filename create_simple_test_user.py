#!/usr/bin/env python3
"""
Script simplifié pour créer un utilisateur de test avec les vrais champs du modèle
"""

import sys
import os
from datetime import datetime, timedelta, date
import json

# Ajouter le répertoire parent au Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.investor_profile import InvestorProfile
from app.models.subscription import Subscription

def create_simple_test_user():
    """Créer un utilisateur client simple avec données de base"""
    
    app = create_app()
    
    with app.app_context():
        # Supprimer l'utilisateur existant s'il existe
        existing_user = User.query.filter_by(email='test.client@gmail.com').first()
        if existing_user:
            if existing_user.investor_profile:
                db.session.delete(existing_user.investor_profile)
            if existing_user.subscription:
                db.session.delete(existing_user.subscription)
            db.session.delete(existing_user)
            db.session.commit()
            print("Ancien utilisateur test supprimé")
        
        # Créer l'utilisateur
        user = User(
            first_name="Thomas",
            last_name="Dupont",
            email="test.client@gmail.com",
            phone="06 12 34 56 78",
            is_admin=False,
            is_prospect=False,
            user_type="client",
            date_created=datetime.utcnow() - timedelta(days=45),
            last_login=datetime.utcnow() - timedelta(hours=2)
        )
        
        user.set_password("test123")
        db.session.add(user)
        db.session.flush()
        
        # Créer l'abonnement
        subscription = Subscription(
            user_id=user.id,
            tier="optima",
            status="active",
            price=20.00
        )
        db.session.add(subscription)
        db.session.flush()
        
        # Données JSON pour les sections dynamiques
        revenus_data = [
            {"name": "Loyers immobiliers", "amount": 850.0},
            {"name": "Dividendes", "amount": 120.0}
        ]
        
        charges_data = [
            {"name": "Crédit immobilier", "amount": 980.0},
            {"name": "Assurances", "amount": 180.0}
        ]
        
        liquidites_data = [
            {"name": "LEP", "amount": 7700.0},
            {"name": "Compte joint", "amount": 3200.0}
        ]
        
        placements_data = [
            {"name": "SCPI", "amount": 15000.0},
            {"name": "Actions", "amount": 8500.0}
        ]
        
        crypto_data = [
            {"symbol": "BTC", "quantity": 0.12},
            {"symbol": "ETH", "quantity": 2.5}
        ]
        
        # Créer le profil investisseur avec seulement les champs existants
        profile = InvestorProfile(
            user_id=user.id,
            
            # Données financières de base (obligatoires)
            monthly_net_income=4500.0,
            current_savings=12000.0,
            monthly_savings_capacity=800.0,
            risk_tolerance="Modéré",
            investment_experience="Intermédiaire",
            investment_goals="Optimiser ma fiscalité et préparer ma retraite",
            investment_horizon="Long terme",
            family_situation="En couple",
            professional_situation="Cadre",
            
            # Identité
            civilite="M.",
            nationalite="Française",
            date_naissance=date(1985, 3, 15),
            lieu_naissance="Lyon, France",
            pays_residence="France",
            
            # Revenus et charges JSON
            revenus_complementaires_json=json.dumps(revenus_data),
            charges_mensuelles_json=json.dumps(charges_data),
            
            # Liquidités
            has_livret_a=True,
            livret_a_value=22950.0,
            has_ldds=True,
            ldds_value=8500.0,
            liquidites_personnalisees_json=json.dumps(liquidites_data),
            
            # Placements
            has_pea=True,
            pea_value=25000.0,
            has_life_insurance=True,
            life_insurance_value=45000.0,
            placements_personnalises_json=json.dumps(placements_data),
            
            # Cryptos
            cryptos_json=json.dumps(crypto_data),
            
            # Immobilier
            has_real_estate=True,
            real_estate_value=280000.0,
            
            # Dates
            date_completed=datetime.utcnow() - timedelta(days=40)
        )
        
        db.session.add(profile)
        db.session.commit()
        
        print("\n🎉 UTILISATEUR CLIENT CRÉÉ AVEC SUCCÈS !")
        print("="*50)
        print(f"👤 Nom: {user.first_name} {user.last_name}")
        print(f"📧 Email: {user.email}")
        print(f"🔑 Mot de passe: test123")
        print(f"💳 Abonnement: {subscription.tier} - {subscription.price}€/mois")
        print(f"📅 Membre depuis: {user.date_created.strftime('%d/%m/%Y')}")
        print()
        print("💰 DONNÉES FINANCIÈRES:")
        print(f"   • Revenus nets: {profile.monthly_net_income:,.0f}€/mois")
        print(f"   • Épargne actuelle: {profile.current_savings:,.0f}€")
        print(f"   • Capacité épargne: {profile.monthly_savings_capacity:,.0f}€/mois")
        print(f"   • Livret A: {profile.livret_a_value:,.0f}€")
        print(f"   • PEA: {profile.pea_value:,.0f}€")
        print(f"   • Assurance Vie: {profile.life_insurance_value:,.0f}€")
        print(f"   • Immobilier: {profile.real_estate_value:,.0f}€")
        print()
        print("🔗 URL pour tester:")
        print(f"   http://127.0.0.1:5001/plateforme/admin/utilisateur/{user.id}")
        print("="*50)

if __name__ == "__main__":
    create_simple_test_user()