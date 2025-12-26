#!/bin/bash

# 🔍 DIAGNOSTIC CONFIGURATION ATLAS
# =================================

SERVER="139.59.158.149"

echo "🔍 DIAGNOSTIC CONFIGURATION ATLAS"
echo "================================="
echo ""

ssh root@$SERVER << 'REMOTE_SCRIPT'

echo "🕵️ DIAGNOSTIC APPROFONDI CONFIGURATION"
echo "======================================"

cd /var/www/atlas

# 1. Vérifier tous les fichiers de config
echo ""
echo "[1] 📄 Fichiers de configuration"
echo "-------------------------------"

echo "Fichiers .env* présents :"
ls -la .env* 2>/dev/null || echo "Aucun fichier .env trouvé"

echo ""
echo "Contenu .env.production :"
if [ -f ".env.production" ]; then
    cat .env.production
else
    echo "❌ .env.production introuvable"
fi

echo ""
echo "Contenu .env (s'il existe) :"
if [ -f ".env" ]; then
    cat .env
else
    echo "❌ .env introuvable"
fi

# 2. Test de lecture des variables par Flask
echo ""
echo "[2] 🧪 Test lecture variables par Flask"
echo "--------------------------------------"

source venv/bin/activate

# Test avec chargement explicite du fichier
python3 << 'PYTHON_CONFIG_TEST'
import os
import sys
sys.path.insert(0, '/var/www/atlas')

print("=== TEST VARIABLES ENVIRONNEMENT ===")

# Test 1: Variables actuelles
print("\nVariables actuelles:")
for key in ['SQLALCHEMY_DATABASE_URI', 'SECRET_KEY', 'FLASK_ENV']:
    value = os.environ.get(key, "NON DÉFINI")
    print(f"  {key}: {value}")

# Test 2: Chargement .env.production avec python-dotenv
print("\n=== CHARGEMENT .env.production ===")
try:
    from dotenv import load_dotenv
    
    # Charger .env.production
    load_dotenv('/var/www/atlas/.env.production')
    print("✅ .env.production chargé")
    
    # Vérifier les variables
    db_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
    print(f"SQLALCHEMY_DATABASE_URI: {db_uri}")
    
    if db_uri:
        print("✅ URL base trouvée")
    else:
        print("❌ URL base manquante")
    
except Exception as e:
    print(f"❌ Erreur chargement .env: {e}")

# Test 3: Import de l'app avec config forcée
print("\n=== TEST CRÉATION APP AVEC CONFIG FORCÉE ===")

# Forcer la configuration avant l'import
os.environ['SQLALCHEMY_DATABASE_URI'] = 'postgresql://atlas:AtlasDB2024_SecurePass!@localhost/atlas_production'
os.environ['SECRET_KEY'] = 'Atlas_Prod_2024_9x8w7v6u5t4r3e2w1q0p9o8i7u6y5t4r3e2w1q'
os.environ['FLASK_ENV'] = 'production'

try:
    from app import create_app
    app = create_app()
    
    print("✅ App créée avec config forcée")
    
    # Test connexion
    with app.app_context():
        from app.extensions import db
        print("✅ Extensions chargées")
        
        # Afficher l'URL utilisée
        print(f"URL DB utilisée: {app.config.get('SQLALCHEMY_DATABASE_URI', 'NON DÉFINIE')}")
        
        # Test connexion simple
        result = db.engine.execute('SELECT 1 as test')
        print("✅ Connexion DB réussie avec config forcée")
        
except Exception as e:
    print(f"❌ Erreur même avec config forcée: {e}")
    import traceback
    traceback.print_exc()
PYTHON_CONFIG_TEST

# 3. Modifier le code Flask pour forcer la config
echo ""
echo "[3] 🔧 Modification temporaire du code Flask"
echo "-------------------------------------------"

# Créer une version de app/__init__.py avec config en dur
echo "Sauvegarde app/__init__.py..."
cp app/__init__.py app/__init__.py.backup

echo "Modification app/__init__.py pour forcer la config..."

# Remplacer la section de configuration
python3 << 'PYTHON_MODIFY'
with open('app/__init__.py', 'r') as f:
    content = f.read()

# Chercher et remplacer la configuration
config_section = '''
    # Configuration forcée pour debug
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://atlas:AtlasDB2024_SecurePass!@localhost/atlas_production'
    app.config['SECRET_KEY'] = 'Atlas_Prod_2024_9x8w7v6u5t4r3e2w1q0p9o8i7u6y5t4r3e2w1q'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
'''

# Ajouter après la ligne de création de l'app
if 'app = Flask(__name__)' in content:
    content = content.replace(
        'app = Flask(__name__)',
        'app = Flask(__name__)' + config_section
    )
    
    with open('app/__init__.py', 'w') as f:
        f.write(content)
    
    print("✅ Configuration forcée ajoutée")
else:
    print("❌ Impossible de modifier automatiquement")
PYTHON_MODIFY

# 4. Test avec la config forcée
echo ""
echo "[4] 🚀 Test avec configuration forcée"
echo "------------------------------------"

python3 << 'PYTHON_FORCED_TEST'
import sys
sys.path.insert(0, '/var/www/atlas')

try:
    from app import create_app
    app = create_app()
    
    print("✅ App créée avec config forcée dans le code")
    print(f"URL DB: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    with app.app_context():
        from app.extensions import db
        db.create_all()
        print("✅ Tables créées avec succès")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
PYTHON_FORCED_TEST

if [ $? -eq 0 ]; then
    echo ""
    echo "🎯 TEST AVEC CONFIG FORCÉE : SUCCÈS !"
    echo "==================================="
    
    # Démarrer Atlas avec la config forcée
    echo "Démarrage d'Atlas..."
    systemctl restart atlas
    sleep 5
    
    # Test HTTP
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000)
    echo "Code HTTP: $HTTP_CODE"
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "🎉 ATLAS FONCTIONNE !"
    else
        echo "⚠️ Atlas ne répond toujours pas"
        systemctl status atlas --no-pager -l
    fi
else
    echo "❌ Config forcée a échoué aussi"
fi

REMOTE_SCRIPT

echo ""
echo "🔍 DIAGNOSTIC TERMINÉ"
echo "===================="