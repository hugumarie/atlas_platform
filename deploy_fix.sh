#!/bin/bash

echo "🔧 Script de correction et déploiement Atlas"
echo "============================================="

# 1. Vérifier les fichiers à committer (sans les secrets)
echo "🔍 1. Vérification des fichiers à sauvegarder..."
echo "Fichiers modifiés (sans secrets):"
git status --porcelain | grep -v -E "(\.env|test_.*\.py|configure_dokku|_simple\.py)" || echo "Aucun fichier sécurisé à committer"

echo ""
echo "❌ Fichiers EXCLUS de la sauvegarde (contiennent des secrets):"
git status --porcelain | grep -E "(\.env|test_.*\.py|configure_dokku|_simple\.py)" || echo "Aucun fichier avec secrets détecté"

echo ""
read -p "🔒 Confirmer la sauvegarde sans les secrets? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Sauvegarde annulée"
    exit 1
fi

# 2. Sauvegarder les modifications (sans secrets)
echo "📦 2. Sauvegarde du code (sans fichiers secrets)..."
git add app/ templates/ static/ *.md *.txt requirements.txt Procfile runtime.txt .gitignore
git add deploy_fix.sh check_status.sh emergency_restart.sh

git commit -m "🔧 Fix: Amélioration gestion erreurs OpenAI Chat API

- Meilleur message d'erreur pour clé API invalide
- Gestion des erreurs 401 dans le chat
- Scripts de déploiement et diagnostic
- Exclusion des fichiers avec secrets

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "✅ Code sauvegardé localement (sans secrets)"

# 2. Pousser sur GitHub
echo "📤 2. Push vers GitHub..."
git push origin main
echo "✅ Code poussé sur GitHub"

# 3. Déployer sur le serveur Dokku
echo "🚀 3. Déploiement sur Dokku..."
git push dokku main

echo ""
echo "⏳ Attendre le déploiement..."
sleep 10

# 4. Vérifier le statut
echo "🔍 4. Vérification du statut..."
ssh dokku@167.172.108.93 "ps:report atlas"

# 5. Vérifier les logs récents
echo "📋 5. Logs récents..."
ssh dokku@167.172.108.93 "logs atlas --tail 20"

echo ""
echo "🎉 Script de déploiement terminé!"
echo "🌐 Testez sur: https://atlas-invest.fr"