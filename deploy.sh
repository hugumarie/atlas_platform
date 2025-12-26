#!/bin/bash

# Script de déploiement NORMAL Atlas (code seulement)
# Usage: ./deploy.sh [--sync-db] [--force-db]

set -e

SERVER_IP="167.172.108.93"
APP_NAME="atlas"
LOCAL_DB_NAME="atlas_db"
LOCAL_DB_USER="postgres"
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Paramètres (SÉCURISÉS par défaut)
SYNC_DATABASE=false  # ⚠️ PAR DÉFAUT: PRÉSERVER LA PROD !
FORCE_DB=false

# Parser les arguments
for arg in "$@"; do
    case $arg in
        --sync-db)
            SYNC_DATABASE=true
            shift
            ;;
        --force-db)
            FORCE_DB=true
            SYNC_DATABASE=true
            shift
            ;;
        *)
            echo "❌ Argument invalide: $arg"
            echo "Usage: $0 [--sync-db] [--force-db]"
            echo ""
            echo "Options:"
            echo "  (aucune)    Déploie le code seulement (RECOMMANDÉ)"
            echo "  --sync-db   ⚠️ Remplace aussi la DB prod par la DB locale"
            echo "  --force-db  ⚠️ Remplace la DB sans confirmation"
            exit 1
            ;;
    esac
done

echo "🚀 DÉPLOIEMENT ATLAS"
echo "===================="
echo "📅 Date: $(date)"
echo "🎯 Serveur: $SERVER_IP"

if [ "$SYNC_DATABASE" = true ]; then
    echo "💾 Mode: CODE + DB (⚠️ DANGEREUX)"
else
    echo "💾 Mode: CODE SEULEMENT (✅ SÉCURISÉ)"
fi

echo ""

# Vérifications
echo "🔍 Vérifications..."

# Git propre
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️ Des fichiers ne sont pas commitées"
    git status --short
    echo ""
    read -p "🤔 Continuer quand même? (oui/non): " continue_deploy
    if [[ "$continue_deploy" != "oui" ]]; then
        echo "❌ Déploiement annulé"
        exit 1
    fi
fi

# Connexion serveur
if ! ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 "dokku@$SERVER_IP" "apps:list" > /dev/null 2>&1; then
    echo "❌ Impossible de se connecter au serveur"
    exit 1
fi
echo "✅ Connexion serveur OK"

# Vérifier DB locale si sync demandée
if [ "$SYNC_DATABASE" = true ]; then
    if ! psql -U "$LOCAL_DB_USER" -h localhost -d "$LOCAL_DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
        echo "❌ Impossible de se connecter à la DB locale"
        exit 1
    fi
    echo "✅ Base de données locale OK"
fi

echo ""

# Sauvegarde de sécurité DB production si sync demandée
if [ "$SYNC_DATABASE" = true ]; then
    echo "🛡️ Sauvegarde sécurité production..."
    mkdir -p "$BACKUP_DIR"
    
    ssh -o StrictHostKeyChecking=no "dokku@$SERVER_IP" "postgres:export $APP_NAME-postgres" > "$BACKUP_DIR/production_backup_${DATE}.sql"
    echo "✅ Backup production: $BACKUP_DIR/production_backup_${DATE}.sql"
    
    pg_dump -U "$LOCAL_DB_USER" -h localhost -d "$LOCAL_DB_NAME" > "$BACKUP_DIR/local_backup_${DATE}.sql"
    echo "✅ Backup local: $BACKUP_DIR/local_backup_${DATE}.sql"
    
    # Vérifier taille
    LOCAL_SIZE=$(wc -l < "$BACKUP_DIR/local_backup_${DATE}.sql")
    echo "📊 Backup local: $LOCAL_SIZE lignes"
    
    if [ "$LOCAL_SIZE" -lt 10 ] && [ "$FORCE_DB" = false ]; then
        echo "❌ Le backup local semble vide !"
        echo "💡 Utilisez --force-db pour forcer"
        exit 1
    fi
    echo ""
