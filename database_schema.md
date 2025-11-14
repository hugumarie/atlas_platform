# 🗄️ ATLAS - Schéma de base de données PostgreSQL proposé

## 📊 Vue d'ensemble du système

```
ATLAS PLATFORM
├── 👥 USERS (Utilisateurs & Prospects)
├── 📈 INVESTOR_PROFILES (Profils financiers détaillés)
├── 💳 SUBSCRIPTIONS (Abonnements INITIA/OPTIMA/ULTIMA)
├── 🏦 PORTFOLIOS (Portefeuilles d'investissement)
├── 💰 CREDITS (Crédits et emprunts)
└── 💳 PAYMENT_METHODS (Méthodes de paiement)
```

---

## 🏗️ STRUCTURE DÉTAILLÉE DES TABLES

### 1. 👥 **USERS** (Table principale)
```sql
CREATE TABLE users (
    -- Identité
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    profile_picture VARCHAR(255),
    
    -- Système
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    date_created TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    
    -- Gestion prospects/clients
    user_type VARCHAR(20) DEFAULT 'client', -- 'prospect', 'client'
    is_prospect BOOLEAN DEFAULT FALSE,
    prospect_source VARCHAR(50), -- 'site_vitrine', 'recommandation'
    prospect_status VARCHAR(20), -- 'nouveau', 'contacté', 'qualifié'
    prospect_notes TEXT,
    appointment_requested BOOLEAN DEFAULT FALSE,
    appointment_status VARCHAR(20), -- 'en_attente', 'confirmé'
    assigned_to VARCHAR(100), -- Conseiller assigné
    last_contact TIMESTAMPTZ,
    
    -- Système d'invitation
    invitation_token VARCHAR(255) UNIQUE,
    invitation_sent_at TIMESTAMPTZ,
    invitation_expires_at TIMESTAMPTZ,
    can_create_account BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_type ON users(user_type, is_prospect);
```

**Contenu** : Hugues MARIE (test.client@gmail.com), comptes admin, prospects

---

