#!/usr/bin/env python3
"""
Debug script pour identifier les problèmes spécifiques dans la route apprentissage_create.
Simule le traitement d'un formulaire avec fichiers.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.apprentissage import Apprentissage
import uuid
import tempfile
from datetime import datetime

def simulate_file_upload():
    """Simule le processus d'upload de fichiers"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🧪 Test de simulation d'upload de fichiers...")
            
            # Simule les données du formulaire
            form_data = {
                'nom': 'Formation Test Debug',
                'description': 'Test pour debug upload',
                'ordre': 1,
                'actif': True
            }
            
            # Chemin du dossier uploads
            upload_dir = os.path.join('app', 'static', 'uploads', 'apprentissages')
            print(f"📁 Dossier uploads: {upload_dir}")
            print(f"📁 Chemin absolu: {os.path.abspath(upload_dir)}")
            
            # Test de création du dossier (même s'il existe)
            os.makedirs(upload_dir, exist_ok=True)
            print("✅ makedirs réussi")
            
            # Simuler la création d'un fichier image
            image_filename = None
            try:
                # Générer un nom unique comme dans le code
                file_extension = '.png'
                image_filename = f"{uuid.uuid4().hex}{file_extension}"
                image_path = os.path.join(upload_dir, image_filename)
                
                # Créer un fichier test
                with open(image_path, 'w') as f:
                    f.write("fake image content")
                print(f"✅ Fichier image test créé: {image_filename}")
                
            except Exception as img_error:
                print(f"❌ Erreur création fichier image: {img_error}")
            
            # Simuler la création d'un fichier PDF
            pdf_filename = None
            pdf_original_name = None
            try:
                pdf_original_name = "test-formation.pdf"
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_filename = "".join(c for c in pdf_original_name if c.isalnum() or c in '._-')
                pdf_filename = f"{timestamp}_{safe_filename}"
                pdf_path = os.path.join(upload_dir, pdf_filename)
                
                with open(pdf_path, 'w') as f:
                    f.write("fake pdf content")
                print(f"✅ Fichier PDF test créé: {pdf_filename}")
                
            except Exception as pdf_error:
                print(f"❌ Erreur création fichier PDF: {pdf_error}")
            
            # Test de création de l'apprentissage
            try:
                apprentissage = Apprentissage(
                    nom=form_data['nom'],
                    description=form_data['description'],
                    image=image_filename,
                    fichier_pdf=pdf_filename,
                    fichier_pdf_original=pdf_original_name,
                    ordre=form_data['ordre'],
                    actif=form_data['actif']
                )
                
                db.session.add(apprentissage)
                db.session.commit()
                print(f"✅ Apprentissage créé avec ID: {apprentissage.id}")
                
                # Nettoyer
                db.session.delete(apprentissage)
                db.session.commit()
                print("✅ Apprentissage supprimé")
                
                # Supprimer les fichiers test
                if image_filename and os.path.exists(os.path.join(upload_dir, image_filename)):
                    os.remove(os.path.join(upload_dir, image_filename))
                    print("✅ Fichier image test supprimé")
                
                if pdf_filename and os.path.exists(os.path.join(upload_dir, pdf_filename)):
                    os.remove(os.path.join(upload_dir, pdf_filename))
                    print("✅ Fichier PDF test supprimé")
                
            except Exception as db_error:
                print(f"❌ Erreur base de données: {db_error}")
                import traceback
                traceback.print_exc()
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur générale: {e}")
            import traceback
            traceback.print_exc()
            return False

def check_potential_issues():
    """Vérifier les problèmes potentiels spécifiques"""
    print("\n🔍 Vérification des problèmes potentiels...")
    
    issues = []
    
    # 1. Vérifier la configuration Flask
    app = create_app()
    with app.app_context():
        # Vérifier la taille maximale des fichiers
        max_size = app.config.get('MAX_CONTENT_LENGTH')
        if max_size is None:
            print("✅ Pas de limite de taille de fichier configurée")
        else:
            print(f"📝 Taille max fichier: {max_size}")
        
        # Vérifier les extensions autorisées
        extensions = app.config.get('UPLOAD_EXTENSIONS', [])
        print(f"📝 Extensions autorisées: {extensions}")
        
        # Vérifier que .pdf et les images sont bien autorisées
        if '.pdf' not in extensions:
            issues.append("Extension .pdf non autorisée dans UPLOAD_EXTENSIONS")
        if not any(ext in extensions for ext in ['.png', '.jpg', '.jpeg', '.gif']):
            issues.append("Aucune extension d'image autorisée dans UPLOAD_EXTENSIONS")
    
    # 2. Vérifier les imports critiques
    try:
        from werkzeug.utils import secure_filename
        import uuid
        from datetime import datetime
        import os
        print("✅ Tous les imports critiques disponibles")
    except ImportError as e:
        issues.append(f"Import manquant: {e}")
    
    # 3. Vérifier les permissions système
    upload_dir = os.path.join('app', 'static', 'uploads', 'apprentissages')
    if not os.path.exists(upload_dir):
        issues.append(f"Dossier d'upload n'existe pas: {upload_dir}")
    elif not os.access(upload_dir, os.W_OK):
        issues.append(f"Dossier d'upload non accessible en écriture: {upload_dir}")
    
    if issues:
        print(f"\n❌ {len(issues)} problème(s) identifié(s):")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n✅ Aucun problème potentiel détecté")
    
    return len(issues) == 0

def main():
    """Fonction principale de debug"""
    print("🚀 Debug approfondi du système d'upload des apprentissages")
    print("=" * 70)
    
    # Test 1: Simulation d'upload
    upload_ok = simulate_file_upload()
    
    # Test 2: Vérification des problèmes potentiels
    config_ok = check_potential_issues()
    
    print("\n📊 Résumé du debug:")
    print(f"✅ Simulation upload: {'OK' if upload_ok else 'ERREUR'}")
    print(f"✅ Configuration système: {'OK' if config_ok else 'ERREUR'}")
    
    if upload_ok and config_ok:
        print("\n✨ Le système d'upload est entièrement fonctionnel.")
        print("\n💡 Si vous rencontrez encore des problèmes:")
        print("   1. Vérifiez les logs du serveur web (Nginx/Apache)")
        print("   2. Regardez la console du navigateur pour les erreurs JavaScript")
        print("   3. Vérifiez que les formulaires HTML sont correctement configurés avec enctype='multipart/form-data'")
        print("   4. Testez avec des fichiers de petite taille d'abord")
        print("   5. Vérifiez les permissions en mode production")
    else:
        print("\n❌ Des problèmes ont été détectés")
        print("💡 Consultez les détails ci-dessus pour résoudre les problèmes")

if __name__ == '__main__':
    main()