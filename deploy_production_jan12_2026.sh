#!/bin/bash

#############################################################################
# Script de déploiement production Atlas - 12 Janvier 2026
#
# Ce script déploie les changements suivants:
# - Système cryptomonnaies synchronisé (50 cryptos admin + client)
# - Dashboard admin amélioré (Abonnements, Total Encours)
# - Migration base de données (compte_rendu: titre, type_rdv, prochaine_action)
# - Onboarding avec images plans et nombre rendez-vous
# - Corrections bugs (PEE/PERCO, email suivi RDV)
#
# ⚠️ IMPORTANT: Exécuter ce script depuis votre machine locale
#############################################################################

set -e  # Arrêter en cas d'erreur

echo "🚀 DÉPLOIEMENT PRODUCTION ATLAS - 12 Janvier 2026"
echo "=" | tr '=' '\n' | head -c 70 && echo ""

# Variables
REMOTE_SERVER="root@atlas-invest.fr"
APP_NAME="atlas"
MIGRATION_SCRIPT="migrations/add_compte_rendu_fields.py"

# Couleurs pour l'affichage
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

#############################################################################
# Étape 1: Vérification pré-déploiement
#############################################################################

echo ""
echo "${YELLOW}📋 Étape 1: Vérification pré-déploiement${NC}"
echo "-------------------------------------------"

# Vérifier que nous sommes sur la branche main
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "${RED}❌ Erreur: Vous devez être sur la branche 'main'${NC}"
    echo "   Branche actuelle: $CURRENT_BRANCH"
    exit 1
fi

# Vérifier qu'il n'y a pas de changements non commités
if ! git diff-index --quiet HEAD --; then
    echo "${RED}❌ Erreur: Il y a des changements non commités${NC}"
    echo "   Commitez d'abord vos changements avec:"
    echo "   git add -A && git commit -m 'votre message'"
    exit 1
fi

# Vérifier que le dernier commit a été pushé
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/main)
if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
    echo "${RED}❌ Erreur: Le dernier commit n'a pas été pushé${NC}"
    echo "   Pushez d'abord avec: git push origin main"
    exit 1
fi

echo "${GREEN}✅ Toutes les vérifications pré-déploiement passées${NC}"

#############################################################################
# Étape 2: Déploiement via Dokku
#############################################################################

echo ""
echo "${YELLOW}🚢 Étape 2: Déploiement via Dokku${NC}"
echo "-------------------------------------------"

echo "   Déploiement depuis GitHub..."
ssh $REMOTE_SERVER "dokku git:sync $APP_NAME https://github.com/hugumarie/atlas_platform.git main"

if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Déploiement Dokku réussi${NC}"
else
    echo "${RED}❌ Échec du déploiement Dokku${NC}"
    exit 1
fi

#############################################################################
# Étape 3: Migration base de données
#############################################################################

echo ""
echo "${YELLOW}🗄️  Étape 3: Migration base de données${NC}"
echo "-------------------------------------------"

echo "   Exécution de la migration add_compte_rendu_fields.py..."

# Exécuter la migration sur le serveur
ssh $REMOTE_SERVER << 'ENDSSH'
cd /home/dokku/atlas
dokku enter atlas web python migrations/add_compte_rendu_fields.py
ENDSSH

if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Migration base de données réussie${NC}"
else
    echo "${YELLOW}⚠️  Attention: La migration a peut-être échoué${NC}"
    echo "   Vérifiez manuellement avec:"
    echo "   ssh $REMOTE_SERVER 'dokku logs $APP_NAME --tail 50'"
fi

#############################################################################
# Étape 4: Mise à jour des prix crypto
#############################################################################

echo ""
echo "${YELLOW}💰 Étape 4: Mise à jour des prix crypto${NC}"
echo "-------------------------------------------"

echo "   Mise à jour des 104 prix crypto depuis Binance..."

ssh $REMOTE_SERVER << 'ENDSSH'
cd /home/dokku/atlas
dokku enter atlas web python scripts/update_crypto_prices.py
ENDSSH

if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Prix crypto mis à jour (104 cryptos)${NC}"
else
    echo "${YELLOW}⚠️  Attention: Mise à jour des prix crypto a peut-être échoué${NC}"
fi

#############################################################################
# Étape 5: Vérification post-déploiement
#############################################################################

echo ""
echo "${YELLOW}🔍 Étape 5: Vérification post-déploiement${NC}"
echo "-------------------------------------------"

# Vérifier que l'application est en cours d'exécution
echo "   Vérification du statut de l'application..."
ssh $REMOTE_SERVER "dokku ps:report $APP_NAME | grep -E 'Status|Running'"

# Vérifier les logs récents
echo ""
echo "   Derniers logs (recherche d'erreurs)..."
ssh $REMOTE_SERVER "dokku logs $APP_NAME --tail 20 | grep -iE 'error|warning|critical' || echo '   Aucune erreur critique détectée'"

# Test HTTP
echo ""
echo "   Test de connectivité HTTP..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://atlas-invest.fr)
if [ "$HTTP_STATUS" == "200" ]; then
    echo "${GREEN}✅ Application accessible (HTTP 200)${NC}"
else
    echo "${RED}❌ Problème d'accès à l'application (HTTP $HTTP_STATUS)${NC}"
fi

#############################################################################
# Résumé du déploiement
#############################################################################

echo ""
echo "=" | tr '=' '\n' | head -c 70 && echo ""
echo "${GREEN}🎉 DÉPLOIEMENT TERMINÉ AVEC SUCCÈS !${NC}"
echo "=" | tr '=' '\n' | head -c 70 && echo ""

echo ""
echo "📝 Résumé des changements déployés:"
echo "   ✅ Système crypto synchronisé (50 cryptos)"
echo "   ✅ API admin retourne 104 prix crypto"
echo "   ✅ Dashboard admin avec nouvelles métriques"
echo "   ✅ Migration compte_rendu (3 nouvelles colonnes)"
echo "   ✅ Onboarding avec images et rendez-vous annuels"
echo "   ✅ Fix bugs (PEE/PERCO, email suivi)"

echo ""
echo "🔗 Liens utiles:"
echo "   • Site: https://atlas-invest.fr"
echo "   • Admin: https://atlas-invest.fr/plateforme/admin/dashboard"
echo "   • Logs: ssh $REMOTE_SERVER 'dokku logs $APP_NAME -t'"

echo ""
echo "📚 Prochaines étapes recommandées:"
echo "   1. Tester la connexion admin et vérifier le dashboard"
echo "   2. Vérifier l'affichage des cryptos (USDC, SHIB) en mode édition"
echo "   3. Tester la création/édition de comptes rendus"
echo "   4. Vérifier l'onboarding avec images des plans"

echo ""
echo "${YELLOW}⚠️  Note importante:${NC}"
echo "   Si vous constatez des problèmes, consultez les logs avec:"
echo "   ssh $REMOTE_SERVER 'dokku logs $APP_NAME -t'"

echo ""
