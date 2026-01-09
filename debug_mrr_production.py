#!/usr/bin/env python3
"""
Script de debug pour analyser le MRR en production
"""

import os
import sys
sys.path.insert(0, '/opt/atlas' if os.path.exists('/opt/atlas') else '.')

from app import create_app, db
from app.models.subscription import Subscription
from app.models.user import User
from sqlalchemy import func

def debug_mrr():
    app = create_app()
    with app.app_context():
        print("=== DEBUG MRR PRODUCTION ===")
        
        # 1. Tous les abonnements
        all_subs = Subscription.query.all()
        print(f"Total abonnements en base: {len(all_subs)}")
        
        # 2. Abonnements actifs
        active_subs = Subscription.query.filter_by(status='active').all()
        print(f"Abonnements actifs: {len(active_subs)}")
        
        # 3. Détail des abonnements actifs
        print("\n=== DÉTAIL ABONNEMENTS ACTIFS ===")
        total_mrr = 0
        for sub in active_subs:
            user = User.query.get(sub.user_id)
            print(f"User: {user.email if user else 'N/A'}")
            print(f"  - Status: {sub.status}")
            print(f"  - Tier: {sub.tier}")
            print(f"  - Price: {sub.price}€")
            print(f"  - Stripe ID: {sub.stripe_subscription_id}")
            print("---")
            total_mrr += sub.price or 0
        
        # 4. MRR calculé
        print(f"\n=== CALCUL MRR ===")
        print(f"MRR total calculé: {total_mrr}€")
        
        # 5. Répartition par tier
        initia = Subscription.query.filter_by(status='active', tier='initia').count()
        optima = Subscription.query.filter_by(status='active', tier='optima').count()
        print(f"Initia: {initia}")
        print(f"Optima: {optima}")
        
        # 6. Requête SQL directe
        mrr_sql = db.session.query(func.sum(Subscription.price)).filter(
            Subscription.status == 'active'
        ).scalar()
        print(f"MRR via SQL: {mrr_sql}")

if __name__ == "__main__":
    debug_mrr()