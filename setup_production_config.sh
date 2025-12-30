#!/bin/bash

# Script pour créer et chiffrer la configuration production
# Usage: ./setup_production_config.sh

echo "🔐 Configuration sécurisée Atlas Production"
echo ""

# Vérifier si OpenSSL est disponible
if ! command -v openssl &> /dev/null; then
    echo "❌ OpenSSL n'est pas installé. Installation requise:"
    echo "   macOS: brew install openssl"
    echo "   Ubuntu: apt install openssl"
    exit 1
fi

# Créer le fichier temporaire non chiffré
TEMP_FILE=".env.production.tmp"
ENCRYPTED_FILE=".env.production.enc"

echo "📝 Création du fichier de configuration..."

cat > "$TEMP_FILE" << 'EOF'
# Configuration Production Atlas - FICHIER CHIFFRÉ
# Remplace ces valeurs par tes vraies clés

# === STRIPE (OBLIGATOIRE) ===
STRIPE_SECRET_KEY=sk_live_REMPLACE_PAR_TA_CLE_SECRETE
STRIPE_PUBLISHABLE_KEY=pk_live_REMPLACE_PAR_TA_CLE_PUBLIQUE
STRIPE_WEBHOOK_SECRET=whsec_REMPLACE_PAR_TON_SECRET_WEBHOOK

# Price IDs des plans (récupérer depuis Stripe Dashboard > Produits)
STRIPE_PRICE_INITIA=price_REMPLACE_PAR_PRICE_ID_INITIA
STRIPE_PRICE_OPTIMA=price_REMPLACE_PAR_PRICE_ID_OPTIMA  
STRIPE_PRICE_MAXIMA=price_REMPLACE_PAR_PRICE_ID_MAXIMA

# === OPENAI (OBLIGATOIRE POUR L'ASSISTANT IA) ===
OPENAI_API_KEY=sk-proj-REMPLACE_PAR_TA_CLE_OPENAI

# === URLs (ADAPTER SI NÉCESSAIRE) ===
SITE_URL=https://atlas-invest.fr
STRIPE_SUCCESS_URL=https://atlas-invest.fr/plateforme/dashboard
STRIPE_CANCEL_URL=https://atlas-invest.fr/onboarding/plan

# === SYSTÈME (AUTO-GÉNÉRÉ) ===
FLASK_ENV=production
FLASK_DEBUG=False

# === EMAIL (OPTIONNEL) ===
# MAILERSEND_API_TOKEN=mlsn.TON_TOKEN_SI_TU_VEUX_EMAILS
EOF

echo "✅ Fichier de configuration créé"
echo ""
echo "🔑 Choisis un mot de passe pour chiffrer ce fichier:"
echo "   (Ce mot de passe sera demandé à chaque déploiement)"

# Chiffrer le fichier avec un mot de passe
openssl enc -aes-256-cbc -salt -pbkdf2 -in "$TEMP_FILE" -out "$ENCRYPTED_FILE"

if [[ $? -eq 0 ]]; then
    # Supprimer le fichier temporaire non chiffré
    rm "$TEMP_FILE"
    
    echo ""
    echo "🔒 Configuration chiffrée avec succès dans: $ENCRYPTED_FILE"
    echo ""
    echo "📝 Prochaines étapes:"
    echo "   1. Éditer le fichier chiffré: ./edit_production_config.sh"
    echo "   2. Remplacer les valeurs STRIPE par tes vraies clés"
    echo "   3. Déployer: ./deploy_production.sh"
    echo ""
    echo "⚠️ IMPORTANT: Mémorise bien ton mot de passe !"
else
    echo "❌ Erreur lors du chiffrement"
    rm -f "$TEMP_FILE"
    exit 1
fi