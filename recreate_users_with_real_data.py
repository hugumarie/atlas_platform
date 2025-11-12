#!/usr/bin/env python3
"""
Script pour recréer les utilisateurs avec leurs vraies données.
"""

import sys
sys.path.append('.')

from datetime import datetime, timedelta
from run import app
from app import db
from app.models.user import User
from app.models.subscription import Subscription
from app.models.investor_profile import InvestorProfile

def recreate_users():
    """
    Supprime la base et recrée les utilisateurs avec données réalistes.
    """
    with app.app_context():
        # Supprimer toutes les données
        db.drop_all()
        db.create_all()
        print("✅ Base de données recréée")
        
        # Créer les utilisateurs avec vraies données
        
        # 1. Admin (inscription il y a 6 mois)
        admin = User(
            email='admin@gmail.com',
            first_name='Admin',
            last_name='Atlas',
            is_admin=True,
            is_prospect=False,
            user_type='client',
            date_created=datetime.utcnow() - timedelta(days=180),
            last_login=datetime.utcnow() - timedelta(hours=2)
        )
        admin.set_password('admin')
        
        # 2. Hugues - inscription il y a 3 mois, Plan INITIA
        hugues_date = datetime.utcnow() - timedelta(days=90)
        hugues = User(
            email='hugues.marie925@gmail.com',
            first_name='Hugues',
            last_name='Marie',
            is_admin=False,
            is_prospect=False,
            user_type='client',
            date_created=hugues_date,
            last_login=datetime.utcnow() - timedelta(days=5)
        )
        hugues.set_password('password')
        
        # 3. Hugo - inscription il y a 1 mois, Plan ULTIMA
        hugo_date = datetime.utcnow() - timedelta(days=30)
        hugo = User(
            email='hugu@gmail.com',
            first_name='Hugo',
            last_name='Test',
            is_admin=False,
            is_prospect=False,
            user_type='client',
            date_created=hugo_date,
            last_login=datetime.utcnow() - timedelta(hours=12)
        )
        hugo.set_password('password')
        
        # 4. Tom - prospect créé il y a 2 semaines
        tom_date = datetime.utcnow() - timedelta(days=14)
        tom = User(
            email='tom@gmail.com',
            first_name='Tom',
            last_name='Gedusor',
            is_admin=False,
            is_prospect=True,
            user_type='prospect',
            prospect_source='site_vitrine',
            prospect_status='nouveau',
            date_created=tom_date,
            appointment_requested=True,
            appointment_status='en_attente'
        )
        tom.password_hash = 'no_password'
        
        # Sauvegarder les utilisateurs
        db.session.add_all([admin, hugues, hugo, tom])
        db.session.commit()
        print("✅ Utilisateurs créés")
        
        # Créer les abonnements
        
        # Abonnement INITIA pour Hugues
        hugues_sub = Subscription(
            user_id=hugues.id,
            tier='initia',
            status='active',
            price=9.99,
            start_date=hugues_date,
            next_billing_date=hugues_date + timedelta(days=30),
            last_payment_date=hugues_date
        )
        
        # Abonnement ULTIMA pour Hugo
        hugo_sub = Subscription(
            user_id=hugo.id,
            tier='ultima',
            status='active',
            price=0,  # Sur devis
            start_date=hugo_date,
            next_billing_date=None,  # Sur devis
            last_payment_date=hugo_date
        )
        
        db.session.add_all([hugues_sub, hugo_sub])
        db.session.commit()
        print("✅ Abonnements créés")
        
        # Créer les profils investisseurs
        
        # Profil Hugues - débutant
        hugues_profile = InvestorProfile(
            user_id=hugues.id,
            monthly_net_income=2500.0,
            current_savings=5000.0,
            monthly_savings_capacity=300.0,
            family_situation='célibataire',
            professional_situation='employé',
            risk_tolerance='conservateur',
            investment_experience='limitée',
            investment_horizon='moyen terme',
            investment_goals='Je souhaite commencer à épargner pour préparer ma retraite et créer un petit patrimoine.',
            has_livret_a=True,
            livret_a_value=3000.0,
            has_current_account=True,
            current_account_value=2000.0
        )
        
        # Profil Hugo - expérimenté avec Plan ULTIMA
        hugo_profile = InvestorProfile(
            user_id=hugo.id,
            monthly_net_income=4500.0,
            current_savings=25000.0,
            monthly_savings_capacity=1200.0,
            family_situation='marié',
            professional_situation='chef d\'entreprise',
            risk_tolerance='dynamique',
            investment_experience='experte',
            investment_horizon='long terme',
            investment_goals='Optimiser ma fiscalité et développer un patrimoine diversifié pour la transmission.',
            has_livret_a=True,
            livret_a_value=22950.0,
            has_pea=True,
            pea_value=15000.0,
            has_per=True,
            per_value=8000.0,
            has_life_insurance=True,
            life_insurance_value=12000.0,
            has_current_account=True,
            current_account_value=3000.0
        )
        
        db.session.add_all([hugues_profile, hugo_profile])
        db.session.commit()
        print("✅ Profils investisseurs créés")
        
        # Résumé
        print(f"""
🎉 DONNÉES CRÉÉES AVEC SUCCÈS:

👤 UTILISATEURS:
- Admin: {admin.email} (admin depuis {admin.date_created.strftime('%d/%m/%Y')})
- Hugues: {hugues.email} (inscrit le {hugues.date_created.strftime('%d/%m/%Y')}) - Plan INITIA
- Hugo: {hugo.email} (inscrit le {hugo.date_created.strftime('%d/%m/%Y')}) - Plan ULTIMA

🔍 PROSPECTS:
- Tom: {tom.email} (prospect depuis le {tom.date_created.strftime('%d/%m/%Y')})

💼 ABONNEMENTS:
- Hugues: Plan INITIA - 9.99€/mois
- Hugo: Plan ULTIMA - Sur devis

📊 PROFILS INVESTISSEURS:
- Hugues: Conservateur, 2500€/mois, 5k€ d'épargne
- Hugo: Dynamique, 4500€/mois, 25k€ d'épargne
        """)

if __name__ == "__main__":
    print("🚀 Recréation des utilisateurs avec vraies données...")
    recreate_users()
    print("🎉 Terminé !")