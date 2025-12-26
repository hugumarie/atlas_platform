#!/bin/bash

# Script de déploiement Atlas PROPRE (sans secrets dans le code)
# Usage: ./deploy_clean.sh [--with-db]

set -e

# Charger les variables d'environnement
if [ -f ".env" ]; then
    source .env
    echo "✅ Variables d'environnement chargées"
else
    echo "❌ Fichier .env manquant !"
    echo "💡 Copiez .env.example vers .env et configurez vos secrets"
    exit 1
fi

# Configuration depuis .env
SERVER_IP="${SERVER_IP:-167.172.108.93}"
APP_NAME="${APP_NAME:-atlas}"
DOKKU_USER="${DOKKU_USER:-dokku}"
POSTGRES_DB="${POSTGRES_DB:-atlas_db}"
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Paramètres
SYNC_DATABASE=false

# Parser les arguments
for arg in "$@"; do
    case $arg in
        --with-db)
            SYNC_DATABASE=true
            shift
            ;;
        *)
            echo "❌ Argument invalide: $arg"
            echo "Usage: $0 [--with-db]"
            exit 1
            ;;
    esac
done

echo "🚀 DÉPLOIEMENT ATLAS PROPRE"
echo "============================"
echo "🎯 Serveur: $SERVER_IP"
echo "📱 App: $APP_NAME"
echo "💾 Sync DB: $SYNC_DATABASE"
echo ""

# Vérifications
echo "🔍 Vérifications..."

# Git status
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️ Fichiers non committés:"
    git status --short
    echo ""
    read -p "🤔 Continuer ? (oui/non): " continue_deploy
    if [[ "$continue_deploy" != "oui" ]]; then
        echo "❌ Déploiement annulé"
        exit 1
    fi
fi

# Connexion serveur
if ! ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 "$DOKKU_USER@$SERVER_IP" "apps:list" > /dev/null 2>&1; then
    echo "❌ Connexion serveur échouée"
    exit 1
fi
echo "✅ Serveur accessible"

# DB locale si nécessaire
if [ "$SYNC_DATABASE" = true ]; then
    if ! psql -d "$POSTGRES_DB" -c "SELECT 1;" > /dev/null 2>&1; then
        echo "❌ Base de données locale inaccessible"
        exit 1
    fi
    echo "✅ Base locale accessible"
fi

echo ""

# Sauvegarde DB si demandée
if [ "$SYNC_DATABASE" = true ]; then
    echo "🛡️ Sauvegarde base de données..."
    mkdir -p "$BACKUP_DIR"
    
    # Backup production
    ssh -o StrictHostKeyChecking=no "$DOKKU_USER@$SERVER_IP" "postgres:export $APP_NAME-postgres" > "$BACKUP_DIR/prod_backup_${DATE}.sql"
    echo "✅ Backup production: $BACKUP_DIR/prod_backup_${DATE}.sql"
    
    # Backup local
    pg_dump -d "$POSTGRES_DB" > "$BACKUP_DIR/local_backup_${DATE}.sql"
    LOCAL_SIZE=$(wc -l < "$BACKUP_DIR/local_backup_${DATE}.sql")
    echo "✅ Backup local: $BACKUP_DIR/local_backup_${DATE}.sql ($LOCAL_SIZE lignes)"
    
    if [ "$LOCAL_SIZE" -lt 10 ]; then
        echo "❌ Backup local semble vide"
        exit 1
    fi
    
    echo "⚠️ ATTENTION: La DB production sera REMPLACÉE !"
    read -p "🤔 Confirmer ? (CONFIRMER en majuscules): " confirm_db
    if [[ "$confirm_db" != "CONFIRMER" ]]; then
        echo "✅ Sync DB annulée"
        SYNC_DATABASE=false
    fi
    echo ""
fi

# Déploiement code
echo "📦 Déploiement du code..."
if git push "$DOKKU_USER@$SERVER_IP:$APP_NAME" main; then
    echo "✅ Code déployé"
else
    echo "❌ Erreur déploiement code"
    exit 1
fi
echo ""

# Sync DB si confirmée
if [ "$SYNC_DATABASE" = true ]; then
    echo "🗄️ Synchronisation base de données..."
    
    # Upload backup
    cat "$BACKUP_DIR/local_backup_${DATE}.sql" | ssh -o StrictHostKeyChecking=no "$DOKKU_USER@$SERVER_IP" "cat > /tmp/atlas_backup.sql"
    echo "📤 Backup envoyé"
    
    # Remplacer DB
    ssh -o StrictHostKeyChecking=no "$DOKKU_USER@$SERVER_IP" << EOF
set -e
echo "⏸️ Arrêt app..."
apps:stop $APP_NAME
echo "🗃️ Recréation DB..."
postgres:destroy $APP_NAME-postgres --force
postgres:create $APP_NAME-postgres
postgres:link $APP_NAME-postgres $APP_NAME
echo "📥 Import données..."
postgres:import $APP_NAME-postgres < /tmp/atlas_backup.sql
rm -f /tmp/atlas_backup.sql
echo "▶️ Redémarrage app..."
apps:start $APP_NAME
EOF
    
    echo "✅ Base synchronisée"
fi

echo ""
echo "🎉 DÉPLOIEMENT TERMINÉ !"
echo "========================"
echo "📍 URL: http://$SERVER_IP"
echo "📅 $(date)"

if [ "$SYNC_DATABASE" = true ]; then
    echo "💾 Backups:"
    echo "   - Production: $BACKUP_DIR/prod_backup_${DATE}.sql"
    echo "   - Local: $BACKUP_DIR/local_backup_${DATE}.sql"
fi

echo ""
echo "🔍 Vérifiez maintenant:"
echo "  1. http://$SERVER_IP"
echo "  2. Fonctionnalités principales"
echo "  3. Connexion utilisateur"
echo ""