#!/bin/bash

# Script pour configurer DigitalOcean Spaces sur le serveur Dokku Atlas Production
# À exécuter sur le serveur atlas-invest.fr

set -e

echo "🔧 Configuration DigitalOcean Spaces pour Atlas Production"
echo "=========================================================="

# Variables
APP_NAME="atlas"
DOKKU_USER="dokku"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages colorés
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérifier que nous sommes sur le bon serveur
if [ "$(hostname)" != "atlas" ]; then
    warning "Ce script doit être exécuté sur le serveur atlas-invest.fr"
    echo "Hostname actuel: $(hostname)"
    read -p "Voulez-vous continuer quand même ? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Vérifier que Dokku est installé
if ! command -v dokku &> /dev/null; then
    error "Dokku n'est pas installé sur ce serveur"
    exit 1
fi

# Vérifier que l'application Atlas existe
if ! dokku apps:exists "$APP_NAME" &> /dev/null; then
    error "L'application Dokku '$APP_NAME' n'existe pas"
    info "Applications disponibles:"
    dokku apps:list
    exit 1
fi

success "Serveur et application Dokku validés"

echo ""
info "Configuration des clés DigitalOcean Spaces..."
echo ""

# Demander les informations DigitalOcean Spaces
read -p "🔑 Access Key ID DigitalOcean Spaces: " SPACES_KEY
read -s -p "🔐 Secret Access Key DigitalOcean Spaces: " SPACES_SECRET
echo ""
read -p "🌍 Endpoint DigitalOcean (ex: https://fra1.digitaloceanspaces.com): " SPACES_ENDPOINT
read -p "🪣 Nom du bucket (ex: atlas-storage): " SPACES_BUCKET

# Valider les entrées
if [[ -z "$SPACES_KEY" || -z "$SPACES_SECRET" || -z "$SPACES_ENDPOINT" || -z "$SPACES_BUCKET" ]]; then
    error "Toutes les informations sont requises"
    exit 1
fi

echo ""
info "Configuration des variables d'environnement Dokku..."

# Configurer les variables d'environnement pour l'application
dokku config:set "$APP_NAME" \
    DIGITALOCEAN_SPACES_KEY="$SPACES_KEY" \
    DIGITALOCEAN_SPACES_SECRET="$SPACES_SECRET" \
    DIGITALOCEAN_SPACES_ENDPOINT="$SPACES_ENDPOINT" \
    DIGITALOCEAN_SPACES_BUCKET="$SPACES_BUCKET"

success "Variables DigitalOcean Spaces configurées"

# Optionnel: Configurer aussi les variables pour les backups
echo ""
read -p "🔄 Voulez-vous aussi configurer les variables pour les backups de base de données ? (y/N): " setup_backup

if [[ $setup_backup =~ ^[Yy]$ ]]; then
    info "Configuration des variables de backup..."
    
    # Récupérer les informations de la base de données
    DB_URL=$(dokku config:get "$APP_NAME" DATABASE_URL || echo "")
    
    if [[ -n "$DB_URL" ]]; then
        info "Base de données détectée automatiquement depuis DATABASE_URL"
        
        # Parser l'URL PostgreSQL
        # Format: postgres://user:password@host:port/database
        DB_USER=$(echo "$DB_URL" | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
        DB_PASSWORD=$(echo "$DB_URL" | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
        DB_HOST=$(echo "$DB_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_PORT=$(echo "$DB_URL" | sed -n 's/.*@[^:]*:\([^/]*\)\/.*/\1/p')
        DB_NAME=$(echo "$DB_URL" | sed -n 's/.*\/\([^?]*\).*/\1/p')
        
        echo ""
        info "Paramètres détectés:"
        echo "  DB_HOST: $DB_HOST"
        echo "  DB_PORT: $DB_PORT"
        echo "  DB_NAME: $DB_NAME"
        echo "  DB_USER: $DB_USER"
        echo ""
        
        read -p "Ces paramètres sont-ils corrects ? (Y/n): " confirm_db
        if [[ ! $confirm_db =~ ^[Nn]$ ]]; then
            # Configurer les variables de backup
            dokku config:set "$APP_NAME" \
                DB_HOST="$DB_HOST" \
                DB_PORT="$DB_PORT" \
                DB_NAME="$DB_NAME" \
                DB_USER="$DB_USER" \
                DB_PASSWORD="$DB_PASSWORD"
            
            success "Variables de backup configurées"
        fi
    else
        warning "DATABASE_URL non trouvée, configuration manuelle nécessaire"
        read -p "Host de la base de données: " DB_HOST
        read -p "Port de la base de données (5432): " DB_PORT
        DB_PORT=${DB_PORT:-5432}
        read -p "Nom de la base de données: " DB_NAME
        read -p "Utilisateur de la base de données: " DB_USER
        read -s -p "Mot de passe de la base de données: " DB_PASSWORD
        echo ""
        
        dokku config:set "$APP_NAME" \
            DB_HOST="$DB_HOST" \
            DB_PORT="$DB_PORT" \
            DB_NAME="$DB_NAME" \
            DB_USER="$DB_USER" \
            DB_PASSWORD="$DB_PASSWORD"
        
        success "Variables de backup configurées manuellement"
    fi
fi

echo ""
info "Affichage de la configuration actuelle (sans les valeurs sensibles)..."
dokku config "$APP_NAME" | grep -E "(DIGITALOCEAN|DB_)" | sed 's/=.*/=***HIDDEN***/'

echo ""
success "Configuration DigitalOcean Spaces terminée !"

echo ""
info "Prochaines étapes recommandées:"
echo "1. Redéployez l'application pour prendre en compte les nouvelles variables:"
echo "   dokku ps:restart $APP_NAME"
echo ""
echo "2. Testez la connexion DigitalOcean Spaces depuis l'application"
echo ""
echo "3. Si vous avez configuré les variables de backup, déployez le système de backup:"
echo "   - Copiez les scripts de backup sur le serveur"
echo "   - Exécutez install_backup_system.sh"
echo "   - Testez avec test_backup_system.py"

# Optionnel: Redémarrer automatiquement
echo ""
read -p "🔄 Voulez-vous redémarrer l'application maintenant ? (Y/n): " restart_app
if [[ ! $restart_app =~ ^[Nn]$ ]]; then
    info "Redémarrage de l'application..."
    dokku ps:restart "$APP_NAME"
    success "Application redémarrée"
fi

echo ""
success "🎉 Configuration DigitalOcean Spaces terminée avec succès !"