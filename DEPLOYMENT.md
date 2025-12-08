# 🚀 Guide de Déploiement - Plateforme Patrimoine

## 📋 Vue d'ensemble

Ce document décrit comment déployer la plateforme de gestion de patrimoine en production.

## 🔧 Déploiement Local (Développement)

### Méthode Rapide
```bash
# Navigation vers le projet
cd "Jepargne digital"

# Lancement automatique
python3 start_app.py
```

### Méthode Manuelle
```bash
# Installation des dépendances
pip3 install -r requirements.txt

# Lancement
python3 run.py
```

## ☁️ Déploiement Production

### Option 1 : Heroku
```bash
# Installation Heroku CLI
brew install heroku/brew/heroku

# Connexion
heroku login

# Création de l'app
heroku create patrimoine-pro

# Configuration des variables
heroku config:set SECRET_KEY="your-super-secret-key"
heroku config:set FLASK_ENV="production"

# Ajout de PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Déploiement
git add .
git commit -m "Deploy to production"
git push heroku main
```

### Option 2 : DigitalOcean Droplet
```bash
# Connexion au serveur
ssh root@your-server-ip

# Installation Python et pip
apt update
apt install python3 python3-pip nginx

# Clone du projet
git clone https://github.com/your-repo/patrimoine-pro.git
cd patrimoine-pro

# Installation des dépendances
pip3 install -r requirements.txt

# Configuration Gunicorn
pip3 install gunicorn

# Lancement
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### Option 3 : Docker
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

```bash
# Construction et lancement
docker build -t patrimoine-pro .
docker run -p 5000:5000 patrimoine-pro
```

## 🗄️ Configuration Base de Données

### SQLite (Développement)
```python
# app/__init__.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patrimoine.db'
```

### PostgreSQL (Production)
```python
# app/__init__.py
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
```

```bash
# Variables d'environnement
export DATABASE_URL="postgresql://user:password@localhost/patrimoine_db"
```

## 🔐 Variables d'Environnement

### Fichier .env
```bash
# Sécurité
SECRET_KEY=your-super-secret-key-very-long-and-complex
FLASK_ENV=production

# Base de données
DATABASE_URL=postgresql://user:password@localhost/patrimoine_db

# OpenAI (pour l'assistant IA)
OPENAI_API_KEY=your-openai-api-key

# Email (pour notifications futures)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password

# Stripe (pour paiements futures)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

## 🌐 Configuration Nginx

```nginx
# /etc/nginx/sites-available/patrimoine-pro
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /path/to/your/app/static;
    }
}
```

## 🔒 SSL/HTTPS avec Let's Encrypt

```bash
# Installation Certbot
apt install certbot python3-certbot-nginx

# Obtention du certificat
certbot --nginx -d your-domain.com

# Renouvellement automatique
crontab -e
# Ajouter : 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring et Logs

### Logs Application
```python
# app/__init__.py
import logging
from logging.handlers import RotatingFileHandler

