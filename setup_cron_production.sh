#!/bin/bash
#######################################################################
# Configuration des cron jobs pour Atlas sur Dokku (PRODUCTION)
#
# ⚠️ CE SCRIPT DOIT ÊTRE EXÉCUTÉ EN TANT QUE ROOT SUR LE SERVEUR
#
# Usage:
#   1. Copier ce script sur le serveur:
#      scp setup_cron_production.sh root@atlas-invest.fr:/tmp/
#
#   2. Se connecter en SSH et exécuter:
#      ssh root@atlas-invest.fr
#      chmod +x /tmp/setup_cron_production.sh
#      /tmp/setup_cron_production.sh
#
# Ce script configure:
# 1. Mise à jour prix crypto (toutes les heures à :05)
# 2. Backup base de données vers Spaces (toutes les heures à :30)
#######################################################################

set -e

echo "======================================================================"
echo "🔧 CONFIGURATION CRON JOBS ATLAS PRODUCTION"
echo "======================================================================"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Ce script doit être exécuté en tant que root"
    echo "   Utilisez: sudo $0"
    exit 1
fi

echo "✅ Exécution en tant que root"
echo ""

#######################################################################
# Étape 1: Créer le script de backup
#######################################################################

echo "📝 Étape 1: Création du script de backup..."

cat > /home/dokku/backup_atlas_db.sh << 'BACKUP_SCRIPT'
#!/bin/bash
set -e

# Charger les variables d'environnement Dokku
eval "$(dokku config:export atlas)"

# Variables
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_FILE="/tmp/atlas_backup_${TIMESTAMP}.sql"

echo "======================================================================"
echo "🚀 BACKUP AUTOMATIQUE BASE DE DONNÉES ATLAS"
echo "📅 Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "======================================================================"

# Export de la base
echo "📦 Export de la base de données..."
if dokku postgres:export atlas-db > "${BACKUP_FILE}"; then
    SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "✅ Backup SQL créé: ${SIZE}"
else
    echo "❌ Erreur lors de l'export"
    exit 1
fi

# Compression
echo "🗜️  Compression..."
if gzip -9 "${BACKUP_FILE}"; then
    COMPRESSED_FILE="${BACKUP_FILE}.gz"
    SIZE=$(du -h "${COMPRESSED_FILE}" | cut -f1)
    echo "✅ Backup compressé: ${SIZE}"
else
    echo "❌ Erreur compression"
    rm -f "${BACKUP_FILE}"
    exit 1
fi

# Upload vers Spaces
echo "☁️  Upload vers Spaces..."
YEAR=$(date '+%Y')
MONTH=$(date '+%m')
DAY=$(date '+%d')
SPACES_PATH="backups/database/${YEAR}/${MONTH}/${DAY}/$(basename ${COMPRESSED_FILE})"

# Vérifier awscli
if ! command -v aws &> /dev/null; then
    echo "📦 Installation AWS CLI..."
    pip3 install awscli --quiet
fi

export AWS_ACCESS_KEY_ID="${DIGITALOCEAN_SPACES_KEY}"
export AWS_SECRET_ACCESS_KEY="${DIGITALOCEAN_SPACES_SECRET}"

if aws s3 cp "${COMPRESSED_FILE}" "s3://${DIGITALOCEAN_SPACES_BUCKET}/${SPACES_PATH}" \
    --endpoint-url="${DIGITALOCEAN_SPACES_ENDPOINT}" \
    --acl private \
    --metadata "backup-date=$(date --iso-8601=seconds),database=atlas_production"; then
    echo "✅ Backup uploadé: ${SPACES_PATH}"
    rm -f "${COMPRESSED_FILE}"
else
    echo "❌ Erreur upload"
    rm -f "${COMPRESSED_FILE}"
    exit 1
fi

echo ""
echo "======================================================================"
echo "✅ BACKUP TERMINÉ AVEC SUCCÈS"
echo "======================================================================"
BACKUP_SCRIPT

chmod +x /home/dokku/backup_atlas_db.sh
chown dokku:dokku /home/dokku/backup_atlas_db.sh

