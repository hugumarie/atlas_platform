#!/usr/bin/env python3
"""
Script de migration pour restructurer la section patrimoine
- Supprime : has_current_account, current_account_value, has_lep, lep_value
- Ajoute : has_pel, pel_value, has_cel, cel_value, has_autres_livrets, autres_livrets_value
"""

import sqlite3
import os

def migrate_patrimoine_database():
    """Migre la base de données pour la nouvelle structure patrimoine"""
    
    # Chemin vers la base de données
    db_path = "instance/patrimoine.db"
    
    if not os.path.exists(db_path):
        print(f"Erreur: Base de données {db_path} introuvable")
        return False
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Migration de la base de données patrimoine...")
        
        # Étape 1: Vérifier les colonnes existantes
        cursor.execute("PRAGMA table_info(investor_profiles)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Colonnes existantes: {columns}")
        
        # Étape 2: Supprimer les anciennes colonnes si elles existent
        columns_to_remove = ['has_current_account', 'current_account_value', 'has_lep', 'lep_value']
        
        # SQLite ne supporte pas DROP COLUMN directement, on doit recréer la table
        print("🗑️  Suppression des colonnes obsolètes...")
        
        # Créer une nouvelle table temporaire sans les colonnes à supprimer
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS investor_profiles_temp AS
            SELECT id, user_id, monthly_net_income, current_savings, monthly_savings_capacity,
                   risk_tolerance, investment_experience, investment_goals, investment_horizon,
                   family_situation, professional_situation, civilite, date_naissance, lieu_naissance,
                   nationalite, pays_residence, pays_residence_fiscal, metier, revenus_complementaires,
                   revenus_complementaires_json, charges_mensuelles, charges_mensuelles_json,
                   has_real_estate, real_estate_value, has_immobilier, immobilier_value,
                   has_autres_biens, autres_biens_value, has_life_insurance, life_insurance_value,
                   has_pea, pea_value, has_livret_a, livret_a_value, has_ldds, ldds_value,
                   has_per, per_value, has_pee, pee_value, other_investments,
                   objectif_constitution_epargne, objectif_retraite, objectif_transmission,
                   objectif_defiscalisation, objectif_immobilier, profil_risque_connu,
                   profil_risque_choisi, question_1_reponse, question_2_reponse, question_3_reponse,
                   question_4_reponse, question_5_reponse, synthese_profil_risque,
                   date_completed, last_updated
            FROM investor_profiles
        """)
        
        # Supprimer l'ancienne table et renommer la nouvelle
        cursor.execute("DROP TABLE investor_profiles")
        cursor.execute("ALTER TABLE investor_profiles_temp RENAME TO investor_profiles")
        
        # Étape 3: Ajouter les nouvelles colonnes
        print("➕ Ajout des nouvelles colonnes...")
        
        new_columns = [
            ("has_pel", "BOOLEAN", "FALSE"),
            ("pel_value", "REAL", "0.0"),
            ("has_cel", "BOOLEAN", "FALSE"), 
            ("cel_value", "REAL", "0.0"),
            ("has_autres_livrets", "BOOLEAN", "FALSE"),
            ("autres_livrets_value", "REAL", "0.0")
        ]
        
        for column_name, column_type, default_value in new_columns:
            try:
                cursor.execute(f"ALTER TABLE investor_profiles ADD COLUMN {column_name} {column_type} DEFAULT {default_value}")
                print(f"  ✅ Colonne {column_name} ajoutée")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"  ⚠️  Colonne {column_name} existe déjà")
                else:
                    raise
        
        # Validation finale
        cursor.execute("PRAGMA table_info(investor_profiles)")
        final_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Colonnes finales: {final_columns}")
        
        # Compter les profils
        cursor.execute("SELECT COUNT(*) FROM investor_profiles")
        profile_count = cursor.fetchone()[0]
        print(f"👥 {profile_count} profils d'investisseurs dans la base")
        
        # Valider les modifications
        conn.commit()
        print("✅ Migration terminée avec succès!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_patrimoine_database()