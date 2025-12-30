#!/bin/bash

# Script pour configurer le volume persistant uploads via SSH
echo "🔧 CONFIGURATION VOLUME PERSISTANT UPLOADS - REMOTE"
echo "=================================================="

SERVER="root@167.172.108.93"
APP_NAME="atlas"

echo "🔗 Test de connexion au serveur..."
if ! ssh -o ConnectTimeout=10 "$SERVER" "echo 'OK'" >/dev/null 2>&1; then
    echo "❌ Impossible de se connecter au serveur"
    exit 1
fi
echo "✅ Connexion OK"

echo ""
echo "📁 ÉTAPE 1: Création des dossiers persistants..."
ssh "$SERVER" "mkdir -p /var/lib/dokku/data/storage/$APP_NAME/uploads"
ssh "$SERVER" "mkdir -p /var/lib/dokku/data/storage/$APP_NAME/uploads/apprentissages"
ssh "$SERVER" "mkdir -p /var/lib/dokku/data/storage/$APP_NAME/uploads/profiles"

echo "👤 ÉTAPE 2: Configuration des permissions..."
ssh "$SERVER" "chown -R 32767:32767 /var/lib/dokku/data/storage/$APP_NAME/"
ssh "$SERVER" "chmod -R 755 /var/lib/dokku/data/storage/$APP_NAME/"

echo "🔗 ÉTAPE 3: Montage du volume persistant..."
ssh "$SERVER" "dokku storage:mount $APP_NAME /var/lib/dokku/data/storage/$APP_NAME/uploads:/app/uploads"

echo "🔄 ÉTAPE 4: Redémarrage de l'application..."
ssh "$SERVER" "dokku ps:restart $APP_NAME"

echo "⏳ Attente 10 secondes pour redémarrage..."
sleep 10

echo "✅ ÉTAPE 5: Vérification du montage..."
echo ""
echo "📊 Rapport du stockage:"
ssh "$SERVER" "dokku storage:report $APP_NAME"

echo ""
echo "📁 Contenu du dossier persistant:"
ssh "$SERVER" "ls -la /var/lib/dokku/data/storage/$APP_NAME/uploads/"

echo ""
echo "🧪 Test d'écriture..."
ssh "$SERVER" "echo 'test' > /var/lib/dokku/data/storage/$APP_NAME/uploads/test.txt"
if ssh "$SERVER" "[ -f /var/lib/dokku/data/storage/$APP_NAME/uploads/test.txt ]"; then
    echo "✅ Écriture réussie"
    ssh "$SERVER" "rm /var/lib/dokku/data/storage/$APP_NAME/uploads/test.txt"
else
    echo "❌ Erreur d'écriture"
fi

echo ""
echo "🧪 Test final site web..."
if curl -s -o /dev/null -w "%{http_code}" https://atlas-invest.fr | grep -q "200\|302"; then
    echo "✅ Site accessible"
else
    echo "⚠️ Site non accessible"
fi

echo ""
echo "================================================"
echo "🎉 CONFIGURATION TERMINÉE !"
echo "================================================"
echo ""
echo "✅ Volume persistant configuré pour /app/uploads"
echo "📁 Vos fichiers ne disparaîtront plus au redémarrage"
echo ""
echo "📝 PROCHAINES ÉTAPES:"
echo "1. Aller sur https://atlas-invest.fr/plateforme/admin/apprentissages"
echo "2. Réuploader vos fichiers d'apprentissage"
echo "3. Tester qu'ils persistent après un redémarrage"
echo ""
echo "🔍 En cas de problème, vérifier les logs:"
echo "   ssh $SERVER 'dokku logs $APP_NAME --tail'"