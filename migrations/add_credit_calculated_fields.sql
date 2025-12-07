-- Migration pour ajouter les champs calculés automatiquement au modèle Credit
-- Date: 2024-11-17
-- Description: Ajoute les colonnes pour stocker les calculs automatiques de crédits

-- Ajout des nouvelles colonnes au modèle Credit
ALTER TABLE credits 
ADD COLUMN IF NOT EXISTS calculated_monthly_payment FLOAT,
ADD COLUMN IF NOT EXISTS calculated_remaining_capital FLOAT,
ADD COLUMN IF NOT EXISTS last_calculation_date TIMESTAMP;

-- Ajout des commentaires pour documentation
COMMENT ON COLUMN credits.calculated_monthly_payment IS 'Mensualité calculée automatiquement selon formule amortissement';
COMMENT ON COLUMN credits.calculated_remaining_capital IS 'Capital restant calculé automatiquement selon amortissement';
COMMENT ON COLUMN credits.last_calculation_date IS 'Date du dernier calcul automatique';

-- Création d'un index sur la date de calcul pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_credits_last_calculation_date ON credits(last_calculation_date);

-- Mise à jour des données existantes (optionnel - peut être fait via l'application)
-- UPDATE credits SET last_calculation_date = NOW() WHERE last_calculation_date IS NULL;

COMMIT;