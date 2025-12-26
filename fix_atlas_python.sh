#!/bin/bash

# 🐍 RÉPARATION ENVIRONNEMENT PYTHON ATLAS
# ========================================

SERVER="139.59.158.149"

echo "🐍 RÉPARATION ENVIRONNEMENT PYTHON"
echo "=================================="
echo ""

ssh root@$SERVER << 'REMOTE_SCRIPT'

echo "🔧 RÉPARATION ATLAS - ENVIRONNEMENT PYTHON"
echo "=========================================="

cd /var/www/atlas

# 1. Stopper Atlas
echo "[1] 🛑 Arrêt d'Atlas..."
systemctl stop atlas 2>/dev/null || true

# 2. Vérifier la structure des fichiers
echo ""
echo "[2] 📁 Structure des fichiers Atlas"
echo "---------------------------------"
echo "Contenu /var/www/atlas:"
ls -la /var/www/atlas/ | head -10

echo ""
echo "Contenu app/:"
if [ -d "app" ]; then
    ls -la app/ | head -5
else
    echo "❌ Dossier app/ introuvable"
fi

# 3. Vérifier les modules Python requis
echo ""
echo "[3] 📦 Vérification modules Python"
echo "---------------------------------"

if [ -f "venv/bin/activate" ]; then
    echo "✅ Environnement virtuel trouvé"
    source venv/bin/activate
    
    echo "Version Python:"
    python3 --version
    
    echo ""
    echo "Modules installés (principaux):"
    pip list | grep -E "(Flask|SQLAlchemy|psycopg2)" || echo "Modules Flask manquants"
    
else
    echo "❌ Environnement virtuel introuvable"
    echo "Recréation de l'environnement..."
    
    python3 -m venv venv
    source venv/bin/activate
fi

# 4. Réinstaller les dépendances si nécessaire
echo ""
echo "[4] 📥 Réinstallation des dépendances"
echo "------------------------------------"

if [ -f "requirements.txt" ]; then
    echo "Installation depuis requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "Installation manuelle des modules essentiels..."
    pip install --upgrade pip
    pip install Flask==3.0.0 Flask-SQLAlchemy==3.0.5 Flask-Login==0.6.3
    pip install SQLAlchemy==2.0.23 psycopg2-binary==2.9.9
    pip install gunicorn==21.2.0 python-dotenv==1.0.0
fi

# 5. Test d'import des modules
echo ""
echo "[5] 🧪 Test d'import des modules"
echo "-------------------------------"

python3 << 'PYTHON_IMPORT_TEST'
import sys
sys.path.append('/var/www/atlas')

modules_to_test = [
    'flask',
    'flask_sqlalchemy', 
    'flask_login',
    'sqlalchemy',
    'psycopg2',
    'gunicorn'
]

print("Test des imports essentiels:")
for module in modules_to_test:
    try:
        __import__(module)
        print(f"✅ {module}")
    except ImportError as e:
        print(f"❌ {module}: {e}")

print("\nTest SQLAlchemy avec PostgreSQL:")
try:
    from sqlalchemy import create_engine, text
    url = "postgresql://atlas:AtlasDB2024_SecurePass!@localhost/atlas_production"
    engine = create_engine(url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 'Python+DB OK' as status"))
        row = result.fetchone()
        print(f"✅ SQLAlchemy + PostgreSQL: {row[0]}")
except Exception as e:
    print(f"❌ SQLAlchemy + PostgreSQL: {e}")
PYTHON_IMPORT_TEST

# 6. Créer un fichier run.py correct si nécessaire
echo ""
echo "[6] 📝 Vérification fichier run.py"
echo "---------------------------------"

if [ ! -f "run.py" ]; then
    echo "Création de run.py..."
    cat > run.py << 'EOF'
#!/usr/bin/env python3
"""
Atlas - Point d'entrée principal
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
EOF
else
    echo "✅ run.py existe"
    echo "Contenu run.py:"
    head -10 run.py
fi

# 7. Test de démarrage Flask
echo ""
echo "[7] 🚀 Test de démarrage Flask"
echo "----------------------------"

export SQLALCHEMY_DATABASE_URI='postgresql://atlas:AtlasDB2024_SecurePass!@localhost/atlas_production'

# Test 1: Import direct de l'app
echo "Test 1: Import de l'application"
python3 << 'PYTHON_APP_TEST'
import sys
sys.path.append('/var/www/atlas')

try:
    from app import create_app
    app = create_app()
    print("✅ create_app() fonctionne")
    
    with app.app_context():
        from app.extensions import db
        print("✅ Extensions importées")
        
        # Test de connexion DB
        db.engine.execute('SELECT 1')
        print("✅ Connexion DB depuis Flask OK")
        
except Exception as e:
    print(f"❌ Erreur Flask: {e}")
    import traceback
    traceback.print_exc()
PYTHON_APP_TEST

# 8. Test Gunicorn
echo ""
echo "Test 2: Démarrage Gunicorn"
timeout 10 python3 -c "
import sys
sys.path.append('/var/www/atlas')
from app import create_app
app = create_app()
print('✅ App créée pour Gunicorn')
" && echo "✅ Gunicorn peut importer l'app" || echo "❌ Problème avec Gunicorn"

# 9. Configuration du service
echo ""
echo "[8] ⚙️ Configuration service systemd"
echo "----------------------------------"

echo "Contenu atlas.service:"
cat /etc/systemd/system/atlas.service 2>/dev/null || echo "❌ Service atlas.service introuvable"

# 10. Permissions
echo ""
echo "[9] 🔐 Vérification permissions"
echo "-----------------------------"
chown -R www-data:www-data /var/www/atlas
chmod -R 755 /var/www/atlas
chmod 644 /var/www/atlas/.env 2>/dev/null || true

echo "Propriétaire des fichiers:"
ls -la /var/www/atlas/ | head -3

REMOTE_SCRIPT

echo ""
echo "🎯 RÉPARATION PYTHON TERMINÉE"
echo "============================="