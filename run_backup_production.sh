#!/bin/bash

# Script wrapper pour exécuter le backup de production avec les bonnes variables d'environnement

set -e  # Arrêter le script en cas d'erreur

# Chemins
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/backup_config.env"
BACKUP_SCRIPT="${SCRIPT_DIR}/backup_database_production.py"

# Vérifier que le fichier de configuration existe
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ ERREUR: Fichier de configuration manquant: $CONFIG_FILE"
    echo "Copiez backup_config.env.example vers backup_config.env et configurez-le"
    exit 1
fi

# Vérifier que le script Python existe
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo "❌ ERREUR: Script de backup manquant: $BACKUP_SCRIPT"
    exit 1
fi

echo "🚀 Démarrage du backup automatique Atlas Production"
echo "📁 Configuration: $CONFIG_FILE"
echo "🐍 Script: $BACKUP_SCRIPT"
echo ""

# Charger les variables d'environnement
set -a  # Export automatique des variables
source "$CONFIG_FILE"
set +a

# Vérifier que Python 3 est disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ ERREUR: Python 3 non trouvé"
    exit 1
fi

# Vérifier que pg_dump est disponible
if ! command -v pg_dump &> /dev/null; then
    echo "❌ ERREUR: pg_dump non trouvé. Installez postgresql-client"
    exit 1
fi

# Vérifier que boto3 est installé
if ! python3 -c "import boto3" 2>/dev/null; then
    echo "❌ ERREUR: Module boto3 non trouvé. Installez-le avec: pip3 install boto3"
    exit 1
fi

# Exécuter le script de backup
echo "⏳ Exécution du backup..."
python3 "$BACKUP_SCRIPT"

echo "✅ Script de backup terminé"