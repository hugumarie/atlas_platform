#!/bin/bash

# Script de déploiement automatique Atlas vers production Dokku
# Usage: ./deploy_production.sh

set -e  # Arrêter en cas d'erreur

echo "🚀 Déploiement Atlas vers production..."

# Vérifications préliminaires
echo "📋 Vérifications préliminaires..."

# Vérifier qu'on est dans le bon répertoire
if [[ ! -f "app/__init__.py" ]]; then
    echo "❌ Erreur: Lancer ce script depuis la racine du projet Atlas"
    exit 1
fi

# Vérifier que git est propre
if [[ -n $(git status --porcelain) ]]; then
    echo "❌ Erreur: Il y a des modifications non commitées"
    echo "   Faire d'abord: git add . && git commit -m 'message'"
    exit 1
fi

# Vérifier la connexion au serveur
echo "🔗 Test de connexion au serveur..."
if ! ssh -o ConnectTimeout=5 root@167.172.108.93 "echo 'Connexion OK'" 2>/dev/null; then
    echo "❌ Erreur: Impossible de se connecter au serveur 167.172.108.93"
    echo "   Vérifier la connexion SSH"
    exit 1
fi

# Vérifier/ajouter le remote dokku
echo "📡 Configuration du remote Dokku..."
if ! git remote get-url dokku >/dev/null 2>&1; then
    echo "   Ajout du remote dokku..."
    git remote add dokku dokku@167.172.108.93:atlas
else
    echo "   Remote dokku déjà configuré"
    git remote set-url dokku dokku@167.172.108.93:atlas
fi

# Backup de sécurité de la base de données
echo "💾 Backup de sécurité de la base de données..."
BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S)"
ssh root@167.172.108.93 "dokku postgres:backup atlas-db $BACKUP_NAME" || {
    echo "⚠️ Backup échoué, continuer quand même ? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
}

# Configuration des variables d'environnement
echo "⚙️ Rappel: Variables d'environnement Stripe à configurer manuellement"
echo "   Connecte-toi au serveur et exécute les commandes du guide DEPLOYMENT_PRODUCTION.md"
echo ""
echo "   Exemple:"
echo "   ssh root@167.172.108.93"
echo "   dokku config:set atlas STRIPE_SECRET_KEY='sk_live_...'"
echo "   dokku config:set atlas STRIPE_PUBLISHABLE_KEY='pk_live_...'"
echo "   # ... autres variables"
echo ""
echo "🤔 Les variables Stripe sont-elles configurées ? (y/N)"
read -r stripe_configured
if [[ ! "$stripe_configured" =~ ^[Yy]$ ]]; then
    echo "❌ Configure d'abord les variables Stripe selon DEPLOYMENT_PRODUCTION.md"
    exit 1
fi

# Déploiement
echo "🚀 Déploiement en cours..."
echo "   Push vers Dokku (cela peut prendre quelques minutes)..."

# Push vers Dokku avec gestion d'erreur
if ! git push dokku main; then
    echo "❌ Erreur lors du déploiement"
    echo "📜 Logs du serveur:"
    ssh root@167.172.108.93 "dokku logs atlas --tail -n 50"
    exit 1
fi

echo "✅ Code déployé avec succès!"

# Attendre que l'application soit prête
echo "⏳ Attente du démarrage de l'application..."
sleep 10

# Tests de vérification
echo "🧪 Tests de vérification..."

# Test 1: Ping de base
echo "   Test 1: Disponibilité du site..."
if curl -s -I https://atlas-invest.fr | grep -q "200 OK"; then
    echo "   ✅ Site accessible"
else
    echo "   ❌ Site non accessible"
    echo "   Vérifier les logs: ssh root@167.172.108.93 'dokku logs atlas --tail'"
fi

# Test 2: Page de connexion  
echo "   Test 2: Page de connexion..."
if curl -s https://atlas-invest.fr/plateforme/login | grep -q "Atlas"; then
    echo "   ✅ Page de connexion accessible"
else
    echo "   ❌ Problème avec la page de connexion"
fi

# Test 3: Webhook Stripe
echo "   Test 3: Configuration Stripe..."
STRIPE_CONFIG=$(ssh root@167.172.108.93 "dokku config atlas | grep STRIPE_SECRET_KEY" 2>/dev/null || echo "")
if [[ -n "$STRIPE_CONFIG" ]]; then
    echo "   ✅ Configuration Stripe détectée"
else
    echo "   ⚠️ Configuration Stripe manquante"
fi

# Affichage des logs récents
echo "📜 Logs récents de l'application:"
ssh root@167.172.108.93 "dokku logs atlas --tail -n 20"

echo ""
echo "🎉 Déploiement terminé!"
echo ""
echo "🔗 URLs importantes:"
echo "   • Site principal: https://atlas-invest.fr"
echo "   • Page de plans: https://atlas-invest.fr/onboarding/plan"
echo "   • Connexion admin: https://atlas-invest.fr/plateforme/login"
echo ""
echo "👤 Compte admin par défaut:"
echo "   • Email: admin@atlas.fr" 
echo "   • Mot de passe: Atlas2024!"
echo ""
echo "🔧 Commandes utiles:"
echo "   • Logs temps réel: ssh root@167.172.108.93 'dokku logs atlas --tail'"
echo "   • Redémarrer: ssh root@167.172.108.93 'dokku ps:restart atlas'"
echo "   • Config: ssh root@167.172.108.93 'dokku config atlas'"
echo ""

# Test final optionnel
echo "🎯 Tester le paiement Stripe maintenant ? (y/N)"
read -r test_payment
if [[ "$test_payment" =~ ^[Yy]$ ]]; then
    echo "1. Va sur: https://atlas-invest.fr/onboarding/plan"
    echo "2. Sélectionne un plan (INITIA ou OPTIMA)"
    echo "3. Vérifie que Stripe Checkout se charge sans erreur"
    echo "4. Ferme la page sans payer (test uniquement)"
fi

echo ""
echo "✨ Atlas déployé en production avec succès !"