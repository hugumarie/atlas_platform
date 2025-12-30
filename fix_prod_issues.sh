#!/bin/bash

# Script de correction des problèmes de production Atlas
echo "🔧 CORRECTION DES PROBLÈMES ATLAS"
echo "================================="

SERVER="root@167.172.108.93"
APP_NAME="atlas"

echo ""
echo "📋 PROBLÈMES À CORRIGER:"
echo "1. MailerSend 401 Unauthenticated" 
echo "2. Fichiers uploads manquants (404)"
echo ""

echo "🔧 ÉTAPE 1: Création volume persistant uploads..."
ssh "$SERVER" "dokku storage:mount $APP_NAME /var/lib/dokku/data/storage/$APP_NAME/uploads:/app/uploads"

echo "📁 ÉTAPE 2: Création des dossiers nécessaires..."
ssh "$SERVER" "mkdir -p /var/lib/dokku/data/storage/$APP_NAME/uploads"
ssh "$SERVER" "mkdir -p /var/lib/dokku/data/storage/$APP_NAME/uploads/apprentissages"
ssh "$SERVER" "mkdir -p /var/lib/dokku/data/storage/$APP_NAME/uploads/profiles"

echo "👤 ÉTAPE 3: Permissions correctes..."
ssh "$SERVER" "chown -R dokku:dokku /var/lib/dokku/data/storage/$APP_NAME/"
ssh "$SERVER" "chmod -R 755 /var/lib/dokku/data/storage/$APP_NAME/"

echo "🔄 ÉTAPE 4: Redémarrage application..."
ssh "$SERVER" "dokku ps:restart $APP_NAME"

echo ""
echo "📧 ÉTAPE 5: Vérification MailerSend..."
echo "Token actuel:"
ssh "$SERVER" "dokku config $APP_NAME | grep MAILER"

echo ""
echo "💡 ACTIONS MANUELLES REQUISES:"
echo ""
echo "1. 📧 Reconfigurer MailerSend avec nouveau token:"
echo "   dokku config:set $APP_NAME MAILERSEND_API_TOKEN=\"mlsn_VOTRE_NOUVEAU_TOKEN\""
echo ""
echo "2. 📁 Réuploader vos fichiers d'apprentissage via l'admin"
echo ""
echo "3. 🧪 Tester l'envoi d'email depuis l'interface admin"
echo ""

echo "🔍 ÉTAPE 6: Tests post-correction..."
echo "Volume uploads:"
ssh "$SERVER" "dokku storage:report $APP_NAME"

echo ""
echo "Dossiers créés:"
ssh "$SERVER" "ls -la /var/lib/dokku/data/storage/$APP_NAME/uploads/"

echo ""
echo "✅ Corrections de base appliquées!"
echo ""
echo "📝 PROCHAINES ÉTAPES:"
echo "1. Vérifier que MailerSend fonctionne avec nouveau token"
echo "2. Réuploader les fichiers manquants"
echo "3. Tester la persistance des fichiers"