#!/usr/bin/env python3
"""
Debug: Vérifier la config MailerSend dans Flask
"""

import os
from dotenv import load_dotenv

# Force le rechargement du .env
load_dotenv(override=True)

print("🔍 DEBUG MAILERSEND CONFIG")
print("=========================")
print()

# Vérifier le token
token = os.getenv('MAILERSEND_API_TOKEN')
print(f"Token lu: {token[:20] if token else 'None'}...")

# Test direct
if token:
    import requests
    response = requests.get(
        "https://api.mailersend.com/v1/domains",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Test API: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Token valide")
    else:
        print("❌ Token invalide")
        print(f"Erreur: {response.text}")
else:
    print("❌ Token manquant")

print()
print("💡 Solution: Redémarrer Flask complètement pour recharger .env")