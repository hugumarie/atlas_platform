#!/bin/bash

echo "🚀 Déploiement Atlas - Configuration Interactive"
echo "==============================================="
echo ""

# Fonction pour lire les inputs de manière sécurisée
read_secret() {
    local prompt="$1"
    local var_name="$2"
    echo -n "$prompt: "
    read -s value
    echo ""
    eval "$var_name='$value'"
}

read_input() {
    local prompt="$1"
    local var_name="$2"
    echo -n "$prompt: "
    read value
    eval "$var_name='$value'"
}

echo "📋 Configuration des clés API de production"
echo "============================================"
echo ""

# Configuration Email
echo "📧 CONFIGURATION EMAIL (pour notifications)"
read_input "Serveur SMTP (ex: smtp.gmail.com)" MAIL_SERVER
read_input "Port SMTP (ex: 587)" MAIL_PORT
read_input "Email d'envoi" MAIL_USERNAME
read_secret "Mot de passe/App Password" MAIL_PASSWORD

echo ""
echo "🤖 CONFIGURATION GPT/OPENAI (optionnel)"
read_secret "Clé API OpenAI (ou laissez vide)" OPENAI_API_KEY

echo ""
echo "💰 CONFIGURATION BINANCE (pour prix crypto)"
read_input "Clé API Binance (ou laissez vide pour utiliser publique)" BINANCE_API_KEY
read_secret "Secret Binance (ou laissez vide)" BINANCE_SECRET_KEY

echo ""
echo "🔐 CONFIGURATION SÉCURITÉ"
read_secret "Clé secrète Flask (minimum 32 caractères)" SECRET_KEY

echo ""
echo "💾 CONFIGURATION BASE DE DONNÉES"
read_input "Nom de la base (défaut: atlas_production_db)" DB_NAME
read_input "Utilisateur DB (défaut: atlas)" DB_USER
read_secret "Mot de passe DB" DB_PASSWORD

# Valeurs par défaut
DB_NAME=${DB_NAME:-atlas_production_db}
DB_USER=${DB_USER:-atlas}
MAIL_PORT=${MAIL_PORT:-587}
MAIL_SERVER=${MAIL_SERVER:-smtp.gmail.com}

echo ""
echo "✅ Configuration terminée ! Création du fichier .env.production..."

# Créer le fichier .env.production
cat > .env.production.new << EOF
# Atlas Production Environment - Configuré le $(date)
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=$SECRET_KEY

# Database Configuration  
SQLALCHEMY_DATABASE_URI=postgresql://$DB_USER:$DB_PASSWORD@localhost/$DB_NAME

# Email Configuration
MAIL_SERVER=$MAIL_SERVER
MAIL_PORT=$MAIL_PORT
MAIL_USE_TLS=True
MAIL_USERNAME=$MAIL_USERNAME
MAIL_PASSWORD=$MAIL_PASSWORD

# OpenAI Configuration (optionnel)
OPENAI_API_KEY=$OPENAI_API_KEY

# Binance API Configuration
BINANCE_API_KEY=$BINANCE_API_KEY
BINANCE_SECRET_KEY=$BINANCE_SECRET_KEY

# Security
WTF_CSRF_ENABLED=True

# Logging
LOG_LEVEL=INFO

# Production Settings
DEBUG=False
TESTING=False
EOF

echo "📁 Fichier .env.production.new créé avec succès !"
echo ""
echo "🔍 Voulez-vous voir un aperçu des configurations ? (y/n)"
read -n 1 show_config
echo ""

if [[ $show_config =~ ^[Yy]$ ]]; then
    echo "📋 Configuration créée :"
    echo "======================"
    grep -v "PASSWORD\|SECRET\|KEY" .env.production.new | while read line; do
        if [[ ! $line =~ ^# ]] && [[ ! -z $line ]]; then
            echo "  ✓ $line"
        fi
    done
    echo "  ✓ [Mots de passe et clés masqués pour sécurité]"
fi

echo ""
echo "✅ Configuration terminée !"
echo ""
echo "📦 Prêt pour le transfert vers le serveur."