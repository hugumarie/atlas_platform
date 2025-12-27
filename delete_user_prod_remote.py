#!/usr/bin/env python3
"""
Script générique pour supprimer un utilisateur de la base de données de production (version serveur).
Usage: python3 delete_user_prod_remote.py email@example.com
"""

import sys
import os
sys.path.append('.')

from app import create_app, db
from app.models.user import User

def delete_user(email):
    """Supprime un utilisateur de la base de données de production."""
    app = create_app()
    
    with app.app_context():
        print("🗑️  SUPPRESSION D'UTILISATEUR - BASE DE DONNÉES PRODUCTION")
        print("=" * 60)
        
        if not email:
            print("❌ Email requis!")
            return
        
        # Rechercher l'utilisateur
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"❌ Aucun utilisateur trouvé avec l'email: {email}")
            return
        
        # Afficher les informations de l'utilisateur
        print(f"\n👤 UTILISATEUR TROUVÉ:")
        print(f"   Nom: {user.first_name} {user.last_name}")
        print(f"   Email: {user.email}")
        print(f"   Type: {'Admin' if user.is_admin else 'Prospect' if user.is_prospect else 'Client'}")
        print(f"   Créé le: {user.date_created.strftime('%d/%m/%Y à %H:%M') if user.date_created else 'Inconnu'}")
        
        if user.investor_profile:
            print(f"   Profil investisseur: OUI")
        
        if user.subscription:
            print(f"   Abonnement: {user.subscription.tier} ({user.subscription.status})")
        
        print(f"\n⚠️  SUPPRESSION AUTOMATIQUE (mode serveur)")
        
        if user.is_admin:
            print(f"🚨 ERREUR: Impossible de supprimer un administrateur via ce script!")
            return
        
        # Supprimer l'utilisateur
        try:
            username = f"{user.first_name} {user.last_name}"
            db.session.delete(user)
            db.session.commit()
            
            print(f"\n✅ SUPPRESSION RÉUSSIE!")
            print(f"✅ L'utilisateur {username} ({email}) a été supprimé de la base de données.")
            
            # Statistiques post-suppression
            total_users = User.query.filter_by(is_admin=False, is_prospect=False).count()
            total_prospects = User.query.filter_by(is_prospect=True).count()
            total_admins = User.query.filter_by(is_admin=True).count()
            
            print(f"\n📊 STATISTIQUES ACTUELLES:")
            print(f"   Clients: {total_users}")
            print(f"   Prospects: {total_prospects}")
            print(f"   Admins: {total_admins}")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERREUR lors de la suppression: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 delete_user_prod_remote.py email@example.com")
        sys.exit(1)
    
    email = sys.argv[1].strip().lower()
    delete_user(email)