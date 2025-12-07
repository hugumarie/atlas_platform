#!/usr/bin/env python3
"""
Migration pour ajouter le champ fichier_pdf_original à la table apprentissages.
Cette migration permet de conserver le nom original des fichiers PDF.

Commandes :
- Pour appliquer la migration : python migrations/add_pdf_original_name.py
- Pour vérifier l'état : python migrations/add_pdf_original_name.py --check
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.apprentissage import Apprentissage
import argparse
from sqlalchemy import inspect, text

def add_pdf_original_column():
    """Ajouter la colonne fichier_pdf_original"""
    app = create_app()
    
    with app.app_context():
        try:
            # Vérifier si la table existe
            inspector = inspect(db.engine)
            if not inspector.has_table('apprentissages'):
                print("❌ La table 'apprentissages' n'existe pas.")
                return False
            
            # Vérifier si la colonne existe déjà
            columns = [col['name'] for col in inspector.get_columns('apprentissages')]
            if 'fichier_pdf_original' in columns:
                print("✅ La colonne 'fichier_pdf_original' existe déjà.")
                return True
            
            # Ajouter la nouvelle colonne
            print("📦 Ajout de la colonne 'fichier_pdf_original'...")
            
            # Utiliser SQL brut pour ajouter la colonne
            with db.engine.connect() as conn:
                with conn.begin():
                    conn.execute(text("ALTER TABLE apprentissages ADD COLUMN fichier_pdf_original VARCHAR(255)"))
            
            print("✅ Colonne 'fichier_pdf_original' ajoutée avec succès.")
            
            # Optionnel : Mettre à jour les enregistrements existants
            print("🔄 Mise à jour des enregistrements existants...")
            try:
                # Récupérer les apprentissages avec des PDFs en utilisant SQL brut
                with db.engine.connect() as conn:
                    result = conn.execute(text("SELECT id, fichier_pdf FROM apprentissages WHERE fichier_pdf IS NOT NULL"))
                    apprentissages_data = result.fetchall()
                
                # Mettre à jour chaque enregistrement
                for row in apprentissages_data:
                    apprentissage_id, filename = row
                    if filename:
                        # Essayer d'extraire le nom original du nom du fichier
                        if '_' in filename and filename.count('_') >= 2:
                            # Format: timestamp_original_name.pdf
                            parts = filename.split('_', 2)
                            if len(parts) >= 3:
                                original_name = '_'.join(parts[2:])
                            else:
                                original_name = filename
                        else:
                            original_name = filename
                        
                        # Mettre à jour avec SQL brut
                        with db.engine.connect() as conn:
                            with conn.begin():
                                conn.execute(text("UPDATE apprentissages SET fichier_pdf_original = :original WHERE id = :id"), 
                                           {'original': original_name, 'id': apprentissage_id})
                
                print(f"✅ {len(apprentissages_data)} enregistrement(s) mis à jour.")
            except Exception as update_error:
                print(f"⚠️ Erreur lors de la mise à jour des enregistrements : {update_error}")
                print("La colonne a été ajoutée mais les données existantes n'ont pas pu être mises à jour.")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout de la colonne : {e}")
            return False

def check_column_status():
    """Vérifier l'état de la colonne fichier_pdf_original"""
    app = create_app()
    
    with app.app_context():
        try:
            # Vérifier l'existence de la table et de la colonne
            inspector = inspect(db.engine)
            
            if not inspector.has_table('apprentissages'):
                print("❌ Table 'apprentissages' : N'EXISTE PAS")
                return False
            
            columns = [col['name'] for col in inspector.get_columns('apprentissages')]
            
            if 'fichier_pdf_original' in columns:
                # Compter le nombre d'enregistrements avec des PDFs
                count_total = Apprentissage.query.filter(Apprentissage.fichier_pdf.isnot(None)).count()
                count_with_original = Apprentissage.query.filter(Apprentissage.fichier_pdf_original.isnot(None)).count()
                print(f"✅ Colonne 'fichier_pdf_original' : EXISTE")
                print(f"📊 {count_with_original}/{count_total} PDF(s) avec nom original")
            else:
                print("❌ Colonne 'fichier_pdf_original' : N'EXISTE PAS")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la vérification : {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Migration pour la colonne fichier_pdf_original')
    parser.add_argument('--check', action='store_true', help='Vérifier l\'état de la colonne')
    
    args = parser.parse_args()
    
    print("🚀 Migration de la colonne 'fichier_pdf_original'")
    print("=" * 50)
    
    if args.check:
        print("🔍 Vérification de l'état de la colonne...")
        check_column_status()
    else:
        print("📦 Ajout de la colonne...")
        success = add_pdf_original_column()
        
        if success:
            print("\n🎉 Migration terminée avec succès !")
            print("\nPour vérifier l'état :")
            print("python migrations/add_pdf_original_name.py --check")
        else:
            print("\n❌ La migration a échoué.")
            sys.exit(1)

if __name__ == '__main__':
    main()