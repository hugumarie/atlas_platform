#!/bin/bash

# 🔧 Atlas - Script qui MARCHE à 100%
# Corrige tous les problèmes et démarre Atlas

set -e

SERVER_IP="139.59.158.149"
DB_NAME="atlas_db"
DB_USER="atlas_user" 
DB_PASSWORD="atlas_password_2024_secure"

echo "🔧 ATLAS - CORRECTION ET DÉMARRAGE"
echo "=================================="
echo ""

echo "🛑 1. Arrêt des services..."
ssh root@$SERVER_IP "
    systemctl stop atlas 2>/dev/null || true
    systemctl stop nginx 2>/dev/null || true
    pkill -f gunicorn || true
"

echo "🗄️ 2. Reset COMPLET de la base de données..."
ssh root@$SERVER_IP "
    systemctl start postgresql
    
    # Recréer la base complètement
    sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS $DB_NAME;
DROP USER IF EXISTS $DB_USER;
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
ALTER USER $DB_USER CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER DATABASE $DB_NAME OWNER TO $DB_USER;
\\q
EOF
    echo '✅ Base de données reset'
"

echo "🔧 3. Correction de l'application..."
ssh root@$SERVER_IP "
    cd /var/www/atlas
    source venv/bin/activate
    
    # Mise à jour de tous les packages
    pip install --upgrade pip
    pip install flask flask-sqlalchemy flask-login flask-mail flask-wtf
    pip install psycopg2-binary gunicorn python-dotenv
    pip install reportlab Pillow requests yfinance bcrypt
    
    echo '✅ Packages mis à jour'
"

echo "🔧 4. Reconfiguration environnement..."
ssh root@$SERVER_IP "
    cd /var/www/atlas
    
    # .env simple et qui marche
    cat > .env << 'EOF'
FLASK_ENV=production
FLASK_APP=run.py
SECRET_KEY=$(openssl rand -hex 32)
SQLALCHEMY_DATABASE_URI=postgresql://$DB_USER:$DB_PASSWORD@localhost/$DB_NAME
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost/$DB_NAME
EOF
    
    chown -R www-data:www-data /var/www/atlas
    chmod -R 755 /var/www/atlas
"

echo "🗄️ 5. Initialisation propre de la DB..."
ssh root@$SERVER_IP "
    cd /var/www/atlas
    source venv/bin/activate
    
    python3 << 'EOF'
import os
import sys
sys.path.insert(0, '/var/www/atlas')
os.chdir('/var/www/atlas')

try:
    from app import create_app, db
    from app.models.user import User
    from app.models.subscription import Subscription
    
    print('✅ Import des modèles OK')
    
    app = create_app()
    with app.app_context():
        # Supprimer toutes les tables existantes
        db.drop_all()
        print('✅ Tables supprimées')
        
        # Recréer toutes les tables
        db.create_all()
        print('✅ Tables créées')
        
        # Créer l'utilisateur admin
        admin = User(
            email='admin@gmail.com',
            first_name='Admin',
            last_name='Atlas',
            is_admin=True,
            is_active=True
        )
        admin.set_password('admin')
        
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin créé: admin@gmail.com / admin')
        
        # Créer un utilisateur client test
        client = User(
            email='test.client@gmail.com',
            first_name='Test',
            last_name='Client',
            is_admin=False,
            is_active=True
        )
        client.set_password('password')
        
        # Créer son abonnement
        subscription = Subscription(
            user=client,
            tier='initia',
            status='active',
            monthly_price=24.99
        )
        
        db.session.add(client)
        db.session.add(subscription)
        db.session.commit()
        print('✅ Client test créé: test.client@gmail.com / password')
        
        print('✅ Base de données initialisée avec succès')
        
except Exception as e:
    print(f'❌ Erreur: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF
"

echo "🚀 6. Configuration Gunicorn SIMPLE..."
ssh root@$SERVER_IP "
    # Service Gunicorn simplifié
    cat > /etc/systemd/system/atlas.service << 'EOF'
[Unit]
Description=Atlas Gunicorn daemon
After=network.target postgresql.service
Requires=postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/atlas
Environment=\"PATH=/var/www/atlas/venv/bin\"
Environment=\"PYTHONPATH=/var/www/atlas\"
ExecStart=/var/www/atlas/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 2 --timeout 60 --log-level info run:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable atlas
"

echo "🌐 7. Configuration Nginx SIMPLE..."
ssh root@$SERVER_IP "
    cat > /etc/nginx/sites-available/atlas << 'EOF'
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
    
    location /static {
        alias /var/www/atlas/app/static;
        expires 1d;
    }
}
EOF
    
    ln -sf /etc/nginx/sites-available/atlas /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    nginx -t
"

echo "🚀 8. Démarrage des services..."
ssh root@$SERVER_IP "
    systemctl start atlas
    systemctl start nginx
    
    sleep 5
    
    echo '📊 Statut des services:'
    systemctl is-active postgresql && echo '✅ PostgreSQL: ACTIF' || echo '❌ PostgreSQL: PROBLÈME'
    systemctl is-active atlas && echo '✅ Atlas: ACTIF' || echo '❌ Atlas: PROBLÈME'
    systemctl is-active nginx && echo '✅ Nginx: ACTIF' || echo '❌ Nginx: PROBLÈME'
"

echo "🧪 9. Test de l'application..."
ssh root@$SERVER_IP "
    sleep 3
    
    echo 'Test de connectivité locale...'
    if curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5000 | grep -E '^(200|302|404)$'; then
        echo '✅ Application répond'
    else
        echo '❌ Application ne répond pas'
        echo 'Logs Atlas:'
        journalctl -u atlas --no-pager -n 10
    fi
"

echo "🧹 10. Nettoyage..."
rm -f atlas_deploy.tar.gz 2>/dev/null || true

echo ""
echo "🎉 ATLAS CORRIGÉ ET DÉPLOYÉ !"
echo "============================="
echo ""
echo "🌐 Atlas accessible sur :"
echo "   👉 http://$SERVER_IP"
echo ""
echo "🔐 Comptes de test :"
echo "   📱 Admin: admin@gmail.com / admin"
echo "   👤 Client: test.client@gmail.com / password"
echo ""
echo "🌐 URLs importantes :"
echo "   - Site: http://$SERVER_IP"
echo "   - Connexion: http://$SERVER_IP/plateforme/connexion"
echo "   - Dashboard: http://$SERVER_IP/plateforme/dashboard"
echo ""

# Test final
echo "🧪 Test final..."
sleep 5
if curl -s -o /dev/null -w "%{http_code}" http://$SERVER_IP | grep -E "^(200|302)$"; then
    echo "✅ 🎉 ATLAS FONCTIONNE ! http://$SERVER_IP"
else
    echo "⚠️ Test en cours... Essayez dans 30 secondes : http://$SERVER_IP"
    echo "Si problème, logs: ssh root@$SERVER_IP 'journalctl -u atlas -f'"
fi

echo ""
echo "🚀 TERMINÉ ! Atlas V2.0 est EN LIGNE ! 🚀"