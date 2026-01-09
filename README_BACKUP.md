# 💾 Atlas - Système de Backup Automatique

## 🎯 Vue d'Ensemble

Ce système assure la sauvegarde automatique de la base de données PostgreSQL d'Atlas vers DigitalOcean Spaces, avec une fréquence horaire et une rétention de 30 jours.

## 📁 Structure des Fichiers

```
atlas/
├── backup_database_production.py     # Script principal Python
├── run_backup_production.sh          # Wrapper bash avec env
├── backup_config.env.example         # Template de configuration
├── backup_config.env                 # Configuration réelle (à créer)
├── install_backup_system.sh          # Installation automatique
├── test_backup_system.py             # Tests et validation
└── crontab_backup_production.txt     # Configuration cron
```

## 🚀 Installation Rapide

### 1. Sur le serveur de production
```bash
# Copier tous les scripts
scp backup_*.* root@atlas-invest.fr:/opt/atlas/
scp *.sh root@atlas-invest.fr:/opt/atlas/

# Se connecter et installer
ssh root@atlas-invest.fr
cd /opt/atlas
chmod +x install_backup_system.sh
./install_backup_system.sh
```

### 2. Configuration
```bash
# Créer la configuration
cp backup_config.env.example backup_config.env
nano backup_config.env  # Remplir avec vos paramètres
chmod 600 backup_config.env
```

### 3. Test
```bash
# Valider l'installation
python3 test_backup_system.py

# Premier backup manuel
sudo -u atlas ./run_backup_production.sh
```

## ⚙️ Configuration Requise

### Variables d'Environnement (`backup_config.env`)

```bash
# PostgreSQL Production
DB_HOST=your_db_host
DB_NAME=atlas_production
DB_USER=atlas_user
DB_PASSWORD=your_secure_password

# DigitalOcean Spaces
DIGITALOCEAN_SPACES_KEY=your_access_key
DIGITALOCEAN_SPACES_SECRET=your_secret_key
DIGITALOCEAN_SPACES_ENDPOINT=https://fra1.digitaloceanspaces.com
DIGITALOCEAN_SPACES_BUCKET=atlas-storage
```

## 🕒 Planification Automatique

### Cron Job (Défaut: Toutes les Heures)
```bash
# Vérifie la configuration cron
sudo -u atlas crontab -l

# Devrait afficher:
5 * * * * /opt/atlas/run_backup_production.sh >> /var/log/atlas/backup_cron.log 2>&1
```

### Alternatives de Fréquence
- **Horaire** : `5 * * * *` (défaut, recommandé)
- **6h** : `0 */6 * * *`
- **Quotidien** : `0 2 * * *`
- **Bureau** : `0 8,12,16,20 * * *`

## 📊 Monitoring

### Logs à Surveiller
```bash
# Logs détaillés
tail -f /var/log/atlas/backup.log

# Logs des exécutions cron
tail -f /var/log/atlas/backup_cron.log

# Dernières 50 lignes
tail -n 50 /var/log/atlas/backup.log
```

### Vérification des Backups
```bash
# Test complet du système
python3 test_backup_system.py

# Backup manuel pour test
sudo -u atlas /opt/atlas/run_backup_production.sh

# État du cron
sudo systemctl status cron
```

## 🗂️ Organisation des Backups

### Structure DigitalOcean Spaces
```
atlas-storage/
└── backups/
    └── database/
        └── 2025/           # Année
            └── 01/         # Mois
                └── 09/     # Jour
                    ├── atlas_backup_20250109_050001.sql.gz
                    ├── atlas_backup_20250109_110001.sql.gz
                    └── ...
```

### Nommage des Fichiers
- **Format** : `atlas_backup_YYYYMMDD_HHMMSS.sql.gz`
- **Exemple** : `atlas_backup_20250109_140302.sql.gz`

## 🔧 Maintenance

