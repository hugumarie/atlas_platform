# Atlas - Plateforme de Gestion de Patrimoine

## 📋 Description du Projet

**Atlas** est une plateforme web de gestion de patrimoine développée avec Flask qui permet aux investisseurs de :
- Gérer leur profil financier complet
- Visualiser leur patrimoine en temps réel
- Accéder à des plans d'investissement personnalisés
- Suivre l'évolution de leurs actifs (liquidités, placements, immobilier, cryptomonnaies)

## 🏗️ Architecture Technique

### Stack Technique
- **Backend** : Flask (Python)
- **Base de données** : PostgreSQL
- **ORM** : SQLAlchemy
- **Authentication** : Flask-Login
- **Frontend** : HTML/CSS/JavaScript + Chart.js
- **Cryptomonnaies** : API Binance pour les prix en temps réel

### Structure du Projet
```
app/
├── models/                 # Modèles SQLAlchemy
│   ├── user.py            # Utilisateurs et authentification
│   ├── investor_profile.py # Profils investisseurs
│   ├── investment_plan.py  # Plans d'investissement
│   └── crypto_price.py     # Prix cryptomonnaies
├── routes/                 # Routes Flask organisées par modules
│   ├── platform/           # Routes de la plateforme applicative
│   │   ├── auth.py         # Authentification
│   │   ├── investor.py     # Dashboard et profil investisseur
│   │   └── admin.py        # Interface administrateur
│   └── site/              # Site vitrine
├── services/              # Services métier
│   ├── patrimoine_calculation.py    # Calculs patrimoniaux
│   ├── patrimony_calculation_engine.py # Moteur de calcul V2
│   ├── binance_price_service.py     # Service prix crypto
│   └── credit_calculation.py        # Calculs de crédits
└── templates/             # Templates Jinja2
    ├── platform/          # Interface applicative
    └── site/             # Site vitrine
```

## 💾 Base de Données

### Tables Principales

#### `users`
- Gestion des comptes utilisateurs
- Authentification et autorisations
- Liens vers abonnements et profils

#### `investor_profiles`
- **Données patrimoniales** : liquidités, placements, immobilier, cryptos, autres biens
- **Colonnes calculées** : `calculated_patrimoine_total_net`, `calculated_total_*`
- **Données JSON** : immobilier détaillé, cryptomonnaies, crédits
- **Profil de risque** : tolérance, horizon, expérience

#### `investment_plans` & `investment_plan_lines`
- Plans d'investissement personnalisés
- Répartition par enveloppe (PEA, CTO, Assurance Vie...)
- Calcul automatique des montants selon capacité d'épargne

#### `crypto_prices`
- Cache des prix cryptomonnaies depuis API Binance
- Mise à jour périodique
- Optimisation des performances

## 🔧 Services et Calculs

### PatrimonyCalculationEngine V2.0
**Service principal de calcul patrimonial**
- Calcul des totaux par catégorie (liquidités, placements, immobilier net, crypto, autres biens)
- Gestion des crédits immobiliers avec capital restant dynamique
- Sauvegarde automatique des résultats en base (`calculated_*` columns)

### BinancePriceService
**Gestion des prix cryptomonnaies**
- Récupération depuis API Binance
- Cache en base de données
- Calcul des valorisations crypto en temps réel

### CreditCalculationService
**Calculs financiers précis**
- Capital restant des crédits immobiliers
- Mensualités et tableaux d'amortissement
- Prise en compte des dates réelles

## 🎯 Fonctionnalités Clés

### Dashboard Investisseur
- **Patrimoine total net** : Affichage de `calculated_patrimoine_total_net`
- **Répartition d'actifs** : Camembert interactif avec Chart.js
- **Plan d'investissement** : Visualisation des allocations
- **Objectif d'épargne annuelle** : Progression basée sur dates réelles

### Interface Admin
- Gestion des utilisateurs
- Recalculs patrimoniaux globaux
- Monitoring des prix cryptomonnaies
- Statistiques et analytics

### Système d'Abonnements
- Gestion des plans (trial, premium)
- Vérification d'accès automatique
- Intégration avec le système de paiement

## ⚠️ Points d'Attention Techniques

### Gestion des Calculs Patrimoniaux
```python
# ❌ ÉVITER : Recalculs automatiques non contrôlés
# Ces appels ont été supprimés car ils corrompaient les données :
# LocalPortfolioService.refresh_user_portfolio_at_login(user)

# ✅ RECOMMANDÉ : Lecture directe des valeurs calculées
patrimoine_total_net = profile.calculated_patrimoine_total_net
```

