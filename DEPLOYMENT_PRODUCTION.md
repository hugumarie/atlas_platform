# 🚀 Déploiement Production Atlas - Version Corrigée

Guide complet pour déployer la nouvelle version d'Atlas avec toutes les corrections Stripe et UX.

## 📋 Prérequis

### Variables d'environnement Stripe requises

Tu devras configurer ces variables sur le serveur Dokku :

```bash
# Configuration Stripe (REMPLACER par tes vraies clés de production)
dokku config:set atlas STRIPE_SECRET_KEY="sk_live_..." 
dokku config:set atlas STRIPE_PUBLISHABLE_KEY="pk_live_..."
dokku config:set atlas STRIPE_WEBHOOK_SECRET="whsec_..."

# Price IDs Stripe pour les plans
dokku config:set atlas STRIPE_PRICE_INITIA="price_..." 
dokku config:set atlas STRIPE_PRICE_OPTIMA="price_..."
dokku config:set atlas STRIPE_PRICE_MAXIMA="price_..."

# Configuration site (adapter selon ton domaine)
dokku config:set atlas SITE_URL="https://atlas-invest.fr"
dokku config:set atlas STRIPE_SUCCESS_URL="https://atlas-invest.fr/plateforme/dashboard"
dokku config:set atlas STRIPE_CANCEL_URL="https://atlas-invest.fr/onboarding/plan"
```

## 🗄️ État de la Base de Données

La migration automatique ajoutera ces nouvelles tables/colonnes :

1. **Colonnes calculées** sur `investor_profiles` :
   - `calculated_patrimoine_total_net`
   - `calculated_total_liquidites`  
   - `calculated_total_placements`
   - `calculated_total_immobilier_net`
   - `calculated_total_cryptomonnaies`
   - `calculated_total_autres_biens`
   - `last_calculation_date`

2. **Tables de plans d'investissement** :
   - `investment_plans`
   - `investment_plan_lines`

3. **Table d'actions** :
   - `investment_actions`

## 🚀 Procédure de Déploiement

### 1. Connexion au serveur

```bash
# Connexion SSH au serveur
ssh root@167.172.108.93
```

### 2. Vérification de l'état actuel

```bash
# Vérifier l'application existante
dokku apps:list

# Vérifier la base de données
dokku postgres:list

# Backup de sécurité avant déploiement
dokku postgres:backup atlas-db backup-$(date +%Y%m%d-%H%M%S)
```

### 3. Configuration des variables d'environnement Stripe

```bash
# IMPORTANT: Remplacer par tes vraies clés Stripe de production !

# Clés Stripe principales
dokku config:set atlas STRIPE_SECRET_KEY="sk_live_VOTRE_CLE_SECRETE"
dokku config:set atlas STRIPE_PUBLISHABLE_KEY="pk_live_VOTRE_CLE_PUBLIQUE" 
dokku config:set atlas STRIPE_WEBHOOK_SECRET="whsec_VOTRE_SECRET_WEBHOOK"

# Price IDs des plans (récupérer depuis Stripe Dashboard)
dokku config:set atlas STRIPE_PRICE_INITIA="price_VOTRE_PRICE_ID_INITIA"
dokku config:set atlas STRIPE_PRICE_OPTIMA="price_VOTRE_PRICE_ID_OPTIMA"
dokku config:set atlas STRIPE_PRICE_MAXIMA="price_VOTRE_PRICE_ID_MAXIMA"

# Configuration URLs
dokku config:set atlas SITE_URL="https://atlas-invest.fr"

# Autres variables importantes  
dokku config:set atlas SECRET_KEY="$(openssl rand -base64 32)"
dokku config:set atlas FLASK_ENV="production"

# Configuration email (optionnel)
dokku config:set atlas MAILERSEND_API_TOKEN="mlsn.VOTRE_TOKEN" 

# Vérifier la configuration
dokku config atlas
```

### 4. Déploiement depuis ta machine locale

