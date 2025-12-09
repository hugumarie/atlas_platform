# 🚀 COMMANDES POUR RELANCER LA PLATEFORME

## 1️⃣ ARRÊTER LE SERVEUR ACTUEL
- Appuyez sur `Ctrl+C` dans le terminal où Flask tourne

## 2️⃣ RELANCER LA PLATEFORME
```bash
cd "/Users/huguesmarie/Documents/Jepargne digital"
python app.py
```

## 3️⃣ MISE À JOUR DES PRIX CRYPTO

### Commande simple (recommandée):
```bash
python -c "from app import create_app; from app.services.binance_price_service import BinancePriceService; app = create_app(); app.app_context().push(); BinancePriceService.update_crypto_prices_in_db(); print('✅ Prix crypto mis à jour')"
```

### Si un script dédié existe:
```bash
python scripts/update_crypto_prices.py
```

## 4️⃣ VÉRIFICATION
- **Plateforme:** http://127.0.0.1:5001
- **Page admin:** http://127.0.0.1:5001/plateforme/admin/utilisateur/2

## 💡 Notes importantes
- Les prix crypto sont automatiquement mis à jour toutes les 5 minutes pendant les calculs patrimoniaux
- Le système utilise maintenant les calculs d'amortissement corrects (36,381€ au lieu de 37,118€)
- Toutes les valeurs JavaScript incorrectes ont été désactivées