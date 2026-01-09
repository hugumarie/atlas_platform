#!/bin/bash

echo "💾 Configuration stockage persistant Atlas"
echo "=========================================="

echo "🔍 1. Vérification des volumes existants..."
ssh dokku@167.172.108.93 "storage:list atlas"

echo ""
echo "📁 2. Création des dossiers persistants sur l'hôte..."
ssh dokku@167.172.108.93 "mkdir -p /var/lib/dokku/data/storage/atlas/uploads"
ssh dokku@167.172.108.93 "mkdir -p /var/lib/dokku/data/storage/atlas/exports" 
ssh dokku@167.172.108.93 "mkdir -p /var/lib/dokku/data/storage/atlas/documents"
ssh dokku@167.172.108.93 "mkdir -p /var/lib/dokku/data/storage/atlas/static/documents"

echo "✅ Dossiers hôte créés"

echo ""
echo "🔗 3. Configuration des montages persistants..."

# Monter les dossiers uploads et exports
ssh dokku@167.172.108.93 "storage:mount atlas /var/lib/dokku/data/storage/atlas/uploads:/app/uploads"
ssh dokku@167.172.108.93 "storage:mount atlas /var/lib/dokku/data/storage/atlas/exports:/app/exports"
ssh dokku@167.172.108.93 "storage:mount atlas /var/lib/dokku/data/storage/atlas/documents:/app/documents"
ssh dokku@167.172.108.93 "storage:mount atlas /var/lib/dokku/data/storage/atlas/static/documents:/app/static/documents"

echo "✅ Volumes montés"

echo ""
echo "🔍 4. Vérification des montages..."
ssh dokku@167.172.108.93 "storage:list atlas"

echo ""
echo "🔄 5. Redémarrage pour appliquer les montages..."
ssh dokku@167.172.108.93 "ps:restart atlas"

echo ""
echo "⏳ Attente du redémarrage (30s)..."
sleep 30

echo ""
echo "✅ 6. Test des dossiers dans le conteneur..."
ssh dokku@167.172.108.93 "run atlas ls -la /app/ | grep -E 'uploads|exports|documents'"

echo ""
echo "🎉 Configuration terminée!"
echo ""
echo "💡 Les dossiers suivants sont maintenant persistants:"
echo "   - /app/uploads -> /var/lib/dokku/data/storage/atlas/uploads"
echo "   - /app/exports -> /var/lib/dokku/data/storage/atlas/exports"
echo "   - /app/documents -> /var/lib/dokku/data/storage/atlas/documents"
echo "   - /app/static/documents -> /var/lib/dokku/data/storage/atlas/static/documents"
echo ""
echo "🔧 Les fichiers sauvegardés survivront aux redéploiements!"