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

**Dernière mise à jour** : 10 Février 2026

### Dernières Modifications (10 Février 2026) 🆕

#### 📱 CORRECTIONS RESPONSIVE POPUP RDV - SITE VITRINE

**Fichier modifié** : `app/templates/site/base_new.html`

**1. Étape 1 (formulaire) — mobile**
- Colonne gauche (panneau vert) cachée sur mobile/tablette avec `d-none d-lg-block` — elle apparaissait comme un bloc vide prenant de l'espace
- `font-size: 16px` sur les inputs pour éviter le zoom automatique iOS
- Paddings ajustés pour un affichage confortable sur petits écrans

**2. Étape 2 (calendrier) — même taille que l'étape 1**
- Suppression de `modal-fullscreen-step2` et `modal-lg-expanded` — les deux étapes gardent maintenant la même taille de modal (`modal-lg`)
- CSS responsive ajusté : `#cal-embed-container` à 520px sur mobile, 480px sur très petits écrans

**3. Fix erreur Cal.com (conflit Bootstrap Modal + Next.js router)**
- Remplacement de `embed.js` Cal.com par une **iframe directe** — l'embed.js patchait `window.history.pushState` dans la page parente, entrant en conflit avec Bootstrap Modal et causant `Cannot read properties of null (reading 'dispatchEvent')`
- URL iframe : `https://app.cal.eu/contact-atlas/30min/embed?embed=30min&layout=month_view&embedType=inline`
- Loader converti en **overlay CSS positionné** au-dessus du container (le container reste toujours visible avec de vraies dimensions pour que l'iframe puisse s'initialiser correctement)
- Timeout augmenté à 15 secondes (adapté aux connexions mobiles lentes)
- postMessage origin corrigé : `https://app.cal.com` → `https://app.cal.eu` (l'origin réelle)

**4. CSS loader overlay**
```css
#cal-loader {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: white;
    z-index: 10;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
```

#### 🖼️ MISE À JOUR PHOTOS ÉQUIPE

**Nouvelles photos ajoutées** :
- `app/static/images/photo_equipe.png` — photo d'équipe groupe
- `app/static/images/photo_profil_hug.png` — nouveau portrait Hugues Marie
- `app/static/images/photo_profil_roland.png` — nouveau portrait Roland Baudinot

**Fichiers modifiés** :
- `app/templates/site/index_exact.html` : Section "Atlas est une société..." — remplacement des deux photos fondateurs superposées par `photo_equipe.png` (photo unique, `flex: 0 0 420px`, badge "Notre équipe")
- `app/templates/site/about.html` : Photos de l'équipe mises à jour (`photo_profil_roland.png`, `photo_profil_hug.png`) + `object-position: center top` pour éviter la coupure des têtes

---

**Dernière mise à jour** : 13 Janvier 2026

### Dernières Modifications (13 Janvier 2026) 🆕

#### 🎨 AMÉLIORATIONS UX ET DESIGN INTERFACE

**1. Nettoyage Interface Données Investisseur**
- **Suppression ligne "Total Actifs/Dettes"** : Retrait de la ligne récapitulative sur `/plateforme/donnees-investisseur`
- **Raison** : Information redondante déjà visible dans le dashboard
- **Fichier modifié** : `app/templates/platform/investor/investor_data.html`

**2. Amélioration Qualité Affichage PDF 📄**
- **Problème résolu** : PDFs flous sur écrans haute résolution (Retina, 4K)
- **Solution technique** :
  - Rendu canvas à haute résolution avec `devicePixelRatio`
  - Scale de sortie 1.5× pour netteté optimale
  - Transform matrix pour PDF.js
  - Échelle par défaut augmentée de 1.0 → 1.5
- **Impact** : PDFs nets et lisibles sur tous les devices sans compromis de sécurité
- **Fichiers modifiés** :
  - `app/templates/platform/investor/learning_pdf.html`
  - `app/templates/platform/admin/learning_pdf.html`

**Code clé implémenté** :
```javascript
const pixelRatio = window.devicePixelRatio || 1;
const outputScale = pixelRatio * 1.5; // 1.5x pour netteté extra

canvas.height = Math.floor(viewport.height * outputScale);
canvas.width = Math.floor(viewport.width * outputScale);
canvas.style.width = Math.floor(viewport.width) + 'px';
canvas.style.height = Math.floor(viewport.height) + 'px';

const transform = outputScale !== 1 ? [outputScale, 0, 0, outputScale, 0, 0] : null;
```

**3. Sécurisation Changement Abonnement 🔐**
- **Nouvelle fonctionnalité** : Confirmation par mot de passe pour changement de plan
- **Design moderne** : Modal avec gradient header, icône exchange, billing détaillé
- **Sécurité** : Vérification backend du mot de passe via `current_user.check_password()`
- **UX** :
  - Affichage du nouveau prix (25€ ou 50€)
  - Explication claire de la facturation (immédiat, prorata, nouveau tarif)
  - Messages d'erreur inline pour mot de passe incorrect
  - Loading states et feedback temps réel

**Fichiers modifiés** :
- `app/templates/platform/investor/profile.html` : Nouveau modal + JavaScript
- `app/routes/platform/investor.py` : Route `/profil/changer-plan` avec vérification

**Design du modal** :
```
┌─────────────────────────────────────┐
│  🔄 (gradient #137C8B → #344D59)   │
│  Changement de plan                 │
│  Confirmez votre nouveau abonnement │
├─────────────────────────────────────┤
│  ┌─────────────────────────────┐   │
│  │ OPTIMA                      │   │
│  │ 50€/mois                    │   │
│  └─────────────────────────────┘   │
│                                     │
│  Ce qui va se passer:               │
│  ✓ Changement immédiat              │
│  ✓ Facturation au prorata           │
│  ✓ Prochain paiement nouveau tarif │
│                                     │
│  [Votre mot de passe]              │
│  [Mot de passe incorrect]          │
│                                     │
│  [Annuler]  [✓ Confirmer]          │
└─────────────────────────────────────┘
```

#### 🐛 CORRECTIONS BUGS CRITIQUES

**1. Fix Service Suppression Utilisateurs**
- **Problème** : Échec de suppression pour certains utilisateurs en production
- **Cause** : Nouvelles tables (comptes_rendus, password_reset_tokens) non gérées
- **Solution** : Extension de `UserDeletionService._delete_investment_plans()` pour 11 tables
- **Tables maintenant supprimées** :
  1. comptes_rendus (NOUVELLE)
  2. investment_actions
  3. investment_plan_lines
  4. investment_plans
  5. password_reset_tokens (NOUVELLE)
  6. invitation_tokens
  7. user_plans
  8. payment_methods
  9. portfolios
  10. subscriptions
  11. investor_profiles

**Fichier modifié** : `app/services/user_deletion_service.py`

**2. Fix Menu Mobile Double-Clic 📱**
- **Problème critique** : Boutons menu mobile nécessitaient 2 clics pour fonctionner
- **Cause** : Menu se fermait AVANT que le clic bouton ne soit traité
- **Solution** : Script centralisé avec gestion événements appropriée
  - **Pour modals Bootstrap** : Écoute événement `show.bs.modal`
  - **Pour liens navigation** : Délai 10ms avant fermeture menu
- **Impact** : Fix appliqué sur **10 pages** du site vitrine

**Nouveau fichier créé** : `app/static/js/mobile-menu-fix.js`

**Pages mises à jour** :
- about.html, cgu.html, cgv.html, contact.html, cookies.html
- index_exact.html, legal.html, pricing.html, privacy.html, solutions.html

**Code de la solution** :
```javascript
// ✅ FIX 1: Liens navigation
document.querySelectorAll('.mobile-menu-link').forEach(link => {
    link.addEventListener('click', function(e) {
        setTimeout(() => toggleMobileMenu(), 10); // 10ms délai
    });
});

// ✅ FIX 2: Modals Bootstrap (RDV)
appointmentModal.addEventListener('show.bs.modal', function () {
    const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');
    if (mobileMenuOverlay && mobileMenuOverlay.classList.contains('active')) {
        hamburger.classList.remove('active');
        mobileMenuOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }
});
```

#### 📝 RÉCAPITULATIF TECHNIQUE

**Nouveaux fichiers** :
- `app/static/js/mobile-menu-fix.js` : Fix universel menu mobile

**Modifications majeures** :
- `app/templates/platform/investor/investor_data.html` : Suppression ligne récap
- `app/templates/platform/investor/learning_pdf.html` : Rendu haute résolution
- `app/templates/platform/admin/learning_pdf.html` : Rendu haute résolution
- `app/templates/platform/investor/profile.html` : Modal confirmation + 400 lignes JS
- `app/routes/platform/investor.py` : Vérification mot de passe changement plan
- `app/services/user_deletion_service.py` : Extension suppression 11 tables
- 10 templates site vitrine : Intégration mobile-menu-fix.js

**Tests effectués en local** :
- ✅ Suppression ligne Total Actifs/Dettes
- ✅ PDFs affichés nets sur écrans haute résolution
- ✅ Menu mobile fonctionne au premier clic
- ✅ Changement plan avec mot de passe fonctionnel
- ✅ Messages d'erreur mot de passe incorrect
- ✅ Design modal moderne et professionnel

### Modifications Précédentes (12 Janvier 2026)

#### ⏰ ACTIVATION COMPLÈTE SYSTÈME CRON JOBS PRODUCTION 🎉

**Système d'automatisation entièrement opérationnel** avec correction du bug AWS CLI.

**Problème résolu** : Les backups automatiques échouaient avec l'erreur `pip3: command not found` car le script tentait d'installer AWS CLI via pip3 lors de l'exécution cron, alors qu'AWS CLI était déjà installé via apt.

**Solution implémentée** :
- **Chemin complet AWS CLI** : Utilisation de `AWS_CMD="/usr/bin/aws"` au lieu de `aws`
- **Suppression installation pip3** : Le script ne tente plus d'installer AWS CLI
- **Compatibilité cron** : Variables PATH correctement gérées dans l'environnement cron

**Tests réussis** :
```bash
# Test mise à jour crypto (16:33:18)
✅ 104 prix crypto mis à jour avec succès
   💰 BITCOIN: 79,285.97€
   💰 ETHEREUM: 2,699.53€
   💰 BINANCECOIN: 779.85€
   💰 SOLANA: 123.70€

# Test backup base de données (16:58:42)
✅ Export PostgreSQL: 68K
✅ Compression gzip: 20K (réduction 70%)
✅ Upload Spaces: backups/database/2026/01/12/atlas_backup_20260112_165842.sql.gz
```

**Système actif** :
| Heure | Tâche | Status |
|-------|-------|--------|
| **:05** chaque heure | Mise à jour 104 prix crypto | ✅ Opérationnel |
| **:30** chaque heure | Backup DB → DigitalOcean Spaces | ✅ Opérationnel |

**Logs disponibles** :
- `/var/log/atlas_crypto.log` - Historique mises à jour crypto
- `/var/log/atlas_backup.log` - Historique backups

**Fichiers modifiés** :
- `setup_cron_production.sh` : Fix chemin AWS CLI (commit `1b95e41`)

**Architecture finale** :
```
Cron → Script → Dokku config → PostgreSQL/Binance → DigitalOcean Spaces
  ↓                ↓                    ↓                       ↓
:05/:30      backup_atlas_db.sh    atlas-db export      s3://atlas-database/
```

#### 📊 AMÉLIORATION SYSTÈME SUIVI PATRIMONIAL

**Nouvelles fonctionnalités comptes rendus** :
- **Titre personnalisable** : Ajout d'un champ titre pour identifier rapidement les comptes rendus
- **Type de RDV** : Liste déroulante avec 3 options (RDV invest, RDV suivi, Contact)
- **Prochaine action** : Liste déroulante pour planifier la suite (Autre invest, Suivi classique)
- **Édition complète** : Modal d'édition avec éditeur Quill pour modifier tous les champs
- **Suppression sécurisée** : Bouton de suppression avec confirmation pour nettoyer l'historique
- **Affichage enrichi** : Timeline améliorée avec badges et métadonnées visibles

**Modifications techniques** :
- Modèle `CompteRendu` étendu avec 3 nouvelles colonnes : `titre`, `type_rdv`, `prochaine_action`
- Routes API complètes : `/compte-rendu/<id>/update` (PUT) et `/compte-rendu/<id>/delete` (DELETE)
- Interface utilisateur cohérente avec design Atlas (couleurs, typographie, boutons)
- Double éditeur Quill (création + édition) pour expérience utilisateur fluide

**⚠️ MIGRATION BASE DE DONNÉES REQUISE POUR DÉPLOIEMENT** :
```bash
# Sur le serveur de production
python migrations/add_compte_rendu_fields.py
```

#### 💰 SYNCHRONISATION COMPLÈTE SYSTÈME CRYPTOMONNAIES

**Problème résolu** : Listes de cryptos désynchronisées entre espace client (50 cryptos) et admin (10 cryptos), causant des prix manquants et des calculs incorrects.

**Modifications apportées** :
- **Liste cryptos admin étendue** : 10 → **50 cryptomonnaies** dans `user_detail.html` (ligne 5857)
- **Mapping symboles complet** : `symbolToId` mis à jour avec les 50 cryptos (ligne 1914)
- **API admin corrigée** : Retourne désormais **tous les prix** disponibles (104 cryptos) au lieu de 10
- **Précision augmentée** : 8 décimales pour les petites cryptos comme SHIB (0.00000729€)
- **Prix mis à jour** : Script `update_crypto_prices.py` exécuté avec succès

**Impact** :
- ✅ USD-COIN (USDC), SHIB et toutes les cryptos maintenant disponibles en admin
- ✅ Calculs patrimoniaux corrects : Total Cryptos = 62,286€ (BTC + USDC + SHIB)
- ✅ Prix unitaires affichés correctement pour toutes les cryptos

**Fichiers modifiés** :
- `app/templates/platform/admin/user_detail.html` : Liste cryptos + mapping symboles
- `app/routes/platform/admin.py` : API `/api/crypto-prices` sans filtrage

#### 📊 AMÉLIORATIONS DASHBOARD ADMIN

**Refonte des métriques** :
- **Nouvelle carte "Abonnements"** : Affiche le nombre d'abonnés Initia et Optima séparément
- **"Total Encours Conseillés"** : Remplace "Profils Complétés", calcule la somme de `calculated_total_placements` + `calculated_total_cryptomonnaies` de tous les clients
- **Suppression "Total Clients"** : Redondant avec "Clients Actifs" + "Prospects"
- **Mois dynamique** : Affichage du mois actuel en français pour "Nouveaux Clients"

**Fichiers modifiés** :
- `app/routes/platform/admin.py` : Calcul `total_encours` et `mois_actuel`
- `app/templates/platform/admin/dashboard.html` : Nouvelle disposition des cartes

#### 🐛 CORRECTIONS BUGS PATRIMOINE

**Fix champ PEE/PERCO** :
- **Problème** : Champ ne s'affichait pas en mode visualisation et n'entrait pas dans les calculs en temps réel
- **Cause** : Incohérence de nommage (`pee_perco_value` dans le template vs `pee_value` dans le modèle)
- **Solution** : Standardisation sur `pee_value` partout (input, display, JavaScript)

**Fichier modifié** :
- `app/templates/platform/investor/investor_data.html` : Lignes 2021, 2539, 4454, 4655

#### 📧 MISE À JOUR EMAIL GÉNÉRIQUE SUIVI RDV

**Nouveau design professionnel** :
- **Objet** : "Suite à notre échange – votre accompagnement Atlas"
- **Couleur principale** : #268190 (couleur Atlas)
- **Logo Atlas** : Ajouté dans la signature (32px de hauteur)
- **Contenu** : Message personnalisé et chaleureux avec CTA vers espace client

**Fichier modifié** :
- `app/routes/platform/admin.py` : Route `send_generic_follow_up_email`

#### 🎓 AMÉLIORATIONS ONBOARDING

**Page sélection des plans** (`/onboarding/plan`) :

1. **Images des plans** :
   - Plan INITIA : `/static/images/plan_initia.png` (icône feuilles blanches sur fond bleu-vert)
   - Plan OPTIMA : `/static/images/plan_optima.png`
   - Dimensions : 120×120px avec coins arrondis (20px)
   - Style : `object-fit: cover` pour meilleur rendu

2. **Informations de suivi** :
   - INITIA : "2 rendez-vous de suivi par an avec votre conseiller Atlas" (dernière ligne des features)
   - OPTIMA : "4 rendez-vous de suivi par an avec votre conseiller Atlas"
   - Synchronisé avec la page de tarifs du site vitrine

3. **Textes de bienvenue améliorés** :
   - Titre : "Bienvenue sur Atlas !" → "Bienvenue chez Atlas !"
   - Sous-titre : Message plus chaleureux "Merci pour votre confiance, nous avons hâte de vous accompagner"

**Fichiers modifiés** :
- `app/models/user_plan.py` : Configuration `PLAN_CONFIGS` avec images et features
- `app/templates/onboarding/plan_selection.html` : Affichage images + CSS styling

#### 📝 RÉCAPITULATIF TECHNIQUE

**Migrations base de données** :
```bash
# Migration déjà créée et documentée
python migrations/add_compte_rendu_fields.py
```

**Scripts de maintenance** :
```bash
# Mise à jour prix crypto (cron job)
python scripts/update_crypto_prices.py
```

**Fichiers sensibles exclus** :
- ✅ `.env` et fichiers de configuration avec clés Stripe
- ✅ Scripts de configuration locale (`configure_*.sh`)
- ✅ Backups base de données (`.sql`, `.gz`)

### Modifications Majeures (9 Janvier 2026)

#### 🚀 Mise à jour v3.0 - Fonctionnalités avancées

**📅 INTÉGRATION CAL.COM COMPLÈTE** :
- Modal 2-étapes pour prise de rendez-vous optimisée
- Workflow : formulaire collecte données → affichage calendrier Cal.com
- Sauvegarde automatique des données utilisateur 
- Fix menu mobile universel sur toutes les pages
- Integration Cal.com embed avec cleanup automatique

**🤖 SYSTÈME RAG (ASSISTANT ATLAS)** :
- Service `AtlasRAGService` avec recherche sémantique avancée
- Base de connaissance Atlas complète (50+ documents MD)
- Intégration OpenAI API avec injection de contexte intelligent
- Cache TF-IDF pour performances optimales
- Interface admin pour gestion et tests RAG
- System prompt dédié depuis `Assistant_atlas.md`

**🎨 REDESIGN INTERFACE UTILISATEUR** :
- Nouvelle section frais (design ChatGPT exact avec variables Atlas)
- FAQ moderne plan investissement avec accordéons pleine largeur
- Fix contraintes base données `investment_actions` → `investment_plan_lines`
- Tableau fonctionnalités (Critères → Fonctionnalités) 
- Corrections line breaks sur page solutions

**📄 MISE À JOUR PAGES LÉGALES** :
- Toutes les dates synchronisées au 9 janvier 2026
- CGU, Privacy, Cookies, Legal, CGV mises à jour

**🔒 SÉCURITÉ ET DÉPLOIEMENT** :
- .gitignore renforcé pour éviter push de fichiers sensibles
- Scripts de configuration restent en local uniquement
- Suppression scripts avec potentielles clés du repo public

### Modifications Précédentes (30 Décembre 2024)
- **GESTION D'ABONNEMENTS STRIPE COMPLÈTE** :
  - Changement de plan avec facturation proratisée automatique
  - Gestion des moyens de paiement depuis l'API Stripe (jamais de données bancaires en base)
  - Annulation d'abonnement simplifiée avec alternatives
  - Interface utilisateur moderne et intuitive

- **STRIPE ELEMENTS INTÉGRATION** :
  - Ajout sécurisé de cartes via Stripe Elements
  - SetupIntent workflow pour la sécurité maximale
  - Validation en temps réel des champs de carte
  - Gestion des erreurs et fallback en mode développement

- **SYSTÈME DE FACTURATION** :
  - Récupération automatique des factures depuis Stripe API
  - Affichage des factures avec téléchargement PDF
  - Historique complet des paiements
  - Interface moderne avec statuts visuels

- **AMÉLIORATION DE L'EXPÉRIENCE UTILISATEUR** :
  - Page profil entièrement refactorisée (`/plateforme/profil`)
  - Messages d'état intelligents selon le contexte (prod/dev)
  - Design cohérent avec la charte graphique Atlas
  - Processus d'annulation simplifié (fini le popup complexe)

### Fonctionnalités Opérationnelles ✅
- Système d'authentification complet
- Dashboard investisseur avec vraies données patrimoniales
- Calculs patrimoniaux précis et sauvegardés
- Interface admin fonctionnelle
- Plans d'investissement personnalisés
- Suivi des prix cryptomonnaies en temps réel
- **🆕 Gestion complète des abonnements Stripe**
- **🆕 Moyens de paiement sécurisés**
- **🆕 Facturation automatique**
- **🆕 Interface utilisateur v2.0**

### Configuration Stripe Production ⚠️
Pour activer toutes les fonctionnalités Stripe :
1. Variables d'environnement requises dans `.env` :
   ```
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_PUBLISHABLE_KEY=pk_live_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   STRIPE_PRICE_INITIA=price_...
   STRIPE_PRICE_OPTIMA=price_...
   ```
2. Redémarrer l'application après ajout des clés
3. Vérifier les logs : "Configuration Stripe chargée (Production)"

### Prochaines Étapes Recommandées
1. **Tests Stripe en production** : Valider tous les flux de paiement
2. **Webhooks Stripe** : Configuration pour les événements automatiques
3. **Optimisation mobile** : Améliorer l'expérience sur smartphone
4. **Notifications** : Système d'alertes pour les seuils patrimoniaux

---

## 🆕 Mise à Jour Majeure (7 Janvier 2026)

### Dashboard Admin Ultra-moderne 🎨

**Refonte complète de l'interface administrateur** avec design compact et couleurs Atlas authentiques.

#### Nouvelles Fonctionnalités Dashboard
- **MRR Réel Calculé** : Calcul automatique du Monthly Recurring Revenue basé sur les vrais prix des abonnements
- **7 Métriques Clés** :
  - MRR avec répartition INITIA/OPTIMA
  - Clients actifs (abonnements payants)
  - Total clients inscrits
  - Prospects en attente
  - Patrimoine moyen par client
  - Profils patrimoniaux complétés
  - Nouveaux clients du mois
- **Tables Interactives** : Listes des derniers clients et prospects avec boutons "Voir profil"
- **Actions Rapides** : Navigation directe vers gestion clients/prospects/espace client

#### Design et UX
```css
/* Vraies couleurs Atlas utilisées */
--atlas-primary: #137C8B;
--atlas-secondary: #709CA7;
--atlas-dark: #344D59;
```
- **Cartes compactes** : Design inspiré du dashboard utilisateur
- **Responsive adaptatif** : 4→2→1 colonnes selon device
- **Animations fluides** : fadeInUp et hover effects
- **Icônes Atlas** : Cohérence visuelle avec le reste de la plateforme

### Système de Suppression Utilisateurs 🗑️

**Service UserDeletionService robuste** pour suppression complète et sécurisée.

#### Fonctionnalités Suppression
- **Double confirmation** : Deux clics de validation sans saisie de texte
- **Suppression Stripe complète** :
  - Annulation automatique des abonnements actifs
  - Suppression des customers Stripe
  - Gestion des erreurs API Stripe
- **Nettoyage database** : 
  - Suppression cascade des données liées
  - Gestion automatique des contraintes FK
  - Logs détaillés de toutes les opérations

#### Architecture Technique
```python
# Service principal dans app/services/user_deletion_service.py
class UserDeletionService:
    @staticmethod
    def delete_user_completely(user_id: int):
        # 1. Annulation Stripe en premier
        # 2. Suppression préparatoire des contraintes FK
        # 3. Suppression ORM de l'utilisateur principal
        # 4. Logs et retour détaillé
```

#### Interface Utilisateur
- **Boutons suppression** : Icônes trash dans les listes admin
- **Prospects ET clients** : Même fonctionnalité pour les deux types d'utilisateurs
- **Feedback temps réel** : Loading states et messages de confirmation
- **Gestion d'erreurs** : Affichage des erreurs avec possibilité de retry

### Relations Database Optimisées 🔧

**Mise à jour des modèles SQLAlchemy** pour gestion cascade correcte.

#### Modèles Mis à Jour
```python
# app/models/user.py
investment_plans = db.relationship('InvestmentPlan', 
                                 backref='user', 
                                 cascade='all, delete-orphan')

# app/models/invitation_token.py  
prospect = db.relationship('User', 
                          backref=db.backref('invitation_tokens', 
                                            cascade='all, delete-orphan'))

# app/models/user_plan.py
user = db.relationship('User', 
                      backref=db.backref('selected_plans', 
                                        cascade='all, delete-orphan'))
```

#### Contraintes Gérées
- **investment_plans** ↔ **users**
- **invitation_tokens** ↔ **users** (prospects)
- **user_plans** ↔ **users**
- **subscriptions** ↔ **users**
- **investor_profiles** ↔ **users**

### Améliorations Site Vitrine 📱

#### Fix Menu Mobile Universel
```javascript
// Fix appliqué sur toutes les pages
function closeMenuOnButtonClick() {
    const mobileMenu = document.querySelector('.mobile-nav');
    if (mobileMenu && mobileMenu.classList.contains('active')) {
        mobileMenu.classList.remove('active');
    }
}
```

#### Pages Légales Mises à Jour
- **Email contact** : `contact@atlas.fr` → `contact@atlas-invest.fr`
- **Dates de modification** : Toutes mises à jour au 7 janvier 2026
- **Pages concernées** : CGU, Confidentialité, Cookies, Mentions légales

#### Performance et UX
- **Animations optimisées** : Réduction du temps d'apparition des sous-menus
- **Layout responsive** : Cartes plans d'investissement en 2x2 sur desktop
- **Navigation cohérente** : Menu mobile fonctionnel sur toutes les pages

### Interface Admin Simplifiée 🎛️

#### Menu Admin Nettoyé
**Suppression des boutons non-fonctionnels** :
- ❌ Transactions
- ❌ Rapports  
- ❌ Notifications
- ❌ Audit & Sécurité

**Conservation des fonctionnalités essentielles** :
- ✅ Dashboard
- ✅ Utilisateurs
- ✅ Prospects
- ✅ Apprentissage
- ✅ Paramètres/Système/Logs

#### Navigation Intelligente
- **Boutons "Voir profil"** dans toutes les listes d'utilisateurs/prospects
- **Liens directs** : Dashboard → pages de gestion spécifiques
- **Alignement parfait** : Tables avec colonnes bien alignées

### Architecture Services 🏗️

#### Nouveau Service UserDeletionService
```
app/services/user_deletion_service.py
├── delete_user_completely()     # Méthode principale
├── _cancel_stripe_subscription() # Gestion Stripe
├── _delete_investment_plans()    # Nettoyage contraintes FK
└── _delete_related_data_sql()    # Suppression SQL directe
```

#### Routes Admin Étendues
```
/plateforme/admin/
├── dashboard                     # Dashboard moderne
├── utilisateur/<id>/supprimer   # Suppression utilisateurs
├── prospect/<id>/supprimer      # Suppression prospects
└── utilisateurs                 # Liste avec boutons suppression
```

### Fonctionnalités Opérationnelles Actuelles ✅

#### Système Admin Complet
- **Dashboard moderne** avec vraies métriques business
- **Gestion utilisateurs** avec suppression sécurisée
- **Gestion prospects** avec conversion et suppression
- **Navigation intuitive** et design cohérent
- **Calculs financiers précis** (MRR, patrimoine, conversions)

#### Site Vitrine Optimisé
- **Menu mobile universel** fonctionnel sur toutes les pages
- **Pages légales à jour** avec bonnes coordonnées
- **Performance améliorée** et animations optimisées
- **Responsive design** parfait sur tous les devices

#### Architecture Robuste
- **Relations database** avec cascade correctes
- **Services métier** modulaires et réutilisables
- **Gestion d'erreurs** complète avec logs détaillés
- **Code documenté** et maintenable

### Configuration Déploiement ⚠️

#### Variables d'Environnement à Préserver
```bash
# ⚠️ NE PAS MODIFIER en production
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
SQLALCHEMY_DATABASE_URI=postgresql://...
SECRET_KEY=...
```

#### Commandes Déploiement Sécurisé
```bash
# 1. Pull des changements SANS toucher aux variables env
git pull origin main

# 2. Redémarrage application
sudo systemctl restart atlas-app

# 3. Vérification logs
sudo journalctl -u atlas-app -f
```

---

## 🚀 Processus de Déploiement Production

### Prérequis Déploiement
- ✅ Commit et push validés sur `main` 
- ✅ Variables d'environnement configurées sur serveur Dokku
- ✅ .gitignore à jour pour éviter push de fichiers sensibles
- ✅ Tests en local réussis

### 🌐 Déploiement sur Serveur Dokku

#### 1. Connexion au serveur
```bash
# Se connecter au serveur de production
ssh root@atlas-invest.fr
```

#### 2. Vérification état actuel
```bash
# Voir les applications Dokku
dokku apps:list

# Voir l'état de l'application Atlas
dokku ps:report atlas

# Voir les variables d'environnement (sans valeurs sensibles)
dokku config atlas
```

#### 3. Déploiement
```bash
# Déployer depuis le repository GitHub
dokku git:sync atlas https://github.com/hugumarie/atlas_platform.git main

# Alternative si problème avec git:sync
cd /home/dokku/atlas
git pull origin main
dokku deploy atlas
```

#### 4. Exécution des migrations (si nécessaire)
```bash
# Copier les fichiers de migration si ce n'est pas déjà fait
# (ils sont normalement déjà dans le repo Git)

# Se connecter au conteneur Dokku
dokku enter atlas web

# Exécuter les migrations nécessaires
# Exemple pour la migration des comptes rendus (12 janvier 2026)
python migrations/add_compte_rendu_fields.py

# Vérifier que la migration a réussi
python migrations/add_compte_rendu_fields.py --check

# Sortir du conteneur
exit
```

**⚠️ IMPORTANT** : Toujours faire un backup de la base avant d'exécuter une migration :
```bash
dokku postgres:backup atlas-db atlas-backup-pre-migration-$(date +%Y%m%d-%H%M%S)
```

#### 5. Vérifications post-déploiement
```bash
# Vérifier que l'application est en cours d'exécution
dokku ps:report atlas

# Voir les logs en temps réel
dokku logs atlas -t

# Tester l'application
curl -I https://atlas-invest.fr
```

### ⚠️ Variables d'Environnement CRITIQUES

**IMPORTANT : Ne JAMAIS modifier ces variables lors du déploiement**
```bash
# Variables Stripe Production (configurées une fois)
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_INITIA=price_...
STRIPE_PRICE_OPTIMA=price_...

# Database Production
SQLALCHEMY_DATABASE_URI=postgresql://...
SECRET_KEY=...

# Services externes
OPENAI_API_KEY=...
MAILERSEND_API_TOKEN=...
```

### 🔧 Commandes Dokku Utiles

#### Gestion des logs
```bash
# Logs en temps réel
dokku logs atlas -t

# Logs des erreurs seulement
dokku logs atlas --tail 100 | grep -i error

# Logs d'une période spécifique
dokku logs atlas --since 1h
```

#### Redémarrage application
```bash
# Redémarrage complet
dokku ps:restart atlas

# Redémarrage après modification config
dokku config:set atlas FLASK_ENV=production
dokku ps:restart atlas
```

#### Base de données
```bash
# Voir l'état PostgreSQL
dokku postgres:info atlas-db

# Backup base de données
dokku postgres:backup atlas-db atlas-backup-$(date +%Y%m%d)

# Voir les backups
dokku postgres:backup-list atlas-db
```

### 🚨 Procédure d'Urgence

En cas de problème critique :
1. **Rollback rapide**
   ```bash
   dokku ps:scale atlas web=0  # Arrêt immédiat
   dokku ps:scale atlas web=1  # Redémarrage
   ```

2. **Retour version précédente**
   ```bash
   dokku git:sync atlas https://github.com/hugumarie/atlas_platform.git <commit-hash>
   ```

3. **Monitoring**
   ```bash
   # CPU/Mémoire
   dokku resource:report atlas
   
   # Santé application
   dokku ps:report atlas
   ```

### ✅ Checklist Post-Déploiement

- [x] Application accessible sur https://atlas-invest.fr
- [x] Connexions utilisateurs fonctionnelles  
- [x] Paiements Stripe opérationnels
- [x] Assistant RAG disponible (/plateforme/assistant)
- [x] Modal Cal.com fonctionnelle
- [x] Pages légales à jour (dates 2026)
- [x] Dashboard admin accessible
- [x] Pas d'erreurs dans les logs

**🎉 DÉPLOIEMENT v3.0 RÉUSSI - 9 janvier 2026 15:11 GMT**
- Commit déployé : `ee406f4` 
- Serveur : atlas-invest.fr (Dokku)
- Status : ✅ Running
- Logs : ✅ Aucune erreur critique
- Trafic : ✅ Pages fonctionnelles

---

## 💾 Système de Backup Automatique (Production) 🆕

### Vue d'Ensemble
**Système complet de sauvegarde automatique** de la base de données PostgreSQL de production vers DigitalOcean Spaces, avec rotation automatique et monitoring.

#### Architecture du Système
```
PostgreSQL Production → pg_dump → Compression gzip → DigitalOcean Spaces
     ↓                    ↓            ↓                    ↓
  Données Atlas    Backup SQL    Fichier .gz        backups/database/YYYY/MM/DD/
```

### 📁 Fichiers du Système

#### Scripts Principaux
- **`backup_database_production.py`** : Script principal de backup
- **`run_backup_production.sh`** : Wrapper avec chargement des variables d'environnement  
- **`backup_config.env.example`** : Template de configuration
- **`install_backup_system.sh`** : Script d'installation automatique
- **`test_backup_system.py`** : Script de test et validation
- **`crontab_backup_production.txt`** : Configuration cron

#### Configuration Requise (`backup_config.env`)
```bash
# Base de données PostgreSQL
DB_HOST=your_production_db_host
DB_NAME=atlas_production
DB_USER=atlas_user
DB_PASSWORD=your_secure_password

# DigitalOcean Spaces
DIGITALOCEAN_SPACES_KEY=your_access_key
DIGITALOCEAN_SPACES_SECRET=your_secret_key
DIGITALOCEAN_SPACES_ENDPOINT=https://fra1.digitaloceanspaces.com
DIGITALOCEAN_SPACES_BUCKET=atlas-storage
```

### 🔧 Configuration DigitalOcean Spaces Production

#### 1. Configuration des Clés Spaces (Dokku)
```bash
# Copier le script de configuration
scp configure_spaces_production.sh root@atlas-invest.fr:/root/

# Se connecter et configurer
ssh root@atlas-invest.fr
cd /root
chmod +x configure_spaces_production.sh
./configure_spaces_production.sh
```

#### Alternative: Configuration Manuelle Dokku
```bash
# Variables Spaces requises
dokku config:set atlas \
    DIGITALOCEAN_SPACES_KEY="your_access_key" \
    DIGITALOCEAN_SPACES_SECRET="your_secret_key" \
    DIGITALOCEAN_SPACES_ENDPOINT="https://fra1.digitaloceanspaces.com" \
    DIGITALOCEAN_SPACES_BUCKET="atlas-storage"

# Redémarrer l'application
dokku ps:restart atlas
```

### 🚀 Installation sur Serveur Production

#### 1. Déploiement des Scripts
```bash
# Copier tous les scripts de backup sur le serveur
scp backup_*.* root@atlas-invest.fr:/opt/atlas/
scp run_backup_production.sh root@atlas-invest.fr:/opt/atlas/
scp install_backup_system.sh root@atlas-invest.fr:/opt/atlas/
```

#### 2. Installation Automatique
```bash
# Sur le serveur de production
cd /opt/atlas
chmod +x install_backup_system.sh
sudo ./install_backup_system.sh
```

#### 3. Configuration
```bash
# Configurer les paramètres de production
cp backup_config.env.example backup_config.env
nano backup_config.env  # Remplir avec les vraies valeurs
chmod 600 backup_config.env  # Sécuriser le fichier
```

#### 4. Test Initial
```bash
# Tester le système
python3 test_backup_system.py

# Test manuel du backup
sudo -u atlas ./run_backup_production.sh
```

### ⏰ Automatisation Cron

#### Configuration Active (Toutes les Heures)
```bash
# Cron job automatique à la minute 5 de chaque heure
5 * * * * /opt/atlas/run_backup_production.sh >> /var/log/atlas/backup_cron.log 2>&1
```

#### Alternatives Disponibles
```bash
# Toutes les 6 heures
0 */6 * * * /opt/atlas/run_backup_production.sh

# Quotidien à 2h00
0 2 * * * /opt/atlas/run_backup_production.sh

# 4 fois par jour (heures de bureau)
0 8,12,16,20 * * * /opt/atlas/run_backup_production.sh
```

### 🏗️ Fonctionnalités du Système

#### Backup Intelligent
- **pg_dump complet** : Dump SQL avec structure + données
- **Compression gzip** : Réduction de 80-90% de la taille
- **Métadonnées** : Date, base source, type de backup
- **Timeout protection** : Limite de 1 heure max par backup

#### Stockage Organisé
```
DigitalOcean Spaces/
└── backups/
    └── database/
        └── 2025/
            └── 01/
                └── 09/
                    ├── atlas_backup_20250109_050001.sql.gz
                    ├── atlas_backup_20250109_110001.sql.gz
                    └── atlas_backup_20250109_170001.sql.gz
```

#### Gestion Automatique
- **Rotation** : Conservation de 30 jours (configurable)
- **Nettoyage automatique** : Suppression des anciens backups
- **Logging complet** : Toutes les opérations tracées
- **Gestion d'erreurs** : Notifications et codes de retour

### 📊 Monitoring et Logs

#### Fichiers de Logs
- **`/var/log/atlas/backup.log`** : Logs détaillés des backups
- **`/var/log/atlas/backup_cron.log`** : Logs des exécutions cron
- **Rotation automatique** : logrotate configuré

#### Surveillance
```bash
# Vérifier les derniers backups
tail -f /var/log/atlas/backup.log

# Voir le statut cron
sudo -u atlas crontab -l

# Vérifier les backups sur Spaces
# Via interface DigitalOcean ou API boto3
```

### 🔧 Maintenance et Dépannage

#### Commandes Utiles
```bash
# Test complet du système
python3 test_backup_system.py

# Backup manuel immédiat
sudo -u atlas /opt/atlas/run_backup_production.sh

# Vérifier la configuration cron
sudo -u atlas crontab -l

# Voir les logs en temps réel
tail -f /var/log/atlas/backup.log

# Lister les backups sur Spaces (nécessite AWS CLI configuré)
aws s3 ls s3://atlas-storage/backups/database/ --endpoint-url=https://fra1.digitaloceanspaces.com --recursive
```

#### Problèmes Courants

**❌ Backup échoue avec erreur de connexion DB**
```bash
# Vérifier la connectivité PostgreSQL
pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER

# Tester la connexion manuellement
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT version();"
```

**❌ Upload vers Spaces échoue**
```bash
# Vérifier les clés d'accès DigitalOcean
python3 -c "
import boto3
client = boto3.client('s3', 
    endpoint_url='https://fra1.digitaloceanspaces.com',
    aws_access_key_id='$DIGITALOCEAN_SPACES_KEY',
    aws_secret_access_key='$DIGITALOCEAN_SPACES_SECRET'
)
print(client.list_buckets())
"
```

**❌ Cron ne s'exécute pas**
```bash
# Vérifier que le service cron tourne
sudo systemctl status cron

# Vérifier les logs système
sudo journalctl -u cron -f

# Tester l'exécution manuelle avec les mêmes variables
sudo -u atlas bash -c 'source /opt/atlas/backup_config.env && /opt/atlas/run_backup_production.sh'
```

### 🔄 Restauration d'un Backup

#### Processus de Restauration
```bash
# 1. Télécharger un backup depuis Spaces
wget "https://fra1.digitaloceanspaces.com/atlas-storage/backups/database/2025/01/09/atlas_backup_20250109_050001.sql.gz"

# 2. Décompresser
gunzip atlas_backup_20250109_050001.sql.gz

# 3. Restaurer (ATTENTION : écrase la base existante)
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < atlas_backup_20250109_050001.sql

# 4. Alternative : restauration vers nouvelle base
createdb -h $DB_HOST -U $DB_USER atlas_restore_test
psql -h $DB_HOST -U $DB_USER -d atlas_restore_test < atlas_backup_20250109_050001.sql
```

### 💡 Bonnes Pratiques

#### Sécurité
- **Permissions restrictives** : backup_config.env en 600 (lecture propriétaire seul)
- **Utilisateur dédié** : Exécution sous utilisateur `atlas` non-root
- **Clés séparées** : Utiliser des clés Spaces dédiées aux backups
- **Rotation des clés** : Renouveler régulièrement les accès

#### Performance
- **Horaires optimaux** : Backups pendant les heures creuses
- **Monitoring espace** : Surveiller l'usage DigitalOcean Spaces
- **Compression efficace** : gzip optimal pour SQL dumps
- **Timeout approprié** : 1h max pour éviter les blocages

#### Fiabilité
- **Tests réguliers** : Restauration test mensuelle
- **Monitoring actif** : Alertes en cas d'échec
- **Redondance** : Conserver plusieurs versions
- **Documentation** : Procédures de restauration à jour

### 📈 Métriques et Statistiques

#### Informations Typiques
- **Taille DB Atlas** : ~50-200 MB (selon nombre d'utilisateurs)
- **Compression gzip** : 80-90% de réduction
- **Durée backup** : 30 secondes - 5 minutes
- **Coût DigitalOcean** : ~$5-15/mois pour stockage + transfert
- **Rétention recommandée** : 30 jours (configurée par défaut)

---

*Ce document est maintenu à jour à chaque session de développement importante.*
---

## ⏰ Système de Cron Jobs Production (12 Janvier 2026) 🆕

### Vue d'Ensemble
**Automatisation complète** des tâches critiques via cron jobs sur le serveur Dokku:
1. **Mise à jour prix crypto**: Toutes les heures à :05
2. **Backup base de données**: Toutes les heures à :30 vers DigitalOcean Spaces

### 📋 Configuration

#### Scripts Automatisés

**1. Script de backup (/home/dokku/backup_atlas_db.sh)**
```bash
#!/bin/bash
# Charge les variables d'environnement Dokku
# Exporte la base avec dokku postgres:export
# Compresse avec gzip -9
# Upload vers Spaces avec AWS CLI
# Compatible PostgreSQL 18.1
```

**2. Crontab utilisateur dokku**
```cron
# ATLAS PRODUCTION CRON JOBS
5 * * * * dokku enter atlas web python scripts/update_crypto_prices.py >> /var/log/atlas_crypto.log 2>&1
30 * * * * /home/dokku/backup_atlas_db.sh >> /var/log/atlas_backup.log 2>&1
```

### 🚀 Installation

#### Méthode Automatique (Recommandée)

**1. Copier le script d'installation**
```bash
scp setup_cron_production.sh root@atlas-invest.fr:/tmp/
```

**2. Exécuter sur le serveur**
```bash
ssh root@atlas-invest.fr
chmod +x /tmp/setup_cron_production.sh
/tmp/setup_cron_production.sh
```

Le script configure automatiquement:
- ✅ Script de backup avec variables d'environnement
- ✅ Crontab avec les 2 tâches
- ✅ Fichiers de log (/var/log/atlas_*.log)
- ✅ Test optionnel du backup

#### Méthode Manuelle

**1. Créer le script de backup**
```bash
ssh root@atlas-invest.fr

cat > /home/dokku/backup_atlas_db.sh << 'SCRIPT'
#!/bin/bash
set -e
eval "$(dokku config:export atlas)"

TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_FILE="/tmp/atlas_backup_${TIMESTAMP}.sql"

# Export & compression
dokku postgres:export atlas-db > "${BACKUP_FILE}"
gzip -9 "${BACKUP_FILE}"

# Upload vers Spaces
YEAR=$(date '+%Y')
MONTH=$(date '+%m')
DAY=$(date '+%d')
SPACES_PATH="backups/database/${YEAR}/${MONTH}/${DAY}/$(basename ${BACKUP_FILE}.gz)"

export AWS_ACCESS_KEY_ID="${DIGITALOCEAN_SPACES_KEY}"
export AWS_SECRET_ACCESS_KEY="${DIGITALOCEAN_SPACES_SECRET}"

aws s3 cp "${BACKUP_FILE}.gz" "s3://${DIGITALOCEAN_SPACES_BUCKET}/${SPACES_PATH}" \
    --endpoint-url="${DIGITALOCEAN_SPACES_ENDPOINT}" \
    --acl private

rm -f "${BACKUP_FILE}.gz"
SCRIPT

chmod +x /home/dokku/backup_atlas_db.sh
chown dokku:dokku /home/dokku/backup_atlas_db.sh
```

**2. Configurer le crontab**
```bash
crontab -u dokku -e

# Ajouter ces lignes:
5 * * * * dokku enter atlas web python scripts/update_crypto_prices.py >> /var/log/atlas_crypto.log 2>&1
30 * * * * /home/dokku/backup_atlas_db.sh >> /var/log/atlas_backup.log 2>&1
```

**3. Créer les fichiers de log**
```bash
touch /var/log/atlas_crypto.log /var/log/atlas_backup.log
chown dokku:dokku /var/log/atlas_*.log
```

### 📊 Monitoring

#### Vérifier le Crontab
```bash
ssh root@atlas-invest.fr
crontab -u dokku -l | grep ATLAS -A 5
```

#### Logs en Temps Réel
```bash
# Prix crypto
ssh root@atlas-invest.fr "tail -f /var/log/atlas_crypto.log"

# Backups
ssh root@atlas-invest.fr "tail -f /var/log/atlas_backup.log"
```

#### Vérifier les Backups dans Spaces
```bash
# Via interface web DigitalOcean Spaces
# Ou via AWS CLI:
aws s3 ls s3://atlas-storage/backups/database/ \
    --endpoint-url=https://fra1.digitaloceanspaces.com \
    --recursive
```

### 🔧 Maintenance

#### Tester Manuellement

**Prix crypto**
```bash
ssh dokku@167.172.108.93 "enter atlas web python scripts/update_crypto_prices.py"
```

**Backup DB**
```bash
ssh root@atlas-invest.fr "/home/dokku/backup_atlas_db.sh"
```

#### Désactiver Temporairement
```bash
ssh root@atlas-invest.fr
crontab -u dokku -e
# Commenter les lignes avec # devant
```

#### Modifier la Fréquence
```bash
# Toutes les 2 heures: 5 */2 * * *
# Toutes les 6 heures: 5 */6 * * *
# Quotidien à 2h:      5 2 * * *
```

### 🚨 Dépannage

#### Les Crons Ne S'Exécutent Pas

**Vérifier le service cron**
```bash
ssh root@atlas-invest.fr
systemctl status cron
```

**Vérifier les permissions**
```bash
ls -la /home/dokku/backup_atlas_db.sh
# Doit être: -rwxr-xr-x dokku dokku
```

**Tester l'export DB manuellement**
```bash
ssh dokku@167.172.108.93 "postgres:export atlas-db" | head -20
```

#### Erreur "AWS CLI Not Found"

```bash
ssh root@atlas-invest.fr
pip3 install awscli
# Ou avec apt:
apt-get update && apt-get install -y awscli
```

#### Backup Échoue

**Vérifier les variables d'environnement**
```bash
ssh dokku@167.172.108.93 "config:get atlas DIGITALOCEAN_SPACES_KEY"
ssh dokku@167.172.108.93 "config:get atlas DIGITALOCEAN_SPACES_SECRET"
```

**Test connexion Spaces**
```bash
export AWS_ACCESS_KEY_ID="DO8..."
export AWS_SECRET_ACCESS_KEY="..."
aws s3 ls --endpoint-url=https://fra1.digitaloceanspaces.com
```

### 📈 Métriques

#### Informations Typiques
- **Taille DB Atlas**: ~50-200 MB (selon utilisateurs)
- **Backup compressé**: ~10-40 MB (compression 80-90%)
- **Durée backup**: 30 secondes - 2 minutes
- **Durée upload**: 10-30 secondes
- **Coût Spaces**: ~$5-15/mois (stockage + transfert)

#### Planning des Exécutions
```
00:05 - Mise à jour prix crypto
00:30 - Backup base de données
01:05 - Mise à jour prix crypto
01:30 - Backup base de données
... (toutes les heures)
```

### ✅ Checklist Post-Installation

- [ ] Crontab configuré et vérifié
- [ ] Script de backup exécutable
- [ ] Fichiers de log créés
- [ ] Test manuel du backup réussi
- [ ] Backup visible dans DigitalOcean Spaces
- [ ] Prix crypto mis à jour
- [ ] Logs accessibles et lisibles

### 🔐 Sécurité

**Bonnes pratiques:**
- ✅ Variables d'environnement jamais en clair dans les scripts
- ✅ Chargement dynamique via `dokku config:export`
- ✅ Backups uploadés avec ACL privé
- ✅ Cleanup automatique fichiers temporaires
- ✅ Logs rotatifs pour éviter saturation disque

---

