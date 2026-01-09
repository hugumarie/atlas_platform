#!/bin/bash

echo "🧪 Test des services Atlas Production"
echo "======================================"

# Créer le script Python sur le serveur
ssh dokku@167.172.108.93 'echo "
import requests
import os
import json

print(\"🔧 Test Configuration\")
print(\"=====================\")

# Test MailerSend
mailersend_token = os.getenv(\"MAILERSEND_API_TOKEN\")
from_email = os.getenv(\"FROM_EMAIL\", \"noreply@atlas-invest.fr\")
openai_key = os.getenv(\"OPENAI_API_KEY\")

print(f\"MailerSend Token: {mailersend_token[:15] if mailersend_token else \'MANQUANT\'}...\")
print(f\"From Email: {from_email}\")
print(f\"OpenAI Key: {openai_key[:15] if openai_key else \'MANQUANT\'}...\")
print()

# Test 1: MailerSend
print(\"📧 Test MailerSend\")
print(\"-\" * 20)

if not mailersend_token:
    print(\"❌ Token MailerSend manquant\")
else:
    email_data = {
        \"from\": {\"email\": from_email, \"name\": \"Atlas Test\"},
        \"to\": [{\"email\": \"hugues.marie925@gmail.com\", \"name\": \"Test Production\"}],
        \"subject\": \"🚀 Test Atlas Production\",
        \"text\": \"Test email depuis production Atlas\"
    }
    
    headers = {
        \"Authorization\": f\"Bearer {mailersend_token}\",
        \"Content-Type\": \"application/json\"
    }
    
    try:
        response = requests.post(\"https://api.mailersend.com/v1/email\", 
                               json=email_data, headers=headers, timeout=30)
        print(f\"Status: {response.status_code}\")
        print(f\"Response: {response.text}\")
        
        if response.status_code == 202:
            print(\"✅ MailerSend: EMAIL ENVOYÉ!\")
        else:
            print(f\"❌ MailerSend: Échec {response.status_code}\")
    except Exception as e:
        print(f\"❌ MailerSend Error: {e}\")

print()

# Test 2: OpenAI
print(\"🤖 Test OpenAI\")
print(\"-\" * 15)

if not openai_key:
    print(\"❌ Clé OpenAI manquante\")
else:
    openai_data = {
        \"model\": \"gpt-3.5-turbo\",
        \"messages\": [{\"role\": \"user\", \"content\": \"Dis juste 'Test OK' si tu reçois ce message\"}],
        \"max_tokens\": 10
    }
    
    headers = {
        \"Authorization\": f\"Bearer {openai_key}\",
        \"Content-Type\": \"application/json\"
    }
    
    try:
        response = requests.post(\"https://api.openai.com/v1/chat/completions\",
                               json=openai_data, headers=headers, timeout=30)
        print(f\"Status: {response.status_code}\")
        
        if response.status_code == 200:
            result = response.json()
            message = result.get(\"choices\", [{}])[0].get(\"message\", {}).get(\"content\", \"Pas de réponse\")
            print(f\"✅ OpenAI: {message}\")
        else:
            print(f\"❌ OpenAI: Échec {response.status_code}\")
            print(f\"Response: {response.text}\")
    except Exception as e:
        print(f\"❌ OpenAI Error: {e}\")

print()
print(\"🏁 Test terminé\")
" > test_services.py && python3 test_services.py'

echo "✅ Test des services terminé"