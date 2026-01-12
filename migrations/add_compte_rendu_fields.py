#!/usr/bin/env python3
"""
Migration pour ajouter les champs titre, type_rdv et prochaine_action à la table comptes_rendus.

Commandes :
- Pour appliquer la migration : python migrations/add_compte_rendu_fields.py
- Pour vérifier l'état : python migrations/add_compte_rendu_fields.py --check
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import inspect, text
import argparse

def add_compte_rendu_columns():
    """Ajouter les colonnes titre, type_rdv et prochaine_action"""
    app = create_app()

    with app.app_context():
        try:
            # Vérifier si la table existe
            inspector = inspect(db.engine)
            if not inspector.has_table('comptes_rendus'):
                print("❌ La table 'comptes_rendus' n'existe pas.")
                return False

            # Vérifier quelles colonnes existent déjà
            columns = [col['name'] for col in inspector.get_columns('comptes_rendus')]
            columns_to_add = []

            if 'titre' not in columns:
                columns_to_add.append(('titre', 'VARCHAR(200)'))
            else:
                print("✅ La colonne 'titre' existe déjà.")

            if 'type_rdv' not in columns:
                columns_to_add.append(('type_rdv', 'VARCHAR(50)'))
            else:
                print("✅ La colonne 'type_rdv' existe déjà.")

            if 'prochaine_action' not in columns:
                columns_to_add.append(('prochaine_action', 'VARCHAR(50)'))
            else:
                print("✅ La colonne 'prochaine_action' existe déjà.")

            # Si toutes les colonnes existent déjà
            if not columns_to_add:
                print("✅ Toutes les colonnes existent déjà.")
                return True

            # Ajouter les nouvelles colonnes
            print(f"📦 Ajout de {len(columns_to_add)} colonne(s)...")

            with db.engine.connect() as conn:
                with conn.begin():
                    for column_name, column_type in columns_to_add:
                        print(f"  - Ajout de '{column_name}'...")
                        conn.execute(text(f"ALTER TABLE comptes_rendus ADD COLUMN {column_name} {column_type}"))
                        print(f"  ✅ Colonne '{column_name}' ajoutée avec succès.")

            return True

        except Exception as e:
            print(f"❌ Erreur lors de l'ajout des colonnes : {e}")
            return False

def check_columns_status():
    """Vérifier l'état des colonnes"""
    app = create_app()

    with app.app_context():
        try:
            # Vérifier l'existence de la table et des colonnes
            inspector = inspect(db.engine)

            if not inspector.has_table('comptes_rendus'):
                print("❌ Table 'comptes_rendus' : N'EXISTE PAS")
                return False

            print("✅ Table 'comptes_rendus' : EXISTE")

            columns = [col['name'] for col in inspector.get_columns('comptes_rendus')]
            required_columns = ['titre', 'type_rdv', 'prochaine_action']

            all_exist = True
            for col_name in required_columns:
                if col_name in columns:
                    print(f"  ✅ Colonne '{col_name}' : EXISTE")
                else:
                    print(f"  ❌ Colonne '{col_name}' : N'EXISTE PAS")
                    all_exist = False

            return all_exist

        except Exception as e:
            print(f"❌ Erreur lors de la vérification : {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Migration pour les colonnes titre, type_rdv et prochaine_action')
    parser.add_argument('--check', action='store_true', help='Vérifier l\'état des colonnes')

    args = parser.parse_args()

    print("🚀 Migration des colonnes CompteRendu")
    print("=" * 50)

    if args.check:
        print("🔍 Vérification de l'état des colonnes...")
        check_columns_status()
    else:
        print("📦 Ajout des colonnes...")
        success = add_compte_rendu_columns()

        if success:
            print("\n🎉 Migration terminée avec succès !")
            print("\nPour vérifier l'état :")
            print("python migrations/add_compte_rendu_fields.py --check")
        else:
            print("\n❌ La migration a échoué.")
            sys.exit(1)

if __name__ == '__main__':
    main()
