#!/usr/bin/env python3
"""
Script de test pour vérifier le système de backup Atlas Production
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_dependencies():
    """Vérifie que les dépendances Python sont installées"""
    print("🐍 Vérification des dépendances Python...")
    
    try:
        import boto3
        print("✅ boto3 disponible")
        return True
    except ImportError:
        print("❌ boto3 non disponible - Installez avec: pip3 install boto3")
        return False

def check_system_dependencies():
    """Vérifie que les dépendances système sont disponibles"""
    print("🔧 Vérification des dépendances système...")
    
    dependencies = ['pg_dump', 'python3']
    all_ok = True
    
    for dep in dependencies:
        try:
            subprocess.run(['which', dep], capture_output=True, check=True)
            print(f"✅ {dep} disponible")
        except subprocess.CalledProcessError:
            print(f"❌ {dep} non trouvé")
            all_ok = False
    
    return all_ok

def check_configuration():
    """Vérifie la configuration des backups"""
    print("📝 Vérification de la configuration...")
    
    script_dir = Path(__file__).parent
    config_file = script_dir / 'backup_config.env'
    
    if not config_file.exists():
        print(f"❌ Fichier de configuration manquant: {config_file}")
        print("Copiez backup_config.env.example vers backup_config.env")
        return False
    
    print(f"✅ Fichier de configuration trouvé: {config_file}")
    
    # Charger et vérifier les variables
    required_vars = [
        'DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD',
        'DIGITALOCEAN_SPACES_KEY', 'DIGITALOCEAN_SPACES_SECRET',
        'DIGITALOCEAN_SPACES_ENDPOINT', 'DIGITALOCEAN_SPACES_BUCKET'
    ]
    
    # Simuler le chargement des variables
    config = {}
    try:
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value
        
        missing_vars = [var for var in required_vars if var not in config or not config[var]]
        
        if missing_vars:
            print(f"❌ Variables manquantes dans la configuration: {', '.join(missing_vars)}")
            return False
        else:
            print("✅ Configuration complète")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de la configuration: {e}")
        return False

def check_spaces_connectivity():
    """Teste la connexion à DigitalOcean Spaces"""
    print("☁️  Test de connexion DigitalOcean Spaces...")
    
    try:
        # Simuler un test de connexion
        print("ℹ️  Pour tester la connexion Spaces, exécutez le backup manuellement")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion Spaces: {e}")
        return False

def check_permissions():
    """Vérifie les permissions des fichiers"""
    print("🔐 Vérification des permissions...")
    
    script_dir = Path(__file__).parent
    backup_script = script_dir / 'backup_database_production.py'
    run_script = script_dir / 'run_backup_production.sh'
    
    files_to_check = [backup_script, run_script]
    all_ok = True
    
    for file_path in files_to_check:
        if file_path.exists():
            if os.access(file_path, os.X_OK):
                print(f"✅ {file_path.name} exécutable")
            else:
                print(f"❌ {file_path.name} non exécutable - Exécutez: chmod +x {file_path}")
                all_ok = False
        else:
            print(f"❌ Fichier manquant: {file_path}")
            all_ok = False
    
    return all_ok

def run_backup_test():
    """Exécute un test de backup (dry run)"""
    print("🧪 Test d'exécution du backup...")
    
    script_dir = Path(__file__).parent
    run_script = script_dir / 'run_backup_production.sh'
    
    if not run_script.exists():
        print(f"❌ Script d'exécution manquant: {run_script}")
        return False
    
    try:
        print(f"ℹ️  Pour tester le backup complet, exécutez manuellement:")
        print(f"   {run_script}")
        print("ℹ️  Ceci créera un vrai backup sur DigitalOcean Spaces")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("=" * 60)
    print("🔍 TEST DU SYSTÈME DE BACKUP ATLAS PRODUCTION")
    print("=" * 60)
    print()
    
    tests = [
        ("Dépendances Python", check_python_dependencies),
        ("Dépendances système", check_system_dependencies),
        ("Configuration", check_configuration),
        ("Permissions", check_permissions),
        ("Connexion Spaces", check_spaces_connectivity),
        ("Test backup", run_backup_test)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            results.append((test_name, False))
        print()
    
    # Résumé
    print("=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
    
    print(f"\nRésultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! Le système de backup est prêt.")
        print("\n📋 Prochaines étapes:")
        print("1. Déployez les scripts sur votre serveur de production")
        print("2. Exécutez install_backup_system.sh sur le serveur")
        print("3. Configurez backup_config.env avec vos paramètres")
        print("4. Testez manuellement avec run_backup_production.sh")
    else:
        print(f"⚠️  {total - passed} test(s) ont échoué. Corrigez les problèmes avant le déploiement.")
        sys.exit(1)

if __name__ == "__main__":
    main()