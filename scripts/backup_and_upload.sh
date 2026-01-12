#!/bin/bash
####################################################################
# Script de backup automatique PostgreSQL vers DigitalOcean Spaces
#
# Ce script:
# 1. Exporte la base de données avec dokku postgres:export
# 2. Compresse le fichier avec gzip
# 3. Upload vers DigitalOcean Spaces
# 4. Nettoie les backups > 30 jours
#
# Conçu pour être exécuté via cron Dokku
####################################################################

set -e  # Arrêter en cas d'erreur

echo "======================================================================"
echo "🚀 BACKUP AUTOMATIQUE BASE DE DONNÉES ATLAS"
echo "📅 Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "======================================================================"
echo ""

# Variables
DB_NAME="atlas-db"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_FILENAME="atlas_backup_${TIMESTAMP}.sql"
BACKUP_PATH="/tmp/${BACKUP_FILENAME}"
COMPRESSED_PATH="${BACKUP_PATH}.gz"

# DigitalOcean Spaces
SPACES_KEY="${DIGITALOCEAN_SPACES_KEY}"
SPACES_SECRET="${DIGITALOCEAN_SPACES_SECRET}"
SPACES_ENDPOINT="${DIGITALOCEAN_SPACES_ENDPOINT:-https://fra1.digitaloceanspaces.com}"
SPACES_BUCKET="${DIGITALOCEAN_SPACES_BUCKET:-atlas-storage}"

# Chemin dans Spaces
YEAR=$(date '+%Y')
MONTH=$(date '+%m')
DAY=$(date '+%d')
SPACES_PATH="backups/database/${YEAR}/${MONTH}/${DAY}/${BACKUP_FILENAME}.gz"

####################################################################
# Étape 1: Export de la base de données
####################################################################

echo "📦 Étape 1: Export de la base de données..."

if dokku postgres:export "${DB_NAME}" > "${BACKUP_PATH}"; then
    BACKUP_SIZE=$(du -h "${BACKUP_PATH}" | cut -f1)
    echo "✅ Backup SQL créé: ${BACKUP_SIZE}"
else
    echo "❌ Erreur lors de l'export de la base"
    exit 1
fi

####################################################################
# Étape 2: Compression
####################################################################

echo ""
echo "🗜️  Étape 2: Compression du backup..."

if gzip -9 "${BACKUP_PATH}"; then
    COMPRESSED_SIZE=$(du -h "${COMPRESSED_PATH}" | cut -f1)
    echo "✅ Backup compressé: ${COMPRESSED_SIZE}"
else
    echo "❌ Erreur lors de la compression"
    rm -f "${BACKUP_PATH}"
    exit 1
fi

####################################################################
# Étape 3: Upload vers DigitalOcean Spaces
####################################################################

echo ""
echo "☁️  Étape 3: Upload vers Spaces..."
echo "   Destination: ${SPACES_PATH}"

# Utiliser AWS CLI (compatible avec Spaces)
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI non installé, installation..."
    pip install awscli --quiet
fi

# Configurer AWS CLI pour Spaces
export AWS_ACCESS_KEY_ID="${SPACES_KEY}"
export AWS_SECRET_ACCESS_KEY="${SPACES_SECRET}"

if aws s3 cp "${COMPRESSED_PATH}" "s3://${SPACES_BUCKET}/${SPACES_PATH}" \
    --endpoint-url="${SPACES_ENDPOINT}" \
    --acl private \
    --metadata "backup-date=$(date --iso-8601=seconds),database=atlas_production,type=postgresql_dump"; then
    echo "✅ Backup uploadé avec succès"
    rm -f "${COMPRESSED_PATH}"
else
    echo "❌ Erreur lors de l'upload"
    rm -f "${COMPRESSED_PATH}"
    exit 1
fi

####################################################################
# Étape 4: Nettoyage des vieux backups
####################################################################

echo ""
echo "🧹 Étape 4: Nettoyage des backups > 30 jours..."

CUTOFF_DATE=$(date -d '30 days ago' '+%Y-%m-%d' 2>/dev/null || date -v-30d '+%Y-%m-%d')

# Lister et supprimer les vieux backups
DELETED_COUNT=0
while read -r file; do
    if [ -n "$file" ]; then
        if aws s3 rm "s3://${SPACES_BUCKET}/${file}" --endpoint-url="${SPACES_ENDPOINT}" 2>/dev/null; then
            echo "  🗑️  Supprimé: ${file}"
            ((DELETED_COUNT++))
        fi
    fi
done < <(aws s3 ls "s3://${SPACES_BUCKET}/backups/database/" --endpoint-url="${SPACES_ENDPOINT}" --recursive | \
         awk '{if ($1 < "'${CUTOFF_DATE}'") print $4}')

if [ "$DELETED_COUNT" -gt 0 ]; then
    echo "✅ ${DELETED_COUNT} ancien(s) backup(s) supprimé(s)"
else
    echo "✅ Aucun backup à supprimer"
fi

####################################################################
# Fin
####################################################################

echo ""
echo "======================================================================"
echo "✅ BACKUP TERMINÉ AVEC SUCCÈS"
echo "📂 Fichier: ${SPACES_PATH}"
echo "📊 Taille compressée: ${COMPRESSED_SIZE}"
echo "======================================================================"

exit 0
