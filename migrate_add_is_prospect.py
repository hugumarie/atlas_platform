#!/usr/bin/env python3
"""
Script de migration pour ajouter le champ is_prospect et migrer les données existantes.
"""

import sys
sys.path.append('.')

from run import app
from app import db
from app.models.user import User

def migrate_users():
    """
    Ajoute la colonne is_prospect et migre les données existantes.
    """
    with app.app_context():
        try:
            # Ajouter la colonne is_prospect si elle n'existe pas
            db.engine.execute("ALTER TABLE users ADD COLUMN is_prospect BOOLEAN DEFAULT FALSE NOT NULL")
            print("✅ Colonne is_prospect ajoutée")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️  Colonne is_prospect existe déjà")
            else:
                print(f"❌ Erreur lors de l'ajout de la colonne: {e}")
        
        # Migrer les données existantes
        users = User.query.all()
        print(f"📊 Migration de {len(users)} utilisateurs...")
        
        for user in users:
            # Règle de migration :
            # - Si user_type = 'prospect' ET pas de mot de passe → is_prospect = True (prospect sans compte)
            # - Si user_type = 'client' OU prospect avec mot de passe → is_prospect = False (utilisateur avec compte)
            
            if user.user_type == 'prospect' and not user.password_hash:
                user.is_prospect = True
                print(f"🔄 {user.email} → prospect sans compte (is_prospect=True)")
            else:
                user.is_prospect = False
                print(f"✅ {user.email} → utilisateur avec compte (is_prospect=False)")
        
        try:
            db.session.commit()
            print("✅ Migration terminée avec succès")
            
            # Afficher le résumé
            prospects = User.query.filter_by(is_prospect=True).count()
            users_with_accounts = User.query.filter_by(is_prospect=False, is_admin=False).count()
            admins = User.query.filter_by(is_admin=True).count()
            
            print(f"""
📈 RÉSUMÉ DE LA MIGRATION:
- Prospects sans compte: {prospects}
- Utilisateurs avec compte: {users_with_accounts}
- Administrateurs: {admins}
- Total: {prospects + users_with_accounts + admins}
            """)
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de la sauvegarde: {e}")

if __name__ == "__main__":
    print("🚀 Démarrage de la migration is_prospect...")
    migrate_users()
    print("🎉 Migration terminée !")