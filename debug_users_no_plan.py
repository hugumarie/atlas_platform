#!/usr/bin/env python3
"""
Debug: Utilisateurs sans plan d'abonnement
"""

from app import create_app, db
from app.models.user import User
from app.models.subscription import Subscription

app = create_app()
with app.app_context():
    print("🔍 UTILISATEURS SANS PLAN")
    print("=========================")
    
    # Tous les utilisateurs non-admin, non-prospect
    users = User.query.filter_by(is_admin=False, is_prospect=False).all()
    
    print(f"📊 {len(users)} utilisateurs trouvés")
    print()
    
    for user in users:
        subscription = Subscription.query.filter_by(user_id=user.id).first()
        
        print(f"👤 {user.email}")
        print(f"   - ID: {user.id}")
        print(f"   - Créé: {user.created_at}")
        print(f"   - Prospect: {user.is_prospect}")
        print(f"   - Subscription date: {user.subscription_date}")
        
        if subscription:
            print(f"   - Plan: {subscription.tier} ({subscription.status})")
            print(f"   - Stripe Customer: {subscription.stripe_customer_id}")
            print(f"   - Stripe Subscription: {subscription.stripe_subscription_id}")
        else:
            print(f"   - ❌ AUCUN ABONNEMENT")
        
        print()
    
    print("💡 RECOMMANDATIONS:")
    print("1. Vérifier les logs de handle_successful_payment")
    print("2. Corriger l'activation d'abonnement")
    print("3. Créer manuellement l'abonnement si nécessaire")