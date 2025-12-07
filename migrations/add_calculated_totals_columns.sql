-- Migration pour ajouter les colonnes de totaux calculés
-- Ajoute les colonnes pour stocker tous les totaux patrimoniaux calculés

-- Ajouter les colonnes pour les totaux calculés
ALTER TABLE investor_profiles 
ADD COLUMN calculated_total_liquidites FLOAT DEFAULT 0.0,
ADD COLUMN calculated_total_placements FLOAT DEFAULT 0.0,
ADD COLUMN calculated_total_immobilier_net FLOAT DEFAULT 0.0,
ADD COLUMN calculated_total_cryptomonnaies FLOAT DEFAULT 0.0,
ADD COLUMN calculated_total_autres_biens FLOAT DEFAULT 0.0,
ADD COLUMN calculated_total_credits_consommation FLOAT DEFAULT 0.0,
ADD COLUMN calculated_total_actifs FLOAT DEFAULT 0.0,
ADD COLUMN calculated_patrimoine_total_net FLOAT DEFAULT 0.0,
ADD COLUMN last_calculation_date TIMESTAMP;

-- Commentaires pour documenter les colonnes
COMMENT ON COLUMN investor_profiles.calculated_total_liquidites IS 'Total des liquidités calculé et sauvegardé';
COMMENT ON COLUMN investor_profiles.calculated_total_placements IS 'Total des placements financiers calculé et sauvegardé';
COMMENT ON COLUMN investor_profiles.calculated_total_immobilier_net IS 'Total immobilier net (valeur - crédits immobiliers) calculé et sauvegardé';
COMMENT ON COLUMN investor_profiles.calculated_total_cryptomonnaies IS 'Total des cryptomonnaies avec prix actuels calculé et sauvegardé';
COMMENT ON COLUMN investor_profiles.calculated_total_autres_biens IS 'Total des autres biens calculé et sauvegardé';
COMMENT ON COLUMN investor_profiles.calculated_total_credits_consommation IS 'Total des crédits de consommation restants calculé et sauvegardé';
COMMENT ON COLUMN investor_profiles.calculated_total_actifs IS 'Total de tous les actifs calculé et sauvegardé';
COMMENT ON COLUMN investor_profiles.calculated_patrimoine_total_net IS 'Patrimoine total net (actifs - crédits) calculé et sauvegardé';
COMMENT ON COLUMN investor_profiles.last_calculation_date IS 'Date de dernière mise à jour des calculs patrimoniaux';