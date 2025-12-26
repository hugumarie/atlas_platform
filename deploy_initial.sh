#!/bin/bash

# Script de déploiement INITIAL Atlas avec utilisateurs de test
# ⚠️ À utiliser UNIQUEMENT pour la première mise en production !

set -e

SERVER_IP="167.172.108.93"
APP_NAME="atlas"
LOCAL_DB_NAME="atlas_db"
LOCAL_DB_USER=""
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "🚀 DÉPLOIEMENT INITIAL ATLAS"
echo "============================="
echo "⚠️ ATTENTION: Ce script va remplacer TOUTE la base de production !"
echo "📅 Date: $(date)"
echo ""

# Vérifications
echo "🔍 Vérifications pré-déploiement..."

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

# DB locale
if ! psql -d "$LOCAL_DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
    echo "❌ Impossible de se connecter à la DB locale"
    exit 1
fi

echo "✅ Vérifications OK"
echo ""

# Confirmation explicite
echo "🛑 CONFIRMATION DÉPLOIEMENT INITIAL"
echo "====================================="
echo "Ce script va :"
echo "  1. 📦 Déployer votre code Atlas"
echo "  2. 💾 REMPLACER la base de production par votre base locale"
echo "  3. 👥 Installer vos utilisateurs de test en production"
echo ""
echo "⚠️ Si une base de données existe déjà, elle sera DÉTRUITE !"
echo ""
read -p "🤔 Confirmez-vous ce déploiement initial ? (OUI en majuscules): " confirmation

if [[ "$confirmation" != "OUI" ]]; then
    echo "❌ Déploiement annulé"
    exit 1
fi

echo ""
echo "🚀 Démarrage déploiement initial..."

# Créer backups
mkdir -p "$BACKUP_DIR"

echo "💾 Sauvegarde base locale..."
pg_dump -d "$LOCAL_DB_NAME" > "$BACKUP_DIR/initial_deploy_${DATE}.sql"

# Vérifier taille backup
LOCAL_SIZE=$(wc -l < "$BACKUP_DIR/initial_deploy_${DATE}.sql")
echo "📊 Backup local: $LOCAL_SIZE lignes"

if [ "$LOCAL_SIZE" -lt 10 ]; then
    echo "❌ Le backup local semble vide ou très petit !"
    exit 1
fi

echo "✅ Backup local créé: $BACKUP_DIR/initial_deploy_${DATE}.sql"

# Déployer le code
echo ""
echo "📦 Déploiement du code..."
if ! git push dokku main; then
    echo "❌ Erreur lors du déploiement du code"
    exit 1
fi
echo "✅ Code déployé"

# Setup base de données
echo ""
echo "🗄️ Configuration base de données..."

# Envoyer backup sur serveur
echo "📤 Envoi backup vers serveur..."
scp -o StrictHostKeyChecking=no "$BACKUP_DIR/initial_deploy_${DATE}.sql" "dokku@$SERVER_IP:/tmp/"

# Setup DB sur serveur
echo "🔧 Installation base de données..."
ssh -o StrictHostKeyChecking=no "dokku@$SERVER_IP" << EOF
set -e

echo "⏸️ Arrêt application..."
apps:stop $APP_NAME || echo "App pas encore démarrée"

echo "🗃️ Suppression ancienne base..."
postgres:destroy $APP_NAME-postgres --force 2>/dev/null || echo "Pas d'ancienne base"

echo "🆕 Création nouvelle base..."
postgres:create $APP_NAME-postgres

echo "🔗 Liaison base à l'app..."
postgres:link $APP_NAME-postgres $APP_NAME

echo "📥 Import des données initiales..."
postgres:import $APP_NAME-postgres < /tmp/initial_deploy_${DATE}.sql

echo "🧹 Nettoyage..."
rm -f /tmp/initial_deploy_${DATE}.sql

echo "▶️ Démarrage application..."
apps:start $APP_NAME
EOF

echo ""
echo "⏳ Attente démarrage (30s)..."
sleep 30

# Test application
if curl -s -o /dev/null -w "%{http_code}" "http://$SERVER_IP" | grep -q "200\|302"; then
    echo "✅ Application accessible"
else
    echo "⚠️ Application peut-être pas encore prête"
fi

echo ""
echo "🎉 DÉPLOIEMENT INITIAL TERMINÉ !"
echo "================================="
echo "📍 URL: http://$SERVER_IP"
echo "👥 Utilisateurs de test installés"
echo "💾 Backup: $BACKUP_DIR/initial_deploy_${DATE}.sql"
echo ""
echo "🔍 Vérifiez maintenant :"
echo "  1. Accès à l'application"
echo "  2. Connexion avec vos comptes de test"
echo "  3. Fonctionnalités principales"
echo ""
echo "📝 Pour les prochaines mises à jour, utilisez:"
echo "  ./deploy.sh (code seulement, préserve la DB prod)"
echo ""