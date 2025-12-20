#!/usr/bin/env python3
"""
Script pour créer automatiquement les tables de plan d'investissement.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.investment_plan import InvestmentPlan, InvestmentPlanLine

def create_tables():
    """Créer les tables de plan d'investissement."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 Création des tables de plan d'investissement...")
            
            # Créer les tables
            db.create_all()
            
            print("✅ Tables créées avec succès!")
            print("  - investment_plans")
            print("  - investment_plan_lines")
            
            # Vérifier que les tables existent
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'investment_plans' in tables and 'investment_plan_lines' in tables:
                print("✅ Vérification : Les tables sont bien créées")
            else:
                print("❌ Erreur : Les tables ne sont pas créées")
                
        except Exception as e:
            print(f"❌ Erreur lors de la création des tables: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_tables()