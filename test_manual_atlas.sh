#!/bin/bash

# 🔍 Atlas - Test manuel pour identifier l'erreur exacte
# Lance l'application en mode debug pour voir l'erreur complète

SERVER_IP="139.59.158.149"

echo "🔍 ATLAS - TEST MANUEL DEBUG"
echo "============================"
echo ""
echo "🎯 Objectif: Identifier l'erreur exacte qui empêche le démarrage"
echo ""

ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no root@$SERVER_IP 'bash -s' << 'REMOTE_SCRIPT'

echo "🛑 Arrêt complet des services..."
systemctl stop atlas
systemctl stop nginx
pkill -f gunicorn 2>/dev/null || true

cd /var/www/atlas

echo ""
echo "🔍 DIAGNOSTIC ÉTAPE PAR ÉTAPE"
echo "============================="

echo ""
echo "📁 Vérification des fichiers essentiels..."
ls -la run.py app/ requirements.txt .env

echo ""
echo "🐍 Activation de l'environnement..."
source venv/bin/activate
python3 --version
pip --version

echo ""
echo "🧪 Test d'import de l'application (MODE DÉTAILLÉ)..."
python3 << 'PYTHON_TEST'
import sys
import os
import traceback

print("🔧 Configuration du chemin...")
sys.path.insert(0, '/var/www/atlas')
os.chdir('/var/www/atlas')

print("📋 Variables d'environnement...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env chargé")
    
    # Afficher les variables importantes
    print(f"FLASK_ENV: {os.getenv('FLASK_ENV', 'non défini')}")
    print(f"SQLALCHEMY_DATABASE_URI: {os.getenv('SQLALCHEMY_DATABASE_URI', 'non défini')}")
except Exception as e:
    print(f"❌ Erreur .env: {e}")

print("\n🧪 Test d'import de l'app...")
try:
    from app import create_app
    print("✅ create_app importé")
except Exception as e:
    print(f"❌ Erreur import create_app: {e}")
    traceback.print_exc()
    exit(1)

print("\n🧪 Test de création de l'application...")
try:
    app = create_app()
    print("✅ Application créée avec succès!")
    print(f"App: {app}")
    print(f"Config: {app.config.get('ENV', 'non défini')}")
except Exception as e:
    print(f"❌ ERREUR CRÉATION APP: {e}")
    print("\n📋 TRACEBACK COMPLET:")
    traceback.print_exc()
    exit(1)

print("\n🧪 Test de configuration des routes...")
try:
    with app.app_context():
        print(f"✅ Contexte app OK")
        print(f"Nombre de routes: {len(list(app.url_map.iter_rules()))}")
        
        # Lister quelques routes pour vérifier
        for rule in list(app.url_map.iter_rules())[:5]:
            print(f"  - {rule.rule} -> {rule.endpoint}")
            
except Exception as e:
    print(f"❌ Erreur contexte app: {e}")
    traceback.print_exc()
    exit(1)

print("\n✅ TOUS LES TESTS PASSENT - L'APP DEVRAIT FONCTIONNER!")
PYTHON_TEST

PYTHON_EXIT_CODE=$?
if [ $PYTHON_EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ Erreur détectée dans le test Python (code $PYTHON_EXIT_CODE)"
    echo "🛑 Arrêt du diagnostic"
    exit 1
fi

echo ""
echo "🚀 Test de démarrage Flask en mode development..."
echo "   (Ctrl+C pour arrêter après quelques secondes si ça fonctionne)"

# Tester le démarrage en mode développement
timeout 15s python3 run.py &
FLASK_PID=$!

echo "   PID Flask: $FLASK_PID"
sleep 5

# Vérifier si le processus est encore actif
if kill -0 $FLASK_PID 2>/dev/null; then
    echo ""
    echo "✅ Flask démarre en mode dev!"
    
    # Test HTTP direct
    echo "🧪 Test HTTP sur le processus Flask..."
    for i in {1..3}; do
        HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5000 2>/dev/null || echo "000")
        echo "  Test $i/3: HTTP $HTTP_CODE"
        if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
            echo "✅ L'application répond en mode dev!"
            break
        fi
        sleep 2
    done
    
    # Arrêter Flask
    kill $FLASK_PID 2>/dev/null || true
    wait $FLASK_PID 2>/dev/null || true
else
    echo "❌ Flask ne démarre pas en mode dev"
    echo "📋 Vérification des processus Python:"
    ps aux | grep python | grep -v grep || echo "Aucun processus Python"
fi

echo ""
echo "🔧 DIAGNOSTIC GUNICORN SPÉCIFIQUE..."
echo "===================================="

echo ""
echo "🧪 Test Gunicorn avec output détaillé..."
cd /var/www/atlas
source venv/bin/activate

# Test Gunicorn avec logs verbeux
echo "Lancement de Gunicorn en mode verbose..."
timeout 10s gunicorn --bind 127.0.0.1:5000 --workers 1 --timeout 30 --log-level debug run:app 2>&1 | head -20

echo ""
echo "🔍 Vérification de la configuration systemd..."
cat /etc/systemd/system/atlas.service

echo ""
echo "📋 Derniers logs systemd pour Atlas..."
journalctl -u atlas --no-pager -n 10

echo ""
echo "🎯 DIAGNOSTIC TERMINÉ"
echo "===================="
echo ""
echo "📝 Résumé:"
echo "  - Si Python Flask démarre en mode dev -> Problème Gunicorn/systemd"
echo "  - Si Python Flask ne démarre pas -> Problème applicatif"
echo ""

REMOTE_SCRIPT

echo ""
echo "🤔 ANALYSE DES RÉSULTATS"
echo "========================"
echo ""
echo "Basé sur les tests ci-dessus:"
echo ""
echo "Si l'application Python fonctionne en mode dev mais pas avec Gunicorn:"
echo "  👉 Problème de configuration Gunicorn/systemd"
echo "  👉 Utilise: ssh root@$SERVER_IP 'systemctl edit atlas'"
echo ""
echo "Si l'application Python ne démarre pas du tout:"
echo "  👉 Problème de dépendances ou de code"
echo "  👉 Regarde les tracebacks Python ci-dessus"
echo ""
echo "🔧 Prochaines étapes suggérées:"
echo "  1. Connecte-toi au serveur: ssh root@$SERVER_IP"
echo "  2. Va dans le dossier: cd /var/www/atlas"
echo "  3. Active l'env: source venv/bin/activate"
echo "  4. Teste manuellement: python3 run.py"