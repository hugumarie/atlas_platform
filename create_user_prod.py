#!/usr/bin/env python3
"""
Script générique pour créer un utilisateur client en base de données production.
Simule un prospect fraîchement converti avec toutes les bonnes valeurs par défaut.
Usage: python3 create_user_prod.py
"""

import sys
import os
from datetime import datetime, timedelta
sys.path.append('.')

from app import create_app, db
from app.models.user import User
from app.models.investor_profile import InvestorProfile
from app.models.subscription import Subscription

def create_user():
    """Crée un utilisateur client avec profil et abonnement par défaut."""
    app = create_app()
    
    with app.app_context():
        print("👤 CRÉATION D'UTILISATEUR CLIENT - BASE DE DONNÉES PRODUCTION")
        print("=" * 65)
        
        # Demander l'email
        email = input("\n📧 Entrez l'email du nouvel utilisateur: ").strip().lower()
        
        if not email:
            print("❌ Email requis!")
            return
        
        # Vérifier que l'utilisateur n'existe pas
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"❌ Un utilisateur avec l'email {email} existe déjà!")
            return
        
        # Demander le prénom et nom (optionnel)
        first_name = input("👤 Prénom (laissez vide pour générer): ").strip()
        last_name = input("👤 Nom (laissez vide pour générer): ").strip()
        
        # Générer des valeurs par défaut si vide
        if not first_name:
            first_name = email.split('@')[0].capitalize()
        if not last_name:
            last_name = "Client"
        
        print(f"\n📋 UTILISATEUR À CRÉER:")
        print(f"   Nom: {first_name} {last_name}")
        print(f"   Email: {email}")
        print(f"   Type: Client (prospect converti)")
        print(f"   Plan: Trial (7 jours)")
        print(f"   Mot de passe: atlas2024 (temporaire)")
        
        # Confirmation
        confirm = input(f"\n❓ Confirmer la création de cet utilisateur ? (o/N): ").strip().lower()
        if confirm not in ['o', 'oui', 'y', 'yes']:
            print("❌ Création annulée.")
            return
        
        try:
            # 1. Créer l'utilisateur
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_admin=False,
                is_active=True,
                is_prospect=False,  # Client, pas prospect
                user_type='client',
                date_created=datetime.utcnow()
            )
            user.set_password('atlas2024')  # Mot de passe temporaire
            
            db.session.add(user)
            db.session.flush()  # Pour obtenir l'ID
            
            # 2. Créer l'abonnement trial
            subscription = Subscription(
                user_id=user.id,
                tier='trial',
                status='trial',
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=7),  # 7 jours de trial
                is_active=True
            )
            
            db.session.add(subscription)
            
            # 3. Créer le profil investisseur par défaut
            investor_profile = InvestorProfile(
                user_id=user.id,
                
                # Informations financières par défaut
                monthly_net_income=3000.0,
                current_savings=10000.0,
                monthly_savings_capacity=500.0,
                annual_savings_target=6000.0,
                
                # Informations personnelles par défaut
                family_situation='celibataire',
                professional_situation='salarie',
                age=30,
                
                # Profil de risque conservateur par défaut
                risk_tolerance='modere',
                investment_experience='debutant',
                investment_horizon='moyen_terme',
                investment_goals='croissance_reguliere',
                
                # Épargne traditionnelle
                has_livret_a=True,
                livret_a_value=15000.0,
                
                # Patrimoine de base
                total_liquidites=25000.0,
                total_placements=0.0,
                total_immobilier_net=0.0,
                total_cryptomonnaies=0.0,
                total_autres_biens=0.0,
                
                # Totaux calculés
                calculated_total_liquidites=25000.0,
                calculated_total_placements=0.0,
                calculated_total_immobilier_net=0.0,
                calculated_total_cryptomonnaies=0.0,
                calculated_total_autres_biens=0.0,
                calculated_total_actifs=25000.0,
                calculated_patrimoine_total_net=25000.0,
                
                last_updated=datetime.utcnow()
            )
            
            db.session.add(investor_profile)
            
            # Sauvegarder tout
            db.session.commit()
            
            print(f"\n✅ UTILISATEUR CRÉÉ AVEC SUCCÈS!")
            print(f"✅ {first_name} {last_name} ({email})")
            print(f"\n📋 DÉTAILS DU COMPTE:")
            print(f"   🔑 Mot de passe: atlas2024 (temporaire)")
            print(f"   📅 Trial jusqu'au: {subscription.end_date.strftime('%d/%m/%Y')}")
            print(f"   💰 Patrimoine initial: 25,000€")
            print(f"   📊 Profil de risque: Modéré")
            
            print(f"\n💡 PROCHAINES ÉTAPES:")
            print(f"   1. L'utilisateur peut se connecter avec atlas2024")
            print(f"   2. Il devrait changer son mot de passe")
            print(f"   3. Il peut compléter son profil investisseur")
            print(f"   4. À la fin du trial, proposer un plan premium")
            
            # Statistiques actuelles
            total_users = User.query.filter_by(is_admin=False, is_prospect=False).count()
            total_prospects = User.query.filter_by(is_prospect=True).count()
            
            print(f"\n📊 STATISTIQUES ACTUELLES:")
            print(f"   Clients: {total_users}")
            print(f"   Prospects: {total_prospects}")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERREUR lors de la création: {e}")

if __name__ == "__main__":
    create_user()