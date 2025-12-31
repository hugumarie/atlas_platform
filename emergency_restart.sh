#!/bin/bash

echo "🚨 Script de redémarrage d'urgence Atlas"
echo "========================================"

echo "🔄 1. Redémarrage de l'application..."
ssh dokku@167.172.108.93 "ps:restart atlas"

echo ""
echo "⏳ 2. Attente de 30 secondes..."
sleep 30

echo ""
echo "🔍 3. Vérification du statut après redémarrage..."
ssh dokku@167.172.108.93 "ps:report atlas"

echo ""
echo "🌐 4. Test de connectivité..."
curl -I --connect-timeout 10 https://atlas-invest.fr

echo ""
echo "📋 5. Logs post-redémarrage..."
ssh dokku@167.172.108.93 "logs atlas --tail 20"

echo ""
echo "🎯 Si ça ne fonctionne toujours pas:"
echo "1. Vérifier les logs: ssh dokku@167.172.108.93 'logs atlas --tail 50'"
echo "2. Reconstruire: ssh dokku@167.172.108.93 'ps:rebuild atlas'"