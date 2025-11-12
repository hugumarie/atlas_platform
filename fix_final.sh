#!/bin/bash

echo "🔧 CORRECTION FINALE - Instructions pas-à-pas"
echo ""
echo "Copiez-collez ces commandes UNE PAR UNE :"
echo ""

echo "1️⃣  Connexion au serveur :"
echo "ssh root@165.227.167.78"
echo ""

echo "2️⃣  Quand il demande le mot de passe, tapez :"
echo "(!=ZL@-nZu7eB?7a"
echo ""

echo "3️⃣  Une fois connecté, démarrez l'application :"
echo "su - appuser"
echo "cd /home/appuser/coach-patrimoine"
echo "source venv/bin/activate"
echo "pkill -f gunicorn || true"
echo "nohup gunicorn --bind 127.0.0.1:5000 --workers 2 wsgi:app > /tmp/gunicorn.log 2>&1 &"
echo "exit"
echo ""

echo "4️⃣  Configurez Nginx (copiez TOUT d'un coup) :"
cat << 'EOF'
cat > /etc/nginx/sites-available/coach-patrimoine << 'NGINXEOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINXEOF
EOF
echo ""

echo "5️⃣  Activez la nouvelle configuration :"
echo "rm -f /etc/nginx/sites-enabled/default"
echo "ln -sf /etc/nginx/sites-available/coach-patrimoine /etc/nginx/sites-enabled/"
echo "nginx -t"
echo "systemctl reload nginx"
echo ""

echo "6️⃣  Testez que ça marche :"
echo "curl http://localhost/"
echo ""

echo "7️⃣  Déconnectez-vous :"
echo "exit"
echo ""

echo "🌐 Votre site sera alors accessible à : http://165.227.167.78"
echo ""
echo "💡 Si ça ne marche toujours pas, faites :"
echo "   systemctl status nginx"
echo "   systemctl status gunicorn"
echo "   tail -f /tmp/gunicorn.log"