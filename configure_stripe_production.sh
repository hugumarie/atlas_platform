#!/bin/bash

echo "💳 Configuration Stripe Production Atlas"
echo "========================================"

# Lire les clés depuis .env local
if [ -f ".env" ]; then
    echo "📋 Lecture des clés Stripe depuis .env local..."
    
    STRIPE_PUB=$(grep "STRIPE_PUBLISHABLE_KEY=" .env | cut -d'=' -f2)
    STRIPE_SEC=$(grep "STRIPE_SECRET_KEY=" .env | cut -d'=' -f2)
    STRIPE_WEBHOOK=$(grep "STRIPE_WEBHOOK_SECRET=" .env | cut -d'=' -f2)
    STRIPE_INITIA=$(grep "STRIPE_PRICE_INITIA=" .env | cut -d'=' -f2)
    STRIPE_OPTIMA=$(grep "STRIPE_PRICE_OPTIMA=" .env | cut -d'=' -f2)
    
    echo "✅ Clés extraites du .env"
    echo "   - Publishable: ${STRIPE_PUB:0:20}..."
    echo "   - Secret: ${STRIPE_SEC:0:15}..."
    echo "   - Webhook: ${STRIPE_WEBHOOK:0:10}..."
    echo "   - Price Initia: $STRIPE_INITIA"
    echo "   - Price Optima: $STRIPE_OPTIMA"
else
    echo "❌ Fichier .env non trouvé"
    exit 1
fi

echo ""
echo "🚀 Configuration sur le serveur Dokku..."

# Configurer les clés Stripe
ssh dokku@167.172.108.93 "config:set atlas STRIPE_PUBLISHABLE_KEY=\"$STRIPE_PUB\""
echo "✅ STRIPE_PUBLISHABLE_KEY configurée"

ssh dokku@167.172.108.93 "config:set atlas STRIPE_SECRET_KEY=\"$STRIPE_SEC\""
echo "✅ STRIPE_SECRET_KEY configurée"

ssh dokku@167.172.108.93 "config:set atlas STRIPE_WEBHOOK_SECRET=\"$STRIPE_WEBHOOK\""
echo "✅ STRIPE_WEBHOOK_SECRET configurée"

ssh dokku@167.172.108.93 "config:set atlas STRIPE_PRICE_INITIA=\"$STRIPE_INITIA\""
echo "✅ STRIPE_PRICE_INITIA configurée"

ssh dokku@167.172.108.93 "config:set atlas STRIPE_PRICE_OPTIMA=\"$STRIPE_OPTIMA\""
echo "✅ STRIPE_PRICE_OPTIMA configurée"

# URLs Stripe
ssh dokku@167.172.108.93 "config:set atlas STRIPE_SUCCESS_URL=\"https://atlas-invest.fr/onboarding/stripe/success\""
ssh dokku@167.172.108.93 "config:set atlas STRIPE_CANCEL_URL=\"https://atlas-invest.fr/onboarding/stripe/cancel\""
echo "✅ URLs Stripe configurées"

echo ""
echo "🔄 Redémarrage de l'application..."
ssh dokku@167.172.108.93 "ps:restart atlas"

echo ""
echo "⏳ Attente du redémarrage (30s)..."
sleep 30

echo ""
echo "🧪 Test de la configuration Stripe..."
ssh dokku@167.172.108.93 "run atlas python -c '
import requests
import os

stripe_key = os.getenv(\"STRIPE_SECRET_KEY\")
print(f\"Test clé: {stripe_key[:15]}...\")

headers = {\"Authorization\": f\"Bearer {stripe_key}\"}
try:
    response = requests.get(\"https://api.stripe.com/v1/balance\", headers=headers, timeout=10)
    print(f\"Status: {response.status_code}\")
    if response.status_code == 200:
        print(\"✅ Configuration Stripe OK!\")
    else:
        print(f\"❌ Erreur: {response.text}\")
except Exception as e:
    print(f\"❌ Erreur: {e}\")
'"

echo ""
echo "🎉 Configuration Stripe terminée!"
echo "🌐 Testez le paiement sur: https://atlas-invest.fr"