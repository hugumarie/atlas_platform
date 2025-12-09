#!/usr/bin/env python3
"""
Script de démarrage pour la plateforme de gestion de patrimoine.
Installe les dépendances et lance l'application.
"""

import subprocess
import sys
import os

def install_requirements():
    """Installe les dépendances Python"""
    print("Installation des dépendances...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dépendances installées avec succès")
    except subprocess.CalledProcessError:
        print("❌ Erreur lors de l'installation des dépendances")
        return False
    return True

def check_database():
    """Vérifie et initialise la base de données"""
    print("Vérification de la base de données...")
    
    # Import des modules Flask après installation des dépendances
    try:
        from app import create_app, db
        app = create_app()
        
        with app.app_context():
            # Créer les tables si elles n'existent pas
            db.create_all()
            print("✅ Base de données initialisée")
            
    except Exception as e:
        print(f"❌ Erreur avec la base de données: {e}")
        return False
    
    return True

def start_application():
    """Lance l'application Flask"""
    print("Démarrage de l'application...")
    print("🌐 L'application sera accessible sur http://127.0.0.1:5000")
    print("📚 Consultez les fichiers README pour plus d'informations")
    print("⚡ Appuyez sur Ctrl+C pour arrêter l'application")
    print("-" * 50)
    
    try:
        # Import et lancement de l'app
        from run import app
        app.run(debug=True, host='127.0.0.1', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Application arrêtée")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")

def main():
    """Fonction principale"""
    print("🚀 Plateforme de Gestion de Patrimoine")
    print("=" * 40)
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists('requirements.txt'):
        print("❌ Fichier requirements.txt non trouvé. Assurez-vous d'être dans le bon répertoire.")
        return
    
    # Installation des dépendances
    if not install_requirements():
        return
    
    # Vérification de la base de données
    if not check_database():
        return
    
    # Démarrage de l'application
    start_application()

if __name__ == '__main__':
    main()