# 🚀 Guide de Déploiement Production - Atlas Invest

**Version du commit à déployer :** `72bc679` - Major Fix: Résolution complète problèmes Stripe + Onboarding + UX

## 📋 Pré-requis avant déploiement

### 1. Sauvegarde Base de Données Production
```bash
# Connexion au serveur de production
ssh root@atlas-invest.fr

# Sauvegarde complète de la base de données
pg_dump -h localhost -U atlas_user atlas_production > /backup/atlas_backup_$(date +%Y%m%d_%H%M%S).sql

# Vérifier la sauvegarde
ls -la /backup/atlas_backup_*.sql
```

### 2. Variables d'Environnement Stripe
Avant le déploiement, s'assurer que ces variables sont configurées en production :
```bash
# Dans /var/www/atlas/.env.stripe (PRODUCTION)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_INITIA=price_...
STRIPE_PRICE_OPTIMA=price_...
STRIPE_PRICE_MAXIMA=price_...
STRIPE_SUCCESS_URL=https://www.atlas-invest.fr/plateforme/dashboard
STRIPE_CANCEL_URL=https://www.atlas-invest.fr/onboarding/plan
```

## 🔄 Procédure de Déploiement

### Étape 1: Push du Code
```bash
# Depuis le local (MacBook)
cd "/Users/huguesmarie/Documents/Jepargne digital"

# Vérifier le commit à déployer
git log --oneline -3

# Pousser vers la production (si repository distant configuré)
git push origin main
```

### Étape 2: Mise à Jour Serveur Production
```bash
# Connexion serveur production
ssh root@atlas-invest.fr

# Aller dans le répertoire de l'application
cd /var/www/atlas/

# Sauvegarder la version actuelle
cp -r . ../atlas_backup_$(date +%Y%m%d_%H%M%S)/

# Récupérer les derniers changements
git fetch origin
git reset --hard 72bc679

# OU si pas de git distant, transfert manuel :
# scp -r "/Users/huguesmarie/Documents/Jepargne digital/*" root@atlas-invest.fr:/var/www/atlas/
```

### Étape 3: Mise à Jour Base de Données

#### A. Vérification Structure Actuelle
```sql
-- Connexion à la base de production
psql -h localhost -U atlas_user -d atlas_production

-- Vérifier les tables existantes
\dt

-- Vérifier la structure investor_profiles
\d investor_profiles

-- Vérifier les contraintes
SELECT constraint_name, check_clause 
FROM information_schema.check_constraints 
WHERE constraint_name LIKE '%investment_horizon%' OR constraint_name LIKE '%risk_tolerance%';
```

#### B. Migrations Nécessaires

```sql
-- 1. Vérifier si la table investment_actions existe
SELECT EXISTS (
   SELECT FROM information_schema.tables 
   WHERE table_name = 'investment_actions'
);

-- 2. Si elle n'existe pas, la créer
CREATE TABLE IF NOT EXISTS investment_actions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    year_month VARCHAR(7) NOT NULL, -- Format YYYY-MM
    support_type VARCHAR(50) NOT NULL,
    label VARCHAR(200) NOT NULL,
    expected_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    notes TEXT
);

-- 3. Créer l'index pour les performances
CREATE INDEX IF NOT EXISTS idx_investment_actions_user_month ON investment_actions(user_id, year_month);
CREATE INDEX IF NOT EXISTS idx_investment_actions_status ON investment_actions(status);

-- 4. Vérifier les contraintes investor_profiles
-- Si les contraintes sont trop restrictives, les ajuster
ALTER TABLE investor_profiles 
DROP CONSTRAINT IF EXISTS chk_investment_horizon;

ALTER TABLE investor_profiles 
ADD CONSTRAINT chk_investment_horizon 
CHECK (investment_horizon IN ('court', 'court terme', 'moyen', 'moyen terme', 'long', 'long terme'));

ALTER TABLE investor_profiles 
DROP CONSTRAINT IF EXISTS chk_risk_tolerance;

ALTER TABLE investor_profiles 
ADD CONSTRAINT chk_risk_tolerance 
CHECK (risk_tolerance IN ('conservateur', 'conservatrice', 'modéré', 'modérée', 'modere', 'moderee', 'dynamique', 'agressif', 'agressive'));
```

#### C. Correction Données Utilisateurs Existants
```sql
-- Corriger les profils existants qui pourraient avoir des valeurs non conformes
UPDATE investor_profiles 
SET investment_horizon = 'court terme' 
WHERE investment_horizon = 'court_terme' OR investment_horizon IS NULL;

UPDATE investor_profiles 
SET risk_tolerance = 'conservateur' 
WHERE risk_tolerance = 'non_defini' OR risk_tolerance IS NULL;

-- Vérifier les utilisateurs sans profil investisseur
SELECT u.id, u.email, u.first_name, u.last_name 
FROM users u 
LEFT JOIN investor_profiles ip ON u.id = ip.user_id 
WHERE ip.id IS NULL AND u.user_type = 'client';
```

### Étape 4: Installation Dépendances
```bash
# Sur le serveur de production
cd /var/www/atlas/

# Activer l'environnement virtuel
source venv/bin/activate

# Installer nouvelles dépendances si nécessaire
pip install -r requirements.txt

# Vérifier les packages critiques
pip show stripe flask-login sqlalchemy psycopg2-binary
```