echo "✅ Script créé: /home/dokku/backup_atlas_db.sh"
echo ""

#######################################################################
# Étape 2: Configurer le crontab
#######################################################################

echo "📝 Étape 2: Configuration du crontab..."

# Sauvegarder le crontab actuel (sans les lignes Atlas)
(crontab -u dokku -l 2>/dev/null | grep -v "ATLAS" | grep -v "atlas" | grep -v "update_crypto" | grep -v "backup_atlas" || true) > /tmp/crontab_dokku

# Ajouter les nouvelles tâches
cat >> /tmp/crontab_dokku << 'CRON_TASKS'

# ====================================================================
# ATLAS PRODUCTION CRON JOBS
# ====================================================================
# Mise à jour prix cryptomonnaies - Toutes les heures à :05
5 * * * * dokku enter atlas web python scripts/update_crypto_prices.py >> /var/log/atlas_crypto.log 2>&1

# Backup base de données vers DigitalOcean Spaces - Toutes les heures à :30
30 * * * * /home/dokku/backup_atlas_db.sh >> /var/log/atlas_backup.log 2>&1

CRON_TASKS

# Installer le nouveau crontab
crontab -u dokku /tmp/crontab_dokku
rm /tmp/crontab_dokku

echo "✅ Crontab configuré pour l'utilisateur dokku"
echo ""

#######################################################################
# Étape 3: Créer les fichiers de log
#######################################################################

echo "📝 Étape 3: Création des fichiers de log..."

touch /var/log/atlas_crypto.log
touch /var/log/atlas_backup.log
chown dokku:dokku /var/log/atlas_crypto.log
chown dokku:dokku /var/log/atlas_backup.log
chmod 644 /var/log/atlas_crypto.log
chmod 644 /var/log/atlas_backup.log

echo "✅ Fichiers de log créés:"
echo "   - /var/log/atlas_crypto.log"
echo "   - /var/log/atlas_backup.log"
echo ""

#######################################################################
# Étape 4: Test du script de backup
#######################################################################

echo "📝 Étape 4: Test du script de backup..."
echo ""

read -p "Voulez-vous tester le backup maintenant? (o/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Oo]$ ]]; then
    echo "🧪 Exécution du test de backup..."
    su - dokku -c "/home/dokku/backup_atlas_db.sh" 2>&1 | tee -a /var/log/atlas_backup.log
else
    echo "⏭️  Test ignoré"
fi

echo ""

#######################################################################
# Résumé
#######################################################################

echo "======================================================================"
echo "✅ CONFIGURATION TERMINÉE AVEC SUCCÈS"
echo "======================================================================"
echo ""
echo "📋 Résumé de la configuration:"
echo ""
echo "🔄 Tâches cron configurées:"
echo "   • Mise à jour prix crypto: Toutes les heures à :05"
echo "   • Backup base de données:  Toutes les heures à :30"
echo ""
echo "📂 Destination backups:"
echo "   DigitalOcean Spaces: backups/database/YYYY/MM/DD/"
echo "   Rétention: 30 jours (cleanup manuel requis)"
echo ""
echo "📝 Logs disponibles:"
echo "   • tail -f /var/log/atlas_crypto.log"
echo "   • tail -f /var/log/atlas_backup.log"
echo ""
echo "🔍 Vérifier le crontab:"
echo "   crontab -u dokku -l | grep ATLAS -A 5"
echo ""
echo "📅 Prochaines exécutions:"
NEXT_CRYPTO=$(date -d "$(date +%Y-%m-%d) $(date +%H):05:00 + 1 hour" '+%Y-%m-%d %H:%M')
NEXT_BACKUP=$(date -d "$(date +%Y-%m-%d) $(date +%H):30:00 + 1 hour" '+%Y-%m-%d %H:%M')
echo "   • Prix crypto: ${NEXT_CRYPTO}"
echo "   • Backup DB:   ${NEXT_BACKUP}"
echo ""
echo "======================================================================"
