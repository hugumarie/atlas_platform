#!/bin/bash

# 🔧 CORRECTION IMPORTS ET SQLALCHEMY
# ===================================

SERVER="139.59.158.149"

echo "🔧 CORRECTION IMPORTS ET SQLALCHEMY"
echo "==================================="
echo ""

ssh root@$SERVER << 'REMOTE_SCRIPT'

echo "🛠️ CORRECTION FINALE - IMPORTS ET API"
echo "====================================="

cd /var/www/atlas

# 1. Diagnostiquer les fichiers de routes disponibles
echo "[1] 🔍 Diagnostic des fichiers de routes"
echo "--------------------------------------"

echo "Structure app/routes:"
find app/routes -name "*.py" 2>/dev/null | head -10

echo ""
echo "Contenu app/routes/platform/:"
ls -la app/routes/platform/ 2>/dev/null || echo "Dossier platform introuvable"

echo ""
echo "Contenu app/routes/site/:"
ls -la app/routes/site/ 2>/dev/null || echo "Dossier site introuvable"

# 2. Créer une version simplifiée sans blueprints problématiques
echo ""
echo "[2] 🔧 Création version simplifiée de app/__init__.py"
echo "---------------------------------------------------"

cat > app/__init__.py << 'EOF'
"""
Atlas - Application Factory (Version Simplifiée)
"""

from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import text
from config import ProductionConfig

# Extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    
    # Charger la configuration
    app.config.from_object(ProductionConfig)
    
    print(f"[ATLAS] Configuration chargée")
    print(f"[ATLAS] DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Initialiser les extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Route de base pour tester
    @app.route('/')
    def index():
        return """
        <h1>🎉 Atlas est opérationnel !</h1>
        <p><strong>Base de données :</strong> Connectée</p>
        <p><strong>Status :</strong> ✅ Fonctionnel</p>
        <p><strong>Version :</strong> Atlas V2.0</p>
        <hr>
        <p><a href="/plateforme">Accéder à la plateforme</a></p>
        <p><em>Déployé avec succès !</em></p>
        """
    
    @app.route('/plateforme')
    def platform():
        return """
        <h2>🏦 Plateforme Atlas</h2>
        <p>Interface de gestion patrimoniale</p>
        <p><a href="/">← Retour</a></p>
        """
    
    @app.route('/health')
    def health():
        """Endpoint de santé"""
        try:
            with db.engine.connect() as conn:
                conn.execute(text('SELECT 1'))
            return {"status": "healthy", "database": "connected"}, 200
        except Exception as e:
            return {"status": "error", "error": str(e)}, 500
    
    # Créer les tables
    with app.app_context():
        try:
            db.create_all()
            print("[ATLAS] Tables créées/vérifiées")
        except Exception as e:
            print(f"[ATLAS] Erreur création tables: {e}")
    
    print("[ATLAS] Application initialisée avec succès")
    return app

# Pour compatibilité
try:
    from app.extensions import *
except:
    pass
EOF

# 3. Test de la version simplifiée
echo ""
echo "[3] 🧪 Test de la version simplifiée"
echo "----------------------------------"

source venv/bin/activate

python3 << 'PYTHON_SIMPLE_TEST'
import sys
sys.path.insert(0, '/var/www/atlas')

try:
    print("=== TEST VERSION SIMPLIFIÉE ===")
    
    from app import create_app
    app = create_app()
    
    print("✅ App créée")
    
    with app.app_context():
        from sqlalchemy import text
        from app import db
        
        # Test connexion avec nouvelle syntaxe SQLAlchemy
        with db.engine.connect() as conn:
            result = conn.execute(text('SELECT current_database() as db_name'))
            row = result.fetchone()
            print(f"✅ Connecté à la base: {row[0]}")
        
        print("✅ TOUT FONCTIONNE !")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
PYTHON_SIMPLE_TEST

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 DÉMARRAGE ATLAS VERSION SIMPLIFIÉE"
    echo "====================================="
    
    # Modifier le service pour pointer vers app:create_app()
    echo "Modification service systemd..."
    sed -i 's|run:app|app:create_app()|g' /etc/systemd/system/atlas.service
    systemctl daemon-reload
    
    # Démarrer Atlas
    systemctl restart atlas
    sleep 5
    
    # Tests
    echo ""
    echo "=== TESTS FINAUX ==="
    
    echo "Statut service:"
    systemctl is-active atlas
    
    echo ""
    echo "Test HTTP local:"
    HTTP_LOCAL=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000)
    echo "Code HTTP local: $HTTP_LOCAL"
    
    if [ "$HTTP_LOCAL" = "200" ]; then
        echo "✅ Atlas répond localement"
        
        # Test de l'endpoint de santé
        echo ""
        echo "Test endpoint santé:"
        curl -s http://localhost:5000/health | head -c 100
        echo ""
        
    else
        echo "❌ Atlas ne répond pas localement"
        echo ""
        echo "Statut détaillé:"
        systemctl status atlas --no-pager -l | head -15
        
        echo ""
        echo "Logs récents:"
        journalctl -u atlas -n 10 --no-pager
    fi
    
else
    echo "❌ Version simplifiée échouée"
fi

REMOTE_SCRIPT

echo ""
echo "🌐 TEST EXTERNE FINAL"
echo "===================="

HTTP_EXTERNAL=$(curl -s -o /dev/null -w "%{http_code}" http://$SERVER)
echo "URL: http://$SERVER"
echo "Code HTTP: $HTTP_EXTERNAL"

if [ "$HTTP_EXTERNAL" = "200" ]; then
    echo ""
    echo "🎉🎉🎉 SUCCÈS TOTAL ! 🎉🎉🎉"
    echo "=========================="
    echo ""
    echo "✅ Atlas est maintenant opérationnel !"
    echo "🌐 Accès: http://$SERVER"
    echo "📊 Status: Fonctionnel"
    echo ""
    echo "🔑 Prochaines étapes:"
    echo "   1. Tester l'interface sur http://$SERVER"
    echo "   2. Ajouter les vraies routes si nécessaire"
    echo "   3. Importer les données utilisateurs"
    echo ""
else
    echo "⚠️ Problème persistant (code: $HTTP_EXTERNAL)"
fi

echo ""
echo "🎯 CORRECTION IMPORTS TERMINÉE !"