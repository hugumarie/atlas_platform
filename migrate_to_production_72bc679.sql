-- ====================================================
-- MIGRATION SCRIPT POUR PRODUCTION - Commit 72bc679
-- Atlas Invest - Résolution problèmes Stripe + UX
-- Date: 30 Décembre 2024
-- ====================================================

-- 1. SAUVEGARDE AUTOMATIQUE (à exécuter avant cette migration)
-- pg_dump -h localhost -U atlas_user atlas_production > /backup/atlas_backup_$(date +%Y%m%d_%H%M%S).sql

BEGIN;

-- ====================================================
-- 2. CRÉATION TABLE INVESTMENT_ACTIONS (si n'existe pas)
-- ====================================================

CREATE TABLE IF NOT EXISTS investment_actions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    year_month VARCHAR(7) NOT NULL, -- Format YYYY-MM
    support_type VARCHAR(50) NOT NULL, -- 'PEA', 'CTO', 'Assurance Vie', etc.
    label VARCHAR(200) NOT NULL, -- Description de l'action
    expected_amount DECIMAL(10,2) NOT NULL, -- Montant attendu
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'done', 'skipped'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    CONSTRAINT chk_investment_actions_status CHECK (status IN ('pending', 'done', 'skipped'))
);

-- Index pour les performances
CREATE INDEX IF NOT EXISTS idx_investment_actions_user_month 
ON investment_actions(user_id, year_month);

CREATE INDEX IF NOT EXISTS idx_investment_actions_status 
ON investment_actions(status);

CREATE INDEX IF NOT EXISTS idx_investment_actions_created 
ON investment_actions(created_at);

-- ====================================================
-- 3. MISE À JOUR CONTRAINTES INVESTOR_PROFILES
-- ====================================================

-- Supprimer les contraintes trop restrictives
ALTER TABLE investor_profiles DROP CONSTRAINT IF EXISTS chk_investment_horizon;
ALTER TABLE investor_profiles DROP CONSTRAINT IF EXISTS chk_risk_tolerance;

-- Recréer avec valeurs correctes
ALTER TABLE investor_profiles 
ADD CONSTRAINT chk_investment_horizon 
CHECK (investment_horizon IN (
    'court', 'court terme', 
    'moyen', 'moyen terme', 
    'long', 'long terme'
));

ALTER TABLE investor_profiles 
ADD CONSTRAINT chk_risk_tolerance 
CHECK (risk_tolerance IN (
    'conservateur', 'conservatrice', 
    'modéré', 'modérée', 'modere', 'moderee',
    'dynamique', 
    'agressif', 'agressive'
));

-- ====================================================
-- 4. CORRECTION DONNÉES EXISTANTES
-- ====================================================

-- Corriger les valeurs non conformes dans investment_horizon
UPDATE investor_profiles 
SET investment_horizon = 'court terme' 
WHERE investment_horizon IN ('court_terme', 'court-terme') 
   OR investment_horizon IS NULL;

UPDATE investor_profiles 
SET investment_horizon = 'moyen terme' 
WHERE investment_horizon IN ('moyen_terme', 'moyen-terme');

UPDATE investor_profiles 
SET investment_horizon = 'long terme' 
WHERE investment_horizon IN ('long_terme', 'long-terme');

-- Corriger les valeurs non conformes dans risk_tolerance  
UPDATE investor_profiles 
SET risk_tolerance = 'conservateur' 
WHERE risk_tolerance IN ('non_defini', 'non-defini', 'conservative', 'prudent') 
   OR risk_tolerance IS NULL;

UPDATE investor_profiles 
SET risk_tolerance = 'modere' 
WHERE risk_tolerance IN ('équilibré', 'equilibre', 'moderate', 'balanced');

UPDATE investor_profiles 
SET risk_tolerance = 'dynamique' 
WHERE risk_tolerance IN ('offensif', 'agressif', 'aggressive', 'dynamic');

-- S'assurer que monthly_net_income, current_savings, monthly_savings_capacity ne sont pas NULL
UPDATE investor_profiles 
SET monthly_net_income = 0.0 
WHERE monthly_net_income IS NULL;

UPDATE investor_profiles 
SET current_savings = 0.0 
WHERE current_savings IS NULL;

UPDATE investor_profiles 
SET monthly_savings_capacity = 0.0 
WHERE monthly_savings_capacity IS NULL;

-- ====================================================
-- 5. VÉRIFICATION UTILISATEURS SANS PROFIL
-- ====================================================

