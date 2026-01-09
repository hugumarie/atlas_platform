#!/bin/bash

echo "🔐 Configuration variables d'environnement production"
echo "===================================================="

# Récupérer les clés depuis .env local (sans les exposer)
if [ -f ".env" ]; then
    echo "📋 Clés trouvées dans .env local"
    
    # Lire les variables importantes
    OPENAI_KEY=$(grep "OPENAI_API_KEY=" .env | cut -d'=' -f2)
    MAILERSEND_TOKEN=$(grep "MAILERSEND_API_TOKEN=" .env | cut -d'=' -f2)
    STRIPE_PUB=$(grep "STRIPE_PUBLISHABLE_KEY=" .env | cut -d'=' -f2)
    STRIPE_SEC=$(grep "STRIPE_SECRET_KEY=" .env | cut -d'=' -f2)
    
    echo "✅ Variables extraites du .env local"
else
    echo "❌ Fichier .env non trouvé"
    exit 1
fi

echo ""
echo "🚀 Configuration des variables sur le serveur Dokku..."

# Configurer les variables une par une (plus sûr)
ssh dokku@167.172.108.93 "config:set atlas OPENAI_API_KEY=\"$OPENAI_KEY\""
echo "✅ OPENAI_API_KEY configurée"

ssh dokku@167.172.108.93 "config:set atlas MAILERSEND_API_TOKEN=\"$MAILERSEND_TOKEN\""
echo "✅ MAILERSEND_API_TOKEN configurée"

ssh dokku@167.172.108.93 "config:set atlas FROM_EMAIL=\"noreply@atlas-invest.fr\""
echo "✅ FROM_EMAIL configurée"

ssh dokku@167.172.108.93 "config:set atlas FROM_NAME=\"Atlas Invest\""
echo "✅ FROM_NAME configurée"

# Variables Stripe (si nécessaire)
if [ ! -z "$STRIPE_PUB" ] && [ ! -z "$STRIPE_SEC" ]; then
    ssh dokku@167.172.108.93 "config:set atlas STRIPE_PUBLISHABLE_KEY=\"$STRIPE_PUB\""
    ssh dokku@167.172.108.93 "config:set atlas STRIPE_SECRET_KEY=\"$STRIPE_SEC\""
    echo "✅ Variables Stripe configurées"
fi

echo ""
echo "🔄 Redémarrage de l'application..."
ssh dokku@167.172.108.93 "ps:restart atlas"

echo ""
echo "🔍 Vérification des variables configurées..."
ssh dokku@167.172.108.93 "config atlas" | grep -E "OPENAI_API_KEY|MAILERSEND_API_TOKEN|FROM_EMAIL"

echo ""
echo "🎉 Configuration terminée!"
echo "🌐 Testez sur: https://atlas-invest.fr"