if app.config['FLASK_ENV'] == 'production':
    file_handler = RotatingFileHandler('logs/patrimoine.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### Monitoring avec Supervisor
```ini
# /etc/supervisor/conf.d/patrimoine-pro.conf
[program:patrimoine-pro]
command=gunicorn -w 4 -b 127.0.0.1:5000 run:app
directory=/path/to/your/app
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/patrimoine-pro.log
```

## 🚀 Script de Déploiement Automatique

```bash
#!/bin/bash
# deploy.sh

echo "🚀 Déploiement de la Plateforme Patrimoine"

# Sauvegarde de la base de données
echo "📁 Sauvegarde de la base de données..."
pg_dump patrimoine_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Arrêt de l'application
echo "⏹️ Arrêt de l'application..."
supervisorctl stop patrimoine-pro

# Mise à jour du code
echo "📥 Mise à jour du code..."
git pull origin main

# Installation des nouvelles dépendances
echo "📦 Installation des dépendances..."
pip3 install -r requirements.txt

# Migration de la base de données
echo "🗄️ Migration de la base de données..."
python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Redémarrage de l'application
echo "🔄 Redémarrage de l'application..."
supervisorctl start patrimoine-pro

# Vérification du statut
echo "✅ Vérification du statut..."
curl -f http://localhost:5000 && echo "Déploiement réussi !" || echo "Erreur de déploiement !"
```

## 🔄 Sauvegarde et Restauration

### Sauvegarde automatique
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/patrimoine-pro"

# Création du dossier de sauvegarde
mkdir -p $BACKUP_DIR

# Sauvegarde de la base de données
pg_dump patrimoine_db > $BACKUP_DIR/db_$DATE.sql

# Sauvegarde des fichiers uploadés
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz app/static/uploads/

# Nettoyage des anciennes sauvegardes (> 30 jours)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Sauvegarde terminée : $DATE"
```

### Cron pour sauvegardes automatiques
```bash
# crontab -e
# Sauvegarde quotidienne à 2h du matin
0 2 * * * /path/to/backup.sh
```

## 📈 Optimisations Performance

### Gunicorn optimisé
```bash
# Configuration recommandée
gunicorn -w 4 \
         --max-requests 1000 \
         --max-requests-jitter 50 \
         --timeout 120 \
         --keep-alive 5 \
         -b 0.0.0.0:5000 \
         run:app
```

### Redis pour cache (optionnel)
```bash
# Installation Redis
apt install redis-server

# Configuration Flask
pip3 install Flask-Caching redis
```

```python
# app/__init__.py
from flask_caching import Cache

cache = Cache()
cache.init_app(app, config={'CACHE_TYPE': 'redis'})
```

## 🔍 Tests de Performance

```bash
# Test de charge avec Apache Bench
ab -n 1000 -c 10 http://your-domain.com/

# Monitoring avec htop
htop

# Vérification des logs
tail -f /var/log/patrimoine-pro.log
```

## 🪙 Configuration Cryptomonnaies - OBLIGATOIRE

### ⚠️ IMPORTANT - Scheduler Intégré Désactivé

Le scheduler Flask intégré a été **DÉSACTIVÉ** pour éviter les appels API en boucle qui causaient des lenteurs.

**Configuration actuelle :**
- ✅ Scheduler intégré : **DÉSACTIVÉ**
- ✅ Script externe : `refresh_crypto_prices.py`
- ⚠️ Cron : **À CONFIGURER EN PRODUCTION**
- ✅ API locale : `/api/crypto-prices` (lecture DB uniquement)

### Configuration CRON Obligatoire

```bash
# Se connecter au serveur
crontab -e

# Ajouter cette ligne pour mise à jour des prix crypto toutes les heures :
0 * * * * cd /path/to/your/atlas/app && python refresh_crypto_prices.py >> ../logs/crypto_refresh.log 2>&1

# Alternative : toutes les 30 minutes pour plus de précision
*/30 * * * * cd /path/to/your/atlas/app && python refresh_crypto_prices.py >> ../logs/crypto_refresh.log 2>&1

# Créer le dossier logs si nécessaire
mkdir -p /path/to/your/atlas/logs
```

### Test de la Configuration Crypto

```bash
# Test manuel du script
cd /path/to/your/atlas/app
python refresh_crypto_prices.py

# Vérifier les logs
tail -f logs/crypto_refresh.log

# Vérifier que l'API fonctionne (doit être ultra-rapide)
curl -X POST http://localhost:5000/api/crypto-prices \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["btc", "eth"]}'
```

### Performance Crypto

- ❌ **Avant** : 2-3 minutes (200+ appels API Binance)
- ✅ **Maintenant** : < 1 seconde (lecture DB locale)

### Monitoring Crypto

```bash
# Vérifier la dernière mise à jour des prix
# (dans votre interface DB ou avec un script)
SELECT symbol, price_eur, last_updated 
FROM crypto_prices 
ORDER BY last_updated DESC 
LIMIT 10;

# Alerter si pas de mise à jour depuis plus de 2h
*/15 * * * * /path/to/check_crypto_freshness.sh
```

## ⚠️ Checklist Pré-Production

- [ ] Variables d'environnement configurées
- [ ] Base de données PostgreSQL prête
- [ ] **CRON crypto configuré et testé**
- [ ] **API crypto locale fonctionnelle**
- [ ] **Scheduler Flask intégré DÉSACTIVÉ**
- [ ] SSL/HTTPS activé
- [ ] Sauvegardes automatiques configurées
- [ ] Monitoring en place
- [ ] Tests de performance effectués
- [ ] Documentation à jour
- [ ] Clés API configurées (OpenAI, Stripe)
- [ ] Emails de notification configurés

## 🚨 Points Critiques Post-Déploiement

1. **Vérifier immédiatement** que le CRON crypto fonctionne
2. **Tester la performance** de la page données investisseur (doit être < 2s)
3. **Surveiller les logs** crypto les premières 24h
4. **Alerter** si échec refresh crypto > 2h consécutives

---

**🚀 Votre plateforme est maintenant prête pour la production !**

**💡 N'oubliez pas de configurer le CRON crypto dès le premier déploiement !**