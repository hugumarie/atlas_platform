import os
import requests

print("Test Stripe Production")
print("=====================")

stripe_key = os.getenv("STRIPE_SECRET_KEY")
if not stripe_key:
    print("ERREUR: STRIPE_SECRET_KEY manquante")
    exit(1)

print(f"Clé trouvée: {stripe_key[:15]}...")

headers = {"Authorization": f"Bearer {stripe_key}"}

try:
    print("Test API Stripe...")
    response = requests.get("https://api.stripe.com/v1/balance", headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ API Stripe fonctionne!")
    else:
        print(f"❌ Erreur: {response.text}")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    
# Test des prix
price_initia = os.getenv("STRIPE_PRICE_INITIA")
print(f"Prix INITIA: {price_initia}")

if price_initia:
    try:
        response = requests.get(f"https://api.stripe.com/v1/prices/{price_initia}", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Prix INITIA valide")
        else:
            print(f"❌ Prix invalide: {response.status_code}")
    except:
        print("❌ Erreur test prix")