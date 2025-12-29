#!/usr/bin/env python3
"""
Migration pour créer la table investment_actions.
"""

from flask import Flask
from sqlalchemy import text
import os
import sys

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def create_investment_actions_table():
    """Crée la table investment_actions."""
    
    app = create_app()
    
    with app.app_context():
        # SQL pour créer la table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS investment_actions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            plan_line_id INTEGER NOT NULL REFERENCES investment_plan_lines(id) ON DELETE CASCADE,
            year_month VARCHAR(7) NOT NULL,
            support_type VARCHAR(50) NOT NULL,
            label VARCHAR(200),
            expected_amount FLOAT NOT NULL DEFAULT 0.0,
            realized_amount FLOAT DEFAULT 0.0,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
            answered_at TIMESTAMP WITHOUT TIME ZONE,
            
            -- Contrainte unique pour éviter les doublons
            CONSTRAINT unique_user_plan_month UNIQUE (user_id, plan_line_id, year_month)
        );
        """
        
        # Créer les index
        create_indexes_sql = """
        CREATE INDEX IF NOT EXISTS idx_investment_actions_user_year_month 
        ON investment_actions (user_id, year_month);
        
        CREATE INDEX IF NOT EXISTS idx_investment_actions_status_year_month 
        ON investment_actions (status, year_month);
        
        CREATE INDEX IF NOT EXISTS idx_investment_actions_user_status 
        ON investment_actions (user_id, status);
        """
        
        try:
            print("🔄 Création de la table investment_actions...")
            
            # Exécuter la création de table
            db.session.execute(text(create_table_sql))
            print("✅ Table investment_actions créée avec succès")
            
            # Exécuter la création des index
            db.session.execute(text(create_indexes_sql))
            print("✅ Index créés avec succès")
            
            # Committer les changements
            db.session.commit()
            print("✅ Migration terminée avec succès")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de la table: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == "__main__":
    success = create_investment_actions_table()
    if success:
        print("\n🎉 Migration investment_actions terminée avec succès !")
        print("\n📋 Prochaines étapes:")
        print("1. Redémarrer Flask")
        print("2. Tester l'import du modèle")
        print("3. Implémenter le générateur d'actions")
    else:
        print("\n❌ La migration a échoué")
        sys.exit(1)