```bash
# Revenir sur ta machine locale
cd "/Users/huguesmarie/Documents/Jepargne digital"

# Vérifier que les modifications sont commitées
git status
git log --oneline -3

# Ajouter le remote Dokku si pas déjà fait
git remote add dokku dokku@167.172.108.93:atlas

# OU mettre à jour s'il existe déjà
git remote set-url dokku dokku@167.172.108.93:atlas

# Déployer la nouvelle version
git push dokku main
```

### 5. Surveillance du déploiement

```bash
# (Sur le serveur) Suivre les logs en temps réel
dokku logs atlas --tail

# Le script release.sh va :
# 1. Créer/migrer toutes les tables automatiquement
# 2. Ajouter les colonnes calculées manquantes
# 3. Créer le compte admin par défaut
# 4. Mettre à jour les prix crypto si configuré
```

## ✅ Vérifications Post-Déploiement

### 1. Test de base

```bash
# Vérifier que l'app fonctionne
curl -I https://atlas-invest.fr

# Vérifier les logs
dokku logs atlas --tail
```

### 2. Test Stripe

1. Aller sur `https://atlas-invest.fr/onboarding/plan`
2. Sélectionner un plan (INITIA ou OPTIMA)
3. Vérifier que le checkout Stripe se charge sans erreur
4. **Ne pas finaliser le paiement** (test uniquement)

### 3. Test du dashboard

1. Connexion admin : `https://atlas-invest.fr/plateforme/login`
   - Email : `admin@atlas.fr`
   - Mot de passe : `Atlas2024!`

2. Vérifier que le dashboard charge sans erreurs

### 4. Vérification base de données

```bash
# Connexion à PostgreSQL
dokku postgres:connect atlas-db

# Vérifier les nouvelles tables
\dt

# Vérifier les nouvelles colonnes
\d investor_profiles

# Quitter
\q
```

## 🔧 Résolution de Problèmes

### Si l'application ne démarre pas

```bash
# Logs détaillés
dokku logs atlas --tail -t

# Redéploiement forcé
git push dokku main --force

# Rebuild complet  
dokku ps:rebuild atlas
```

### Si erreurs Stripe

```bash
# Vérifier configuration Stripe
dokku config atlas | grep STRIPE

# Tester les clés depuis le serveur
dokku run atlas python3 -c "
import stripe, os
stripe.api_key = os.environ['STRIPE_SECRET_KEY']
print('Stripe OK:', stripe.Account.retrieve())
"
```

### Si problèmes de base de données

```bash
# Vérifier la connexion
dokku postgres:connect atlas-db

# Recréer la liaison si nécessaire
dokku postgres:unlink atlas-db atlas
dokku postgres:link atlas-db atlas

# Redémarrer l'app
dokku ps:restart atlas
```

## 📊 Monitoring Post-Production

```bash
# Surveiller les performances
dokku ps:report atlas

# Logs d'erreurs seulement
dokku logs atlas --tail | grep -i error

# Statistiques PostgreSQL
dokku postgres:info atlas-db
```

## 🎯 Nouvelles Fonctionnalités Déployées

Cette version inclut :

✅ **Corrections Stripe majeures**
- Gestion MAXIMA plan fixée
- Webhook processing robuste
- Fallback automatique pour échecs de webhook

✅ **UX simplifiée**  
- Questionnaire supprimé
- Accès direct au dashboard après paiement
- Suppression des messages de blocage

✅ **Gestion d'accès améliorée**
- Exception "recent client" 24h
- Access libre aux pages apprentissage/assistant
- Gestion gracieuse des profils manquants

✅ **Email automatique**
- Email de bienvenue après paiement
- Intégration MailerSend

---

## 🆘 En cas de problème critique

1. **Rollback rapide** :
```bash
# Revenir à la version précédente
dokku ps:stop atlas
dokku postgres:restore atlas-db backup-DERNIERE-DATE
git reset --hard HEAD~1
git push dokku main --force
```

2. **Contact support** :
   - Logs complets : `dokku logs atlas --tail > debug.log`
   - Configuration : `dokku config atlas > config.txt`
   - État base de données : `dokku postgres:info atlas-db`

**✨ Déploiement réussi = Plateforme Atlas pleinement fonctionnelle en production !**