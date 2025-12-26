#!/bin/bash

# 🔍 DIAGNOSTIC SIMPLE
# ===================

SERVER="139.59.158.149"

echo "🔍 DIAGNOSTIC SIMPLE - QU'EST-CE QUI NE VA PAS ?"
echo "================================================"

# 1. Test de connexion de base
echo ""
echo "[1] 🌐 Test de connexion serveur"
echo "-------------------------------"
ping -c 1 $SERVER >/dev/null && echo "✅ Serveur accessible" || echo "❌ Serveur inaccessible"

# 2. Vérifier ce qui tourne sur le serveur
echo ""
echo "[2] 📊 État actuel du serveur"
echo "----------------------------"

ssh root@$SERVER << 'REMOTE_CHECK'
echo "=== SERVICES ACTIFS ==="
systemctl is-active atlas 2>/dev/null && echo "✅ Atlas service: ACTIF" || echo "❌ Atlas service: INACTIF"
systemctl is-active nginx 2>/dev/null && echo "✅ Nginx: ACTIF" || echo "❌ Nginx: INACTIF"
systemctl is-active postgresql 2>/dev/null && echo "✅ PostgreSQL: ACTIF" || echo "❌ PostgreSQL: INACTIF"

echo ""
echo "=== PORTS EN ÉCOUTE ==="
netstat -tlnp 2>/dev/null | grep -E ':(80|5000|5432)' | head -5

echo ""
echo "=== PROCESSUS ATLAS ==="
ps aux | grep -E "(atlas|gunicorn|flask)" | grep -v grep || echo "Aucun processus Atlas trouvé"

echo ""
echo "=== LOGS ATLAS (5 dernières lignes) ==="
journalctl -u atlas -n 5 --no-pager 2>/dev/null || echo "Pas de logs Atlas"

echo ""
echo "=== ERREURS RÉCENTES ==="
journalctl -u atlas --since "5 minutes ago" --no-pager 2>/dev/null | grep -i error || echo "Pas d'erreurs récentes"

echo ""
echo "=== CONTENU /var/www/atlas ==="
ls -la /var/www/atlas/ 2>/dev/null | head -10 || echo "/var/www/atlas introuvable"

echo ""
echo "=== CONFIGURATION ACTUELLE ==="
if [ -f "/var/www/atlas/app/__init__.py" ]; then
    echo "✅ app/__init__.py existe"
    head -20 /var/www/atlas/app/__init__.py | grep -E "(Flask|create_app|config)"
else
    echo "❌ app/__init__.py introuvable"
fi

if [ -f "/var/www/atlas/config.py" ]; then
    echo "✅ config.py existe"
    head -10 /var/www/atlas/config.py
else
    echo "❌ config.py introuvable"
fi
REMOTE_CHECK

# 3. Test HTTP direct
echo ""
echo "[3] 🌐 Tests HTTP directs"
echo "-----------------------"

echo "Test HTTP principal:"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$SERVER 2>/dev/null)
echo "Code: $HTTP_CODE"

if [ "$HTTP_CODE" != "200" ]; then
    echo ""
    echo "Détail de la réponse:"
    curl -v http://$SERVER 2>&1 | head -20
fi

echo ""
echo "🎯 DIAGNOSTIC TERMINÉ"
echo "===================="
echo ""
echo "📋 Résumé:"
echo "   - Serveur accessible: $(ping -c 1 $SERVER >/dev/null && echo "✅" || echo "❌")"
echo "   - HTTP répond: $([ "$HTTP_CODE" = "200" ] && echo "✅" || echo "❌ ($HTTP_CODE)")"
echo ""

if [ "$HTTP_CODE" != "200" ]; then
    echo "🔧 Actions suggérées:"
    echo "   1. Vérifier les logs: ssh root@$SERVER 'journalctl -fu atlas'"
    echo "   2. Redémarrer si besoin: ssh root@$SERVER 'systemctl restart atlas'"
    echo "   3. Vérifier la config: ssh root@$SERVER 'cd /var/www/atlas && ls -la'"
fi