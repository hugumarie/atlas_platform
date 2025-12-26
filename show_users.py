#!/usr/bin/env python3
"""
Script pour afficher tous les utilisateurs de la base Atlas
"""

from app import create_app, db
from app.models.user import User

def show_all_users():
    app = create_app()
    
    with app.app_context():
        users = User.query.all()
        
        print(f"\n🔍 TOTAL: {len(users)} utilisateurs trouvés\n")
        print("=" * 50)
        
        for i, user in enumerate(users, 1):
            print(f"\n👤 UTILISATEUR #{i}")
            print(f"📧 Email: {user.email}")
            print(f"🆔 ID: {user.id}")
            
            # Afficher toutes les colonnes
            for column in user.__table__.columns:
                column_name = column.name
                value = getattr(user, column_name, 'N/A')
                
                # Ne pas afficher le mot de passe hashé
                if 'password' not in column_name.lower():
                    print(f"   {column_name}: {value}")
            
            print("-" * 30)

if __name__ == "__main__":
    show_all_users()