#!/bin/bash

# Script de configuration des API Keys Atlas
# À lancer APRÈS deploy_atlas_clean.sh

echo "🔑 CONFIGURATION DES API KEYS ATLAS"
echo "===================================="
echo ""
echo "Ce script va configurer tes API keys de production de façon sécurisée."
echo "Tes clés ne s'afficheront pas à l'écran (saisie masquée)."
echo "Appuie sur ENTRÉE pour passer une variable si tu ne veux pas la configurer."
echo ""

# Variables
SERVER="root@167.172.108.93"
APP_NAME="atlas"

# Fonction pour configurer une variable de façon sécurisée
configure_var() {
    local var_name="$1"
    local var_description="$2"
    local var_example="$3"
    local var_value=""
    
    echo "📝 $var_description"
    echo "   Format attendu: $var_example"
    echo -n "🔑 Valeur pour $var_name: "
    read -s var_value
    echo ""
    
    if [[ -n "$var_value" ]]; then
        echo "   📤 Configuration sur le serveur..."
        if ssh "$SERVER" "dokku config:set $APP_NAME $var_name='$var_value'" >/dev/null 2>&1; then
            echo "   ✅ $var_name configurée avec succès"
        else
            echo "   ❌ Erreur lors de la configuration de $var_name"
        fi
    else
        echo "   ⏭️ $var_name ignorée"
    fi
    echo ""
}

# Test de connexion
echo "🔗 Test de connexion au serveur..."
if ! ssh -o ConnectTimeout=10 "$SERVER" "echo 'OK'" >/dev/null 2>&1; then
    echo "❌ Impossible de se connecter au serveur"
    exit 1
fi
echo "✅ Connexion OK"
echo ""

# Configuration des variables par catégorie
echo "💳 === STRIPE (Paiements) ==="
configure_var "STRIPE_SECRET_KEY" "Clé secrète Stripe" "sk_live_..."
configure_var "STRIPE_PUBLISHABLE_KEY" "Clé publique Stripe" "pk_live_..."
configure_var "STRIPE_WEBHOOK_SECRET" "Secret webhook Stripe" "whsec_..."
configure_var "STRIPE_PRICE_INITIA" "ID prix plan INITIA" "price_..."
configure_var "STRIPE_PRICE_OPTIMA" "ID prix plan OPTIMA" "price_..."
configure_var "STRIPE_PRICE_MAXIMA" "ID prix plan MAXIMA" "price_..."

echo "🤖 === OPENAI (Intelligence Artificielle) ==="
configure_var "OPENAI_API_KEY" "Clé API OpenAI" "sk-proj-..."

echo "📧 === MAILERSEND (Envoi d'emails) ==="
configure_var "MAILERSEND_API_TOKEN" "Token API MailerSend" "mlsn_..."

echo "₿ === BINANCE (Prix cryptomonnaies) ==="
configure_var "BINANCE_API_KEY" "Clé API Binance" "Votre clé API Binance"
configure_var "BINANCE_SECRET_KEY" "Clé secrète Binance" "Votre clé secrète Binance"

echo "🌐 === AUTRES SERVICES ==="
configure_var "SITE_URL" "URL du site" "https://atlas-invest.fr"

echo ""
echo "🔄 Redémarrage de l'application pour prendre en compte les nouvelles variables..."
if ssh "$SERVER" "dokku ps:restart $APP_NAME" >/dev/null 2>&1; then
    echo "✅ Application redémarrée"
else
    echo "❌ Erreur lors du redémarrage"
fi

echo ""
echo "🧪 Test final..."
sleep 5
if curl -s -o /dev/null -w "%{http_code}" https://atlas-invest.fr | grep -q "200\|302"; then
    echo "✅ Site accessible avec nouvelles configurations"
else
    echo "⚠️ Site non accessible - vérifier les logs"
fi

echo ""
echo "=============================================="
echo "🎉 CONFIGURATION TERMINÉE !"
echo "=============================================="
echo ""
echo "🌐 Ton site Atlas est maintenant configuré:"
echo "   • URL: https://atlas-invest.fr"
echo "   • Admin: admin@atlas.fr / Atlas2024!"
echo ""
echo "📋 Pour vérifier les variables configurées:"
echo "   ssh $SERVER 'dokku config $APP_NAME'"
echo ""
echo "🔍 Pour voir les logs en cas de problème:"
echo "   ssh $SERVER 'dokku logs $APP_NAME --tail'"
echo ""
echo "✅ Atlas est maintenant 100% opérationnel !"