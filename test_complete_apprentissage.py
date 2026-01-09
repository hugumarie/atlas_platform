#!/usr/bin/env python3

"""
Test complet du système d'apprentissage avec DigitalOcean Spaces
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Ajouter le répertoire de l'app au chemin Python  
sys.path.append('.')

def test_system():
    """Test complet du système d'apprentissage"""
    print("🧪 Test système complet d'apprentissage")
    print("=" * 50)
    
    try:
        from app import create_app, db
        from app.models.apprentissage import Apprentissage
        
        app = create_app()
        with app.app_context():
            print("✅ Application Flask créée")
            
            # Test 1: Lister les formations existantes
            formations = Apprentissage.query.filter_by(actif=True).all()
            print(f"📚 Formations trouvées: {len(formations)}")
            
            for formation in formations:
                print(f"   - {formation.nom} (Storage: {formation.storage_type})")
                print(f"     PDF: {formation.get_pdf_url()}")
                print(f"     Image: {formation.get_image_url()}")
                print(f"     Actif: {formation.actif}")
                print()
            
            # Test 2: Vérifier la connectivité DigitalOcean
            from app.services.digitalocean_storage import get_spaces_service
            spaces_service = get_spaces_service()
            
            if spaces_service:
                print("✅ Service DigitalOcean Spaces disponible")
                files = spaces_service.list_files('apprentissages/')
                print(f"📁 Fichiers sur DigitalOcean: {len(files)}")
                for file in files[:3]:
                    print(f"   - {file['key']} ({file['size']} bytes)")
            else:
                print("⚠️ Service DigitalOcean Spaces non disponible")
            
            print("\n✅ Tous les tests passés!")
            return True
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_system()
    if success:
        print("\n🎉 Système d'apprentissage prêt!")
        print("📝 Vous pouvez maintenant:")
        print("   - Consulter les formations: http://127.0.0.1:5001/plateforme/apprentissages")
        print("   - Administrer: http://127.0.0.1:5001/plateforme/admin/apprentissages")
    else:
        print("\n❌ Des problèmes subsistent")