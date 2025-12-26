#!/bin/bash

echo "🚀 Atlas - Déploiement Complet sur Serveur"
echo "==========================================="

# Variables
ATLAS_DIR="/var/www/atlas"
SERVICE_USER="www-data"

# Vérification des prérequis
check_prerequisites() {
    echo "🔍 Vérification des prérequis..."
    
    if [ ! -f "/root/atlas_production_20251223_023409.tar.gz" ]; then
        echo "❌ Package Atlas non trouvé dans /root/"
        exit 1
    fi
    
    if [ ! -f "/root/.env.production.new" ]; then
        echo "❌ Fichier .env.production.new non trouvé"
        exit 1
    fi
    
    echo "✅ Prérequis OK"
}

# Installation des dépendances
install_dependencies() {
    echo "📦 Installation des dépendances système..."
    apt update
    apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx supervisor git curl ufw
    echo "✅ Dépendances installées"
}

# Configuration PostgreSQL
setup_database() {
    echo "💾 Configuration de PostgreSQL..."
    
    # Lire les variables du fichier .env
    source /root/.env.production.new
    
    # Extraire les infos de connection
    DB_NAME=$(echo $SQLALCHEMY_DATABASE_URI | sed 's/.*\/\([^?]*\).*/\1/')
    DB_USER=$(echo $SQLALCHEMY_DATABASE_URI | sed 's/.*:\/\/\([^:]*\):.*/\1/')
    DB_PASS=$(echo $SQLALCHEMY_DATABASE_URI | sed 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/')
    
    # Configuration PostgreSQL
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;"
    sudo -u postgres psql -c "DROP USER IF EXISTS $DB_USER;"
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASS';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;"
    
    echo "✅ Base de données configurée"
}

# Configuration de l'application
setup_application() {
    echo "⚙️ Configuration de l'application Atlas..."
    
    # Créer le répertoire et extraire
    mkdir -p $ATLAS_DIR
    cd $ATLAS_DIR
    rm -rf * .env.production
    
    # Extraire le package
    tar -xzf /root/atlas_production_20251223_023409.tar.gz --strip-components=1
    
    # Copier la configuration
    cp /root/.env.production.new .env.production
    
    # Créer l'environnement virtuel
    python3 -m venv venv
    source venv/bin/activate
    
    # Installer les dépendances Python avec timeout plus long
    pip install --timeout 300 -r requirements.txt
    
    # Configurer les permissions
    chown -R $SERVICE_USER:$SERVICE_USER $ATLAS_DIR
    chmod -R 755 $ATLAS_DIR
    chmod 600 $ATLAS_DIR/.env.production
    
    echo "✅ Application configurée"
}

# Import de la base de données
import_database() {
    echo "📥 Import de la base de données..."
    
    cd $ATLAS_DIR
    source venv/bin/activate
    source .env.production
    
    # Import du dump SQL
    psql $SQLALCHEMY_DATABASE_URI < atlas_database_import.sql
    
    # Test de l'application
    python3 -c "
import os
os.chdir('$ATLAS_DIR')
from app import create_app
app = create_app()
with app.app_context():
    from app.models.user import User
    user_count = User.query.count()
    print(f'✅ {user_count} utilisateurs importés')
"
    
    echo "✅ Base de données importée"
}

# Configuration des services
setup_services() {
    echo "🔧 Configuration des services système..."
    
    # Configuration de Gunicorn
    cat > $ATLAS_DIR/gunicorn_config.py << 'EOF'
bind = "127.0.0.1:5000"
workers = 1
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
worker_class = "sync"
worker_connections = 1000
EOF

    # Service systemd pour Atlas
    cat > /etc/systemd/system/atlas.service << EOF
[Unit]
Description=Atlas Wealth Management Platform
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$ATLAS_DIR
Environment=PATH=$ATLAS_DIR/venv/bin
EnvironmentFile=$ATLAS_DIR/.env.production
ExecStart=$ATLAS_DIR/venv/bin/gunicorn -c gunicorn_config.py run:app
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Configuration Nginx
    cat > /etc/nginx/sites-available/atlas << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    client_max_body_size 100M;
    
    # Timeout configurations
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
    fastcgi_send_timeout 300s;
    fastcgi_read_timeout 300s;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/atlas/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
}
EOF

    # Activer le site
    ln -sf /etc/nginx/sites-available/atlas /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    echo "✅ Services configurés"
}

# Configuration sécurité
setup_security() {
    echo "🔐 Configuration sécurité..."
    
    # Firewall basique
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 'Nginx Full'
    ufw --force enable
    
    echo "✅ Firewall configuré"
}

# Démarrage des services
start_services() {
    echo "🚀 Démarrage des services..."
    
    # Test Nginx
    nginx -t
    if [ $? -ne 0 ]; then
        echo "❌ Erreur configuration Nginx"
        exit 1
    fi
    
    # Démarrer les services
    systemctl daemon-reload
    systemctl enable postgresql
    systemctl start postgresql
    systemctl enable nginx
    systemctl restart nginx
    systemctl enable atlas
    systemctl start atlas
    
    sleep 3
    
    echo "✅ Services démarrés"
}

# Test final
test_deployment() {
    echo "🧪 Test du déploiement..."
    
    # Test local
    curl -s -o /dev/null -w "%{http_code}" http://localhost/ > /tmp/test_result
    if [ "$(cat /tmp/test_result)" = "200" ]; then
        echo "✅ Test local réussi"
    else
        echo "⚠️ Test local échoué (code: $(cat /tmp/test_result))"
    fi
    
    # Vérifier les services
    systemctl is-active --quiet atlas && echo "✅ Service Atlas actif" || echo "❌ Service Atlas inactif"
    systemctl is-active --quiet nginx && echo "✅ Service Nginx actif" || echo "❌ Service Nginx inactif"
    systemctl is-active --quiet postgresql && echo "✅ Service PostgreSQL actif" || echo "❌ Service PostgreSQL inactif"
}

# Fonction principale
main() {
    echo "🎬 Démarrage du déploiement automatisé..."
    echo ""
    
    check_prerequisites
    install_dependencies
    setup_database
    setup_application
    import_database
    setup_services
    setup_security
    start_services
    test_deployment
    
    echo ""
    echo "🎉 DÉPLOIEMENT ATLAS TERMINÉ !"
    echo "============================="
    echo "🌐 URL: http://139.59.158.149"
    echo "🔑 Comptes:"
    echo "   - Admin: admin@gmail.com"
    echo "   - Client: test.client@gmail.com"
    echo ""
    echo "📊 Status des services:"
    systemctl status atlas --no-pager -l | head -5
    echo ""
    echo "🔧 Commandes utiles:"
    echo "   - Logs Atlas: journalctl -fu atlas"
    echo "   - Logs Nginx: tail -f /var/log/nginx/error.log"
    echo "   - Redémarrer: systemctl restart atlas"
    echo ""
    echo "🎯 Votre plateforme Atlas est maintenant en ligne !"
}

# Exécution
main