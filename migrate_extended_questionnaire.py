#!/usr/bin/env python3
"""
Script de migration pour le questionnaire étendu.
Recrée la base de données avec tous les nouveaux champs du questionnaire.
"""

import sys
sys.path.append('.')

from datetime import datetime, timedelta
from run import app
from app import db
from app.models.user import User
from app.models.subscription import Subscription
from app.models.investor_profile import InvestorProfile
from app.models.credit import Credit

def migrate_extended_questionnaire():
    """
    Recrée la base de données avec le schema étendu du questionnaire.
    Préserve les données existantes quand possible.
    """
    with app.app_context():
        print("🔄 Migration vers le questionnaire étendu...")
        
        # Sauvegarder les données existantes
        print("📋 Sauvegarde des données existantes...")
        existing_users = []
        existing_profiles = []
        existing_subscriptions = []
        
        try:
            # Sauvegarder les utilisateurs
            users = User.query.all()
            for user in users:
                existing_users.append({
                    'email': user.email,
                    'password_hash': user.password_hash,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone,
                    'is_admin': user.is_admin,
                    'is_prospect': user.is_prospect,
                    'user_type': user.user_type,
                    'prospect_source': user.prospect_source,
                    'prospect_status': user.prospect_status,
                    'date_created': user.date_created,
                    'last_login': user.last_login
                })
                
                # Sauvegarder le profil investisseur s'il existe
                if user.investor_profile:
                    existing_profiles.append({
                        'user_email': user.email,
                        'monthly_net_income': user.investor_profile.monthly_net_income,
                        'current_savings': user.investor_profile.current_savings,
                        'monthly_savings_capacity': user.investor_profile.monthly_savings_capacity,
                        'risk_tolerance': user.investor_profile.risk_tolerance,
                        'investment_experience': user.investor_profile.investment_experience,
                        'investment_goals': user.investor_profile.investment_goals,
                        'investment_horizon': user.investor_profile.investment_horizon,
                        'family_situation': user.investor_profile.family_situation,
                        'professional_situation': user.investor_profile.professional_situation,
                        'has_livret_a': user.investor_profile.has_livret_a,
                        'livret_a_value': user.investor_profile.livret_a_value,
                        'has_pea': user.investor_profile.has_pea,
                        'pea_value': user.investor_profile.pea_value,
                        'has_per': getattr(user.investor_profile, 'has_per', False),
                        'per_value': getattr(user.investor_profile, 'per_value', 0.0),
                        'has_life_insurance': user.investor_profile.has_life_insurance,
                        'life_insurance_value': user.investor_profile.life_insurance_value,
                        'has_current_account': getattr(user.investor_profile, 'has_current_account', False),
                        'current_account_value': getattr(user.investor_profile, 'current_account_value', 0.0),
                        'has_real_estate': user.investor_profile.has_real_estate,
                        'real_estate_value': user.investor_profile.real_estate_value,
                    })
                
                # Sauvegarder l'abonnement s'il existe
                if user.subscription:
                    existing_subscriptions.append({
                        'user_email': user.email,
                        'tier': user.subscription.tier,
                        'status': user.subscription.status,
                        'price': user.subscription.price,
                        'start_date': user.subscription.start_date,
                        'next_billing_date': user.subscription.next_billing_date,
                        'last_payment_date': user.subscription.last_payment_date
                    })
            
            print(f"✅ Sauvegardé {len(existing_users)} utilisateurs")
            print(f"✅ Sauvegardé {len(existing_profiles)} profils")
            print(f"✅ Sauvegardé {len(existing_subscriptions)} abonnements")
            
        except Exception as e:
            print(f"⚠️  Erreur lors de la sauvegarde: {e}")
            print("🔄 Création d'une nouvelle base vide...")
        
        # Supprimer et recréer toutes les tables
        print("🗑️  Suppression de l'ancienne base de données...")
        db.drop_all()
        
        print("🏗️  Création du nouveau schéma...")
        db.create_all()
        
        # Restaurer les données
        print("🔄 Restauration des données...")
        
        # Recréer les utilisateurs
        users_map = {}
        for user_data in existing_users:
            user = User(
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone=user_data.get('phone'),
                is_admin=user_data.get('is_admin', False),
                is_prospect=user_data.get('is_prospect', False),
                user_type=user_data.get('user_type', 'client'),
                prospect_source=user_data.get('prospect_source'),
                prospect_status=user_data.get('prospect_status'),
                date_created=user_data.get('date_created', datetime.utcnow()),
                last_login=user_data.get('last_login')
            )
            user.password_hash = user_data['password_hash']
            db.session.add(user)
            users_map[user_data['email']] = user
        
        db.session.commit()
        print(f"✅ Restauré {len(existing_users)} utilisateurs")
        
        # Recréer les profils investisseurs avec nouveaux champs
        for profile_data in existing_profiles:
            user = users_map.get(profile_data['user_email'])
            if user:
                profile = InvestorProfile(
                    user_id=user.id,
                    monthly_net_income=profile_data['monthly_net_income'],
                    current_savings=profile_data['current_savings'],
                    monthly_savings_capacity=profile_data['monthly_savings_capacity'],
                    risk_tolerance=profile_data['risk_tolerance'],
                    investment_experience=profile_data['investment_experience'],
                    investment_goals=profile_data['investment_goals'],
                    investment_horizon=profile_data['investment_horizon'],
                    family_situation=profile_data['family_situation'],
                    professional_situation=profile_data['professional_situation'],
                    
                    # Champs existants
                    has_livret_a=profile_data['has_livret_a'],
                    livret_a_value=profile_data['livret_a_value'],
                    has_pea=profile_data['has_pea'],
                    pea_value=profile_data['pea_value'],
                    has_per=profile_data.get('has_per', False),
                    per_value=profile_data.get('per_value', 0.0),
                    has_life_insurance=profile_data['has_life_insurance'],
                    life_insurance_value=profile_data['life_insurance_value'],
                    has_current_account=profile_data.get('has_current_account', False),
                    current_account_value=profile_data.get('current_account_value', 0.0),
                    has_real_estate=profile_data['has_real_estate'],
                    real_estate_value=profile_data['real_estate_value'],
                    
                    # Nouveaux champs avec valeurs par défaut
                    civilite=None,
                    date_naissance=None,
                    nationalite=None,
                    pays_residence=None,
                    revenus_bruts_mensuels=None,
                    charges_mensuelles=None,
                    has_immobilier=False,
                    immobilier_value=0.0,
                    has_autres_biens=False,
                    autres_biens_value=0.0,
                    objectif_constitution_epargne=False,
                    objectif_retraite=False,
                    objectif_transmission=False,
                    objectif_defiscalisation=False,
                    objectif_immobilier=False,
                    profil_risque_connu=False,
                    profil_risque_choisi=None,
                    question_1_reponse=None,
                    question_2_reponse=None,
                    question_3_reponse=None,
                    question_4_reponse=None,
                    question_5_reponse=None,
                    synthese_profil_risque=None
                )
                db.session.add(profile)
        
        db.session.commit()
        print(f"✅ Restauré {len(existing_profiles)} profils avec nouveaux champs")
        
        # Recréer les abonnements
        for sub_data in existing_subscriptions:
            user = users_map.get(sub_data['user_email'])
            if user:
                subscription = Subscription(
                    user_id=user.id,
                    tier=sub_data['tier'],
                    status=sub_data['status'],
                    price=sub_data['price'],
                    start_date=sub_data['start_date'],
                    next_billing_date=sub_data['next_billing_date'],
                    last_payment_date=sub_data['last_payment_date']
                )
                db.session.add(subscription)
        
        db.session.commit()
        print(f"✅ Restauré {len(existing_subscriptions)} abonnements")
        
        # Résumé final
        print(f"""
🎉 MIGRATION TERMINÉE AVEC SUCCÈS !

📊 STATISTIQUES:
- Utilisateurs: {User.query.count()}
- Prospects: {User.query.filter_by(is_prospect=True).count()}
- Clients: {User.query.filter_by(is_prospect=False, is_admin=False).count()}
- Profils investisseurs: {InvestorProfile.query.count()}
- Abonnements: {Subscription.query.count()}

🆕 NOUVEAUX CHAMPS DISPONIBLES:
✅ Section Identité: civilité, date_naissance, nationalité, pays_résidence
✅ Section Revenus: revenus_bruts_mensuels, charges_mensuelles  
✅ Section Patrimoine: immobilier, autres_biens (nouvelles catégories)
✅ Section Objectifs: 5 objectifs d'investissement
✅ Section Profil de risque: profil_risque_connu, profil_risque_choisi
✅ Section Questions: 5 questions + synthèse automatique
✅ Support des crédits multiples via modèle Credit

🔧 PROCHAINES ÉTAPES:
1. Tester le nouveau questionnaire
2. Mettre à jour la route de traitement du formulaire
3. Ajouter les nouveaux calculs au dashboard
        """)

if __name__ == "__main__":
    print("🚀 Lancement de la migration vers le questionnaire étendu...")
    migrate_extended_questionnaire()
    print("🎉 Migration terminée !")