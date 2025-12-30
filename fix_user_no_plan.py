#!/usr/bin/env python3
"""
Corriger les utilisateurs sans plan d'abonnement
"""

from app import create_app, db
from app.models.user import User
from app.models.subscription import Subscription
from datetime import datetime, timedelta

app = create_app()
with app.app_context():
    print("🔧 CORRECTION UTILISATEURS SANS PLAN")
    print("===================================")
    
    # Trouver hugues.marie925@gmail.com
    user = User.query.filter_by(email='hugues.marie925@gmail.com').first()
    
    if not user:
        print("❌ Utilisateur hugues.marie925@gmail.com non trouvé")
    else:
        print(f"✅ Utilisateur trouvé: {user.email}")
        
        # Vérifier s'il a déjà un abonnement
        existing_sub = Subscription.query.filter_by(user_id=user.id).first()
        
        if existing_sub:
            print(f"✅ Abonnement existant: {existing_sub.tier} ({existing_sub.status})")
        else:
            # Créer un abonnement INITIA par défaut (le plus probable)
            subscription = Subscription(
                user_id=user.id,
                tier='initia',
                status='active',
                start_date=datetime.utcnow(),
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(subscription)
            db.session.commit()
            
            print(f"✅ Abonnement INITIA créé pour {user.email}")
            print(f"   - Période: {subscription.current_period_start.strftime('%d/%m/%Y')} → {subscription.current_period_end.strftime('%d/%m/%Y')}")
    
    print()
    print("🧪 Test d'accès au dashboard maintenant disponible !")