### 2. 📈 **INVESTOR_PROFILES** (Profils financiers)
```sql
CREATE TABLE investor_profiles (
    -- Base
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- 💰 INFORMATIONS FINANCIÈRES DE BASE
    monthly_net_income DECIMAL(12,2) NOT NULL DEFAULT 0,
    monthly_savings_capacity DECIMAL(12,2) NOT NULL DEFAULT 0,
    current_savings DECIMAL(12,2) DEFAULT 0,
    impots_mensuels DECIMAL(12,2) DEFAULT 0,
    
    -- 🎯 PROFIL D'INVESTISSEUR
    risk_tolerance VARCHAR(20) DEFAULT 'modéré', -- 'conservateur', 'modéré', 'dynamique'
    investment_experience VARCHAR(20) DEFAULT 'intermédiaire',
    investment_goals TEXT,
    investment_horizon VARCHAR(20) DEFAULT 'moyen',
    
    -- 👤 SITUATION PERSONNELLE
    civilite VARCHAR(10), -- 'M.', 'Mme'
    date_naissance DATE,
    lieu_naissance VARCHAR(100),
    nationalite VARCHAR(50),
    pays_residence VARCHAR(50),
    pays_residence_fiscal VARCHAR(50),
    family_situation VARCHAR(30),
    professional_situation VARCHAR(50),
    metier VARCHAR(100),
    
    -- 🎯 OBJECTIFS D'INVESTISSEMENT (10 objectifs)
    objectif_premiers_pas BOOLEAN DEFAULT FALSE,
    objectif_constituer_capital BOOLEAN DEFAULT FALSE,
    objectif_diversifier BOOLEAN DEFAULT FALSE,
    objectif_optimiser_rendement BOOLEAN DEFAULT FALSE,
    objectif_preparer_retraite BOOLEAN DEFAULT FALSE,
    objectif_securite_financiere BOOLEAN DEFAULT FALSE,
    objectif_projet_immobilier BOOLEAN DEFAULT FALSE,
    objectif_revenus_complementaires BOOLEAN DEFAULT FALSE,
    objectif_transmettre_capital BOOLEAN DEFAULT FALSE,
    objectif_proteger_famille BOOLEAN DEFAULT FALSE,
    
    -- 📊 QUESTIONS PROFIL DE RISQUE DÉTAILLÉES
    tolerance_risque VARCHAR(20), -- 'faible', 'moderee', 'elevee'
    horizon_placement VARCHAR(20), -- 'court', 'moyen', 'long'
    besoin_liquidite VARCHAR(30), -- 'court_terme', 'long_terme'
    experience_investissement VARCHAR(30), -- 'debutant', 'intermediaire', 'confirme'
    attitude_volatilite VARCHAR(30), -- 'vendre', 'attendre', 'investir_plus'
    
    -- 💧 LIQUIDITÉS (Épargne disponible)
    has_livret_a BOOLEAN DEFAULT FALSE,
    livret_a_value DECIMAL(12,2) DEFAULT 0,
    has_ldds BOOLEAN DEFAULT FALSE,
    ldds_value DECIMAL(12,2) DEFAULT 0,
    has_lep BOOLEAN DEFAULT FALSE,
    lep_value DECIMAL(12,2) DEFAULT 0,
    has_pel_cel BOOLEAN DEFAULT FALSE,
    pel_cel_value DECIMAL(12,2) DEFAULT 0,
    has_current_account BOOLEAN DEFAULT FALSE,
    current_account_value DECIMAL(12,2) DEFAULT 0,
    liquidites_personnalisees_json JSONB, -- Autres comptes
    
    -- 📈 PLACEMENTS FINANCIERS
    has_pea BOOLEAN DEFAULT FALSE,
    pea_value DECIMAL(12,2) DEFAULT 0,
    has_per BOOLEAN DEFAULT FALSE,
    per_value DECIMAL(12,2) DEFAULT 0,
    has_life_insurance BOOLEAN DEFAULT FALSE,
    life_insurance_value DECIMAL(12,2) DEFAULT 0,
    has_pee BOOLEAN DEFAULT FALSE,
    pee_value DECIMAL(12,2) DEFAULT 0,
    has_scpi BOOLEAN DEFAULT FALSE,
    scpi_value DECIMAL(12,2) DEFAULT 0,
    placements_personnalises_json JSONB, -- Autres placements
    
    -- 🏠 IMMOBILIER 
    has_immobilier BOOLEAN DEFAULT FALSE,
    immobilier_value DECIMAL(12,2) DEFAULT 0,
    immobilier_data_json JSONB, -- Détails : type, surface, crédit
    
    -- 💎 AUTRES BIENS
    has_autres_biens BOOLEAN DEFAULT FALSE,
    autres_biens_value DECIMAL(12,2) DEFAULT 0,
    autres_biens_data_json JSONB, -- Art, bijoux, voitures
    
    -- ₿ CRYPTOMONNAIES
    cryptomonnaies_data_json JSONB, -- Symbol, quantity, valeur temps réel
    
    -- 💳 CRÉDITS
    credits_data_json JSONB, -- Crédits conso détaillés
    
    -- 💰 FLUX MENSUELS
    revenus_complementaires DECIMAL(12,2) DEFAULT 0,
    revenus_complementaires_json JSONB, -- Loyers, dividendes
    charges_mensuelles DECIMAL(12,2) DEFAULT 0,
    charges_mensuelles_json JSONB, -- Crédits, loyer
    
    -- ⏰ MÉTADONNÉES
    date_completed TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_investor_profiles_user ON investor_profiles(user_id);
CREATE INDEX idx_investor_profiles_risk ON investor_profiles(risk_tolerance);
```

**Contenu JSON exemples** :
```json
// liquidites_personnalisees_json
[{"name": "Livret BNP", "amount": 5000.0}]

// immobilier_data_json
[{
  "type": "Appartement",
  "description": "T3 Paris 11e", 
  "valeur": 450000,
  "surface": 65,
  "has_credit": true,
  "credit_montant": 320000,
  "credit_taux": 1.8,
  "credit_duree": 20
}]

// cryptomonnaies_data_json
[{"symbol": "BTC", "quantity": 0.5}, {"symbol": "ETH", "quantity": 2.0}]
```

