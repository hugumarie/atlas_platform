#!/usr/bin/env python3

"""
Test manuel d'upload vers DigitalOcean Spaces
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Ajouter le répertoire de l'app au chemin Python  
sys.path.append('.')

def create_test_file():
    """Créer un fichier test"""
    test_content = """# Formation Test Atlas

Cette formation vous explique les bases de l'investissement.

## Points clés:
- Diversification
- Horizon de placement
- Tolérance au risque

Atlas - Votre conseiller patrimonial
"""
    test_file = '/tmp/test_formation_atlas.pdf'
    with open(test_file, 'w') as f:
        f.write(test_content)
    return test_file

def test_manual_upload():
    """Test manuel d'upload"""
    print("📤 Test manuel d'upload vers DigitalOcean")
    print("=" * 50)
    
    try:
        from app.services.digitalocean_storage import get_spaces_service
        from app import create_app
        
        app = create_app()
        with app.app_context():
            
            # Obtenir le service
            spaces_service = get_spaces_service()
            if not spaces_service:
                print("❌ Service DigitalOcean non disponible")
                return False
                
            # Créer un fichier test
            test_file_path = create_test_file()
            print(f"📄 Fichier test créé: {test_file_path}")
            
            # Simuler un upload
            with open(test_file_path, 'rb') as f:
                from werkzeug.datastructures import FileStorage
                
                # Créer un objet FileStorage pour simuler l'upload
                fake_file = FileStorage(
                    stream=f,
                    filename='test_formation_atlas.pdf',
                    content_type='application/pdf'
                )
                
                # Tenter l'upload
                print("🚀 Début upload vers DigitalOcean...")
                result = spaces_service.upload_file(
                    file=fake_file,
                    folder_path='apprentissages/pdfs'
                )
                
                if result['success']:
                    print(f"✅ Upload réussi!")
                    print(f"   URL: {result['url']}")
                    print(f"   Key: {result['key']}")
                    
                    # Tester l'accès au fichier
                    import requests
                    response = requests.head(result['url'])
                    if response.status_code == 200:
                        print("✅ Fichier accessible publiquement")
                    else:
                        print(f"⚠️ Statut HTTP: {response.status_code}")
                        
                    return True
                else:
                    print(f"❌ Erreur upload: {result['error']}")
                    return False
                    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Nettoyer
        if os.path.exists('/tmp/test_formation_atlas.pdf'):
            os.remove('/tmp/test_formation_atlas.pdf')

if __name__ == "__main__":
    success = test_manual_upload()
    if success:
        print("\n🎉 Upload vers DigitalOcean fonctionnel!")
        print("📝 Le système est prêt pour créer des formations")
    else:
        print("\n❌ Problème avec l'upload DigitalOcean")