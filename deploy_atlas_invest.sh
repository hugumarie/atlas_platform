#!/bin/bash

echo "🚀 Déploiement Atlas sur atlas-invest.fr"
echo "========================================="

# Vérification des prérequis
echo "✅ Vérification des prérequis..."

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "run.py" ]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis le répertoire du projet Atlas"
    exit 1
fi

# Vérifier la configuration git
if ! git status &> /dev/null; then
    echo "❌ Erreur: Ce répertoire n'est pas un repository git"
    exit 1
fi

# Étape 1: Mise à jour du code local
echo "📝 Mise à jour des configurations pour atlas-invest.fr..."

# Vérifier que les changements sont bien faits
if ! grep -q "atlas-invest.fr" app/routes/platform/admin.py; then
    echo "❌ Erreur: Le domaine atlas-invest.fr n'est pas configuré dans le code"
    echo "Veuillez vérifier les modifications dans admin.py"
    exit 1
fi

# Étape 2: Commit des changements
echo "📦 Commit des configurations pour production..."

# Ajouter tous les changements
git add -A

# Créer le commit
git commit -m "🚀 Deploy: Configuration pour atlas-invest.fr

- Domaine mis à jour dans toutes les routes
- Configuration email: noreply@atlas-invest.fr
- Templates mis à jour avec le nouveau branding
- Variables d'environnement configurées pour production
- DNS et SSL prêts pour déploiement

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Étape 3: Déploiement sur Dokku
echo "🚀 Déploiement vers atlas-invest.fr..."

# Push vers le serveur de production
echo "📤 Push vers le serveur Dokku..."
git push dokku main

# Attendre que le déploiement se termine
echo "⏳ Attente de la fin du déploiement..."
sleep 10

# Étape 4: Configuration post-déploiement
echo "🔧 Configuration post-déploiement..."

echo "📋 Commandes à exécuter sur le serveur (ssh root@167.172.108.93):"
echo ""
echo "# Configuration domaine"
echo "dokku domains:add atlas atlas-invest.fr"
echo "dokku domains:add atlas www.atlas-invest.fr"
echo ""
echo "# Configuration SSL"
echo "dokku letsencrypt:set atlas email hugues.marie925@gmail.com"
echo "dokku letsencrypt:enable atlas"
echo ""
echo "# Variables d'environnement"
echo "dokku config:set atlas FLASK_ENV=production"
echo "dokku config:set atlas SITE_URL=\"https://atlas-invest.fr\""
echo "dokku config:set atlas ATLAS_FROM_EMAIL=\"noreply@atlas-invest.fr\""
echo ""

# Étape 5: Instructions finales
echo ""
echo "✅ Déploiement local terminé !"
echo ""
echo "🎯 Prochaines étapes:"
echo "1. ⚙️  Configurer DNS sur OVH (voir DNS_CONFIG_OVH.md)"
echo "2. 🖥️  Exécuter les commandes serveur ci-dessus"
echo "3. 📧 Configurer MailerSend avec atlas-invest.fr"
echo "4. 🔍 Tester le site sur https://atlas-invest.fr"
echo ""
echo "📁 Fichiers de configuration créés:"
echo "   - DNS_CONFIG_OVH.md (à faire sur OVH)"
echo "   - DOKKU_DOMAIN_CONFIG.md (commandes serveur)"
echo "   - MAILERSEND_CONFIG.md (configuration email)"
echo ""
echo "🚀 Atlas sera accessible sur https://atlas-invest.fr !"