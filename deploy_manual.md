# 🚀 Déploiement Manuel Coach Patrimoine

## Étapes à suivre depuis votre terminal

### 1. 🔑 Connexion au serveur
```bash
ssh root@165.227.167.78
```
Mot de passe : `(!=ZL@-nZu7eB?7a`

### 2. 📦 Mise à jour et installation des outils
```bash
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv nginx git unzip -y
```

### 3. 👤 Créer utilisateur dédié
```bash
adduser appuser --disabled-password --gecos ""
usermod -aG sudo appuser
mkdir -p /home/appuser/coach-patrimoine
chown -R appuser:appuser /home/appuser/coach-patrimoine
```

### 4. 📤 Transférer l'application (depuis votre Mac)
**Ouvrez un NOUVEAU terminal sur votre Mac** et executez :
```bash
cd "/Users/huguesmarie/Documents/Jepargne digital"
tar -czf app.tar.gz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' .
scp app.tar.gz root@165.227.167.78:/home/appuser/coach-patrimoine/
```

### 5. 🗂️ Extraire et configurer (retour sur le serveur)
**Retour dans le terminal du serveur :**
```bash
cd /home/appuser/coach-patrimoine
tar -xzf app.tar.gz
rm app.tar.gz
chown -R appuser:appuser /home/appuser/coach-patrimoine
```

### 6. 🔐 Créer le fichier de configuration
```bash
cat > .env << 'EOF'
OPENAI_API_KEY=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
FLASK_ENV=production
SECRET_KEY=coach-patrimoine-secret-key-production-2024
EOF
```

### 7. 📝 Créer le fichier WSGI
```bash
cat > wsgi.py << 'EOF'
import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
EOF
```

### 8. 🐍 Configurer Python
```bash
su - appuser
cd /home/appuser/coach-patrimoine
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install flask flask-sqlalchemy flask-login openai gunicorn python-dotenv
```

### 9. 🗄️ Initialiser les données de démo
```bash
python3 init_demo_data.py
```

### 10. 🌐 Configurer Nginx (retour en root)
```bash
exit  # Pour sortir de appuser et revenir en root
```

```bash
cat > /etc/nginx/sites-available/coach-patrimoine << 'EOF'
server {
    listen 80;
    server_name 165.227.167.78;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/appuser/coach-patrimoine/app/static;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
}
EOF
```

### 11. 🔗 Activer le site
```bash
ln -sf /etc/nginx/sites-available/coach-patrimoine /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
systemctl enable nginx
```

### 12. 🚀 Lancer l'application
```bash
su - appuser
cd /home/appuser/coach-patrimoine
source venv/bin/activate
gunicorn --bind 127.0.0.1:5000 --workers 2 --daemon wsgi:app
```

### 13. ✅ Vérifier que ça marche
```bash
curl http://127.0.0.1:5000
exit  # Sortir de appuser
exit  # Sortir du serveur
```

## 🎯 Votre site sera accessible à :
**http://165.227.167.78**

## 👥 Comptes de test créés :
- **Admin :** admin@azur.com / Admin123!
- **Marie :** marie@test.com / Test123! (conservateur)
- **Paul :** paul@test.com / Test123! (dynamique)  
- **Sophie :** sophie@test.com / Test123! (modéré)

## 🔧 Pour redémarrer l'application :
```bash
ssh root@165.227.167.78
su - appuser
cd /home/appuser/coach-patrimoine
source venv/bin/activate
pkill -f gunicorn
gunicorn --bind 127.0.0.1:5000 --workers 2 --daemon wsgi:app
```