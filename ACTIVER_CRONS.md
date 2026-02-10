# 🚀 Activation des Cron Jobs Atlas - Guide Rapide

## Méthode 1: Script Automatique (Recommandée - 2 minutes)

```bash
# 1. Connexion SSH en tant que root
ssh root@atlas-invest.fr

# 2. Télécharger et exécuter le script
curl -o /tmp/setup_cron.sh https://raw.githubusercontent.com/hugumarie/atlas_platform/main/setup_cron_production.sh
chmod +x /tmp/setup_cron.sh
/tmp/setup_cron.sh
```

Le script va automatiquement:
- ✅ Créer le script de backup
- ✅ Configurer le crontab
- ✅ Créer les fichiers de log
- ✅ Proposer un test

---

## Méthode 2: Manuel (Si script automatique échoue)

### Étape 1: Créer le script de backup

```bash
ssh root@atlas-invest.fr

cat > /home/dokku/backup_atlas_db.sh << 'SCRIPT'
#!/bin/bash
set -e
eval "$(dokku config:export atlas)"

TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_FILE="/tmp/atlas_backup_${TIMESTAMP}.sql"

echo "🚀 BACKUP $(date '+%Y-%m-%d %H:%M:%S')"
dokku postgres:export atlas-db > "${BACKUP_FILE}"
gzip -9 "${BACKUP_FILE}"

YEAR=$(date '+%Y')
MONTH=$(date '+%m')
DAY=$(date '+%d')
SPACES_PATH="backups/database/${YEAR}/${MONTH}/${DAY}/$(basename ${BACKUP_FILE}.gz)"

export AWS_ACCESS_KEY_ID="${DIGITALOCEAN_SPACES_KEY}"
export AWS_SECRET_ACCESS_KEY="${DIGITALOCEAN_SPACES_SECRET}"

aws s3 cp "${BACKUP_FILE}.gz" "s3://${DIGITALOCEAN_SPACES_BUCKET}/${SPACES_PATH}" \
    --endpoint-url="${DIGITALOCEAN_SPACES_ENDPOINT}" --acl private

rm -f "${BACKUP_FILE}.gz"
echo "✅ Backup terminé: ${SPACES_PATH}"
SCRIPT

chmod +x /home/dokku/backup_atlas_db.sh
chown dokku:dokku /home/dokku/backup_atlas_db.sh
```

### Étape 2: Configurer le crontab

```bash
# Éditer le crontab de l'utilisateur dokku
crontab -u dokku -e

# Ajouter ces lignes à la fin:
5 * * * * dokku enter atlas web python scripts/update_crypto_prices.py >> /var/log/atlas_crypto.log 2>&1
30 * * * * /home/dokku/backup_atlas_db.sh >> /var/log/atlas_backup.log 2>&1
```

### Étape 3: Créer les logs

```bash
touch /var/log/atlas_crypto.log /var/log/atlas_backup.log
chown dokku:dokku /var/log/atlas_*.log
```

---

## Vérification

```bash
# Voir le crontab
crontab -u dokku -l

# Test manuel backup
/home/dokku/backup_atlas_db.sh

# Test prix crypto
dokku enter atlas web python scripts/update_crypto_prices.py

# Surveiller les logs
tail -f /var/log/atlas_backup.log
```

---

## Résultat Attendu

Une fois configuré:
- **:05** - Prix crypto mis à jour (104 cryptos)
- **:30** - Backup DB vers Spaces (compressé)

Logs disponibles:
- `/var/log/atlas_crypto.log`
- `/var/log/atlas_backup.log`

Backups organisés:
```
backups/database/2026/01/12/
├── atlas_backup_20260112_1730.sql.gz
├── atlas_backup_20260112_1830.sql.gz
└── atlas_backup_20260112_1930.sql.gz
```
