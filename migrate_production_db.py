#!/usr/bin/env python3
"""
Migration de la base de données production pour Atlas
Ajoute les colonnes manquantes créées en développement
"""

import os
import sys

def main():
    """Migration principale"""
    
    print("🔧 MIGRATION BASE DE DONNÉES ATLAS PRODUCTION")
    print("=" * 50)
    print()
    
    # Import des modules Flask
    try:
        from app import create_app, db
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            print("✅ Connexion à la base de données réussie")
            print()
            
            # Liste des migrations à appliquer
            migrations = [
                {
                    'table': 'investor_profiles',
                    'column': 'calculated_risk_profile',
                    'type': 'VARCHAR(20)',
                    'description': 'Profil de risque calculé (PRUDENT, EQUILIBRE, DYNAMIQUE)'
                },
                {
                    'table': 'apprentissages',
                    'column': 'categorie', 
                    'type': 'VARCHAR(100)',
                    'description': 'Catégorie de formation (enveloppes, produits, strategies, autres)'
                },
                {
                    'table': 'apprentissages',
                    'column': 'storage_type',
                    'type': 'VARCHAR(20) DEFAULT \'local\'',
                    'description': 'Type de stockage (local ou digitalocean)'
                },
                {
                    'table': 'apprentissages',
                    'column': 'fichier_pdf_url',
                    'type': 'VARCHAR(500)', 
                    'description': 'URL publique du PDF sur DigitalOcean Spaces'
                },
                {
                    'table': 'apprentissages',
                    'column': 'image_url',
                    'type': 'VARCHAR(500)',
                    'description': 'URL publique de l\'image sur DigitalOcean Spaces'
                }
            ]
            
            # Appliquer chaque migration
            for migration in migrations:
                table = migration['table']
                column = migration['column'] 
                col_type = migration['type']
                description = migration['description']
                
                print(f"📋 {table}.{column}")
                print(f"   Type: {col_type}")
                print(f"   Description: {description}")
                
                try:
                    # Vérifier si la colonne existe déjà
                    check_sql = text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = :table_name 
                        AND column_name = :column_name
                    """)
                    
                    result = db.session.execute(check_sql, {
                        'table_name': table,
                        'column_name': column
                    }).fetchone()
                    
                    if result:
                        print(f"   ✅ Existe déjà")
                    else:
                        # Ajouter la colonne
                        alter_sql = text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
                        db.session.execute(alter_sql)
                        db.session.commit()
                        print(f"   ✅ Ajoutée avec succès")
                        
                except Exception as e:
                    print(f"   ❌ Erreur: {e}")
                    db.session.rollback()
                    return False
                    
                print()
            
            print("🎉 MIGRATION TERMINÉE AVEC SUCCÈS !")
            print()
            print("📊 Résumé:")
            print("   - investor_profiles.calculated_risk_profile: Profil de risque calculé")
            print("   - apprentissages.categorie: Catégories de formations") 
            print("   - apprentissages.storage_type: Type de stockage (local/cloud)")
            print("   - apprentissages.fichier_pdf_url: URLs DigitalOcean PDF")
            print("   - apprentissages.image_url: URLs DigitalOcean images")
            print()
            print("✅ Base de données production synchronisée avec le développement")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur de migration: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)