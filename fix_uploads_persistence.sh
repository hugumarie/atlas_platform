#!/bin/bash

# Script pour corriger la persistance des fichiers uploads sur le serveur
echo "🔧 CORRECTION PERSISTANCE FICHIERS UPLOADS"
echo "=========================================="
echo ""

echo "📁 ÉTAPE 1: Création des dossiers persistants..."
mkdir -p /var/lib/dokku/data/storage/atlas/uploads
mkdir -p /var/lib/dokku/data/storage/atlas/uploads/apprentissages
mkdir -p /var/lib/dokku/data/storage/atlas/uploads/profiles

echo "👤 ÉTAPE 2: Configuration des permissions..."
chown -R dokku:dokku /var/lib/dokku/data/storage/atlas/
chmod -R 755 /var/lib/dokku/data/storage/atlas/

echo "🔗 ÉTAPE 3: Montage du volume persistant..."
dokku storage:mount atlas /var/lib/dokku/data/storage/atlas/uploads:/app/uploads

echo "🔄 ÉTAPE 4: Redémarrage de l'application..."
dokku ps:restart atlas

echo "✅ ÉTAPE 5: Vérification du montage..."
echo ""
echo "📊 Rapport du stockage:"
dokku storage:report atlas

echo ""
echo "📁 Contenu du dossier persistant:"
ls -la /var/lib/dokku/data/storage/atlas/uploads/

echo ""
echo "🧪 Test d'écriture..."
echo "test" > /var/lib/dokku/data/storage/atlas/uploads/test.txt
if [ -f /var/lib/dokku/data/storage/atlas/uploads/test.txt ]; then
    echo "✅ Écriture réussie"
    rm /var/lib/dokku/data/storage/atlas/uploads/test.txt
else
    echo "❌ Erreur d'écriture"
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
echo "1. Réuploader vos fichiers d'apprentissage via l'admin"
echo "2. Tester qu'ils persistent après redémarrage"
echo "3. Vérifier les URL des fichiers dans l'interface"