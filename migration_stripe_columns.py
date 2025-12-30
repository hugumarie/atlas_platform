#!/usr/bin/env python3
import psycopg2
import os

try:
    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    cur = conn.cursor()
    
    # Colonnes Stripe
    migrations = [
        "ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR(255)",
        "ALTER TABLE users ADD COLUMN subscription_date TIMESTAMP"
    ]
    
    for migration in migrations:
        try:
            cur.execute(migration)
            col_name = migration.split()[3]
            print(f"✅ {col_name} ajoutée")
        except Exception as e:
            if "already exists" in str(e):
                col_name = migration.split()[3]
                print(f"✅ {col_name} existe déjà")
            else:
                print(f"❌ Erreur: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Migration Stripe terminée")
except Exception as e:
    print(f"❌ Erreur: {e}")