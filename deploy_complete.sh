#!/bin/bash

# 🚀 Atlas - Déploiement COMPLET avec toutes dépendances
# Script bordel qui règle tous les problèmes

set -e

SERVER_IP="139.59.158.149"
DB_NAME="atlas_db"
DB_USER="atlas_user"
DB_PASSWORD="atlas_password_2024_secure"

echo "🚀 ATLAS - Déploiement COMPLET"
echo "=============================="
echo ""

# Vérifier qu'on est dans le bon dossier
if [ ! -f "run.py" ]; then
    echo "❌ Erreur : run.py non trouvé"
    echo "   Assurez-vous d'être dans le dossier Atlas"
    exit 1
fi

echo "📦 1. Préparation du package Atlas..."
# Supprimer l'ancienne archive si elle existe
rm -f atlas_deploy.tar.gz

# Créer un archive temporaire (excluant les fichiers inutiles)
tar --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='.env' \
    --exclude='*.log' \
    --exclude='atlas_deploy.tar.gz' \
    -czf atlas_deploy.tar.gz .

echo "   ✅ Archive créée ($(du -h atlas_deploy.tar.gz | cut -f1))"

echo ""
echo "📤 2. Upload vers le serveur..."
scp atlas_deploy.tar.gz root@$SERVER_IP:/tmp/

echo ""
echo "🛠️ 3. Installation COMPLÈTE des dépendances système..."
ssh root@$SERVER_IP "
    export DEBIAN_FRONTEND=noninteractive
    apt update -y
    apt upgrade -y
    
    # Installer TOUTES les dépendances système
    apt install -y python3 python3-pip python3-venv python3-dev \
                   nginx postgresql postgresql-contrib git supervisor \
                   ufw curl build-essential libpq-dev pkg-config \
                   python3-psycopg2 libfreetype6-dev libjpeg-dev \
                   libpng-dev zlib1g-dev libssl-dev libffi-dev \
                   redis-server
    
    # Démarrer PostgreSQL
    systemctl start postgresql
    systemctl enable postgresql
    
    echo '✅ Dépendances système installées'
"

echo ""
echo "🗄️ 4. Configuration PostgreSQL..."
ssh root@$SERVER_IP "
    # Créer la base de données et l'utilisateur
    sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS $DB_NAME;
DROP USER IF EXISTS $DB_USER;
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER USER $DB_USER CREATEDB;
\\q
EOF
    echo '✅ PostgreSQL configuré'
"

echo ""
echo "🔧 5. Extraction et configuration Atlas..."
ssh root@$SERVER_IP "
    # Nettoyage et extraction
    rm -rf /var/www/atlas
    mkdir -p /var/www/atlas
    cd /var/www/atlas
    tar -xzf /tmp/atlas_deploy.tar.gz
    
    echo '✅ Fichiers extraits'
"

echo ""
echo "🐍 6. Configuration Python COMPLÈTE..."
ssh root@$SERVER_IP "
    cd /var/www/atlas
    
    # Environnement virtuel
    python3 -m venv venv
    source venv/bin/activate
    
    # Mise à jour pip
    pip install --upgrade pip setuptools wheel
    
    # Installation des dépendances de base
    pip install -r requirements.txt
    
    # Installation de TOUTES les dépendances manquantes
    pip install gunicorn psycopg2-binary python-dotenv \
                reportlab Pillow requests yfinance \
                redis celery flask-mail cryptography \
                pycryptodome bcrypt
    
    echo '✅ Python et dépendances installés'
"

echo ""
echo "🔧 7. Configuration environnement..."
ssh root@$SERVER_IP "
    cd /var/www/atlas
    
    # Fichier .env COMPLET
    cat > .env << EOF
# Configuration Flask
FLASK_ENV=production
FLASK_APP=run.py
SECRET_KEY=$(openssl rand -hex 64)

# Base de données PostgreSQL (production)
SQLALCHEMY_DATABASE_URI=postgresql://$DB_USER:$DB_PASSWORD@localhost/$DB_NAME
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost/$DB_NAME

# Configuration OpenAI (pour l'assistant IA)
OPENAI_API_KEY=your-api-key-here

# Configuration serveur
HOST=0.0.0.0
PORT=5000
DEBUG=False

# Configuration emails (si nécessaire)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=
MAIL_PASSWORD=

# Configuration Binance API (pour les prix crypto)
BINANCE_API_KEY=
BINANCE_SECRET_KEY=
EOF
    
    # Permissions
    chown -R www-data:www-data /var/www/atlas
    chmod -R 755 /var/www/atlas
    
    echo '✅ Configuration terminée'
"

