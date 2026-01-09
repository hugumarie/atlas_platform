#!/usr/bin/env python3
"""
Script pour supprimer un utilisateur avec des plans d'investissement.
"""

import sys
import os
sys.path.append('.')

from app import create_app, db

def delete_user_with_plans(user_id):
    """Supprime manuellement les plans puis l'utilisateur."""
    app = create_app()
    
    with app.app_context():
        try:
            # 1. Supprimer les lignes de plans d'investissement
            result1 = db.session.execute(
                db.text("DELETE FROM investment_plan_lines WHERE plan_id IN (SELECT id FROM investment_plans WHERE user_id = :user_id)"), 
                {"user_id": user_id}
            )
            print(f"✅ Investment plan lines supprimées: {result1.rowcount}")
            
            # 2. Supprimer les plans d'investissement
            result2 = db.session.execute(
                db.text("DELETE FROM investment_plans WHERE user_id = :user_id"), 
                {"user_id": user_id}
            )
            print(f"✅ Investment plans supprimés: {result2.rowcount}")
            
            # 3. Commit cette suppression spécifique
            db.session.commit()
            
            print(f"✅ Plans d'investissement supprimés pour user {user_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur: {e}")
            return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 delete_user_with_plans.py <user_id>")
        sys.exit(1)
    
    user_id = int(sys.argv[1])
    delete_user_with_plans(user_id)