fi

# Déploiement code
echo "📦 Déploiement du code..."

if git push dokku main; then
    echo "✅ Code déployé avec succès"
else
    echo "❌ Erreur lors du déploiement"
    exit 1
fi
echo ""

# Synchronisation DB si demandée
if [ "$SYNC_DATABASE" = true ]; then
    echo "🗄️ Synchronisation base de données..."
    
    if [ "$FORCE_DB" = false ]; then
        echo "🛑 ATTENTION CRITIQUE !"
        echo "======================="
        echo "Vous allez REMPLACER la base de production par votre base locale !"
        echo "📊 Données qui seront PERDUES:"
        echo "  - Tous les utilisateurs créés en production"
        echo "  - Toutes les données saisies par les vrais utilisateurs"
        echo "  - Tout l'historique et les configurations"
        echo ""
        echo "📊 Données qui seront installées:"
        echo "  - Vos utilisateurs de test locaux"
        echo "  - Vos données de développement"
        echo ""
        read -p "🤔 Êtes-vous ABSOLUMENT SÛR ? (CONFIRMER en majuscules): " confirm_db
        
        if [[ "$confirm_db" != "CONFIRMER" ]]; then
            echo "✅ Synchronisation DB annulée (sage décision)"
            echo "🎉 Déploiement code terminé avec succès"
            exit 0
        fi
    fi
    
    echo "⚠️ Début synchronisation DB..."
    
    # Envoyer backup
    scp -o StrictHostKeyChecking=no "$BACKUP_DIR/local_backup_${DATE}.sql" "dokku@$SERVER_IP:/tmp/"
    
    # Remplacer DB
    ssh -o StrictHostKeyChecking=no "dokku@$SERVER_IP" << EOF
set -e
echo "⏸️ Arrêt application..."
apps:stop $APP_NAME

echo "🗃️ Destruction base production..."
postgres:destroy $APP_NAME-postgres --force

echo "🆕 Création nouvelle base..."
postgres:create $APP_NAME-postgres
postgres:link $APP_NAME-postgres $APP_NAME

echo "📥 Import données locales..."
postgres:import $APP_NAME-postgres < /tmp/local_backup_${DATE}.sql
rm -f /tmp/local_backup_${DATE}.sql

echo "▶️ Redémarrage application..."
apps:start $APP_NAME
EOF
    
    echo "✅ Base de données synchronisée"
else
    echo "✅ Base de données production PRÉSERVÉE"
fi

echo ""

# Vérifications finales
echo "🔍 Vérifications finales..."
echo "⏳ Attente redémarrage (20s)..."
sleep 20

if curl -s -o /dev/null -w "%{http_code}" "http://$SERVER_IP" | grep -q "200\|302"; then
    echo "✅ Application accessible"
else
    echo "⚠️ Application peut-être pas encore prête"
fi

echo ""
echo "🎉 DÉPLOIEMENT TERMINÉ !"
echo "========================"
echo "📍 URL: http://$SERVER_IP"
echo "📅 Date: $(date)"

if [ "$SYNC_DATABASE" = true ]; then
    echo "💾 Base de données: REMPLACÉE par locale"
    echo "📁 Backups:"
    echo "   - Production: $BACKUP_DIR/production_backup_${DATE}.sql"
    echo "   - Local: $BACKUP_DIR/local_backup_${DATE}.sql"
    echo ""
    echo "🆘 En cas de problème, restaurer:"
    echo "   ssh dokku@$SERVER_IP postgres:import $APP_NAME-postgres < $BACKUP_DIR/production_backup_${DATE}.sql"
else
    echo "💾 Base de données: PRÉSERVÉE (données prod intactes)"
fi

echo ""
echo "🔍 Vérifiez maintenant:"
echo "  1. Accès à l'application"
echo "  2. Fonctionnalités principales"
if [ "$SYNC_DATABASE" = true ]; then
    echo "  3. Connexion avec vos comptes de test"
else
    echo "  3. Connexion avec vos comptes de production"
fi
echo ""