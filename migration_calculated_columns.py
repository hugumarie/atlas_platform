#!/usr/bin/env python3
import psycopg2
import os

try:
    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    
    # Colonnes calculées investor_profiles - une transaction par colonne
    migrations = [
        "ALTER TABLE investor_profiles ADD COLUMN calculated_total_liquidites FLOAT DEFAULT 0.0",
        "ALTER TABLE investor_profiles ADD COLUMN calculated_total_placements FLOAT DEFAULT 0.0",
        "ALTER TABLE investor_profiles ADD COLUMN calculated_total_immobilier_net FLOAT DEFAULT 0.0",
        "ALTER TABLE investor_profiles ADD COLUMN calculated_total_cryptomonnaies FLOAT DEFAULT 0.0",
        "ALTER TABLE investor_profiles ADD COLUMN calculated_total_autres_biens FLOAT DEFAULT 0.0",
        "ALTER TABLE investor_profiles ADD COLUMN calculated_patrimoine_total_net FLOAT DEFAULT 0.0",
        "ALTER TABLE investor_profiles ADD COLUMN last_calculation_date TIMESTAMP"
    ]
    
    for migration in migrations:
        try:
            cur = conn.cursor()
            cur.execute(migration)
            conn.commit()
            col_name = migration.split()[3].replace("calculated_", "")
            print(f"✅ {col_name} ajoutée")
            cur.close()
        except Exception as e:
            if "already exists" in str(e):
                conn.rollback()
                col_name = migration.split()[3].replace("calculated_", "")
                print(f"✅ {col_name} existe déjà")
            else:
                conn.rollback()
                print(f"❌ Erreur: {e}")
            if 'cur' in locals():
                cur.close()
    
    conn.close()
    print("✅ Migration colonnes calculées terminée")
except Exception as e:
    print(f"❌ Erreur: {e}")