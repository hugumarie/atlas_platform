#!/usr/bin/env python3
"""
Script générique pour créer un utilisateur client en base de données production (version serveur).
Usage: python3 create_user_prod_remote.py email@example.com [prenom] [nom]
"""

import sys
import os
from datetime import datetime, timedelta, timezone
sys.path.append('.')

from app import create_app, db
from app.models.user import User
from app.models.investor_profile import InvestorProfile
from app.models.subscription import Subscription

def create_user(email, first_name=None, last_name=None):
    """Crée un utilisateur client avec profil et abonnement par défaut."""
    app = create_app()
    
    with app.app_context():
        print("👤 CRÉATION D'UTILISATEUR CLIENT - BASE DE DONNÉES PRODUCTION")
        print("=" * 65)
        
        if not email:
            print("❌ Email requis!")
            return
        
        # Vérifier que l'utilisateur n'existe pas
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"❌ Un utilisateur avec l'email {email} existe déjà!")
            return
        
        # Générer des valeurs par défaut si vide
        if not first_name:
            first_name = email.split('@')[0].capitalize()
        if not last_name:
            last_name = "Client"
        
        print(f"\n📋 UTILISATEUR À CRÉER:")
        print(f"   Nom: {first_name} {last_name}")
        print(f"   Email: {email}")
        print(f"   Type: Client")
        print(f"   Plan: Premium ACTIF")
        print(f"   Mot de passe: AtlasUser2025!")
        print(f"   Patrimoine: 0€ (vierge à configurer)")
        
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
                date_created=datetime.now(timezone.utc)
            )
            user.set_password('AtlasUser2025!')  # Mot de passe permanent
            
            db.session.add(user)
            db.session.flush()  # Pour obtenir l'ID
            
            # 2. Créer l'abonnement premium actif
            subscription = Subscription(
                user_id=user.id,
                tier='premium',
                status='active',
                start_date=datetime.now(timezone.utc),
                end_date=datetime.now(timezone.utc) + timedelta(days=365),  # 1 an
                is_active=True
            )
            
            db.session.add(subscription)
            
            # 3. Créer le profil investisseur minimal (vierge)
            investor_profile = InvestorProfile(
                user_id=user.id,
                
                # Informations financières minimales
                monthly_net_income=0.0,
                current_savings=0.0,
                monthly_savings_capacity=0.0,
                
                # Informations personnelles vides
                family_situation='celibataire',
                professional_situation='salarie',
                
                # Profil de risque minimal
                risk_tolerance='modere',
                investment_experience='debutant',
                investment_horizon='moyen_terme',
                investment_goals='À définir',
                
                # Épargne à zéro
                has_livret_a=False,
                livret_a_value=0.0,
                
                # Patrimoine à zéro
                calculated_total_liquidites=0.0,
                calculated_total_placements=0.0,
                calculated_total_immobilier_net=0.0,
                calculated_total_cryptomonnaies=0.0,
                calculated_total_autres_biens=0.0,
                calculated_total_actifs=0.0,
                calculated_patrimoine_total_net=0.0,
                
                last_updated=datetime.now(timezone.utc)
            )
            
            db.session.add(investor_profile)
            
            # Sauvegarder tout
            db.session.commit()
            
            print(f"\n✅ UTILISATEUR CRÉÉ AVEC SUCCÈS!")
            print(f"✅ {first_name} {last_name} ({email})")
            print(f"\n📋 DÉTAILS DU COMPTE:")
            print(f"   🔑 Mot de passe: AtlasUser2025!")
            print(f"   📅 Abonnement premium jusqu'au: {subscription.end_date.strftime('%d/%m/%Y')}")
            print(f"   💰 Patrimoine initial: 0€ (vierge)")
            print(f"   📊 Profil: Minimal à compléter")
            print(f"   ✅ Statut: PREMIUM ACTIF")
            
            print(f"\n💡 PROCHAINES ÉTAPES:")
            print(f"   1. L'utilisateur peut se connecter immédiatement")
            print(f"   2. Compléter ses informations personnelles")
            print(f"   3. Saisir ses données patrimoniales")
            print(f"   4. Configurer ses objectifs d'investissement")
            
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
    if len(sys.argv) < 2:
        print("Usage: python3 create_user_prod_remote.py email@example.com [prenom] [nom]")
        sys.exit(1)
    
    email = sys.argv[1].strip().lower()
    first_name = sys.argv[2] if len(sys.argv) > 2 else None
    last_name = sys.argv[3] if len(sys.argv) > 3 else None
    
    create_user(email, first_name, last_name)