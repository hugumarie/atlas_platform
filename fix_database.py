#!/usr/bin/env python3
"""
Script pour corriger la base de données - Ajouter les colonnes manquantes
"""

import psycopg2
import sys

def main():
    try:
        # Connexion à la base de données
        print("🔌 Connexion à la base de données...")
        conn = psycopg2.connect('postgresql://huguesmarie:@localhost:5432/atlas_db')
        cur = conn.cursor()
        
        # Liste des migrations à exécuter
        migrations = [
            "ALTER TABLE investor_profiles ADD COLUMN IF NOT EXISTS professional_situation_other VARCHAR(100);",
            "ALTER TABLE investor_profiles ADD COLUMN IF NOT EXISTS has_pel_cel BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE investor_profiles ADD COLUMN IF NOT EXISTS pel_cel_value DOUBLE PRECISION DEFAULT 0.0;",
            "ALTER TABLE investor_profiles ADD COLUMN IF NOT EXISTS has_scpi BOOLEAN DEFAULT FALSE;", 
            "ALTER TABLE investor_profiles ADD COLUMN IF NOT EXISTS scpi_value DOUBLE PRECISION DEFAULT 0.0;"
        ]
        
        # Exécuter chaque migration
        for i, migration in enumerate(migrations, 1):
            print(f"⚙️  Exécution migration {i}/{len(migrations)}...")
            cur.execute(migration)
            
        # Migration des données PEL/CEL si les anciens champs existent
        print("📊 Migration des données PEL/CEL...")
        try:
            cur.execute("""
                UPDATE investor_profiles 
                SET 
                    pel_cel_value = COALESCE(pel_value, 0) + COALESCE(cel_value, 0),
                    has_pel_cel = (COALESCE(pel_value, 0) + COALESCE(cel_value, 0)) > 0
                WHERE 
                    (pel_value IS NOT NULL AND pel_value > 0) 
                    OR (cel_value IS NOT NULL AND cel_value > 0);
            """)
            print("✅ Migration des données PEL/CEL terminée")
        except psycopg2.errors.UndefinedColumn:
            print("ℹ️  Anciens champs PEL/CEL non trouvés - migration des données ignorée")
        
        # Valider les changements
        conn.commit()
        print("✅ Toutes les migrations ont été appliquées avec succès!")
        
        # Vérifier que les colonnes ont été créées
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'investor_profiles' 
            AND column_name IN ('professional_situation_other', 'has_pel_cel', 'pel_cel_value', 'has_scpi', 'scpi_value')
            ORDER BY column_name;
        """)
        
        columns = cur.fetchall()
        print(f"📋 Colonnes créées : {', '.join([col[0] for col in columns])}")
        
    except psycopg2.Error as e:
        print(f"❌ Erreur de base de données : {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()
            print("🔌 Connexion fermée")

if __name__ == "__main__":
    main()