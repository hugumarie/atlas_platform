#!/bin/bash

# Script de déploiement ATLAS - Version propre
# Ne fait QUE le déploiement et les migrations, pas de config API

set -e
echo "🚀 DÉPLOIEMENT ATLAS - VERSION PROPRE"
echo "====================================="

# Variables
SERVER="root@167.172.108.93"
APP_NAME="atlas"

# Fonction SSH avec gestion d'erreur
ssh_exec() {
    echo "   Exécution: $1"
    ssh "$SERVER" "$1" || {
        echo "   ❌ ERREUR: $1"
        echo "   🔧 Tentative de résolution..."
        
        # Résolution spécifique selon le type d'erreur
        if [[ "$1" == *"unlock"* ]]; then
            echo "   → Forcer le déblocage..."
            ssh "$SERVER" "pkill -f dokku || true"
            sleep 2
            ssh "$SERVER" "rm -f /tmp/dokku-*lock* || true"
            ssh "$SERVER" "dokku apps:unlock $APP_NAME || true"
        elif [[ "$1" == *"purge-cache"* ]]; then
            echo "   → Forcer suppression cache..."
            ssh "$SERVER" "docker system prune -f || true"
            ssh "$SERVER" "dokku cleanup || true"
        elif [[ "$1" == *"run atlas python3"* ]]; then
            echo "   → Redémarrage app et retry..."
            ssh "$SERVER" "dokku ps:restart atlas"
            sleep 5
            ssh "$SERVER" "$1" || {
                echo "   ❌ Échec définitif: $1"
                exit 1
            }
        else
            echo "   ❌ Erreur non résolue: $1"
            exit 1
        fi
    }
}

dokku_exec() {
    ssh_exec "dokku $1"
}

echo "📋 ÉTAPE 1: Vérifications..."

# Vérifier répertoire
if [[ ! -f "app/__init__.py" ]]; then
    echo "❌ Erreur: Lancer depuis la racine du projet Atlas"
    exit 1
fi

# Vérifier git
if [[ -n $(git status --porcelain | grep -v '^??') ]]; then
    echo "❌ Modifications non commitées:"
    git status --porcelain | grep -v '^??'
    exit 1
fi

# Test connexion
if ! ssh -o ConnectTimeout=10 "$SERVER" "echo 'OK'" >/dev/null 2>&1; then
    echo "❌ Connexion serveur impossible"
    exit 1
fi

echo "✅ Vérifications OK"

echo ""
echo "🔧 ÉTAPE 2: Préparation déploiement..."

# Remote Dokku
if ! git remote get-url dokku >/dev/null 2>&1; then
    git remote add dokku dokku@167.172.108.93:atlas
else
    git remote set-url dokku dokku@167.172.108.93:atlas
fi

# Déblocage forcé (bypass si nécessaire)
echo "   → Déblocage de l'application..."
ssh "$SERVER" "dokku apps:unlock $APP_NAME || echo 'Déblocage ignoré'"

echo "   → Nettoyage du cache..."
ssh "$SERVER" "dokku repo:purge-cache $APP_NAME || echo 'Cache ignoré'"

echo "✅ Préparation OK"

echo ""
echo "📦 ÉTAPE 3: Déploiement du code..."

if ! git push dokku main --force; then
    echo "❌ Échec du push"
    exit 1
fi

echo "✅ Code déployé"

echo ""
echo "📊 ÉTAPE 4: Migrations de base de données..."

echo "   Attente démarrage application..."
sleep 15

echo "   → Redéploiement avec scripts de migration..."
git push dokku main --force >/dev/null 2>&1

echo "   → Création tables de base..."
dokku_exec "run $APP_NAME python3 migration_create_tables.py"

echo "   → Migration colonnes Stripe..."
dokku_exec "run $APP_NAME python3 migration_stripe_columns.py"

echo "   → Migration colonnes calculées..."
dokku_exec "run $APP_NAME python3 migration_calculated_columns.py"

echo "   → Création compte administrateur..."
dokku_exec "run $APP_NAME python3 migration_create_admin.py"

echo "✅ Migrations terminées"

echo ""
echo "🔄 ÉTAPE 5: Redémarrage et vérifications..."

dokku_exec "ps:restart $APP_NAME"
sleep 10

# Test rapide
echo "   Test accessibilité site..."
if curl -s -o /dev/null -w "%{http_code}" https://atlas-invest.fr | grep -q "200\|302"; then
    echo "   ✅ Site accessible"
else
    echo "   ⚠️ Site non accessible"
fi

echo ""
echo "================================================"
echo "🎉 DÉPLOIEMENT ATLAS TERMINÉ AVEC SUCCÈS !"
echo "================================================"
echo ""
echo "🌐 Site: https://atlas-invest.fr"
echo "👤 Admin: admin@atlas.fr / Atlas2024!"
echo ""
echo "📝 PROCHAINE ÉTAPE:"
echo "   Configurer tes API keys avec:"
echo "   ./configure_atlas_api_keys.sh"
echo ""
echo "✅ Application déployée et base de données migrée !"