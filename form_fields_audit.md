# AUDIT COMPLET DES CHAMPS DU FORMULAIRE INVESTISSEUR

## SECTION 1: INFORMATIONS PERSONNELLES
- `civilite` (select)
- `last_name` (text)
- `first_name` (text) 
- `family_situation` (select)
- `phone` (tel)
- `nationalite` (select)
- `date_naissance` (date)
- `lieu_naissance` (text)
- `pays_residence` (text)

## SECTION 2: OBJECTIFS D'INVESTISSEMENT
- `objectif_premiers_pas` (checkbox)
- `objectif_constituer_capital` (checkbox)
- `objectif_diversifier` (checkbox)
- `objectif_optimiser_rendement` (checkbox)
- `objectif_preparer_retraite` (checkbox)
- `objectif_securite_financiere` (checkbox)
- `objectif_projet_immobilier` (checkbox)
- `objectif_revenus_complementaires` (checkbox)
- `objectif_transmettre_capital` (checkbox)
- `objectif_proteger_famille` (checkbox)

## SECTION 3: PROFIL DE RISQUE
- `tolerance_risque` (radio: faible/moderee/elevee)
- `horizon_placement` (radio: court/moyen/long)
- `besoin_liquidite` (radio: court_terme/long_terme)
- `experience_investissement` (radio: debutant/intermediaire/confirme)
- `attitude_volatilite` (radio: vendre/attendre/investir_plus)

## SECTION 4: REVENUS
- `professional_situation` (select)
- `professional_situation_other` (text)
- `metier` (text)
- `monthly_net_income` (number)
- `impots_mensuels` (number)
- `monthly_savings_capacity` (number)
- `revenu_complementaire_name[]` (text array)
- `revenu_complementaire_amount[]` (number array)
- `charge_mensuelle_name[]` (text array)
- `charge_mensuelle_amount[]` (number array)

## SECTION 3: EPARGNE
### Liquidités
- `livret_a_value` (number)
- `ldds_value` (number)
- `pel_cel_value` (number)
- `liquidite_personnalisee_name[]` (text array)
- `liquidite_personnalisee_amount[]` (number array)

### Placements
- `pea_value` (number)
- `cto_value` (number)
- `life_insurance_value` (number)
- `per_value` (number)
- `pee_value` (number)
- `private_equity_value` (number)
- `scpi_value` (number)
- `placement_personnalise_name[]` (text array)
- `placement_personnalise_amount[]` (number array)

## SECTION: IMMOBILIER
- `bien_type[]` (select array)
- `bien_description[]` (text array)
- `bien_valeur[]` (number array)
- `bien_surface[]` (number array)
- `bien_has_credit[]` (checkbox array)
- `credit_montant[]` (number array)
- `credit_duree[]` (number array)
- `credit_tag[]` (number array - TAU)
- `credit_taeg[]` (number array - TAEG)
- `credit_date[]` (month array)

## SECTION: CRYPTOMONNAIES
- `crypto_symbol[]` (select array)
- `crypto_quantity[]` (number array)

## SECTION: AUTRES BIENS
- `autre_bien_name[]` (text array)
- `autre_bien_description[]` (text array)
- `autre_bien_valeur[]` (number array)

## SECTION: CRÉDITS
- `credit_description[]` (text array)
- `credit_montant_initial[]` (number array)
- `credit_taux[]` (number array)
- `credit_duree[]` (number array)
- `credit_date_depart[]` (month array)