#!/bin/bash

# Script pour éditer la configuration production chiffrée
# Usage: ./edit_production_config.sh

echo "📝 Édition configuration production chiffrée..."

ENCRYPTED_FILE=".env.production.enc"
TEMP_FILE=".env.production.tmp"

# Vérifier que le fichier chiffré existe
if [[ ! -f "$ENCRYPTED_FILE" ]]; then
    echo "❌ Fichier chiffré non trouvé: $ENCRYPTED_FILE"
    echo "   Créer d'abord avec: ./setup_production_config.sh"
    exit 1
fi

echo "🔑 Déchiffrement du fichier de configuration..."

# Déchiffrer temporairement
if ! openssl enc -aes-256-cbc -d -pbkdf2 -in "$ENCRYPTED_FILE" -out "$TEMP_FILE"; then
    echo "❌ Échec du déchiffrement (mot de passe incorrect ?)"
    rm -f "$TEMP_FILE"
    exit 1
fi

echo "✅ Fichier déchiffré, ouverture dans l'éditeur..."

# Ouvrir dans l'éditeur (priorité: nano, puis vi)
if command -v nano &> /dev/null; then
    nano "$TEMP_FILE"
elif command -v vi &> /dev/null; then
    vi "$TEMP_FILE"
else
    echo "❌ Aucun éditeur trouvé (nano, vi)"
    rm -f "$TEMP_FILE"
    exit 1
fi

echo ""
echo "💾 Sauvegarde des modifications..."

# Demander confirmation avant re-chiffrement
echo "🤔 Sauvegarder les modifications ? (y/N)"
read -r save_changes

if [[ "$save_changes" =~ ^[Yy]$ ]]; then
    echo "🔐 Re-chiffrement avec le même mot de passe..."
    
    # Re-chiffrer avec le même mot de passe
    if openssl enc -aes-256-cbc -salt -pbkdf2 -in "$TEMP_FILE" -out "$ENCRYPTED_FILE"; then
        echo "✅ Configuration sauvegardée et chiffrée"
    else
        echo "❌ Erreur lors du re-chiffrement"
        echo "⚠️ Le fichier temporaire reste: $TEMP_FILE"
        exit 1
    fi
else
    echo "❌ Modifications annulées"
fi

# Nettoyer le fichier temporaire
rm -f "$TEMP_FILE"

echo ""
echo "✨ Fichier configuration prêt pour déploiement"
echo "   Déployer maintenant: ./deploy_production.sh"