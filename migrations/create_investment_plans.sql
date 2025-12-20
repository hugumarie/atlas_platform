-- Migration pour créer les tables de plan d'investissement
-- Date: 20 décembre 2025

-- Table des plans d'investissement
CREATE TABLE IF NOT EXISTS investment_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL DEFAULT 'Plan principal',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table des lignes de plan d'investissement
CREATE TABLE IF NOT EXISTS investment_plan_lines (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES investment_plans(id) ON DELETE CASCADE,
    support_envelope VARCHAR(100) NOT NULL,
    description VARCHAR(200) NOT NULL,
    reference VARCHAR(50),
    percentage FLOAT NOT NULL DEFAULT 0.0,
    order_index INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_investment_plans_user_active ON investment_plans(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_plan_lines_plan_order ON investment_plan_lines(plan_id, order_index);

-- Contraintes
ALTER TABLE investment_plan_lines ADD CONSTRAINT chk_percentage_positive CHECK (percentage >= 0);
ALTER TABLE investment_plan_lines ADD CONSTRAINT chk_percentage_max CHECK (percentage <= 100);

-- Trigger pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_investment_plan_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE OR REPLACE TRIGGER trigger_investment_plans_updated_at
    BEFORE UPDATE ON investment_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_investment_plan_updated_at();

CREATE OR REPLACE TRIGGER trigger_investment_plan_lines_updated_at
    BEFORE UPDATE ON investment_plan_lines
    FOR EACH ROW
    EXECUTE FUNCTION update_investment_plan_updated_at();

-- Commentaires pour documentation
COMMENT ON TABLE investment_plans IS 'Plans d investissement mensuel des utilisateurs';
COMMENT ON TABLE investment_plan_lines IS 'Lignes de détail des plans d investissement';
COMMENT ON COLUMN investment_plans.user_id IS 'ID de l utilisateur propriétaire du plan';
COMMENT ON COLUMN investment_plans.name IS 'Nom du plan (par défaut: Plan principal)';
COMMENT ON COLUMN investment_plans.is_active IS 'Indique si le plan est actif';
COMMENT ON COLUMN investment_plan_lines.support_envelope IS 'Type d enveloppe (PEA, Assurance Vie, etc.)';
COMMENT ON COLUMN investment_plan_lines.description IS 'Description du placement (ex: ETF World)';
COMMENT ON COLUMN investment_plan_lines.reference IS 'Référence du placement (ex: ISIN)';
COMMENT ON COLUMN investment_plan_lines.percentage IS 'Pourcentage du montant mensuel à investir';
COMMENT ON COLUMN investment_plan_lines.order_index IS 'Ordre d affichage des lignes';

-- Données de test (optionnel - à commenter en production)
/*
INSERT INTO investment_plans (user_id, name) VALUES (1, 'Plan principal') ON CONFLICT DO NOTHING;
INSERT INTO investment_plan_lines (plan_id, support_envelope, description, reference, percentage, order_index) VALUES 
    (1, 'PEA', 'ETF World', 'FR0011869353', 60.0, 1),
    (1, 'Assurance Vie', 'Fonds euros', '', 30.0, 2),
    (1, 'Livret A', 'Épargne de précaution', '', 10.0, 3)
ON CONFLICT DO NOTHING;
*/