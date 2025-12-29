#!/usr/bin/env python3
"""
Script de test pour diagnostiquer les problèmes d'upload des formations/apprentissages.
Ce script teste la création d'une formation avec upload de fichiers.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.apprentissage import Apprentissage
import tempfile
from datetime import datetime

def test_apprentissage_creation():
    """Test de création d'un apprentissage"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🧪 Test de création d'apprentissage...")
            
            # 1. Vérifier que la table existe
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            table_exists = inspector.has_table('apprentissages')
            print(f"✅ Table apprentissages existe: {table_exists}")
            
            # 2. Vérifier le dossier uploads
            upload_dir = os.path.join('app', 'static', 'uploads', 'apprentissages')
            upload_exists = os.path.exists(upload_dir)
            upload_writable = os.access(upload_dir, os.W_OK) if upload_exists else False
            print(f"✅ Dossier uploads existe: {upload_exists}")
            print(f"✅ Dossier uploads accessible en écriture: {upload_writable}")
            print(f"📁 Chemin upload: {os.path.abspath(upload_dir)}")
            
            # 3. Tenter de créer un apprentissage simple (sans fichier)
            test_apprentissage = Apprentissage(
                nom="Test Formation",
                description="Formation de test pour diagnostique",
                ordre=999,
                actif=True
            )
            
            db.session.add(test_apprentissage)
            db.session.commit()
            print(f"✅ Apprentissage créé avec ID: {test_apprentissage.id}")
            
            # 4. Tester la création d'un fichier de test
            if upload_exists and upload_writable:
                from datetime import datetime as dt
                test_file_path = os.path.join(upload_dir, f"test_{dt.now().strftime('%Y%m%d_%H%M%S')}.txt")
                try:
                    with open(test_file_path, 'w') as f:
                        f.write("Test file for upload directory")
                    print(f"✅ Fichier de test créé: {test_file_path}")
                    
                    # Nettoyer le fichier de test
                    os.remove(test_file_path)
                    print("✅ Fichier de test supprimé")
                except Exception as file_error:
                    print(f"❌ Erreur création fichier test: {file_error}")
            
            # 5. Vérifier les imports nécessaires
            try:
                import uuid
                import werkzeug.utils
                from datetime import datetime
                print("✅ Tous les imports nécessaires sont disponibles")
            except ImportError as import_error:
                print(f"❌ Import manquant: {import_error}")
            
            # 6. Nettoyer - supprimer l'apprentissage de test
            db.session.delete(test_apprentissage)
            db.session.commit()
            print("✅ Apprentissage de test supprimé")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")
            import traceback
            traceback.print_exc()
            return False

def check_form_processing():
    """Vérifier les aspects spécifiques du traitement des formulaires"""
    print("\n🔍 Diagnostic du traitement des formulaires...")
    
    # Vérifier les importations dans admin.py
    try:
        from flask import request
        from werkzeug.utils import secure_filename
        import uuid
        import os
        print("✅ Imports Flask/Werkzeug OK")
    except ImportError as e:
        print(f"❌ Import manquant: {e}")
        return False
    
    # Vérifier la configuration Flask pour les uploads
    app = create_app()
    with app.app_context():
        print(f"📝 UPLOAD_FOLDER: {app.config.get('UPLOAD_FOLDER')}")
        print(f"📝 MAX_CONTENT_LENGTH: {app.config.get('MAX_CONTENT_LENGTH')}")
        print(f"📝 UPLOAD_EXTENSIONS: {app.config.get('UPLOAD_EXTENSIONS')}")
    
    return True

def main():
    """Fonction principale de diagnostic"""
    print("🚀 Diagnostic du système d'upload des apprentissages")
    print("=" * 60)
    
    # Test 1: Vérification de base
    success = test_apprentissage_creation()
    
    # Test 2: Vérification formulaires
    form_ok = check_form_processing()
    
    print("\n📊 Résumé du diagnostic:")
    print(f"✅ Création apprentissage: {'OK' if success else 'ERREUR'}")
    print(f"✅ Configuration formulaires: {'OK' if form_ok else 'ERREUR'}")
    
    if success and form_ok:
        print("\n✨ Le système d'upload semble fonctionnel.")
        print("💡 Si les uploads échouent, le problème pourrait être:")
        print("   - Problème de validation côté client (JavaScript)")
        print("   - Erreur de traitement spécifique dans la route POST")
        print("   - Problème de permissions en environnement de production")
        print("   - Taille de fichier dépassant les limites du serveur web")
    else:
        print("\n❌ Problèmes détectés dans le système d'upload")
        print("💡 Vérifiez les erreurs ci-dessus pour identifier la cause")

if __name__ == '__main__':
    main()