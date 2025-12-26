#!/bin/bash

echo "⚙️ Configuration finale d'Atlas Production"
echo "=========================================="

cd /var/www/atlas

# Configuration des variables d'environnement
echo "🔐 Configuration des variables d'environnement..."
cat > .env.production << 'EOF'
# Atlas Production Environment
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=AtlasSecureKey2024_ChangeThis_ProductionSecret

# Database Configuration  
SQLALCHEMY_DATABASE_URI=postgresql://atlas:atlas_secure_pass_2024@localhost/atlas_production_db

# Email Configuration (optionnel pour l'instant)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=
MAIL_PASSWORD=

# Security
WTF_CSRF_ENABLED=True

# Logging
LOG_LEVEL=INFO
EOF

# Import de la base de données
echo "💾 Import de la base de données..."
source venv/bin/activate
export $(grep -v '^#' .env.production | xargs)

# Import du dump SQL
sudo -u postgres psql -d atlas_production_db -f atlas_database_import.sql

echo "✅ Base de données importée"

# Test de l'application
echo "🧪 Test de l'application..."
python3 -c "
from app import create_app
import os
os.environ['FLASK_ENV'] = 'production'
app = create_app()
with app.app_context():
    from app.models.user import User
    user_count = User.query.count()
    print(f'✅ Application OK - {user_count} utilisateurs importés')
"

# Configuration de Gunicorn
echo "🌐 Configuration de Gunicorn..."
cat > gunicorn_config.py << 'EOF'
bind = "127.0.0.1:5000"
workers = 2
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
worker_class = "sync"
EOF

# Configuration du service systemd
echo "⚙️ Configuration du service systemd..."
cat > /etc/systemd/system/atlas.service << 'EOF'
[Unit]
Description=Atlas Wealth Management Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/atlas
Environment=PATH=/var/www/atlas/venv/bin
EnvironmentFile=/var/www/atlas/.env.production
ExecStart=/var/www/atlas/venv/bin/gunicorn -c gunicorn_config.py run:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Permissions
echo "🔐 Configuration des permissions..."
chown -R www-data:www-data /var/www/atlas
chmod -R 755 /var/www/atlas

# Configuration Nginx
echo "🌐 Configuration de Nginx..."
cat > /etc/nginx/sites-available/atlas << 'EOF'
server {
    listen 80;
    server_name 139.59.158.149;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    location /static/ {
        alias /var/www/atlas/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    client_max_body_size 100M;
}
EOF

# Activation du site Nginx
ln -sf /etc/nginx/sites-available/atlas /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test et reload Nginx
nginx -t && systemctl reload nginx

# Démarrage des services
echo "🚀 Démarrage des services..."
systemctl daemon-reload
systemctl enable atlas
systemctl start atlas
systemctl enable nginx
systemctl start nginx

echo ""
echo "🎉 ATLAS DÉPLOYÉ AVEC SUCCÈS !"
echo "============================="
echo "🌐 URL: http://139.59.158.149"
echo "🔑 Comptes disponibles:"
echo "   - Admin: admin@gmail.com"
echo "   - Client: test.client@gmail.com"
echo ""
echo "📊 Status des services:"
systemctl status atlas --no-pager -l
echo ""
systemctl status nginx --no-pager -l
echo ""
echo "🔧 Pour voir les logs:"
echo "   journalctl -fu atlas"
echo "   tail -f /var/log/nginx/error.log"