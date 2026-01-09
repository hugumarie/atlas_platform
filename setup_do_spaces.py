#!/usr/bin/env python3

"""
Configuration et test DigitalOcean Spaces pour Atlas
"""

import os
import sys

def setup_environment():
    """Configure les variables d'environnement pour DigitalOcean Spaces"""
    print("🔧 Configuration DigitalOcean Spaces")
    print("=" * 50)
    
    # Demander les clés à l'utilisateur
    access_key = input("Entrez votre DigitalOcean ACCESS KEY: ").strip()
    
    if not access_key:
        print("❌ ACCESS KEY requis")
        return False
    
    # Secret key fournie
    secret_key = 'BfYxk8Oegh5/75dm5+TiZQwXdc8qqZ1AB+S+Ou5j3D8'
    
    # Configuration des variables d'environnement
    os.environ['DO_SPACES_ACCESS_KEY'] = access_key
    os.environ['DO_SPACES_SECRET_KEY'] = secret_key
    
    print(f"✅ ACCESS_KEY configuré: {access_key[:8]}...")
    print(f"✅ SECRET_KEY configuré: {secret_key[:8]}...")
    
    return True

def test_connection():
    """Test la connexion à DigitalOcean Spaces"""
    print("\n🧪 Test de connexion...")
    
    try:
        # Ajouter le répertoire de l'app au chemin Python
        sys.path.append('/Users/huguesmarie/Documents/Jepargne digital')
        
        from app.services.digitalocean_storage import DigitalOceanSpacesService
        
        # Créer le service
        service = DigitalOceanSpacesService(
            access_key=os.environ['DO_SPACES_ACCESS_KEY'],
            secret_key=os.environ['DO_SPACES_SECRET_KEY']
        )
        
        # Test simple - lister les fichiers
        print("📂 Listage des fichiers...")
        files = service.list_files('apprentissages/')
        
        print(f"✅ Connexion réussie!")
        print(f"📁 Dossier 'apprentissages' contient {len(files)} fichiers")
        
        if files:
            print("   Exemples de fichiers:")
            for file in files[:3]:
                print(f"   - {file['key']} ({file['size']} bytes)")
        else:
            print("   (Dossier vide - c'est normal si c'est la première utilisation)")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def save_env_file():
    """Sauvegarde les clés dans un fichier .env pour usage futur"""
    try:
        env_path = '/Users/huguesmarie/Documents/Jepargne digital/.env'
        
        # Lire le fichier .env existant
        env_content = ""
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_content = f.read()
        
        # Ajouter/mettre à jour les clés DigitalOcean
        lines = env_content.strip().split('\n') if env_content.strip() else []
        
        # Supprimer les anciennes clés DigitalOcean
        lines = [line for line in lines if not line.startswith('DO_SPACES_')]
        
        # Ajouter les nouvelles clés
        lines.append(f"DO_SPACES_ACCESS_KEY={os.environ['DO_SPACES_ACCESS_KEY']}")
        lines.append(f"DO_SPACES_SECRET_KEY={os.environ['DO_SPACES_SECRET_KEY']}")
        
        # Sauvegarder
        with open(env_path, 'w') as f:
            f.write('\n'.join(lines) + '\n')
        
        print(f"✅ Configuration sauvegardée dans {env_path}")
        return True
        
    except Exception as e:
        print(f"⚠️ Erreur sauvegarde .env: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Configuration DigitalOcean Spaces pour Atlas")
    print()
    
    # Configuration
    if not setup_environment():
        print("❌ Configuration échouée")
        sys.exit(1)
    
    # Test
    if not test_connection():
        print("❌ Test de connexion échoué")
        sys.exit(1)
    
    # Sauvegarde
    save_env_file()
    
    print("\n✅ Configuration terminée avec succès!")
    print("📝 Vous pouvez maintenant utiliser DigitalOcean Spaces dans Atlas")
    print()
    print("🔄 Redémarrez l'application Flask pour charger les nouvelles variables d'environnement")