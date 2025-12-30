# 🔐 Déploiement Sécurisé Atlas

Système de déploiement avec configuration **chiffrée par mot de passe**.

## 🚀 Procédure Complète (3 étapes)

### 1. Créer la configuration chiffrée
```bash
./setup_production_config.sh
```
- Crée le fichier `.env.production.enc` **chiffré**
- Te demande un **mot de passe** (mémorise-le bien !)

### 2. Configurer tes clés Stripe
```bash
./edit_production_config.sh
```
- Déchiffre temporairement le fichier
- Ouvre l'éditeur pour remplacer les clés Stripe
- Re-chiffre automatiquement après édition

**Variables à remplacer :**
- `STRIPE_SECRET_KEY=sk_live_TA_VRAIE_CLE`
- `STRIPE_PUBLISHABLE_KEY=pk_live_TA_VRAIE_CLE`
- `STRIPE_WEBHOOK_SECRET=whsec_TON_SECRET`
- `STRIPE_PRICE_INITIA=price_TON_ID_PLAN_INITIA`
- `STRIPE_PRICE_OPTIMA=price_TON_ID_PLAN_OPTIMA`
- `STRIPE_PRICE_MAXIMA=price_TON_ID_PLAN_MAXIMA`

### 3. Déployer automatiquement
```bash
./deploy_production.sh
```
- Demande ton **mot de passe** pour déchiffrer
- Envoie automatiquement toutes les variables au serveur
- Déploie avec `git push dokku main`
- Teste le déploiement automatiquement

## 🔒 Sécurité

✅ **Fichier chiffré AES-256** : `.env.production.enc`  
✅ **Pas de clés en clair** sur le disque  
✅ **Mot de passe requis** à chaque déploiement  
✅ **Nettoyage automatique** des fichiers temporaires  
✅ **Chiffrement PBKDF2** résistant aux attaques  

## 🎯 Avantages

- 🔐 **Sécurité maximale** : clés jamais stockées en clair
- ⚡ **Déploiement simple** : une commande après configuration
- 🎯 **Automatisation complète** : variables envoyées automatiquement
- 💰 **Prix crypto gratuits** : API publique Binance (pas de clés requises)
- 🔄 **Réutilisable** : configuration sauvegardée pour futurs déploiements

## 📝 Récupérer les clés Stripe

1. **Stripe Dashboard** → [https://dashboard.stripe.com](https://dashboard.stripe.com)
2. **Clés API** → Mode Live → Copier `Secret Key` et `Publishable Key`
3. **Webhooks** → Copier `Signing Secret`
4. **Produits** → Pour chaque plan → Copier le `Price ID`

## 🔧 Commandes Utiles

```bash
# Re-éditer la configuration
./edit_production_config.sh

# Voir l'état du déploiement  
ssh root@167.172.108.93 "dokku logs atlas --tail"

# Redémarrer l'application
ssh root@167.172.108.93 "dokku ps:restart atlas"

# Voir les variables configurées
ssh root@167.172.108.93 "dokku config atlas"
```

## ⚠️ Important

- **Mémorise ton mot de passe** - pas de récupération possible !
- **Backup de `.env.production.enc`** - garde une copie sécurisée
- **Ne jamais committer** le fichier `.env.production.tmp` (auto-nettoyé)

---

**✨ Configuration sécurisée, déploiement automatisé !** 🚀