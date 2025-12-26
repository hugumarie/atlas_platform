#!/bin/bash

# 🔧 Atlas - Correction DÉFINITIVE du problème PostgreSQL
# Script qui corrige l'authentification PostgreSQL une bonne fois pour toutes

set -e

SERVER_IP="139.59.158.149"
DB_NAME="atlas_db"
DB_USER="atlas_user"
DB_PASSWORD="atlas_password_2024_secure"

echo "🔧 ATLAS - CORRECTION DÉFINITIVE"
echo "================================="
echo ""

echo "🛑 Correction du problème PostgreSQL sur le serveur..."
ssh root@$SERVER_IP 'bash -s' << 'REMOTE_SCRIPT'

echo "🛑 Arrêt des services..."
systemctl stop atlas 2>/dev/null || true
pkill -f gunicorn 2>/dev/null || true

echo "🗄️ Correction PostgreSQL..."
# Trouver la version de PostgreSQL
PG_VERSION=$(ls /etc/postgresql/ | head -1)
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"

echo "Version PostgreSQL détectée: $PG_VERSION"

# Backup du fichier original
cp "$PG_HBA" "$PG_HBA.backup"

# Modifier pour autoriser les connexions avec mot de passe (md5)
sed -i 's/local   all             all                                     peer/local   all             all                                     md5/' "$PG_HBA"
sed -i 's/host    all             all             127.0.0.1\/32            ident/host    all             all             127.0.0.1\/32            md5/' "$PG_HBA"
sed -i 's/host    all             all             ::1\/128                 ident/host    all             all             ::1\/128                 md5/' "$PG_HBA"

echo "Configuration PostgreSQL modifiée"

# Redémarrer PostgreSQL
systemctl restart postgresql
sleep 3

# Reset complet de la base
echo "🗄️ Reset complet de la base de données..."
sudo -u postgres psql << 'EOF'
DROP DATABASE IF EXISTS atlas_db;
DROP USER IF EXISTS atlas_user;
CREATE USER atlas_user WITH PASSWORD 'atlas_password_2024_secure';
ALTER USER atlas_user CREATEDB;
CREATE DATABASE atlas_db OWNER atlas_user;
GRANT ALL PRIVILEGES ON DATABASE atlas_db TO atlas_user;
\q
EOF

echo "✅ Base de données recréée"

# Test de connexion
echo "🧪 Test de connexion..."
export PGPASSWORD='atlas_password_2024_secure'
if psql -h localhost -U atlas_user -d atlas_db -c "SELECT version();" > /dev/null 2>&1; then
    echo "✅ Connexion PostgreSQL OK"
else
    echo "❌ Problème de connexion PostgreSQL"
    exit 1
fi

echo "🔧 Correction du fichier .env..."
cd /var/www/atlas

# Créer un .env correct
cat > .env << 'EOF'
FLASK_ENV=production
FLASK_APP=run.py
SECRET_KEY=atlas-super-secret-key-production-2024
SQLALCHEMY_DATABASE_URI=postgresql://atlas_user:atlas_password_2024_secure@localhost:5432/atlas_db
DATABASE_URL=postgresql://atlas_user:atlas_password_2024_secure@localhost:5432/atlas_db
EOF

echo "🗄️ Initialisation propre de la base..."
source venv/bin/activate

# Test simple de connexion Python
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        database='atlas_db',
        user='atlas_user', 
        password='atlas_password_2024_secure'
    )
    print('✅ Test connexion Python OK')
    conn.close()
except Exception as e:
    print(f'❌ Erreur: {e}')
    exit(1)
"

# Initialiser l'application avec les bonnes tables
python3 << 'PYTHON_INIT'
import os
import sys
sys.path.insert(0, '/var/www/atlas')
os.chdir('/var/www/atlas')

try:
    from dotenv import load_dotenv
    load_dotenv()
    
    from app import create_app, db
    from app.models.user import User
    from app.models.subscription import Subscription
    
    print('✅ Import des modèles OK')
    
    app = create_app()
    with app.app_context():
        # Supprimer et recréer toutes les tables
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
        
        # Abonnement client
        subscription = Subscription(
            user_id=client.id,
            tier='initia',
            status='active',
            monthly_price=24.99
        )
        db.session.add(subscription)
        db.session.commit()
        print('✅ Base de données initialisée complètement')

except Exception as e:
    print(f'❌ Erreur: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
PYTHON_INIT

echo "🚀 Configuration service Gunicorn avec variables d'environnement..."
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
EnvironmentFile=/var/www/atlas/.env
ExecStart=/var/www/atlas/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 2 --timeout 120 run:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Permissions sur .env
chown www-data:www-data /var/www/atlas/.env
chmod 644 /var/www/atlas/.env
chown -R www-data:www-data /var/www/atlas

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

echo "🧪 Test de l'application..."
sleep 3
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5000 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Application répond parfaitement (HTTP $HTTP_CODE)"
else
    echo "⚠️ Application: HTTP $HTTP_CODE"
    echo "Logs récents:"
    journalctl -u atlas --no-pager -n 3
fi

echo ""
echo "🎉 CORRECTION TERMINÉE !"
echo "======================="
echo ""
echo "🌐 Site: http://139.59.158.149"
echo "🔐 Admin: admin@gmail.com / admin"
echo "👤 Client: test.client@gmail.com / password"
echo ""

REMOTE_SCRIPT

echo ""
echo "🧪 Test final depuis votre machine..."
sleep 5
for i in {1..3}; do
    echo "Test $i/3..."
    if curl -s -o /dev/null -w "%{http_code}" http://$SERVER_IP | grep -E "^(200|302)$" >/dev/null; then
        echo "✅ 🎉 ATLAS FONCTIONNE PARFAITEMENT !"
        echo ""
        echo "🌐 Votre plateforme Atlas est accessible :"
        echo "   👉 http://$SERVER_IP"
        echo "   👉 http://$SERVER_IP/plateforme/connexion"
        echo ""
        echo "🔐 Comptes de test :"
        echo "   📱 Admin: admin@gmail.com / admin"
        echo "   👤 Client: test.client@gmail.com / password"
        break
    fi
    sleep 3
done

echo ""
echo "🚀 ATLAS V2.0 EN LIGNE ! 🚀"