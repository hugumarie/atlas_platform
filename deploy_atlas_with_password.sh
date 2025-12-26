#!/bin/bash

# 🚀 Atlas - Déploiement avec mot de passe
set -e

SERVER_IP="139.59.158.149"
SERVER_PASS="Da^tKH_M9f3rDMN"
DB_NAME="atlas_db"
DB_USER="atlas_user"
DB_PASSWORD="atlas_password_2024_secure"

echo "🚀 ATLAS - Déploiement avec mise à jour"
echo "======================================="

# Vérifier sshpass
if ! command -v sshpass >/dev/null 2>&1; then
    echo "🔧 Installation de sshpass..."
    brew install hudochenkov/sshpass/sshpass 2>/dev/null || {
        echo "⚠️ Impossible d'installer sshpass automatiquement"
        echo "Installez-le avec: brew install hudochenkov/sshpass/sshpass"
        exit 1
    }
fi

# Vérifier qu'on est dans le bon dossier
if [ ! -f "run.py" ]; then
    echo "❌ Erreur : run.py non trouvé"
    exit 1
fi

echo "📦 1. Préparation du package Atlas..."
rm -f atlas_deploy.tar.gz
tar --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='.env' \
    --exclude='*.log' \
    --exclude='atlas_deploy.tar.gz' \
    --exclude='deploy*.sh' \
    --exclude='fix*.sh' \
    --exclude='debug*.sh' \
    -czf atlas_deploy.tar.gz .

echo "   ✅ Archive créée ($(du -h atlas_deploy.tar.gz | cut -f1))"

echo ""
echo "📤 2. Upload vers le serveur..."
sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no atlas_deploy.tar.gz root@$SERVER_IP:/tmp/

echo ""
echo "🔧 3. Mise à jour Atlas sur le serveur..."
sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no root@$SERVER_IP "
    echo '🔄 Arrêt des services...'
    systemctl stop atlas
    
    echo '📁 Sauvegarde et extraction...'
    cd /var/www/atlas
    # Sauvegarder le .env actuel
    cp .env .env.backup 2>/dev/null || true
    
    # Extraction de la nouvelle version
    tar -xzf /tmp/atlas_deploy.tar.gz
    
    echo '⚙️ Restauration configuration...'
    # Restaurer le .env
    if [ -f .env.backup ]; then
        mv .env.backup .env
    else
        # Créer un nouveau .env
        cat > .env << EOF
FLASK_ENV=production
FLASK_APP=run.py
SECRET_KEY=$(openssl rand -hex 32)
SQLALCHEMY_DATABASE_URI=postgresql://$DB_USER:$DB_PASSWORD@localhost/$DB_NAME
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost/$DB_NAME
DEBUG=False
EOF
    fi
    
    echo '🐍 Mise à jour dépendances Python...'
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn psycopg2-binary python-dotenv
    
    echo '🔧 Mise à jour configuration service...'
    cat > /etc/systemd/system/atlas.service << 'EOF'
[Unit]
Description=Atlas Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/atlas
Environment=\"PATH=/var/www/atlas/venv/bin\"
ExecStart=/var/www/atlas/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 run:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF
    
    echo '🗄️ Test de la base de données...'
    python3 -c \"
from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    try:
        # Vérifier la connexion DB
        db.create_all()
        print('✅ Base de données OK')
        
        # Vérifier admin
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
            print('✅ Admin créé')
        else:
            print('✅ Admin existe')
            
    except Exception as e:
        print(f'❌ Erreur DB: {e}')
        import traceback
        traceback.print_exc()
\"
    
    echo '🚀 Redémarrage services...'
    chown -R www-data:www-data /var/www/atlas
    systemctl daemon-reload
    systemctl start atlas
    systemctl restart nginx
    
    echo '✅ Mise à jour terminée'
"

echo ""
echo "🧪 4. Test final..."
sleep 5
sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no root@$SERVER_IP "
    echo '📊 Statut services:'
    systemctl is-active atlas && echo 'Atlas: ✅ ACTIF' || echo 'Atlas: ❌ INACTIF'
    systemctl is-active nginx && echo 'Nginx: ✅ ACTIF' || echo 'Nginx: ❌ INACTIF'
    
    echo ''
    echo '🌐 Test connectivité:'
    HTTP_CODE=\$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5000)
    echo \"Atlas: \$HTTP_CODE\"
"

echo ""
echo "🧹 5. Nettoyage..."
rm -f atlas_deploy.tar.gz
sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no root@$SERVER_IP "rm -f /tmp/atlas_deploy.tar.gz"

echo ""
echo "🎉 MISE À JOUR ATLAS TERMINÉE !"
echo "==============================="
echo ""
echo "🌐 Atlas accessible sur : http://$SERVER_IP"
echo "🔐 Connexion admin : admin@gmail.com / admin"
echo ""
echo "📝 Vérifications :"
echo "  - Logs Atlas : sshpass -p '$SERVER_PASS' ssh root@$SERVER_IP 'journalctl -u atlas -f'"
echo "  - Test direct : curl http://$SERVER_IP"