### Nettoyage Automatique
- **Rétention** : 30 jours (configurable)
- **Fréquence** : À chaque backup
- **Action** : Suppression automatique des anciens fichiers

### Commandes Utiles
```bash
# Forcer un nettoyage
python3 -c "
from backup_database_production import cleanup_old_backups, get_production_config
import logging
logger = logging.getLogger()
config = get_production_config()
cleanup_old_backups(config, logger, retention_days=30)
"

# Vérifier l'espace utilisé
du -sh /var/log/atlas/

# Redémarrer le cron si nécessaire
sudo systemctl restart cron
```

## 🔄 Restauration d'Urgence

### Processus Standard
```bash
# 1. Identifier le backup à restaurer
# Via interface DigitalOcean ou commande
aws s3 ls s3://atlas-storage/backups/database/ --recursive --endpoint-url=https://fra1.digitaloceanspaces.com

# 2. Télécharger
wget "https://fra1.digitaloceanspaces.com/atlas-storage/backups/database/2025/01/09/atlas_backup_20250109_050001.sql.gz"

# 3. Décompresser
gunzip atlas_backup_20250109_050001.sql.gz

# 4. Restaurer (ATTENTION: écrase la base)
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < atlas_backup_20250109_050001.sql
```

### Restauration de Test (Recommandée)
```bash
# Créer une base de test
createdb -h $DB_HOST -U $DB_USER atlas_restore_test

# Restaurer dans la base de test
psql -h $DB_HOST -U $DB_USER -d atlas_restore_test < atlas_backup_20250109_050001.sql

# Vérifier les données
psql -h $DB_HOST -U $DB_USER -d atlas_restore_test -c "SELECT COUNT(*) FROM users;"

# Supprimer après test
dropdb -h $DB_HOST -U $DB_USER atlas_restore_test
```

## 🚨 Dépannage

### Problèmes Fréquents

**❌ Permission denied**
```bash
# Vérifier les permissions
ls -la /opt/atlas/backup_*
chmod +x /opt/atlas/run_backup_production.sh
chmod 600 /opt/atlas/backup_config.env
```

**❌ pg_dump: command not found**
```bash
# Installer postgresql-client
sudo apt-get update
sudo apt-get install postgresql-client
```

**❌ ModuleNotFoundError: No module named 'boto3'**
```bash
# Installer boto3
pip3 install boto3
# ou pour l'utilisateur atlas spécifiquement
sudo -u atlas pip3 install boto3
```

**❌ Connection refused (PostgreSQL)**
```bash
# Tester la connexion
pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER

# Tester l'authentification
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT version();"
```

**❌ Access denied (DigitalOcean Spaces)**
```bash
# Vérifier les clés d'accès dans backup_config.env
# Tester la connexion Spaces
python3 -c "
import boto3
client = boto3.client('s3',
    endpoint_url='$DIGITALOCEAN_SPACES_ENDPOINT',
    aws_access_key_id='$DIGITALOCEAN_SPACES_KEY',
    aws_secret_access_key='$DIGITALOCEAN_SPACES_SECRET'
)
print(client.list_buckets())
"
```

## 📈 Métriques Typiques

- **Durée backup** : 30s - 5min (selon taille DB)
- **Taille compressée** : 10-20% de la taille originale
- **Fréquence** : Horaire (24 backups/jour)
- **Rétention** : 30 jours (720 backups max)
- **Coût estimé** : $5-15/mois DigitalOcean

## 📞 Support

Pour toute question sur le système de backup :
1. Vérifiez les logs : `/var/log/atlas/backup.log`
2. Testez avec : `python3 test_backup_system.py`
3. Consultez la documentation complète dans `CLAUDE.md`
4. En cas de problème critique, restaurez depuis le backup le plus récent

---

**⚠️ Important** : Ce système sauvegarde uniquement la base de données. Les fichiers uploadés (images, PDFs) sont déjà stockés sur DigitalOcean Spaces et ne nécessitent pas de backup supplémentaire.