---

### 3. 💳 **SUBSCRIPTIONS** (Abonnements)
```sql
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- Abonnement
    status VARCHAR(20) DEFAULT 'trial', -- 'active', 'trial', 'cancelled'
    tier VARCHAR(20) DEFAULT 'initia', -- 'initia', 'optima', 'ultima'
    price DECIMAL(8,2) DEFAULT 20.00,
    
    -- Dates
    start_date TIMESTAMPTZ DEFAULT NOW(),
    end_date TIMESTAMPTZ,
    next_billing_date TIMESTAMPTZ,
    trial_end_date TIMESTAMPTZ,
    cancelled_date TIMESTAMPTZ,
    created_date TIMESTAMPTZ DEFAULT NOW(),
    last_payment_date TIMESTAMPTZ,
    
    -- Paiement
    payment_method VARCHAR(50) DEFAULT 'simulation'
);
```

**Contenu** : Plan INITIA actif pour Hugues MARIE

---

### 4. 🏦 **PORTFOLIOS** (Portefeuilles)
```sql
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    strategy VARCHAR(50), -- 'conservateur', 'équilibré', 'dynamique'
    total_value DECIMAL(15,2) DEFAULT 0,
    created_date TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE portfolio_holdings (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    asset_type VARCHAR(50), -- 'stock', 'etf', 'crypto', 'bond'
    symbol VARCHAR(20),
    quantity DECIMAL(15,8),
    purchase_price DECIMAL(12,4),
    current_price DECIMAL(12,4),
    purchase_date TIMESTAMPTZ,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 5. 💰 **CREDITS** (Crédits détaillés)
```sql
CREATE TABLE credits (
    id SERIAL PRIMARY KEY,
    investor_profile_id INTEGER REFERENCES investor_profiles(id) ON DELETE CASCADE,
    
    -- Détails crédit
    credit_type VARCHAR(50), -- 'immobilier', 'auto', 'consommation'
    description VARCHAR(200),
    initial_amount DECIMAL(12,2),
    remaining_amount DECIMAL(12,2),
    interest_rate DECIMAL(5,4), -- Ex: 1.85 pour 1.85%
    duration_years INTEGER,
    monthly_payment DECIMAL(12,2),
    start_date DATE,
    end_date DATE,
    
    -- Métadonnées
    created_date TIMESTAMPTZ DEFAULT NOW(),
    updated_date TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 6. 💳 **PAYMENT_METHODS** (Moyens de paiement)
```sql
CREATE TABLE payment_methods (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    method_type VARCHAR(20), -- 'card', 'sepa', 'paypal'
    provider VARCHAR(50), -- 'stripe', 'paypal'
    provider_id VARCHAR(100),
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🔗 RELATIONS ET INDEX

### Relations principales :
```
users (1) ←→ (1) investor_profiles
users (1) ←→ (1) subscriptions  
users (1) ←→ (1) portfolios
users (1) ←→ (*) payment_methods
investor_profiles (1) ←→ (*) credits
portfolios (1) ←→ (*) portfolio_holdings
```

### Index de performance :
- Email utilisateurs (recherche rapide)
- Profil de risque (filtres admin)
- Dates de création (tri chronologique)
- JSON GIN indexes (recherche dans JSONB)

---

## 🎯 AVANTAGES POSTGRESQL

1. **JSONB** : Requêtes directes dans les données JSON complexes
2. **Types décimaux** : Précision parfaite pour l'argent
3. **Contraintes** : Validation au niveau base de données
4. **Performance** : Index sophistiqués, requêtes optimisées
5. **Extensibilité** : Prêt pour millions d'utilisateurs

---

## 📈 EXEMPLES DE DONNÉES

**User actuel** : Hugues MARIE
- Revenus: 4,500€/mois, Épargne: 1,000€/mois  
- Profil: Modéré, Intermédiaire, Moyen terme
- Objectifs: Constituer capital, Préparer retraite
- Patrimoine: Liquidités + Immobilier + Placements
- Abonnement: INITIA actif