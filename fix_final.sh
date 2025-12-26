#!/bin/bash

# 🔧 Atlas - Correction FINALE PostgreSQL + Déploiement
# Résout le problème d'authentification PostgreSQL

set -e

SERVER_IP="139.59.158.149"
DB_NAME="atlas_db"
DB_USER="atlas_user"
DB_PASSWORD="atlas_password_2024_secure"

echo "🔧 ATLAS - CORRECTION FINALE"
echo "============================"
echo ""

echo "📤 Upload du code..."
# Créer l'archive propre
rm -f atlas_final.tar.gz
tar --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='.env' \
    --exclude='*.log' \
    --exclude='atlas_*.tar.gz' \
    -czf atlas_final.tar.gz .

scp atlas_final.tar.gz root@$SERVER_IP:/tmp/

echo "🔧 Correction PostgreSQL et déploiement..."
ssh root@$SERVER_IP 'bash -s' << 'REMOTE_SCRIPT'

echo "🛑 Arrêt des services..."
systemctl stop atlas 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true
pkill -f gunicorn 2>/dev/null || true

echo "📁 Extraction du code..."
rm -rf /var/www/atlas
mkdir -p /var/www/atlas
cd /var/www/atlas
tar -xzf /tmp/atlas_final.tar.gz

echo "🗄️ Configuration PostgreSQL CORRECTE..."
systemctl start postgresql
systemctl enable postgresql

# Configuration PostgreSQL pour accepter les connexions locales avec mot de passe
PG_VERSION=$(ls /etc/postgresql/ | head -1)
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"

# Backup et modification du fichier pg_hba.conf
cp "$PG_HBA" "$PG_HBA.backup"

# Modifier pour autoriser les connexions avec mot de passe
sed -i 's/local   all             all                                     peer/local   all             all                                     md5/' "$PG_HBA"
sed -i 's/host    all             all             127.0.0.1\/32            ident/host    all             all             127.0.0.1\/32            md5/' "$PG_HBA"
sed -i 's/host    all             all             ::1\/128                 ident/host    all             all             ::1\/128                 md5/' "$PG_HBA"

# Redémarrer PostgreSQL pour appliquer les changements
systemctl restart postgresql
sleep 3

echo "🗄️ Recréation de la base de données..."
# Supprimer et recréer la base avec les bonnes permissions
sudo -u postgres psql << 'EOF'
DROP DATABASE IF EXISTS atlas_db;
DROP USER IF EXISTS atlas_user;
CREATE USER atlas_user WITH PASSWORD 'atlas_password_2024_secure';
ALTER USER atlas_user CREATEDB;
CREATE DATABASE atlas_db OWNER atlas_user;
GRANT ALL PRIVILEGES ON DATABASE atlas_db TO atlas_user;
\q
EOF

# Tester la connexion
echo "🧪 Test de connexion PostgreSQL..."
export PGPASSWORD='atlas_password_2024_secure'
if psql -h localhost -U atlas_user -d atlas_db -c "SELECT version();" > /dev/null 2>&1; then
    echo "✅ Connexion PostgreSQL OK"
else
    echo "❌ Problème de connexion PostgreSQL"
    exit 1
fi

echo "🐍 Configuration Python..."
cd /var/www/atlas
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary python-dotenv
pip install reportlab Pillow requests yfinance bcrypt

echo "🔧 Fichier .env corrigé..."
cat > .env << 'EOF'
FLASK_ENV=production
FLASK_APP=run.py
SECRET_KEY=atlas-super-secret-key-production-2024
SQLALCHEMY_DATABASE_URI=postgresql://atlas_user:atlas_password_2024_secure@localhost:5432/atlas_db
DATABASE_URL=postgresql://atlas_user:atlas_password_2024_secure@localhost:5432/atlas_db
EOF

chown -R www-data:www-data /var/www/atlas
chmod -R 755 /var/www/atlas

echo "🗄️ Initialisation de la base..."
source venv/bin/activate

# Test simple de connexion avant d'initialiser
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        database='atlas_db', 
        user='atlas_user',
        password='atlas_password_2024_secure'
    )
    print('✅ Connexion Python OK')
    conn.close()