### Cache et Performance
- **Problème résolu** : Les valeurs `calculated_patrimoine_total_net` étaient recalculées automatiquement à la connexion (874€ au lieu de 83,523€)
- **Solution** : Suppression des hooks automatiques + lecture pure de la base de données

### Structure des Données JSON
```python
# Exemple structure immobilier_data_json
immobilier_data = [
    {
        "nom": "Appartement Paris",
        "valeur": 250000.0,
        "has_credit": True,
        "credit_montant": 215000.0,
        "credit_taux": 2.5,
        "credit_duree": 25,  # années
        "credit_date": "2024-10"  # format YYYY-MM
    }
]
```

## 🔄 Workflows Importants

### Recalcul Patrimonial Complet
```python
# Utiliser PatrimonyCalculationEngine V2.0
PatrimonyCalculationEngine.calculate_and_save_all(
    investor_profile, 
    force_recalculate=True, 
    save_to_db=True
)
```

### Mise à Jour Prix Crypto
```python
# Via service Binance
BinancePriceService.update_crypto_prices_in_db()
# Ou via cron : flask refresh-crypto-prices
```

## 📝 Conventions de Code

### Routes
- **Platform routes** : `/plateforme/*` (application)
- **Site routes** : `/site/*` (vitrine)
- **API routes** : `/plateforme/api/*`

### Templates
- **Base template** : `platform/base.html` pour l'application
- **Styling** : CSS Atlas avec variables CSS custom
- **Responsivité** : Mobile-first approach

### Base de Données
- **Préfixes colonnes calculées** : `calculated_*`
- **Données JSON** : suffixe `_json` (ex: `immobilier_data_json`)
- **Contraintes** : Foreign keys avec CASCADE approprié

## 🚀 Déploiement et Maintenance

### Variables d'Environnement
```bash
FLASK_ENV=development
SQLALCHEMY_DATABASE_URI=postgresql://user:pass@localhost/atlas_db
SECRET_KEY=your-secret-key
```

### Tâches de Maintenance
- **Prix crypto** : Cron job `refresh_crypto_prices.py`
- **Recalculs patrimoniaux** : Interface admin disponible
- **Backups DB** : Scripts dans `/backups/`

## 🐛 Problèmes Connus et Solutions

### Problème Valeurs Dashboard (RÉSOLU)
**Symptôme** : Patrimoine total affichait 874€ au lieu de 83,523€ à la première connexion
**Cause** : `refresh_user_portfolio_at_login()` recalculait automatiquement les valeurs
**Solution** : Suppression des hooks automatiques + lecture pure de `calculated_patrimoine_total_net`

### Cache Navigateur
**Problème** : CSS et templates parfois mis en cache
**Solution** : Headers anti-cache configurés dans `app/__init__.py`

## 📞 Contact et Support

- **Développement** : Claude AI Assistant
- **Utilisateur Principal** : Hugues Marie (hugues.marie925@gmail.com)
- **Base de données** : PostgreSQL sur localhost:5432

---

## 🔄 État Actuel du Projet

**Dernière mise à jour** : 29 Décembre 2024

### Dernières Modifications (29 Décembre 2024) 🆕
- **Mise à jour complète des offres commerciales** sur la page d'accueil :
  - **INITIA** : 25€/mois - "Pour débuter dans l'investissement"
  - **OPTIMA** : 50€/mois - "Pour structurer et optimiser son patrimoine existant" 
  - **ULTIMA** : "Nous consulter" - "Pour des situations patrimoniales spécifiques"
- **Nouveau contenu des avantages** :
  - Analyse de situation, stratégie d'investissement, tableau de bord Atlas
  - Pilotage, contenus pédagogiques, accompagnement 100% indépendant
  - Optimisation patrimoine existant, classes d'actifs supplémentaires
  - Allocation multi-actifs, optimisation transmission, problématiques spécifiques
- **Amélioration UX** : Alignement parfait des boutons CTA avec CSS flexbox
- **Disclaimer légal** : "Tarifs TTC. Sans engagement. Vous restez libre de résilier à tout moment."

### Fonctionnalités Opérationnelles ✅
- Système d'authentification complet
- Dashboard investisseur avec vraies données patrimoniales
- Calculs patrimoniaux précis et sauvegardés
- Interface admin fonctionnelle
- Plans d'investissement personnalisés
- Suivi des prix cryptomonnaies en temps réel

### Prochaines Étapes Recommandées
1. **Tests automatisés** : Ajouter une suite de tests pour les calculs patrimoniaux
2. **Optimisation mobile** : Améliorer l'expérience sur smartphone
3. **Notifications** : Système d'alertes pour les seuils patrimoniaux
4. **Rapports PDF** : Génération de rapports patrimoniaux détaillés

---

*Ce document est maintenu à jour à chaque session de développement importante.*