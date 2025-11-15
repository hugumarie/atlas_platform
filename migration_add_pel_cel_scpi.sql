-- Migration pour ajouter les champs pel_cel_value et scpi_value
-- À exécuter dans PostgreSQL

-- Ajouter les nouveaux champs
ALTER TABLE investor_profiles ADD COLUMN IF NOT EXISTS has_pel_cel BOOLEAN DEFAULT FALSE;
ALTER TABLE investor_profiles ADD COLUMN IF NOT EXISTS pel_cel_value DOUBLE PRECISION DEFAULT 0.0;
ALTER TABLE investor_profiles ADD COLUMN IF NOT EXISTS has_scpi BOOLEAN DEFAULT FALSE;
ALTER TABLE investor_profiles ADD COLUMN IF NOT EXISTS scpi_value DOUBLE PRECISION DEFAULT 0.0;

-- Migrer les données PEL/CEL existantes vers le nouveau champ combiné (si elles existent)
UPDATE investor_profiles 
SET 
    pel_cel_value = COALESCE(pel_value, 0) + COALESCE(cel_value, 0),
    has_pel_cel = (COALESCE(pel_value, 0) + COALESCE(cel_value, 0)) > 0
WHERE 
    (pel_value IS NOT NULL AND pel_value > 0) 
    OR (cel_value IS NOT NULL AND cel_value > 0);

-- Supprimer les anciens champs PEL/CEL séparés (optionnel, à faire plus tard)
-- ALTER TABLE investor_profiles DROP COLUMN IF EXISTS has_pel;
-- ALTER TABLE investor_profiles DROP COLUMN IF EXISTS pel_value;
-- ALTER TABLE investor_profiles DROP COLUMN IF EXISTS has_cel;
-- ALTER TABLE investor_profiles DROP COLUMN IF EXISTS cel_value;