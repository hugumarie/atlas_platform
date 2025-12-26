#!/bin/bash

# 🔍 Debug Atlas Deployment - Diagnostic complet
# Exécuter ce script depuis le serveur Digital Ocean

echo "🔍 DIAGNOSTIC ATLAS DEPLOYMENT"
echo "==============================="
echo ""

# Informations système
echo "📊 1. INFORMATIONS SYSTÈME"
echo "--------------------------"
echo "Uptime: $(uptime)"
echo "Disk usage: $(df -h / | tail -n1)"
echo "Memory: $(free -h | head -n2 | tail -n1)"
echo "OS: $(lsb_release -d | cut -f2)"
echo ""

# Vérifier les services
echo "🔧 2. STATUT DES SERVICES"
echo "------------------------"
services=("postgresql" "nginx" "atlas")
for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        echo "✅ $service: ACTIF"
    else
        echo "❌ $service: INACTIF"
    fi
done
echo ""

# Vérifier les ports
echo "🌐 3. PORTS D'ÉCOUTE"
echo "-------------------"
echo "Port 80 (Nginx): $(ss -ln | grep ':80' | wc -l) connexions"
echo "Port 5000 (Gunicorn): $(ss -ln | grep ':5000' | wc -l) connexions"
echo "Port 5432 (PostgreSQL): $(ss -ln | grep ':5432' | wc -l) connexions"
echo ""

# Vérifier les fichiers Atlas
echo "📁 4. FICHIERS ATLAS"
echo "-------------------"
if [ -d "/var/www/atlas" ]; then
    echo "✅ Dossier Atlas existe: $(du -sh /var/www/atlas | cut -f1)"
    echo "Fichiers principaux:"
    ls -la /var/www/atlas/run.py /var/www/atlas/app/ /var/www/atlas/.env 2>/dev/null || echo "⚠️ Fichiers manquants"
else
    echo "❌ Dossier Atlas n'existe pas"
fi
echo ""

# Vérifier la base de données
echo "🗄️ 5. BASE DE DONNÉES"
echo "---------------------"
if command -v psql >/dev/null 2>&1; then
    if sudo -u postgres psql -c "\l" | grep -q "atlas_db"; then
        echo "✅ Base de données atlas_db existe"
        echo "Tables:"
        sudo -u postgres psql -d atlas_db -c "\dt" 2>/dev/null | head -n 10
    else
        echo "❌ Base de données atlas_db n'existe pas"
    fi
else
    echo "❌ PostgreSQL non installé"
fi
echo ""

# Vérifier les logs d'erreur
echo "📝 6. LOGS RÉCENTS"
echo "-----------------"
echo "=== Logs Atlas (dernières 10 lignes) ==="
journalctl -u atlas --no-pager -n 10 2>/dev/null || echo "Pas de logs Atlas"
echo ""
echo "=== Logs Nginx Error (dernières 5 lignes) ==="
tail -n 5 /var/log/nginx/error.log 2>/dev/null || echo "Pas de logs Nginx"
echo ""

# Test de connectivité interne
echo "🧪 7. TESTS DE CONNECTIVITÉ"
echo "---------------------------"
echo "Test local port 5000:"
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000 2>/dev/null; then
    echo "✅ Port 5000 répond"
else
    echo "❌ Port 5000 ne répond pas"
fi

echo "Test local port 80:"
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:80 2>/dev/null; then
    echo "✅ Port 80 répond"
else
    echo "❌ Port 80 ne répond pas"
fi
echo ""

# Configuration firewall
echo "🔒 8. FIREWALL (UFW)"
echo "-------------------"
if command -v ufw >/dev/null 2>&1; then
    ufw status
else
    echo "UFW non installé"
fi
echo ""

# Python et dépendances
echo "🐍 9. ENVIRONNEMENT PYTHON"
echo "-------------------------"
if [ -f "/var/www/atlas/venv/bin/python" ]; then
    echo "✅ Virtual env existe"
    echo "Python version: $(/var/www/atlas/venv/bin/python --version)"
    echo "Packages installés:"
    /var/www/atlas/venv/bin/pip list | head -n 10
else
    echo "❌ Virtual env n'existe pas"
fi
echo ""

echo "🎯 DIAGNOSTIC TERMINÉ"
echo "Pour plus de détails, voir:"
echo "  - journalctl -u atlas -f"
echo "  - tail -f /var/log/nginx/error.log"
echo "  - systemctl status atlas"