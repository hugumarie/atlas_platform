#!/usr/bin/env python3
"""
Migration pour créer la table apprentissages.
Cette migration ajoute la fonctionnalité de gestion des formations/apprentissages.

Commandes :
- Pour appliquer la migration : python migrations/add_apprentissage_table.py
- Pour vérifier l'état : python migrations/add_apprentissage_table.py --check
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.apprentissage import Apprentissage
import argparse
from sqlalchemy import inspect

def create_apprentissage_table():
    """Créer la table apprentissages"""
    app = create_app()
    
    with app.app_context():
        try:
            # Vérifier si la table existe déjà
            inspector = inspect(db.engine)
            if inspector.has_table('apprentissages'):
                print("✅ La table 'apprentissages' existe déjà.")
                return True
            
            # Créer la table
            print("📦 Création de la table 'apprentissages'...")
            db.create_all()
            print("✅ Table 'apprentissages' créée avec succès.")
            
            # Créer le dossier pour les uploads si nécessaire
            upload_dir = os.path.join('app', 'static', 'uploads', 'apprentissages')
            os.makedirs(upload_dir, exist_ok=True)
            print("📁 Dossier uploads créé :", upload_dir)
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de la table : {e}")
            return False

def check_table_status():
    """Vérifier l'état de la table apprentissages"""
    app = create_app()
    
    with app.app_context():
        try:
            # Vérifier l'existence de la table
            inspector = inspect(db.engine)
            table_exists = inspector.has_table('apprentissages')
            
            if table_exists:
                # Compter le nombre d'enregistrements
                count = Apprentissage.query.count()
                print(f"✅ Table 'apprentissages' : EXISTE ({count} enregistrement(s))")
                
                # Vérifier le dossier uploads
                upload_dir = os.path.join('app', 'static', 'uploads', 'apprentissages')
                if os.path.exists(upload_dir):
                    files_count = len([f for f in os.listdir(upload_dir) if f.endswith('.pdf')])
                    print(f"📁 Dossier uploads : EXISTE ({files_count} fichier(s) PDF)")
                else:
                    print("📁 Dossier uploads : N'EXISTE PAS")
                
            else:
                print("❌ Table 'apprentissages' : N'EXISTE PAS")
            
            return table_exists
            
        except Exception as e:
            print(f"❌ Erreur lors de la vérification : {e}")
            return False

def add_sample_data():
    """Ajouter des données d'exemple (optionnel)"""
    app = create_app()
    
    with app.app_context():
        try:
            # Vérifier si des données existent déjà
            if Apprentissage.query.count() > 0:
                print("ℹ️ Des formations existent déjà, aucune donnée d'exemple ajoutée.")
                return True
            
            print("📚 Ajout de formations d'exemple...")
            
            formations_exemple = [
                {
                    'nom': 'Introduction aux placements financiers',
                    'description': 'Découvrez les bases de l\'investissement et apprenez à diversifier votre portefeuille pour optimiser vos rendements.',
                    'ordre': 1
                },
                {
                    'nom': 'Optimisation fiscale et PEA',
                    'description': 'Maîtrisez les enveloppes fiscales avantageuses et réduisez votre imposition sur les plus-values.',
                    'ordre': 2
                },
                {
                    'nom': 'Assurance vie et stratégie patrimoniale',
                    'description': 'Utilisez l\'assurance vie comme pilier de votre stratégie d\'épargne et de transmission.',
                    'ordre': 3
                }
            ]
            
            for formation_data in formations_exemple:
                formation = Apprentissage(
                    nom=formation_data['nom'],
                    description=formation_data['description'],
                    ordre=formation_data['ordre'],
                    actif=True
                )
                db.session.add(formation)
            
            db.session.commit()
            print(f"✅ {len(formations_exemple)} formations d'exemple ajoutées.")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de l'ajout des données d'exemple : {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Migration pour la table apprentissages')
    parser.add_argument('--check', action='store_true', help='Vérifier l\'état de la table')
    parser.add_argument('--sample', action='store_true', help='Ajouter des données d\'exemple')
    parser.add_argument('--force', action='store_true', help='Forcer la recréation de la table')
    
    args = parser.parse_args()
    
    print("🚀 Migration de la table 'apprentissages'")
    print("=" * 50)
    
    if args.check:
        print("🔍 Vérification de l'état de la table...")
        check_table_status()
        
    elif args.sample:
        print("📚 Ajout de données d'exemple...")
        add_sample_data()
        
    elif args.force:
        print("⚠️ Mode force - Recréation de la table...")
        app = create_app()
        with app.app_context():
            # Supprimer la table si elle existe
            inspector = inspect(db.engine)
            if inspector.has_table('apprentissages'):
                Apprentissage.__table__.drop(db.engine)
                print("🗑️ Table supprimée.")
            
            # Recréer la table
            create_apprentissage_table()
        
    else:
        print("📦 Création de la table...")
        success = create_apprentissage_table()
        
        if success:
            print("\n🎉 Migration terminée avec succès !")
            print("\nPour ajouter des formations d'exemple :")
            print("python migrations/add_apprentissage_table.py --sample")
            print("\nPour vérifier l'état :")
            print("python migrations/add_apprentissage_table.py --check")
        else:
            print("\n❌ La migration a échoué.")
            sys.exit(1)

if __name__ == '__main__':
    main()