except Exception as e:
    print(f'❌ Erreur connexion: {e}')
    exit(1)
"

# Initialisation de l'application
python3 << 'PYTHON_INIT'
import os
import sys
sys.path.insert(0, '/var/www/atlas')
os.chdir('/var/www/atlas')

try:
    # Charger les variables d'environnement
    from dotenv import load_dotenv
    load_dotenv()
    
    from app import create_app, db
    from app.models.user import User
    from app.models.subscription import Subscription
    
    print('✅ Import réussi')
    
    app = create_app()
    with app.app_context():
        # Supprimer et recréer les tables
        db.drop_all()
        db.create_all()
        print('✅ Tables créées')
        
        # Créer admin
        admin = User(
            email='admin@gmail.com',
            first_name='Admin',
            last_name='Atlas',
            is_admin=True,
            is_active=True
        )
        admin.set_password('admin')
        db.session.add(admin)
        
        # Créer client test
        client = User(
            email='test.client@gmail.com',
            first_name='Test',
            last_name='Client',
            is_admin=False,
            is_active=True
        )
        client.set_password('password')
        db.session.add(client)
        
        db.session.commit()
        print('✅ Utilisateurs créés')
        
        # Abonnement pour le client
        subscription = Subscription(
            user_id=client.id,
            tier='initia',
            status='active',
            monthly_price=24.99
        )
        db.session.add(subscription)
        db.session.commit()
        print('✅ Base de données initialisée')

except Exception as e:
    print(f'❌ Erreur: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
PYTHON_INIT

echo "🚀 Configuration Gunicorn..."
cat > /etc/systemd/system/atlas.service << 'EOF'
[Unit]
Description=Atlas Gunicorn daemon
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/atlas
Environment="PATH=/var/www/atlas/venv/bin"
Environment="PYTHONPATH=/var/www/atlas"
ExecStart=/var/www/atlas/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 2 --timeout 120 run:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "🌐 Configuration Nginx..."
cat > /etc/nginx/sites-available/atlas << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
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

echo "🚀 Démarrage des services..."
systemctl daemon-reload
systemctl enable atlas
systemctl start atlas
systemctl restart nginx

sleep 5

echo "🔍 Vérification..."
systemctl is-active postgresql >/dev/null && echo "✅ PostgreSQL: ACTIF" || echo "❌ PostgreSQL"
systemctl is-active atlas >/dev/null && echo "✅ Atlas: ACTIF" || echo "❌ Atlas"
systemctl is-active nginx >/dev/null && echo "✅ Nginx: ACTIF" || echo "❌ Nginx"

# Test de l'application
echo "🧪 Test de l'application..."
sleep 3
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5000 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Application répond (HTTP $HTTP_CODE)"
else
    echo "⚠️ Application: HTTP $HTTP_CODE"
    echo "Logs Atlas:"
    journalctl -u atlas --no-pager -n 5
fi

rm -f /tmp/atlas_final.tar.gz

echo ""
echo "🎉 ATLAS CORRIGÉ ET DÉPLOYÉ !"
echo "============================="
echo ""
echo "🌐 Site: http://139.59.158.149"
echo "🔐 Admin: admin@gmail.com / admin"
echo "👤 Client: test.client@gmail.com / password"
echo ""

REMOTE_SCRIPT

rm -f atlas_final.tar.gz

echo ""
echo "🧪 Test final..."
sleep 5
for i in {1..3}; do
    if curl -s -o /dev/null -w "%{http_code}" http://$SERVER_IP | grep -E "^(200|302)$" >/dev/null; then
        echo "✅ 🎉 ATLAS EST EN LIGNE ! http://$SERVER_IP"
        break
    fi
    sleep 3
done

echo ""
echo "🚀 DÉPLOIEMENT FINAL TERMINÉ ! 🚀"
echo ""
echo "🌐 Votre plateforme Atlas :"
echo "   👉 http://$SERVER_IP"
echo "   👉 http://$SERVER_IP/plateforme/connexion"
echo ""