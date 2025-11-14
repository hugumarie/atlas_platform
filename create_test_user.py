#!/usr/bin/env python3
"""
Script pour créer un utilisateur de test complet avec toutes ses données
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import json

# Ajouter le répertoire parent au Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.investor_profile import InvestorProfile
from app.models.subscription import Subscription
from werkzeug.security import generate_password_hash

def create_test_user():
    """Créer un utilisateur client complet avec données fictives"""
    
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
        
        # Définir le mot de passe
        user.set_password("test123")
        
        db.session.add(user)
        db.session.flush()
        
        # Créer l'abonnement (20€/mois actif)
        subscription = Subscription(
            user_id=user.id,
            tier="optima",
            status="active", 
            price=20.00,
            start_date=datetime.utcnow() - timedelta(days=30),
            next_billing_date=datetime.utcnow() + timedelta(days=30)
        )
        
        db.session.add(subscription)
        db.session.flush()
        
        # Données des revenus complémentaires
        revenus_data = [
            {"name": "Loyers immobiliers", "amount": 850.0},
            {"name": "Dividendes", "amount": 120.0},
            {"name": "Travaux freelance", "amount": 300.0}
        ]
        
        # Données des charges
        charges_data = [
            {"name": "Crédit immobilier", "amount": 980.0},
            {"name": "Assurances", "amount": 180.0},
            {"name": "Crèche enfants", "amount": 450.0}
        ]
        
        # Liquidités personnalisées
        liquidites_data = [
            {"name": "LEP", "amount": 7700.0},
            {"name": "Compte joint", "amount": 3200.0}
        ]
        
        # Placements personnalisés
        placements_data = [
            {"name": "SCPI Primonial", "amount": 15000.0},
            {"name": "Actions individuelles", "amount": 8500.0},
            {"name": "Obligations d'État", "amount": 5000.0}
        ]
        
        # Cryptomonnaies
        crypto_data = [
            {"symbol": "BTC", "quantity": 0.12},
            {"symbol": "ETH", "quantity": 2.5},
            {"symbol": "ADA", "quantity": 1500.0}
        ]
        
        # Créer le profil investisseur complet
        profile = InvestorProfile(
            user_id=user.id,
            
            # Informations personnelles étendues
            civilite="M.",
            nationalite="Française", 
            date_naissance=datetime(1985, 3, 15),
            lieu_naissance="Lyon, France",
            pays_residence="France",
            
            # Données financières de base
            monthly_net_income=4500.0,
            current_savings=12000.0,
            monthly_savings_capacity=800.0,
            
            # Revenus complémentaires
            revenus_complementaires_json=json.dumps(revenus_data),
            
            # Charges mensuelles  
            charges_mensuelles_json=json.dumps(charges_data),
            
            # Liquidités
            has_livret_a=True,
            livret_a_value=22950.0,  # Plafond légal
            has_current_account=True,
            current_account_value=2800.0,
            has_ldds=True,
            ldds_value=8500.0,
            has_lep=False,  # Géré dans liquidités personnalisées
            lep_value=0.0,
            has_pel_cel=True,
            pel_cel_value=14500.0,
            liquidites_personnalisees_json=json.dumps(liquidites_data),
            
            # Placements financiers
            has_pea=True,
            pea_value=25000.0,
            has_per=True, 
            per_value=18000.0,
            has_life_insurance=True,
            life_insurance_value=45000.0,
            has_pee=True,
            pee_value=12000.0,
            has_scpi=False,  # Géré dans placements personnalisés
            scpi_value=0.0,
            placements_personnalises_json=json.dumps(placements_data),
            
            # Cryptomonnaies
            cryptomonnaies_json=json.dumps(crypto_data),
            
            # Immobilier
            has_primary_residence=True,
            primary_residence_value=280000.0,
            primary_residence_debt=180000.0,
            has_rental_property=True,
            rental_property_value=150000.0,
            rental_property_debt=95000.0,
            
            # Situation personnelle
            family_situation="En couple avec enfants",
            number_of_children=2,
            professional_situation="Cadre",
            
            # Profil d'investissement
            risk_tolerance="Modéré",
            investment_experience="Intermédiaire", 
            investment_horizon="Long terme (>10 ans)",
            investment_goals="Je souhaite optimiser ma fiscalité tout en préparant ma retraite. Objectifs prioritaires: constitution d'un patrimoine diversifié pour mes enfants, optimisation de mes investissements locatifs existants, et développement d'une épargne retraite solide via PER et investissements en actions européennes.",
            
            # Objectifs patrimoniaux
            objectif_constitution_epargne=True,
            objectif_achat_immobilier=False,  # Déjà propriétaire
            objectif_retraite=True,
            objectif_transmission=True,
            objectif_fiscalite=True,
            
            # Profil de risque MiFID
            profil_risque_choisi="modere",
            
            # Questions MiFID (scores sur 5)
            question_1_reponse="3",  # Connaissances financières
            question_2_reponse="4",  # Expérience investissements
            question_3_reponse="2",  # Tolérance perte
            question_4_reponse="5",  # Horizon placement
            question_5_reponse="3",  # Réaction baisse -20%
            
            profile_completed=True,
            completed_at=datetime.utcnow() - timedelta(days=40)
        )
        
        db.session.add(profile)
        db.session.commit()
        
        # Calculer quelques statistiques
        total_liquidites = (profile.livret_a_value + profile.current_account_value + 
                           profile.ldds_value + profile.pel_cel_value + 
                           sum(liq["amount"] for liq in liquidites_data))
        
        total_placements = (profile.pea_value + profile.per_value + 
                          profile.life_insurance_value + profile.pee_value +
                          sum(place["amount"] for place in placements_data))
        
        patrimoine_immobilier = (profile.primary_residence_value + profile.rental_property_value -
                               profile.primary_residence_debt - profile.rental_property_debt)
        
        patrimoine_total = total_liquidites + total_placements + patrimoine_immobilier
        
        taux_epargne = (profile.monthly_savings_capacity / profile.monthly_net_income * 100)
        
        print("\n🎉 UTILISATEUR CLIENT CRÉÉ AVEC SUCCÈS !")
        print("="*50)
        print(f"👤 Nom: {user.first_name} {user.last_name}")
        print(f"📧 Email: {user.email}")
        print(f"🔑 Mot de passe: test123")
        print(f"💳 Abonnement: {subscription.tier} - {subscription.price}€/mois")
        print(f"📅 Membre depuis: {user.date_created.strftime('%d/%m/%Y')}")
        print()
        print("💰 SITUATION FINANCIÈRE:")
        print(f"   • Revenus nets: {profile.monthly_net_income:,.0f}€/mois")
        print(f"   • Capacité épargne: {profile.monthly_savings_capacity:,.0f}€/mois")
        print(f"   • Taux d'épargne: {taux_epargne:.1f}%")
        print()
        print("🏦 PATRIMOINE:")
        print(f"   • Liquidités: {total_liquidites:,.0f}€")
        print(f"   • Placements: {total_placements:,.0f}€") 
        print(f"   • Immobilier net: {patrimoine_immobilier:,.0f}€")
        print(f"   • TOTAL: {patrimoine_total:,.0f}€")
        print()
        print("🔗 URL pour tester:")
        print(f"   http://127.0.0.1:5001/plateforme/admin/utilisateur/{user.id}")
        print("="*50)

if __name__ == "__main__":
    create_test_user()