-- Lister les utilisateurs clients sans profil investisseur
-- (Pour information - ces profils seront créés automatiquement par l'application)
DO $$ 
DECLARE 
    missing_profiles_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO missing_profiles_count
    FROM users u 
    LEFT JOIN investor_profiles ip ON u.id = ip.user_id 
    WHERE ip.id IS NULL 
      AND u.user_type = 'client' 
      AND u.is_active = TRUE;
    
    RAISE NOTICE 'Utilisateurs sans profil investisseur: %', missing_profiles_count;
    
    IF missing_profiles_count > 0 THEN
        RAISE NOTICE 'Ces profils seront créés automatiquement lors de la première connexion';
    END IF;
END $$;

-- ====================================================
-- 6. VÉRIFICATION ABONNEMENTS STRIPE
-- ====================================================

-- Vérifier les abonnements sans stripe_subscription_id
-- (Peut indiquer des problèmes de webhook à corriger manuellement)
DO $$ 
DECLARE 
    missing_stripe_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO missing_stripe_count
    FROM subscriptions s
    JOIN users u ON s.user_id = u.id
    WHERE s.stripe_subscription_id IS NULL 
      AND s.status = 'active'
      AND u.user_type = 'client';
    
    RAISE NOTICE 'Abonnements actifs sans stripe_subscription_id: %', missing_stripe_count;
    
    IF missing_stripe_count > 0 THEN
        RAISE WARNING 'ATTENTION: % abonnements actifs sans ID Stripe - Vérifier manuellement', missing_stripe_count;
    END IF;
END $$;

-- ====================================================
-- 7. NETTOYAGE ET OPTIMISATION
-- ====================================================

-- Mettre à jour les statistiques pour l'optimiseur
ANALYZE investor_profiles;
ANALYZE investment_actions;
ANALYZE users;
ANALYZE subscriptions;

-- Vérifier l'intégrité référentielle
DO $$ 
DECLARE 
    orphaned_profiles INTEGER;
    orphaned_subscriptions INTEGER;
BEGIN
    -- Profils orphelins
    SELECT COUNT(*) INTO orphaned_profiles
    FROM investor_profiles ip
    LEFT JOIN users u ON ip.user_id = u.id
    WHERE u.id IS NULL;
    
    -- Abonnements orphelins  
    SELECT COUNT(*) INTO orphaned_subscriptions
    FROM subscriptions s
    LEFT JOIN users u ON s.user_id = u.id
    WHERE u.id IS NULL;
    
    IF orphaned_profiles > 0 THEN
        RAISE WARNING 'ATTENTION: % profils investisseurs orphelins détectés', orphaned_profiles;
    END IF;
    
    IF orphaned_subscriptions > 0 THEN
        RAISE WARNING 'ATTENTION: % abonnements orphelins détectés', orphaned_subscriptions;
    END IF;
END $$;

-- ====================================================
-- 8. VALIDATION FINALE
-- ====================================================

-- Vérifier que toutes les contraintes sont respectées
DO $$ 
DECLARE 
    invalid_horizons INTEGER;
    invalid_tolerance INTEGER;
    null_income INTEGER;
BEGIN
    -- Vérifier investment_horizon
    SELECT COUNT(*) INTO invalid_horizons
    FROM investor_profiles 
    WHERE investment_horizon NOT IN ('court', 'court terme', 'moyen', 'moyen terme', 'long', 'long terme')
       OR investment_horizon IS NULL;
    
    -- Vérifier risk_tolerance
    SELECT COUNT(*) INTO invalid_tolerance
    FROM investor_profiles 
    WHERE risk_tolerance NOT IN ('conservateur', 'conservatrice', 'modéré', 'modérée', 'modere', 'moderee', 'dynamique', 'agressif', 'agressive')
       OR risk_tolerance IS NULL;
    
    -- Vérifier monthly_net_income
    SELECT COUNT(*) INTO null_income
    FROM investor_profiles 
    WHERE monthly_net_income IS NULL;
    
    IF invalid_horizons > 0 THEN
        RAISE EXCEPTION 'ERREUR: % profils avec investment_horizon invalide', invalid_horizons;
    END IF;
    
    IF invalid_tolerance > 0 THEN
        RAISE EXCEPTION 'ERREUR: % profils avec risk_tolerance invalide', invalid_tolerance;
    END IF;
    
    IF null_income > 0 THEN
        RAISE EXCEPTION 'ERREUR: % profils avec monthly_net_income NULL', null_income;
    END IF;
    
    RAISE NOTICE 'VALIDATION OK: Toutes les contraintes sont respectées';
END $$;

-- ====================================================
-- 9. LOG DE LA MIGRATION
-- ====================================================

-- Créer une table de log des migrations si elle n'existe pas
CREATE TABLE IF NOT EXISTS migration_log (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    executed_by VARCHAR(100) DEFAULT CURRENT_USER,
    success BOOLEAN DEFAULT TRUE
);

-- Enregistrer cette migration
INSERT INTO migration_log (version, description, success) 
VALUES (
    '72bc679', 
    'Major Fix: Résolution problèmes Stripe + Onboarding + UX - Création investment_actions, correction contraintes profiles', 
    TRUE
);

COMMIT;

-- ====================================================
-- 10. RAPPORT FINAL
-- ====================================================

SELECT 
    'MIGRATION 72bc679 TERMINÉE AVEC SUCCÈS' AS status,
    NOW() AS completed_at,
    (SELECT COUNT(*) FROM users WHERE user_type = 'client') AS total_clients,
    (SELECT COUNT(*) FROM investor_profiles) AS total_profiles,
    (SELECT COUNT(*) FROM subscriptions WHERE status = 'active') AS active_subscriptions,
    (SELECT COUNT(*) FROM investment_actions) AS investment_actions_created;

-- Instructions post-migration
\echo ''
\echo '======================================================'
\echo 'MIGRATION 72bc679 TERMINÉE'
\echo '======================================================'
\echo ''
\echo 'PROCHAINES ÉTAPES:'
\echo '1. Redémarrer l''application Atlas'
\echo '2. Tester la création d''un nouveau compte'
\echo '3. Vérifier la connexion utilisateurs existants'
\echo '4. Contrôler les logs d''erreur'
\echo ''
\echo 'En cas de problème:'
\echo '- Consulter /var/log/atlas/application.log'
\echo '- Restaurer depuis /backup/atlas_backup_*.sql'
\echo ''
\echo '======================================================'