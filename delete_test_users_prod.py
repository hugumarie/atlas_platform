#!/usr/bin/env python3
"""
Script pour supprimer les utilisateurs de test en production.
"""

import sys
import os
sys.path.append('.')

from app import create_app, db
from app.models.user import User

def delete_test_users():
    app = create_app()
    
    with app.app_context():
        # Liste des emails à supprimer
        emails_to_delete = [
            'mich@yopmail.com',
            'curry@yopmail.fr', 
            'celine@yopmail.com',
            'usertest@yopmail.com'
        ]
        
        print('🗑️ Suppression des utilisateurs de test en production...')
        
        deleted_count = 0
        for email in emails_to_delete:
            user = User.query.filter_by(email=email).first()
            if user:
                print(f'✅ Suppression: {user.first_name} {user.last_name} ({email})')
                # La cascade delete s'occupe automatiquement des profils investisseurs
                db.session.delete(user)
                deleted_count += 1
            else:
                print(f'❌ Utilisateur non trouvé: {email}')
        
        try:
            db.session.commit()
            print(f'✅ Suppression terminée! {deleted_count} utilisateur(s) supprimé(s)')
            
            # Vérifier les utilisateurs restants
            remaining_users = User.query.filter_by(is_admin=False, is_prospect=False).all()
            print(f'👥 Utilisateurs clients restants: {len(remaining_users)}')
            for user in remaining_users:
                print(f'  - {user.first_name} {user.last_name} ({user.email})')
                
            # Vérifier les prospects
            prospects = User.query.filter_by(is_prospect=True).all()
            print(f'🎯 Prospects restants: {len(prospects)}')
            for prospect in prospects:
                print(f'  - {prospect.first_name} {prospect.last_name} ({prospect.email})')
            
        except Exception as e:
            db.session.rollback()
            print(f'❌ Erreur: {e}')

if __name__ == "__main__":
    delete_test_users()