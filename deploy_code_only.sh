#!/bin/bash

echo "🚀 Déploiement code Atlas (sans secrets)"
echo "========================================"

# 1. Vérifier les fichiers à committer (sans les secrets)
echo "🔍 1. Vérification des fichiers à sauvegarder..."
echo "Fichiers modifiés (sans secrets):"
git status --porcelain | grep -v -E "(\.env|test_.*\.py|configure_dokku|_simple\.py|cookies\.txt)" || echo "Aucun fichier sécurisé à committer"

echo ""
echo "❌ Fichiers EXCLUS de la sauvegarde (contiennent des secrets):"
git status --porcelain | grep -E "(\.env|test_.*\.py|configure_dokku|_simple\.py|cookies\.txt)" || echo "Aucun fichier avec secrets détecté"

echo ""
read -p "🔒 Confirmer la sauvegarde sans les secrets? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Sauvegarde annulée"
    exit 1
fi

# 2. Sauvegarder les modifications (sans secrets)
echo "📦 2. Sauvegarde du code (sans fichiers secrets)..."
git add app/ templates/ static/ *.md requirements.txt Procfile runtime.txt .gitignore
git add deploy_*.sh check_status.sh emergency_restart.sh

# 3. Commit
git commit -m "🔧 Fix: Amélioration gestion erreurs OpenAI Chat API

- Meilleur message d'erreur pour clé API invalide (401)
- Gestion des erreurs API dans /plateforme/api/chat
- Scripts de déploiement et diagnostic
- Protection des fichiers avec secrets

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "✅ Code sauvegardé localement (sans secrets)"

# 4. Push GitHub
echo "📤 3. Push vers GitHub..."
git push origin main
echo "✅ Code poussé sur GitHub"

# 5. Push Dokku pour déploiement
echo "🚀 4. Déploiement sur Dokku (avec nouveau code)..."
git push dokku main

echo ""
echo "⏳ 5. Attendre le déploiement (60s)..."
sleep 60

# 6. Vérifier le statut
echo "🔍 6. Vérification du statut..."
ssh dokku@167.172.108.93 "ps:report atlas"

# 7. Test de connectivité
echo ""
echo "🌐 7. Test de connectivité..."
curl -I --connect-timeout 10 https://atlas-invest.fr

# 8. Logs récents
echo ""
echo "📋 8. Logs récents..."
ssh dokku@167.172.108.93 "logs atlas --tail 20"

echo ""
echo "🎉 Déploiement terminé!"
echo "🔧 Pour configurer les clés API en production:"
echo "   1. Connectez-vous sur le serveur"
echo "   2. Utilisez la console Dokku pour configurer les variables"
echo "🌐 Testez sur: https://atlas-invest.fr"