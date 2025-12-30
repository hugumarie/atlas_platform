#!/usr/bin/env python3
"""
Corriger TOUS les utilisateurs sans plan d'abonnement
"""

from app import create_app, db
from app.models.user import User
from app.models.subscription import Subscription
from datetime import datetime, timedelta

app = create_app()
with app.app_context():
    print("🔧 CORRECTION DE TOUS LES UTILISATEURS SANS PLAN")
    print("==============================================")
    
    # Trouver tous les utilisateurs non-admin, non-prospect sans abonnement
    users = User.query.filter_by(is_admin=False, is_prospect=False).all()
    
    fixed_count = 0
    
    for user in users:
        # Vérifier s'il a un abonnement
        existing_sub = Subscription.query.filter_by(user_id=user.id).first()
        
        if not existing_sub:
            print(f"🔧 Correction de {user.email}...")
            
            # Créer un abonnement INITIA par défaut
            subscription = Subscription(
                user_id=user.id,
                tier='initia',  # Plan par défaut
                status='active',
                start_date=user.created_at or datetime.utcnow(),
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(subscription)
            fixed_count += 1
            
            print(f"   ✅ Abonnement INITIA créé")
        else:
            print(f"✅ {user.email} a déjà un abonnement ({existing_sub.tier})")
    
    if fixed_count > 0:
        db.session.commit()
        print(f"\n🎉 {fixed_count} utilisateur(s) corrigé(s) !")
    else:
        print(f"\n✅ Tous les utilisateurs ont déjà un abonnement")
    
    print()
    print("📋 Prochaine étape: Redémarrer Flask pour tester avec le système de secours")