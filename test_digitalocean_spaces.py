#!/usr/bin/env python3

"""
Test de l'intégration DigitalOcean Spaces pour Atlas
"""

import os
import sys

# Ajouter le répertoire de l'app au chemin Python
sys.path.append('/Users/huguesmarie/Documents/Jepargne digital')

def test_digitalocean_config():
    """Teste la configuration et connexion DigitalOcean"""
    print("🧪 Test de l'intégration DigitalOcean Spaces")
    print("=" * 50)
    
    try:
        # Import du service
        from app.services.digitalocean_storage import DigitalOceanSpacesService
        
        # Configuration avec les vraies clés
        # Note: Vous devez avoir une ACCESS_KEY aussi, pas seulement la SECRET_KEY
        access_key = input("Entrez votre DigitalOcean Spaces ACCESS KEY: ").strip()
        secret_key = 'BfYxk8Oegh5/75dm5+TiZQwXdc8qqZ1AB+S+Ou5j3D8'  # La clé que vous avez fournie
        
        print(f"🔑 Access Key: {access_key[:8]}...")
        print(f"🔑 Secret Key: {secret_key[:8]}...")
        
        # Création du service
        service = DigitalOceanSpacesService(
            access_key=access_key,
            secret_key=secret_key
        )
        
        # Test de connexion - lister les fichiers
        print("\n📂 Test de connexion - listage des fichiers...")
        files = service.list_files('apprentissages/')
        
        print(f"✅ Connexion réussie!")
        print(f"📁 Fichiers trouvés dans apprentissages/: {len(files)}")
        
        for file in files[:5]:  # Afficher les 5 premiers
            print(f"   - {file['key']} ({file['size']} bytes)")
        
        # Test d'URL
        test_key = "apprentissages/test.pdf"
        url = service.get_file_url(test_key)
        print(f"\n🌐 URL de test: {url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_digitalocean_config()
    if success:
        print("\n✅ Test réussi - DigitalOcean Spaces prêt à utiliser!")
    else:
        print("\n❌ Test échoué - Vérifiez la configuration")