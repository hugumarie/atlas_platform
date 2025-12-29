#!/usr/bin/env python3
"""
Script pour récupérer les Price IDs des produits Stripe Atlas
"""

import stripe
import os
from dotenv import load_dotenv

# Charger la configuration Stripe
load_dotenv('.env.stripe')

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def get_prices_for_products():
    """Récupère tous les Price IDs pour les produits Atlas"""
    
    product_mapping = {
        'prod_Th5YhhyDjbrAh2': 'INITIA',
        'prod_Th5UwEX4Xlh3xE': 'OPTIMA'
    }
    
    print("🔍 Récupération des Price IDs depuis Stripe...")
    print("=" * 50)
    
    try:
        for product_id, plan_name in product_mapping.items():
            print(f"\n📋 {plan_name} (Product: {product_id})")
            
            # Récupérer les prix pour ce produit
            prices = stripe.Price.list(
                product=product_id,
                active=True,
                type='recurring'
            )
            
            if prices.data:
                for price in prices.data:
                    currency = price.currency.upper()
                    amount = price.unit_amount / 100 if price.unit_amount else 0
                    interval = price.recurring.interval if price.recurring else 'N/A'
                    
                    print(f"  💰 Price ID: {price.id}")
                    print(f"     Amount: {amount} {currency}/{interval}")
                    print(f"     Created: {price.created}")
                    print(f"     Active: {price.active}")
                    
                    # Afficher les métadonnées si disponibles
                    if hasattr(price, 'metadata') and price.metadata:
                        print(f"     Metadata: {price.metadata}")
                    
                    print()
            else:
                print(f"  ❌ Aucun prix actif trouvé pour {plan_name}")
                
        print("\n" + "=" * 50)
        print("✅ Récupération terminée !")
        print("\n🔧 Configuration .env.stripe à mettre à jour :")
        print("STRIPE_PRICE_INITIA=price_xxx")
        print("STRIPE_PRICE_OPTIMA=price_xxx")
        
    except stripe.error.AuthenticationError:
        print("❌ Erreur d'authentification Stripe")
        print("Vérifiez votre clé secrète dans .env.stripe")
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")

if __name__ == "__main__":
    get_prices_for_products()