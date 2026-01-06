#!/bin/bash

echo "🚀 Démarrage d'Atlas Platform v2.0..."

# Arrêter les serveurs existants
echo "🔄 Arrêt des serveurs existants..."
pkill -f "python.*run.py" 2>/dev/null || true
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
lsof -ti:5002 | xargs kill -9 2>/dev/null || true
sleep 1

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

# Vérifier les variables d'environnement Stripe
echo ""
echo "🔐 Vérification configuration Stripe..."

# Charger le .env si les variables ne sont pas en environnement
if [ -f .env ]; then
    export $(grep -E '^STRIPE_SECRET_KEY|^STRIPE_PUBLISHABLE_KEY' .env | xargs)
fi

if [ -n "$STRIPE_SECRET_KEY" ] && [ -n "$STRIPE_PUBLISHABLE_KEY" ]; then
    echo "✅ Clés Stripe configurées (Mode PRODUCTION)"
    echo "   - Secret Key: ${STRIPE_SECRET_KEY:0:20}..."
    echo "   - Publishable Key: ${STRIPE_PUBLISHABLE_KEY:0:20}..."
else
    echo "⚠️ Clés Stripe manquantes (Mode DÉVELOPPEMENT)"
    echo "   - Les moyens de paiement ne fonctionneront pas"
    echo "   - Vérifiez le fichier .env"
fi

# Afficher les informations de connexion
echo ""
echo "🎯 Atlas Platform prête !"
echo "================================"
echo "📊 Base de données: PostgreSQL (atlas_db)"
echo "🌐 Lancement de Flask sur http://127.0.0.1:5001"
echo ""
echo "🔑 Comptes disponibles:"
echo "  - Admin: admin@gmail.com"
echo "  - Client: test.client@gmail.com"
echo ""
echo "🌐 URLs importantes:"
echo "  - Site vitrine: http://127.0.0.1:5001"
echo "  - Connexion: http://127.0.0.1:5001/plateforme/connexion"
echo "  - Dashboard: http://127.0.0.1:5001/plateforme/dashboard"
echo "  - Profil utilisateur: http://127.0.0.1:5001/plateforme/profil"
echo ""
echo "🆕 Dernières améliorations (v2.0):"
echo "  ✅ Gestion complète des abonnements"
echo "  ✅ Moyens de paiement Stripe sécurisés"
echo "  ✅ Factures automatiques via Stripe"
echo "  ✅ Annulation d'abonnement simplifiée"
echo "  ✅ Interface utilisateur améliorée"
echo "  ✅ Calculs patrimoniaux optimisés"
echo ""

# Mise à jour des prix crypto (optionnelle)
echo "💰 Mise à jour des prix crypto (peut prendre 30-60 secondes)..."
read -p "🤔 Voulez-vous mettre à jour les prix crypto maintenant ? [y/N]: " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Mise à jour en cours..."
    if python refresh_crypto_prices.py; then
        echo "✅ Prix crypto mis à jour avec succès"
    else
        echo "⚠️ Erreur mise à jour crypto, continuer quand même..."
    fi
else
    echo "⏭️ Mise à jour crypto ignorée (vous pouvez la faire plus tard avec: python refresh_crypto_prices.py)"
fi
echo ""

# Lancer Flask
echo "🚀 Démarrage de Flask..."
python3 run.py &

# Attendre que Flask démarre
sleep 3

# Afficher les informations finales
echo ""
echo "🎉 ATLAS PLATFORM V2.0 DÉMARRÉ AVEC SUCCÈS !"
echo "=========================================="
echo ""
echo "🔗 LIENS UTILES :"
echo "   📱 Site vitrine:      http://127.0.0.1:5001"
echo "   🔑 Connexion:         http://127.0.0.1:5001/plateforme/connexion" 
echo "   📊 Dashboard:         http://127.0.0.1:5001/plateforme/dashboard"
echo "   👤 Profil utilisateur: http://127.0.0.1:5001/plateforme/profil"
echo "   ⚙️  Admin:            http://127.0.0.1:5001/plateforme/admin"
echo ""
echo "⚡ TESTS IMPORTANTS :"
echo "   1. Connectez-vous avec test.client@gmail.com"
echo "   2. Allez sur /plateforme/profil" 
echo "   3. Testez 'Ajouter un nouveau moyen de paiement'"
echo "   4. Vérifiez que les champs de carte Stripe s'affichent"
echo ""
echo "🔄 COMMANDES UTILES :"
echo "   Relancer Atlas:      ./start_atlas.sh"
echo "   Arrêter Flask:       Ctrl+C ou pkill -f python3"
echo "   Forcer arrêt:        pkill -f 'python.*run.py' && lsof -ti:5001,5002 | xargs kill -9"
echo "   Logs en direct:      tail -f logs/atlas.log"
echo ""
echo "📞 Support: En cas de problème, vérifiez la console ou contactez le développeur"
echo ""

# Le processus Flask continue en arrière-plan
echo "🎯 Flask lancé en arrière-plan (PID: $!)"
echo "💡 Utilisez 'Ctrl+C' puis 'pkill -f python3' pour arrêter"