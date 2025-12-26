#!/bin/bash

# 🔧 Atlas - Fix reportlab et dépendances manquantes
# Résout le problème ModuleNotFoundError: No module named 'reportlab'

SERVER_IP="139.59.158.149"

echo "🔧 ATLAS - FIX REPORTLAB"
echo "========================"
echo ""
echo "🎯 Problème identifié: ModuleNotFoundError: No module named 'reportlab'"
echo "🎯 Solution: Installation des dépendances manquantes"
echo ""

ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no root@$SERVER_IP 'bash -s' << 'REMOTE_SCRIPT'

echo "🛑 Arrêt d'Atlas pour installation des dépendances..."
systemctl stop atlas

cd /var/www/atlas
source venv/bin/activate

echo ""
echo "📦 Installation des dépendances système pour reportlab..."
apt update -y >/dev/null
apt install -y python3-dev build-essential libffi-dev libssl-dev \
              libjpeg-dev libpng-dev libfreetype6-dev zlib1g-dev \
              pkg-config >/dev/null

echo ""
echo "🐍 Installation des modules Python manquants..."

# Liste complète des dépendances requises
pip install reportlab==4.0.4
pip install Pillow==10.0.0
pip install requests==2.31.0
pip install yfinance==0.2.18
pip install cryptography==41.0.3
pip install matplotlib==3.7.2
pip install pandas==2.0.3
pip install numpy==1.24.3

echo "✅ Dépendances installées"

echo ""
echo "🧪 Test des imports..."
python3 -c "
try:
    import reportlab
    print('✅ reportlab: OK')
except ImportError as e:
    print(f'❌ reportlab: {e}')

try:
    from reportlab.lib.pagesizes import A4
    print('✅ reportlab.lib.pagesizes: OK')
except ImportError as e:
    print(f'❌ reportlab.lib.pagesizes: {e}')

try:
    import PIL
    print('✅ PIL: OK')
except ImportError as e:
    print(f'❌ PIL: {e}')

try:
    import requests
    print('✅ requests: OK')
except ImportError as e:
    print(f'❌ requests: {e}')
"

echo ""
echo "🧪 Test de l'import du module investor.py..."
python3 -c "
import sys, os
sys.path.insert(0, '/var/www/atlas')
os.chdir('/var/www/atlas')

try:
    from dotenv import load_dotenv
    load_dotenv()
    
    from app.routes.platform.investor import platform_investor_bp
    print('✅ app.routes.platform.investor: OK')
except ImportError as e:
    print(f'❌ app.routes.platform.investor: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "🧪 Test complet de création de l'app..."
python3 -c "
import sys, os
sys.path.insert(0, '/var/www/atlas')
os.chdir('/var/www/atlas')

try:
    from dotenv import load_dotenv
    load_dotenv()
    
    from app import create_app
    app = create_app()
    print('✅ Application Flask créée avec succès !')
    print(f'Routes enregistrées: {len(app.url_map._rules)}')
except Exception as e:
    print(f'❌ Erreur création app: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"

echo ""
echo "🚀 Redémarrage d'Atlas..."
systemctl start atlas

echo ""
echo "⏰ Attente démarrage (10 secondes)..."
sleep 10

echo ""
echo "🔍 Vérification du service..."
if systemctl is-active atlas >/dev/null 2>&1; then
    echo "✅ Atlas service ACTIF"
else
    echo "❌ Atlas service INACTIF"
    echo ""
    echo "📋 Logs récents:"
    journalctl -u atlas --no-pager -n 5
fi

echo ""
echo "🧪 Test HTTP local..."
for i in {1..5}; do
    HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5000 2>/dev/null || echo "000")
    echo "Test $i/5: HTTP $HTTP_CODE"
    
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
        echo ""
        echo "🎉 ✅ APPLICATION ATLAS FONCTIONNE !"
        echo "===================================="
        systemctl restart nginx
        exit 0
    elif [ "$HTTP_CODE" = "500" ]; then
        echo "⚠️ Erreur serveur 500 - Regardons les logs..."
        tail -n 3 /var/log/atlas_error.log 2>/dev/null || echo "Pas de logs"
        if [ $i -eq 5 ]; then
            echo ""
            echo "❌ Erreur 500 persistante"
            journalctl -u atlas --no-pager -n 3
        fi
    elif [ "$HTTP_CODE" = "000" ] && [ $i -eq 5 ]; then
        echo ""
        echo "❌ Service ne répond toujours pas"
        echo "📋 Derniers logs:"
        journalctl -u atlas --no-pager -n 3
    fi
    
    sleep 3
done

echo ""
echo "🎯 FIX REPORTLAB TERMINÉ"
echo "========================"

REMOTE_SCRIPT

echo ""
echo "🧪 Test final externe..."
sleep 5

for i in {1..3}; do
    HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 15 http://$SERVER_IP 2>/dev/null || echo "000")
    echo "Test externe $i/3: HTTP $HTTP_CODE"
    
    case $HTTP_CODE in
        200|302) 
            echo ""
            echo "🎉🚀 ATLAS EST ENFIN EN LIGNE !"
            echo "==============================="
            echo ""
            echo "🌐 Votre plateforme Atlas :"
            echo "   👉 http://$SERVER_IP"
            echo "   👉 http://$SERVER_IP/plateforme/connexion"
            echo ""
            echo "🔐 Connexion :"
            echo "   📧 admin@gmail.com"
            echo "   🔑 admin"
            echo ""
            echo "✅ Le problème reportlab a été résolu !"
            exit 0
            ;;
        500) 
            echo "⚠️ Erreur 500 - Problème applicatif"
            if [ $i -eq 3 ]; then
                echo "   Connectez-vous pour voir les logs détaillés"
            fi
            ;;
        502) 
            echo "⚠️ Bad Gateway - Service ne démarre pas"
            ;;
        *)
            echo "⚠️ Code inattendu: $HTTP_CODE"
            ;;
    esac
    
    if [ $i -lt 3 ]; then
        sleep 5
    fi
done

echo ""
echo "🔍 Si le problème persiste :"
echo "   ssh root@$SERVER_IP"
echo "   journalctl -u atlas -f"
echo "   cd /var/www/atlas && source venv/bin/activate && python3 run.py"