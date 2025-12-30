#!/usr/bin/env python3
import psycopg2
import os

try:
    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    
    # Colonnes Stripe - une transaction par colonne
    migrations = [
        "ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR(255)",
        "ALTER TABLE users ADD COLUMN subscription_date TIMESTAMP"
    ]
    
    for migration in migrations:
        try:
            cur = conn.cursor()
            cur.execute(migration)
            conn.commit()
            col_name = migration.split()[3]
            print(f"✅ {col_name} ajoutée")
            cur.close()
        except Exception as e:
            if "already exists" in str(e):
                conn.rollback()
                col_name = migration.split()[3]
                print(f"✅ {col_name} existe déjà")
            else:
                conn.rollback()
                print(f"❌ Erreur: {e}")
            if 'cur' in locals():
                cur.close()
    
    conn.close()
    print("✅ Migration Stripe terminée")
except Exception as e:
    print(f"❌ Erreur: {e}")