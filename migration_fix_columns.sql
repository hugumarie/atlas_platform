-- Migration pour ajouter les nouveaux champs manquants
-- À exécuter dans PostgreSQL

-- Ajouter professional_situation_other
ALTER TABLE investor_profiles ADD COLUMN IF NOT EXISTS professional_situation_other VARCHAR(100);

-- Ajouter les nouveaux champs PEL/CEL et SCPI (si pas déjà fait)
ALTER TABLE investor_profiles ADD COLUMN IF NOT EXISTS has_pel_cel BOOLEAN DEFAULT FALSE;
ALTER TABLE investor_profiles ADD COLUMN IF NOT EXISTS pel_cel_value DOUBLE PRECISION DEFAULT 0.0;
ALTER TABLE investor_profiles ADD COLUMN IF NOT EXISTS has_scpi BOOLEAN DEFAULT FALSE;
ALTER TABLE investor_profiles ADD COLUMN IF NOT EXISTS scpi_value DOUBLE PRECISION DEFAULT 0.0;

-- Migrer les données PEL/CEL existantes vers le nouveau champ combiné (si les anciens existent)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='investor_profiles' AND column_name='pel_value') THEN
        UPDATE investor_profiles 
        SET 
            pel_cel_value = COALESCE(pel_value, 0) + COALESCE(cel_value, 0),
            has_pel_cel = (COALESCE(pel_value, 0) + COALESCE(cel_value, 0)) > 0
        WHERE 
            (pel_value IS NOT NULL AND pel_value > 0) 
            OR (cel_value IS NOT NULL AND cel_value > 0);
    END IF;
END $$;