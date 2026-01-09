#!/bin/bash

echo "💳 Test API Stripe en production"
echo "================================"

echo "🧪 Test direct de l'API Stripe..."
ssh dokku@167.172.108.93 "run atlas python -c '
import requests
import os
import json

stripe_key = os.getenv(\"STRIPE_SECRET_KEY\")
print(f\"🔑 Clé secrète: {stripe_key[:15]}...\")

headers = {\"Authorization\": f\"Bearer {stripe_key}\"}

print(\"\\n📊 Test 1: Balance Stripe...\")
try:
    response = requests.get(\"https://api.stripe.com/v1/balance\", headers=headers, timeout=10)
    print(f\"Status: {response.status_code}\")
    if response.status_code == 200:
        print(\"✅ API Stripe OK!\")
    else:
        print(f\"❌ Erreur: {response.text}\")
except Exception as e:
    print(f\"❌ Erreur réseau: {e}\")

print(\"\\n💰 Test 2: Prix configurés...\")
price_initia = os.getenv(\"STRIPE_PRICE_INITIA\")
price_optima = os.getenv(\"STRIPE_PRICE_OPTIMA\")
print(f\"Price INITIA: {price_initia}\")
print(f\"Price OPTIMA: {price_optima}\")

if price_initia:
    try:
        response = requests.get(f\"https://api.stripe.com/v1/prices/{price_initia}\", headers=headers, timeout=10)
        if response.status_code == 200:
            price_data = response.json()
            amount = price_data.get(\"unit_amount\", 0) / 100
            print(f\"✅ Prix INITIA: {amount}€\")
        else:
            print(f\"❌ Prix INITIA invalide: {response.text}\")
    except Exception as e:
        print(f\"❌ Erreur prix INITIA: {e}\")

print(\"\\n🚀 Test 3: Création session checkout...\")
try:
    checkout_data = {
        \"payment_method_types[]\": \"card\",
        \"line_items[0][price]\": price_initia,
        \"line_items[0][quantity]\": 1,
        \"mode\": \"subscription\",
        \"success_url\": \"https://atlas-invest.fr/success\",
        \"cancel_url\": \"https://atlas-invest.fr/cancel\"
    }
    
    response = requests.post(\"https://api.stripe.com/v1/checkout/sessions\", 
                           data=checkout_data, headers=headers, timeout=10)
    if response.status_code == 200:
        session = response.json()
        print(f\"✅ Session créée: {session.get(\"id\", \"N/A\")}\")
    else:
        print(f\"❌ Erreur session: {response.text}\")
except Exception as e:
    print(f\"❌ Erreur création session: {e}\")
'"

echo ""
echo "🎯 Si tout fonctionne, testez sur le site :"
echo "   https://atlas-invest.fr"