echo ""
echo "🗄️ 8. Initialisation base de données avec RETRY..."
ssh root@$SERVER_IP "
    cd /var/www/atlas
    source venv/bin/activate
    
    # Test avec retry en cas d'erreur
    for i in {1..3}; do
        echo \"Tentative \$i/3...\"
        python3 -c \"
import sys
import os
sys.path.insert(0, '/var/www/atlas')
os.chdir('/var/www/atlas')

try:
    from app import create_app, db
    from app.models.user import User
    
    app = create_app()
    with app.app_context():
        # Créer toutes les tables
        db.create_all()
        print('✅ Tables créées')
        
        # Créer admin
        admin = User.query.filter_by(email='admin@gmail.com').first()
        if not admin:
            admin = User(
                email='admin@gmail.com',
                first_name='Admin',
                last_name='Atlas',
                is_admin=True
            )
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print('✅ Admin créé: admin@gmail.com / admin')
        else:
            print('✅ Admin existe déjà')
        
        print('✅ Base de données OK')
        
except Exception as e:
    print(f'❌ Erreur: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
\" && break || sleep 5
    done
"

echo ""
echo "🚀 9. Configuration des services..."
ssh root@$SERVER_IP "
    # Service Gunicorn
    cat > /etc/systemd/system/atlas.service << 'EOF'
[Unit]
Description=Atlas Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/atlas
Environment=\"PATH=/var/www/atlas/venv/bin\"
ExecStart=/var/www/atlas/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 --timeout 120 run:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    # Configuration Nginx
    cat > /etc/nginx/sites-available/atlas << 'EOF'
server {
    listen 80;
    server_name _;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
    
    location /static {
        alias /var/www/atlas/app/static;
        expires 1y;
        add_header Cache-Control \"public, immutable\";
    }
}
EOF
    
    # Activation des services
    systemctl daemon-reload
    systemctl stop atlas 2>/dev/null || true
    systemctl disable atlas 2>/dev/null || true
    systemctl enable atlas
    systemctl start atlas
    
    ln -sf /etc/nginx/sites-available/atlas /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    nginx -t
    systemctl restart nginx
    
    echo '✅ Services configurés et démarrés'
"

echo ""
echo "⏰ 10. Configuration du cron crypto + Script de démarrage Atlas..."
ssh root@$SERVER_IP "
    # Script de mise à jour crypto (basé sur votre refresh_crypto_prices.py)
    cat > /var/www/atlas/update_crypto_prices.sh << 'EOF'
#!/bin/bash
cd /var/www/atlas
source venv/bin/activate
export PYTHONPATH=/var/www/atlas

echo \"💰 Mise à jour des prix crypto...\"
if python3 refresh_crypto_prices.py; then
    echo \"✅ Prix crypto mis à jour avec succès\"
else
    echo \"⚠️ Erreur mise à jour crypto, continuer quand même...\"
fi
EOF
    
    # Script de démarrage Atlas (basé sur votre start_atlas.sh)
    cat > /var/www/atlas/start_atlas_server.sh << 'EOF'
#!/bin/bash

echo \"🚀 Démarrage d'Atlas Platform (Serveur)...\"

# Vérifier PostgreSQL
echo \"📊 Vérification PostgreSQL...\"
if systemctl is-active postgresql > /dev/null 2>&1; then
    echo \"✅ PostgreSQL déjà démarré\"
else
    echo \"🔄 Démarrage de PostgreSQL...\"
    systemctl start postgresql
    sleep 2 
fi

# Test de connexion à la base
echo \"🔍 Test de connexion à la base...\"
cd /var/www/atlas
source venv/bin/activate

if python3 -c \"
import psycopg2
try:
    conn = psycopg2.connect('postgresql://$DB_USER:$DB_PASSWORD@localhost/$DB_NAME')
    print('✅ Base de données accessible')
    conn.close()
except Exception as e:
    print(f'❌ Erreur de connexion à la base: {e}')
    exit(1)
\"; then
    echo \"✅ Connexion DB OK\"
else
    echo \"❌ Erreur de connexion à la base\"
    exit 1
fi

# Afficher les informations de connexion
echo \"\"
echo \"🎯 Atlas Platform prête !\"
echo \"================================\"
echo \"📊 Base de données: PostgreSQL (atlas_db)\"
echo \"🌐 Serveur accessible sur http://$SERVER_IP\"
echo \"\"
echo \"🔑 Comptes disponibles:\"
echo \"  - Admin: admin@gmail.com / admin\"
echo \"  - Client: test.client@gmail.com\"
echo \"\"
echo \"🌐 URLs importantes:\"
echo \"  - Site vitrine: http://$SERVER_IP\"
echo \"  - Connexion: http://$SERVER_IP/plateforme/connexion\"
echo \"  - Dashboard: http://$SERVER_IP/plateforme/dashboard\"
echo \"\"

# Mise à jour des prix crypto
echo \"💰 Mise à jour des prix crypto...\"
if ./update_crypto_prices.sh; then
    echo \"✅ Prix crypto mis à jour avec succès\"
else
    echo \"⚠️ Erreur mise à jour crypto, continuer quand même...\"
fi
echo \"\"

# Vérifier les services
echo \"🔍 Vérification des services...\"
systemctl status atlas --no-pager
systemctl status nginx --no-pager

echo \"✅ Atlas Platform démarrée avec succès !\"
EOF
    
    # Rendre les scripts exécutables
    chmod +x /var/www/atlas/update_crypto_prices.sh
    chmod +x /var/www/atlas/start_atlas_server.sh
    chown www-data:www-data /var/www/atlas/update_crypto_prices.sh
    chown www-data:www-data /var/www/atlas/start_atlas_server.sh
    
    # Ajouter au crontab
    (crontab -l 2>/dev/null | grep -v update_crypto_prices; echo '0 * * * * /var/www/atlas/update_crypto_prices.sh >> /var/log/atlas_crypto.log 2>&1') | crontab -
    
    touch /var/log/atlas_crypto.log
    chown www-data:www-data /var/log/atlas_crypto.log
    
    echo '✅ Scripts configurés'
    
    # Test initial des prix crypto
    echo '🧪 Test initial crypto...'
    /var/www/atlas/update_crypto_prices.sh
    
    # Exécuter le script de démarrage pour vérifier tout
    echo '🧪 Test du script de démarrage...'
    /var/www/atlas/start_atlas_server.sh
"

echo ""
echo "🔍 11. Vérification COMPLÈTE..."
ssh root@$SERVER_IP "
    echo '📊 Statut des services :'
    systemctl is-active atlas && echo 'Atlas: ✅ ACTIF' || echo 'Atlas: ❌ INACTIF'
    systemctl is-active nginx && echo 'Nginx: ✅ ACTIF' || echo 'Nginx: ❌ INACTIF'
    systemctl is-active postgresql && echo 'PostgreSQL: ✅ ACTIF' || echo 'PostgreSQL: ❌ INACTIF'
    
    echo ''
    echo '🌐 Test de connectivité :'
    sleep 5
    HTTP_CODE=\$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5000)
    if [ \"\$HTTP_CODE\" = \"200\" ] || [ \"\$HTTP_CODE\" = \"302\" ]; then
        echo \"✅ Application répond (HTTP \$HTTP_CODE)\"
    else
        echo \"⚠️ Application démarrage... (HTTP \$HTTP_CODE)\"
    fi
"

echo ""
echo "🧹 12. Nettoyage..."
rm -f atlas_deploy.tar.gz
ssh root@$SERVER_IP "rm -f /tmp/atlas_deploy.tar.gz"

echo ""
echo "🎉 DÉPLOIEMENT COMPLET TERMINÉ !"
echo "================================="
echo ""
echo "🌐 Atlas accessible sur :"
echo "   👉 http://$SERVER_IP"
echo ""
echo "🔐 Connexion admin :"
echo "   Email : admin@gmail.com"
echo "   Mot de passe : admin"
echo ""
echo "📝 Commandes de diagnostic :"
echo "   - Logs Atlas : ssh root@$SERVER_IP 'journalctl -u atlas -f'"
echo "   - Logs Nginx : ssh root@$SERVER_IP 'tail -f /var/log/nginx/error.log'"
echo "   - Logs crypto : ssh root@$SERVER_IP 'tail -f /var/log/atlas_crypto.log'"
echo "   - Redémarrer Atlas : ssh root@$SERVER_IP 'systemctl restart atlas'"
echo "   - Statut complet : ssh root@$SERVER_IP 'systemctl status atlas nginx postgresql'"
echo ""
echo "⏰ Mise à jour crypto automatique toutes les heures"
echo ""

# Test final avec retry
echo "🧪 Test final de connectivité (avec retry)..."
for i in {1..5}; do
    echo "Test $i/5..."
    sleep 3
    if curl -s -o /dev/null -w "%{http_code}" http://$SERVER_IP | grep -q "200\|302"; then
        echo "✅ 🎉 ATLAS EST EN LIGNE ! http://$SERVER_IP"
        break
    elif [ $i -eq 5 ]; then
        echo "⚠️ Atlas peut encore démarrer... Essayez dans 2-3 minutes : http://$SERVER_IP"
    fi
done

echo ""
echo "🚀 ATLAS V2.0 DÉPLOYÉ AVEC SUCCÈS ! 🚀"