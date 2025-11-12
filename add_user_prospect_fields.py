#!/usr/bin/env python3
"""
Script pour ajouter les nouveaux champs prospects à la table users existante.
"""

import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au path pour importer l'app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def add_prospect_fields_to_users():
    """
    Ajoute les nouveaux champs prospects à la table users existante.
    """
    app = create_app()
    
    with app.app_context():
        try:
            print("Ajout des nouveaux champs prospects à la table users...")
            
            # Liste des nouveaux champs à ajouter
            new_columns = [
                "ALTER TABLE users ADD COLUMN user_type VARCHAR(20) DEFAULT 'client' NOT NULL",
                "ALTER TABLE users ADD COLUMN prospect_source VARCHAR(50)",
                "ALTER TABLE users ADD COLUMN prospect_status VARCHAR(20) DEFAULT 'nouveau'",
                "ALTER TABLE users ADD COLUMN prospect_notes TEXT",
                "ALTER TABLE users ADD COLUMN appointment_requested BOOLEAN DEFAULT 0 NOT NULL",
                "ALTER TABLE users ADD COLUMN appointment_status VARCHAR(20) DEFAULT 'en_attente'",
                "ALTER TABLE users ADD COLUMN assigned_to VARCHAR(100)",
                "ALTER TABLE users ADD COLUMN last_contact DATETIME",
                "ALTER TABLE users ADD COLUMN invitation_token VARCHAR(255) UNIQUE",
                "ALTER TABLE users ADD COLUMN invitation_sent_at DATETIME",
                "ALTER TABLE users ADD COLUMN invitation_expires_at DATETIME",
                "ALTER TABLE users ADD COLUMN can_create_account BOOLEAN DEFAULT 0 NOT NULL"
            ]
            
            # Exécuter chaque ALTER TABLE
            for sql in new_columns:
                try:
                    db.session.execute(db.text(sql))
                    print(f"✓ {sql}")
                except Exception as e:
                    if "duplicate column name" in str(e) or "already exists" in str(e):
                        print(f"- Colonne déjà existante: {sql}")
                    else:
                        print(f"✗ Erreur: {sql} - {e}")
            
            # Sauvegarder les changements
            db.session.commit()
            
            print("\n✅ Migration terminée avec succès!")
            print("Vous pouvez maintenant utiliser l'application normalement.")
            
        except Exception as e:
            print(f"❌ Erreur lors de la migration: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == "__main__":
    add_prospect_fields_to_users()