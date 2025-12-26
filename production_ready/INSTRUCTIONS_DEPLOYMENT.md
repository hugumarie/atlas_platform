# Instructions de Déploiement Atlas Production

## 📋 Prérequis sur le serveur de production

1. **PostgreSQL** installé et configuré
2. **Python 3.8+** avec pip
3. **Serveur web** (nginx recommandé)
4. **Certificat SSL** configuré

## 🚀 Étapes de déploiement

### 1. Transférer les fichiers
```bash
# Transférer tout le dossier production_ready sur votre serveur
scp -r production_ready/ user@votre-serveur:/var/www/atlas/
```

### 2. Configuration sur le serveur
```bash
cd /var/www/atlas

# Configurer l'environnement
# IMPORTANT: Éditez .env.production avec vos vraies valeurs
nano .env.production

# Créer la base de données
sudo -u postgres createdb atlas_production_db

# Donner les droits à l'utilisateur de la base
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE atlas_production_db TO votre_user;"
```

### 3. Installation et import
```bash
# Installer les dépendances
pip3 install -r requirements.txt

# Importer la base de données
psql -d atlas_production_db -f atlas_database_import.sql

# Ou utiliser le script automatique
chmod +x deploy_production.sh
./deploy_production.sh
```

### 4. Configuration serveur web (nginx)
```nginx
server {
    listen 80;
    server_name votre-domaine.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name votre-domaine.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/atlas/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 5. Lancement avec Gunicorn (recommandé)
```bash
# Installation de gunicorn
pip3 install gunicorn

# Lancement
gunicorn -w 4 -b 127.0.0.1:5000 run:app

# Ou avec un service systemd (recommandé)
sudo nano /etc/systemd/system/atlas.service
```

## 🔧 Service systemd exemple
```ini
[Unit]
Description=Atlas Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/atlas
Environment=PATH=/var/www/atlas/venv/bin
ExecStart=/var/www/atlas/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## ⚠️ Points importants

1. **Sécurité**: Changez TOUTES les clés dans .env.production
2. **Base de données**: Configurez des sauvegardes automatiques
3. **Logs**: Surveillez les logs d'erreur
4. **Monitoring**: Mettez en place un monitoring (ex: Prometheus)
5. **Firewall**: Configurez le firewall pour n'ouvrir que les ports nécessaires

## 🔧 Maintenance

- **Sauvegardes**: `pg_dump atlas_production_db > backup_$(date +%Y%m%d).sql`
- **Logs**: Vérifier régulièrement `/var/log/nginx/` et les logs de l'application
- **Mises à jour**: Testez toujours en staging avant la production

