#!/bin/bash

# Script d'installation du système de backup automatique Atlas Production
# À exécuter sur le serveur de production

set -e

echo "🚀 Installation du système de backup automatique Atlas"
echo "=================================================="

# Variables
ATLAS_DIR="/opt/atlas"  # Modifiez selon votre installation
LOG_DIR="/var/log/atlas"
SERVICE_USER="atlas"    # Modifiez selon votre utilisateur de service

# Vérifier les permissions
if [ "$EUID" -ne 0 ]; then
    echo "❌ Ce script doit être exécuté en tant que root"
    exit 1
fi

# Créer le répertoire de logs
echo "📁 Création du répertoire de logs..."
mkdir -p "$LOG_DIR"
chown "$SERVICE_USER:$SERVICE_USER" "$LOG_DIR"
chmod 755 "$LOG_DIR"

# Installer les dépendances système
echo "📦 Installation des dépendances..."
apt-get update
apt-get install -y postgresql-client python3-pip

# Installer boto3 pour l'utilisateur de service
echo "🐍 Installation de boto3..."
sudo -u "$SERVICE_USER" pip3 install boto3

# Vérifier que les fichiers de backup existent
BACKUP_SCRIPT="$ATLAS_DIR/backup_database_production.py"
RUN_SCRIPT="$ATLAS_DIR/run_backup_production.sh"
CONFIG_EXAMPLE="$ATLAS_DIR/backup_config.env.example"

if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo "❌ Script de backup non trouvé: $BACKUP_SCRIPT"
    echo "Assurez-vous que les fichiers ont été déployés correctement"
    exit 1
fi

# Rendre les scripts exécutables
chmod +x "$BACKUP_SCRIPT"
chmod +x "$RUN_SCRIPT"

# Créer le fichier de configuration s'il n'existe pas
CONFIG_FILE="$ATLAS_DIR/backup_config.env"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "📝 Création du fichier de configuration..."
    cp "$CONFIG_EXAMPLE" "$CONFIG_FILE"
    chown "$SERVICE_USER:$SERVICE_USER" "$CONFIG_FILE"
    chmod 600 "$CONFIG_FILE"  # Permissions restrictives pour les mots de passe
    
    echo ""
    echo "⚠️  IMPORTANT: Configurez le fichier $CONFIG_FILE avec vos paramètres de production"
    echo ""
fi

# Configuration du cron
echo "⏰ Configuration du cron job..."
CRON_LINE="5 * * * * $RUN_SCRIPT >> $LOG_DIR/backup_cron.log 2>&1"

# Ajouter le cron job pour l'utilisateur de service
sudo -u "$SERVICE_USER" crontab -l 2>/dev/null | grep -v "$RUN_SCRIPT" | sudo -u "$SERVICE_USER" crontab -
echo "$CRON_LINE" | sudo -u "$SERVICE_USER" crontab -

echo "✅ Installation terminée!"
echo ""
echo "📋 Étapes suivantes:"
echo "1. Configurez $CONFIG_FILE avec vos paramètres de production"
echo "2. Testez le backup manuellement : sudo -u $SERVICE_USER $RUN_SCRIPT"
echo "3. Vérifiez les logs : tail -f $LOG_DIR/backup.log"
echo "4. Vérifiez le cron : sudo -u $SERVICE_USER crontab -l"
echo ""
echo "📊 Le backup s'exécutera automatiquement toutes les heures à la minute 5"
echo "📁 Les backups seront stockés dans DigitalOcean Spaces sous backups/database/"
echo "🗂️  Les logs sont disponibles dans $LOG_DIR/"