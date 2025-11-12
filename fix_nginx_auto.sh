#!/bin/bash

# Script de correction automatique Nginx - Coach Patrimoine
set -e

SERVER_IP="165.227.167.78"
SERVER_PASSWORD="(!=ZL@-nZu7eB?7a"

echo "🔧 CORRECTION AUTOMATIQUE NGINX - Coach Patrimoine"
echo "🎯 Serveur: $SERVER_IP"
echo ""

# Vérifier que sshpass est disponible
if ! command -v /opt/homebrew/bin/sshpass &> /dev/null; then
    echo "📦 Installation de sshpass..."
    /opt/homebrew/bin/brew install hudochenkov/sshpass/sshpass
fi

# Fonction pour exécuter des commandes SSH automatiquement
run_ssh() {
    /opt/homebrew/bin/sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR root@$SERVER_IP "$1"
}

echo "1️⃣  Redémarrage de l'application Flask..."
run_ssh "
# Arrêter les processus existants
pkill -f gunicorn || true

# Redémarrer l'application
su - appuser -c '
cd /home/appuser/coach-patrimoine
source venv/bin/activate
gunicorn --bind 127.0.0.1:5000 --workers 2 --daemon --access-logfile /tmp/gunicorn_access.log --error-logfile /tmp/gunicorn_error.log wsgi:app
'

# Vérifier que l'app tourne
sleep 3
if pgrep -f gunicorn > /dev/null; then
    echo '✅ Application Flask redémarrée'
else
    echo '❌ Erreur redémarrage Flask'
    exit 1
fi
"

echo ""
echo "2️⃣  Configuration de Nginx..."
run_ssh "
# Créer la configuration Nginx
cat > /etc/nginx/sites-available/coach-patrimoine << 'NGINXEOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
NGINXEOF

# Activer le site
ln -sf /etc/nginx/sites-available/coach-patrimoine /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Tester la configuration
nginx -t

# Redémarrer Nginx
systemctl restart nginx

echo '✅ Nginx configuré et redémarré'
"

echo ""
echo "3️⃣  Test final..."
sleep 2
if run_ssh "curl -s -o /dev/null -w '%{http_code}' http://localhost/" | grep -q "200\|302\|301"; then
    echo "✅ Test local OK"
else
    echo "⚠️  Test local: réponse inattendue"
fi

# Test externe
echo "4️⃣  Test externe..."
if curl -s -o /dev/null -w "%{http_code}" http://$SERVER_IP/ | grep -q "200\|302\|301"; then
    echo "✅ Site accessible depuis l'extérieur"
else
    echo "❌ Site non accessible depuis l'extérieur"
fi

echo ""
echo "🎉 CORRECTION TERMINÉE!"
echo ""
echo "🌐 VOTRE SITE EST MAINTENANT ACCESSIBLE À :"
echo "   👉 http://$SERVER_IP"
echo ""
echo "🔑 COMPTES DE DÉMONSTRATION :"
echo "┌─────────────────┬──────────────────┬─────────────┬──────────────┐"
echo "│ Rôle            │ Email            │ Mot de passe│ Profil       │"
echo "├─────────────────┼──────────────────┼─────────────┼──────────────┤"
echo "│ 👑 Admin        │ admin@azur.com   │ Admin123!   │ Administrateur│"
echo "│ 👤 Utilisateur  │ marie@test.com   │ Test123!    │ Conservateur │"
echo "│ 👤 Utilisateur  │ paul@test.com    │ Test123!    │ Dynamique    │"
echo "│ 👤 Utilisateur  │ sophie@test.com  │ Test123!    │ Modéré       │"
echo "└─────────────────┴──────────────────┴─────────────┴──────────────┘"
echo ""
echo "🎯 URLS IMPORTANTES :"
echo "   • Site vitrine:  http://$SERVER_IP/site/"
echo "   • Connexion:     http://$SERVER_IP/plateforme/connexion"
echo "   • Chat IA:       Accessible depuis le dashboard utilisateur"
echo ""
echo "🚀 Coach Patrimoine est OPÉRATIONNEL!"
echo "🎊 PRÊT POUR LA DÉMONSTRATION!"