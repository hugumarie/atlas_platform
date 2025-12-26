#!/usr/bin/env python3
"""
Script de création d'utilisateurs pour Atlas
Usage: python create_users.py
"""

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def create_admin():
    """Crée l'utilisateur administrateur par défaut"""
    admin = User(
        email='admin@atlas.com',
        password_hash=generate_password_hash('admin'),
        role='admin',
        email_verified=True
    )
    return admin

def create_test_user():
    """Crée un utilisateur de test"""
    user = User(
        email='test@atlas.com',
        password_hash=generate_password_hash('test'),
        role='user',
        email_verified=True
    )
    return user

def main():
    """Fonction principale"""
    app = create_app()
    
    with app.app_context():
        print("🚀 Création des utilisateurs Atlas...")
        
        # Supprimer les anciens utilisateurs s'ils existent
        old_admin = User.query.filter_by(email='admin@atlas.com').first()
        if old_admin:
            db.session.delete(old_admin)
            print("🗑️ Ancien admin supprimé")
            
        old_test = User.query.filter_by(email='test@atlas.com').first()
        if old_test:
            db.session.delete(old_test)
            print("🗑️ Ancien utilisateur test supprimé")
        
        # Créer les nouveaux utilisateurs
        admin = create_admin()
        test_user = create_test_user()
        
        db.session.add(admin)
        db.session.add(test_user)
        db.session.commit()
        
        print("✅ Utilisateurs créés avec succès !")
        print("")
        print("👤 ADMIN:")
        print("   Email: admin@atlas.com")
        print("   Mot de passe: admin")
        print("")
        print("👤 UTILISATEUR TEST:")
        print("   Email: test@atlas.com")
        print("   Mot de passe: test")
        print("")
        print("🌐 Connexion sur: http://167.172.108.93")

if __name__ == '__main__':
    main()