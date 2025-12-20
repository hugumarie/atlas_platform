# 🚀 Atlas Crypto Price System

## 📋 Vue d'ensemble

Le système de prix crypto d'Atlas utilise l'API Binance pour récupérer les prix en temps réel des 50 principales cryptomonnaies (incluant stablecoins) et les stocke en base de données PostgreSQL pour des performances optimales.

## 🔄 Intégration au démarrage

### **Script de lancement `start_atlas.sh`**
```bash
./start_atlas.sh
```

**Séquence automatique :**
1. ✅ Vérification et démarrage PostgreSQL
2. ✅ **Refresh automatique des prix crypto** via `refresh_crypto_prices.py`
3. ✅ Chargement des 50 cryptos depuis l'API Binance
4. ✅ Sauvegarde en base de données (format EUR)
5. ✅ Démarrage de l'application Flask avec prix à jour

### **Double protection du chargement crypto**
- **Niveau 1**: Script `refresh_crypto_prices.py` dans `start_atlas.sh`
- **Niveau 2**: Vérification automatique dans `app/__init__.py` si lancé autrement
- **Fallback**: API crypto rechargera les prix si besoin dans l'interface

## 📡 API pour l'interface d'édition

### Route `/plateforme/api/crypto-prices`
- ✅ Retourne tous les prix disponibles en format JSON
- ✅ Auto-refresh si moins de 40 cryptos récents (<60min)  
- ✅ Format: `{"bitcoin": {"price": 75000.123, "eur": 75000.123, "age_minutes": 5}}`

### Interface utilisateur
- ✅ Liste complète des Top 50 cryptos par capitalisation boursière
- ✅ Calculs temps réel: quantité × prix = valeur détenue
- ✅ Total crypto automatique  
- ✅ Boutons de suppression fonctionnels (event delegation)

## 📊 Top 50 Cryptomonnaies supportées

Toutes vérifiées compatibles avec l'API Binance :

1. Bitcoin (BTC) ✅
2. Ethereum (ETH) ✅
3. Tether (USDT) ✅
4. BNB (BNB) ✅
5. Solana (SOL) ✅
6. USDC (USDC) ✅
7. XRP (XRP) ✅
8. Dogecoin (DOGE) ✅
9. Cardano (ADA) ✅
10. TRON (TRX) ✅
... et 40 autres cryptos incluant stablecoins

## 🛠️ Scripts utilitaires

### `refresh_crypto_startup.py`
```bash
python refresh_crypto_startup.py
```
- Force la mise à jour des prix crypto au démarrage
- Peut être utilisé avec un cron job ou systemd
- Retourne code 0 si succès, 1 si erreur

### Commande CLI Atlas
```bash
flask refresh_crypto_prices
```
- Commande intégrée à Flask pour mise à jour manuelle

## 🔧 Configuration technique

### Base de données
- **Table**: `crypto_prices`
- **Colonnes**: `symbol`, `price_usd`, `price_eur`, `updated_at`
- **Index**: sur `symbol` et `updated_at`

### APIs utilisées
- **Binance**: `https://api.binance.com/api/v3/ticker/price`
- **Taux change**: `https://api.exchangerate-api.com/v4/latest/USD`

### Services
- **`BinancePriceService`**: Gestion centralisée des prix
- **`CryptoPrice`**: Modèle SQLAlchemy pour stockage

## 🚨 Monitoring

### Logs de démarrage
```
✅ Atlas startup: 50 prix crypto déjà à jour
🔄 Atlas startup: Chargement des prix crypto depuis Binance...
✅ Atlas startup: 104 prix crypto chargés avec succès
```

### Vérifications API
```
✅ API: 104 prix disponibles pour l'interface
🔄 API crypto: Pas assez de prix récents (15/50), mise à jour depuis Binance...
```

## 📈 Performance

- **Démarrage à froid**: ~3-5 secondes pour charger tous les prix
- **API response**: <100ms (lecture directe en base)
- **Cache**: Prix valides 30-60min selon le contexte
- **Fallback**: Gestion d'erreur sans crash de l'application

## 🔒 Sécurité

- ✅ Aucune clé API requise (endpoints publics)
- ✅ Timeout des requêtes (10 secondes)
- ✅ Gestion d'erreur robuste
- ✅ Validation des données reçues
- ✅ Protection contre les appels API excessifs

## 🎯 Statut actuel

- **✅ 50/50 cryptos supportés**
- **✅ 4/4 stablecoins majeurs**
- **✅ API temps réel fonctionnelle**
- **✅ Interface d'édition complète**
- **✅ Chargement automatique au démarrage**

---
*Système mis à jour le 17/12/2024*