### Étape 5: Configuration Stripe Production
```bash
# Vérifier la configuration Stripe
cd /var/www/atlas/

# Tester la connexion Stripe
python3 -c "
import stripe
import os
from dotenv import load_dotenv
load_dotenv('.env.stripe')
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
print('Stripe configuré:', stripe.api_key[:12] + '...' if stripe.api_key else 'ERREUR')
try:
    prices = stripe.Price.list(limit=3)
    print('Connexion Stripe OK - Prices trouvés:', len(prices.data))
except Exception as e:
    print('ERREUR Stripe:', e)
"
```

### Étape 6: Redémarrage Services
```bash
# Redémarrer l'application
systemctl restart atlas-app

# Ou si utilisation de gunicorn
pkill -f gunicorn
cd /var/www/atlas/
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 run:app &

# Redémarrer nginx
systemctl restart nginx

# Vérifier les services
systemctl status atlas-app
systemctl status nginx
```

## ✅ Tests Post-Déploiement

### 1. Tests Fonctionnels Critiques
```bash
# Tester la page d'accueil
curl -I https://www.atlas-invest.fr/

# Tester la connexion
curl -I https://www.atlas-invest.fr/plateforme/connexion

# Tester l'API Stripe (depuis le serveur)
curl -I https://www.atlas-invest.fr/onboarding/stripe/create-session
```

### 2. Tests Interface Utilisateur
- [ ] ✅ Inscription nouveau client avec paiement Stripe
- [ ] ✅ Connexion client existant (Victor) sans boucle
- [ ] ✅ Accès dashboard avec valeurs patrimoniales correctes  
- [ ] ✅ Navigation toutes pages sans blocage profil
- [ ] ✅ Création automatique profil investisseur
- [ ] ✅ Email de bienvenue envoyé

### 3. Tests Base de Données
```sql
-- Vérifier que les nouveaux utilisateurs peuvent se connecter
SELECT u.id, u.email, u.created_at, s.status, s.tier 
FROM users u 
LEFT JOIN subscriptions s ON u.id = s.user_id 
WHERE u.created_at > '2025-12-29' 
ORDER BY u.created_at DESC;

-- Vérifier les profils créés automatiquement
SELECT ip.id, ip.user_id, ip.monthly_net_income, ip.risk_tolerance, ip.investment_horizon
FROM investor_profiles ip 
JOIN users u ON ip.user_id = u.id
WHERE u.created_at > '2025-12-29';
```

## 🚨 Rollback si Problème

En cas de problème critique :

```bash
# 1. Restaurer la sauvegarde de l'application
cd /var/www/
rm -rf atlas/
mv atlas_backup_YYYYMMDD_HHMMSS/ atlas/

# 2. Restaurer la base de données
psql -h localhost -U atlas_user -d atlas_production < /backup/atlas_backup_YYYYMMDD_HHMMSS.sql

# 3. Redémarrer les services
systemctl restart atlas-app nginx

# 4. Vérifier que tout fonctionne
curl -I https://www.atlas-invest.fr/plateforme/connexion
```

## 📊 Monitoring Post-Déploiement

### Logs à Surveiller
```bash
# Logs application
tail -f /var/log/atlas/application.log

# Logs nginx
tail -f /var/log/nginx/atlas_access.log
tail -f /var/log/nginx/atlas_error.log

# Logs PostgreSQL
tail -f /var/log/postgresql/postgresql-*.log

# Surveiller les erreurs Stripe
grep -i "stripe\|payment" /var/log/atlas/application.log
```

### Métriques Critiques
- [ ] Taux de réussite des paiements Stripe
- [ ] Temps de réponse pages principales
- [ ] Erreurs 500 (doivent être à 0)
- [ ] Création réussie nouveaux comptes
- [ ] Emails de bienvenue envoyés

## 📝 Checklist Finale

### Avant Déploiement
- [ ] ✅ Sauvegarde base de données créée
- [ ] ✅ Variables Stripe production configurées
- [ ] ✅ Code local complètement testé
- [ ] ✅ Commit 72bc679 validé

### Pendant Déploiement  
- [ ] ✅ Code poussé sur serveur production
- [ ] ✅ Migrations base de données exécutées
- [ ] ✅ Dépendances mises à jour
- [ ] ✅ Services redémarrés proprement

### Après Déploiement
- [ ] ✅ Tests fonctionnels passent
- [ ] ✅ Aucune erreur dans les logs
- [ ] ✅ Stripe fonctionne correctement
- [ ] ✅ Emails envoyés automatiquement
- [ ] ✅ Utilisateurs existants non impactés

---

## 🎯 Objectif

Ce déploiement apporte :
- **Stabilité** : Fin des boucles de redirection et erreurs Stripe
- **UX améliorée** : Onboarding fluide pour nouveaux clients
- **Robustesse** : Gestion d'erreurs et fallbacks partout
- **Fonctionnalités** : Email automatique, profils auto-créés

**Fenêtre de maintenance recommandée :** 15-30 minutes en heures creuses

**Contact support :** hugues.marie925@gmail.com

---
*Documentation créée le 30 Décembre 2024 - Version 1.0*