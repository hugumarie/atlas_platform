#!/bin/bash

echo "🚀 ATLAS - DÉPLOIEMENT ULTRA SIMPLE"
echo "===================================="
echo ""

# Variables
SERVER_IP="139.59.158.149"
ATLAS_DIR="/var/www/atlas"
BACKUP_DIR="/root/atlas_backups"

# Fonction pour afficher des messages colorés
log_info() { echo -e "\033[32m[INFO]\033[0m $1"; }
log_warn() { echo -e "\033[33m[WARN]\033[0m $1"; }
log_error() { echo -e "\033[31m[ERROR]\033[0m $1"; }

# Vérifier les prérequis
check_files() {
    log_info "🔍 Vérification des fichiers..."
    
    if ! ls atlas_production_*.tar.gz >/dev/null 2>&1; then
        log_error "Package Atlas non trouvé ! Exécutez d'abord : ./migrate_to_production.sh"
        exit 1
    fi
    
    if [ ! -f "atlas_config.env" ]; then
        log_error "Fichier atlas_config.env manquant !"
        exit 1
    fi
    
    log_info "✅ Fichiers OK"
}

# Transfert des fichiers
transfer_files() {
    log_info "📤 Transfert vers le serveur..."
    
    PACKAGE=$(ls atlas_production_*.tar.gz | head -1)
    
    scp "$PACKAGE" root@$SERVER_IP:/root/
    scp atlas_config.env root@$SERVER_IP:/root/
    
    # Créer le script de déploiement serveur
    cat > /tmp/deploy_on_server.sh << 'EOF'
#!/bin/bash

echo "🚀 Déploiement Atlas sur serveur"
echo "================================"

# Variables
ATLAS_DIR="/var/www/atlas"
BACKUP_DIR="/root/atlas_backups"

# Fonction log
log_info() { echo -e "\033[32m[INFO]\033[0m $1"; }

# Arrêter Atlas si en cours
log_info "🛑 Arrêt d'Atlas..."
systemctl stop atlas 2>/dev/null || true

# Sauvegarde de l'ancien déploiement
if [ -d "$ATLAS_DIR" ]; then
    log_info "💾 Sauvegarde de l'ancien Atlas..."
    mkdir -p $BACKUP_DIR
    cp -r $ATLAS_DIR "$BACKUP_DIR/atlas_$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
fi

# Nettoyage et préparation
log_info "🧹 Nettoyage..."
rm -rf $ATLAS_DIR
mkdir -p $ATLAS_DIR
cd $ATLAS_DIR

# Installation des dépendances système si nécessaire
log_info "📦 Vérification des dépendances..."
which python3 >/dev/null || apt update && apt install -y python3 python3-pip python3-venv
which psql >/dev/null || apt install -y postgresql postgresql-contrib
which nginx >/dev/null || apt install -y nginx
which ufw >/dev/null || apt install -y ufw

# Extraction du package Atlas
log_info "📦 Extraction d'Atlas..."
PACKAGE=$(ls /root/atlas_production_*.tar.gz | head -1)
tar -xzf "$PACKAGE" --strip-components=1 2>/dev/null || {
    tar -xzf "$PACKAGE"
    if [ -d "production_ready" ]; then
        mv production_ready/* .
        rmdir production_ready 2>/dev/null || true
    fi
}

# Structure correcte de l'application
log_info "📁 Configuration de la structure..."
if [ ! -d "app" ]; then
    mkdir -p app
    for item in models routes services tasks templates static __init__.py scheduler.py; do
        if [ -e "$item" ]; then
            mv "$item" app/ 2>/dev/null || true
        fi
    done
fi

# Charger la configuration
log_info "⚙️ Configuration des variables..."
source /root/atlas_config.env

# Créer le fichier .env.production
cat > .env.production << ENVEOF
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=$FLASK_SECRET_KEY
SQLALCHEMY_DATABASE_URI=postgresql://atlas:$DATABASE_PASSWORD@localhost/atlas_production_db
MAIL_SERVER=$MAIL_SERVER
MAIL_PORT=$MAIL_PORT
MAIL_USE_TLS=True
MAIL_USERNAME=$MAIL_USERNAME
MAIL_PASSWORD=$MAIL_PASSWORD
OPENAI_API_KEY=$OPENAI_API_KEY
BINANCE_API_KEY=$BINANCE_API_KEY
BINANCE_SECRET_KEY=$BINANCE_SECRET_KEY
WTF_CSRF_ENABLED=True
LOG_LEVEL=INFO
DEBUG=False
TESTING=False
ENVEOF

# Configuration PostgreSQL
log_info "💾 Configuration PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

sudo -u postgres psql -c "CREATE DATABASE atlas_production_db;" 2>/dev/null || true
sudo -u postgres psql -c "DROP USER IF EXISTS atlas;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER atlas WITH ENCRYPTED PASSWORD '$DATABASE_PASSWORD';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE atlas_production_db TO atlas;"
sudo -u postgres psql -c "ALTER USER atlas SUPERUSER;"

# Environnement Python
log_info "🐍 Configuration Python..."
python3 -m venv venv
source venv/bin/activate
pip install --timeout 300 -r requirements.txt

# Création des tables
log_info "🗃️ Création des tables..."
export FLASK_APP=run.py
python3 << PYEOF
import sys
import os
sys.path.insert(0, '/var/www/atlas')
os.environ['SQLALCHEMY_DATABASE_URI'] = 'postgresql://atlas:$DATABASE_PASSWORD@localhost/atlas_production_db'

from app import create_app
app = create_app()
with app.app_context():
    from app.models import db
    db.create_all()
    print('✅ Tables créées')
PYEOF

# Import des données si disponible
if [ -f "atlas_database_import.sql" ]; then
    log_info "📥 Import des données..."
    sudo -u postgres psql -d atlas_production_db -f atlas_database_import.sql >/dev/null 2>&1 || true
fi

# Configuration des services
log_info "🔧 Configuration des services..."

# Service systemd Atlas
cat > /etc/systemd/system/atlas.service << SERVICEEOF
[Unit]
Description=Atlas Wealth Management Platform
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=$ATLAS_DIR
Environment=PATH=$ATLAS_DIR/venv/bin
EnvironmentFile=$ATLAS_DIR/.env.production
ExecStart=$ATLAS_DIR/venv/bin/gunicorn -w 1 -b 127.0.0.1:5000 --timeout 120 run:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Configuration Nginx
cat > /etc/nginx/sites-available/atlas << NGINXEOF
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
    
    location /static/ {
        alias $ATLAS_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
NGINXEOF

ln -sf /etc/nginx/sites-available/atlas /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Configuration du cron pour les prix crypto
log_info "⏰ Configuration du cron crypto..."
cat > /etc/cron.d/atlas-crypto << CRONEOF
# Mise à jour des prix crypto toutes les heures
0 * * * * www-data cd $ATLAS_DIR && $ATLAS_DIR/venv/bin/python refresh_crypto_prices.py >> /var/log/atlas_crypto.log 2>&1
CRONEOF

# Permissions
log_info "🔐 Configuration des permissions..."
chown -R www-data:www-data $ATLAS_DIR
chmod 600 $ATLAS_DIR/.env.production
chmod +x /etc/cron.d/atlas-crypto

# Firewall
log_info "🔒 Configuration firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# Démarrage des services
log_info "🚀 Démarrage des services..."
nginx -t && systemctl restart nginx
systemctl daemon-reload
systemctl enable atlas
systemctl restart atlas

# Première mise à jour des prix crypto
log_info "💰 Première mise à jour crypto..."
cd $ATLAS_DIR
source venv/bin/activate
python refresh_crypto_prices.py 2>/dev/null || echo "Mise à jour crypto en arrière-plan"

# Test final
sleep 5
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ || echo "000")

echo ""
echo "🎉 DÉPLOIEMENT TERMINÉ !"
echo "========================"
echo "🌐 URL: http://139.59.158.149"
echo "📊 Code HTTP: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Atlas fonctionne parfaitement !"
else
    echo "⚠️ Problème détecté (code: $HTTP_CODE)"
    echo "🔧 Vérifiez les logs: journalctl -fu atlas"
fi

echo ""
echo "🔑 Comptes disponibles:"
echo "   - Admin: admin@gmail.com"
echo "   - Client: test.client@gmail.com"
echo ""
echo "📊 Services:"
systemctl --no-pager status atlas nginx postgresql | grep -E "(atlas.service|nginx.service|postgresql.service|Active:)" | head -6
echo ""
echo "🎯 Atlas est en production !"
EOF

    scp /tmp/deploy_on_server.sh root@$SERVER_IP:/root/
    rm /tmp/deploy_on_server.sh
    
    log_info "✅ Fichiers transférés"
}

# Exécution sur le serveur
deploy_on_server() {
    log_info "🎬 Exécution du déploiement..."
    
    ssh root@$SERVER_IP "chmod +x /root/deploy_on_server.sh && /root/deploy_on_server.sh"
}

# Test final
test_deployment() {
    log_info "🧪 Test final..."
    
    sleep 3
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$SERVER_IP/ || echo "000")
    
    if [ "$HTTP_CODE" = "200" ]; then
        log_info "🎉 DÉPLOIEMENT RÉUSSI !"
        log_info "🌐 Atlas accessible sur: http://$SERVER_IP"
    else
        log_warn "⚠️ Problème détecté (code HTTP: $HTTP_CODE)"
        log_info "🔧 Connectez-vous au serveur pour déboguer: ssh root@$SERVER_IP"
    fi
}

# Fonction principale
main() {
    echo "Atlas sera déployé sur: $SERVER_IP"
    echo "Répertoire: $ATLAS_DIR"
    echo ""
    echo "Appuyez sur Entrée pour continuer ou Ctrl+C pour annuler..."
    read
    
    check_files
    transfer_files
    deploy_on_server
    test_deployment
}

# Exécution
main