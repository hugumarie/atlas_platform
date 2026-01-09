#!/bin/bash

echo "🔧 Test spécifique route create-payment-setup"
echo "============================================="

echo "🧪 Test de la route problématique..."
ssh dokku@167.172.108.93 "run atlas python -c '
from app import create_app
from app.services.stripe_service import stripe_service

app = create_app()
with app.app_context():
    print(f\"Stripe service safe_mode: {stripe_service.safe_mode}\")
    print(f\"Stripe service initialized: {stripe_service._initialized}\")
    
    # Test import stripe
    try:
        import stripe
        print(f\"✅ Module stripe importé: {stripe.__version__}\")
    except Exception as e:
        print(f\"❌ Erreur import stripe: {e}\")
    
    # Test clé API
    import os
    key = os.getenv(\"STRIPE_SECRET_KEY\")
    if key:
        print(f\"✅ STRIPE_SECRET_KEY présente: {key[:15]}...\")
        stripe.api_key = key
        
        # Test création customer
        try:
            customers = stripe.Customer.list(limit=1)
            print(f\"✅ API Stripe accessible: {len(customers.data)} customers\")
        except Exception as e:
            print(f\"❌ Erreur API Stripe: {e}\")
    else:
        print(\"❌ STRIPE_SECRET_KEY manquante\")
'"

echo ""
echo "💡 Si l'erreur persiste, vérifiez les logs en temps réel pendant le test."