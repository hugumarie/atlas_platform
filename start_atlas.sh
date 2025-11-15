#!/bin/bash

echo "🚀 Démarrage d'Atlas Platform..."

# Vérifier PostgreSQL
echo "📊 Vérification PostgreSQL..."
if brew services list | grep postgresql@16 | grep started > /dev/null; then
    echo "✅ PostgreSQL déjà démarré"
else
    echo "🔄 Démarrage de PostgreSQL..."
    brew services start postgresql@16
    sleep 2
fi

# Test de connexion à la base
echo "🔍 Test de connexion à la base..."
if /opt/homebrew/opt/postgresql@16/bin/psql -d atlas_db -c "SELECT COUNT(*) FROM users;" > /dev/null 2>&1; then
    echo "✅ Base de données accessible"
else
    echo "❌ Erreur de connexion à la base"
    exit 1
fi

# Afficher les informations de connexion
echo ""
echo "🎯 Atlas Platform prête !"
echo "================================"
echo "📊 Base de données: PostgreSQL (atlas_db)"
echo "🌐 Lancement de Flask sur http://127.0.0.1:5000"
echo ""
echo "🔑 Comptes disponibles:"
echo "  - Admin: admin@gmail.com"
echo "  - Client: test.client@gmail.com"
echo ""
echo "🌐 URLs importantes:"
echo "  - Site vitrine: http://127.0.0.1:5000"
echo "  - Connexion: http://127.0.0.1:5000/platform/login"
echo "  - Dashboard: http://127.0.0.1:5000/platform/dashboard"
echo ""

# Lancer Flask
echo "🚀 Démarrage de Flask..."
python3 -m flask run --host=127.0.0.1 --port=5000