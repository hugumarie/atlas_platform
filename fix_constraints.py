#!/usr/bin/env python3
"""
Script pour corriger les contraintes de validation de la base de données
"""

import psycopg2
import sys

def main():
    try:
        # Connexion à la base de données
        print("🔌 Connexion à la base de données...")
        conn = psycopg2.connect('postgresql://huguesmarie:@localhost:5432/atlas_db')
        cur = conn.cursor()
        
        # Vérifier les contraintes existantes
        print("🔍 Vérification des contraintes existantes...")
        cur.execute("""
            SELECT conname, contype, pg_get_constraintdef(oid) as constraint_def
            FROM pg_constraint 
            WHERE conrelid = 'investor_profiles'::regclass 
            AND contype = 'c';
        """)
        
        constraints = cur.fetchall()
        print(f"📋 Contraintes trouvées : {len(constraints)}")
        
        for constraint in constraints:
            print(f"  - {constraint[0]}: {constraint[2]}")
        
        # Corriger la contrainte chk_investment_experience
        print("⚙️  Correction de la contrainte chk_investment_experience...")
        
        # Supprimer l'ancienne contrainte
        try:
            cur.execute("ALTER TABLE investor_profiles DROP CONSTRAINT IF EXISTS chk_investment_experience;")
            print("✅ Ancienne contrainte supprimée")
        except Exception as e:
            print(f"ℹ️  Pas d'ancienne contrainte à supprimer : {e}")
        
        # Ajouter la nouvelle contrainte avec les bonnes valeurs
        cur.execute("""
            ALTER TABLE investor_profiles 
            ADD CONSTRAINT chk_investment_experience 
            CHECK (investment_experience IN ('débutant', 'débutante', 'intermédiaire', 'intermediaire', 'confirmé', 'confirmée', 'expert', 'experte'));
        """)
        print("✅ Nouvelle contrainte investment_experience créée")
        
        # Corriger d'autres contraintes potentiellement problématiques
        print("⚙️  Correction d'autres contraintes...")
        
        # Contrainte risk_tolerance
        try:
            cur.execute("ALTER TABLE investor_profiles DROP CONSTRAINT IF EXISTS chk_risk_tolerance;")
            cur.execute("""
                ALTER TABLE investor_profiles 
                ADD CONSTRAINT chk_risk_tolerance 
                CHECK (risk_tolerance IN ('conservateur', 'conservatrice', 'modéré', 'modérée', 'modere', 'moderee', 'dynamique', 'agressif', 'agressive'));
            """)
            print("✅ Contrainte risk_tolerance mise à jour")
        except Exception as e:
            print(f"ℹ️  Contrainte risk_tolerance : {e}")
        
        # Contrainte investment_horizon
        try:
            cur.execute("ALTER TABLE investor_profiles DROP CONSTRAINT IF EXISTS chk_investment_horizon;")
            cur.execute("""
                ALTER TABLE investor_profiles 
                ADD CONSTRAINT chk_investment_horizon 
                CHECK (investment_horizon IN ('court', 'court terme', 'moyen', 'moyen terme', 'long', 'long terme'));
            """)
            print("✅ Contrainte investment_horizon mise à jour")
        except Exception as e:
            print(f"ℹ️  Contrainte investment_horizon : {e}")
            
        # Valider les changements
        conn.commit()
        print("✅ Toutes les contraintes ont été corrigées!")
        
        # Vérifier les nouvelles contraintes
        print("🔍 Vérification des nouvelles contraintes...")
        cur.execute("""
            SELECT conname, pg_get_constraintdef(oid) as constraint_def
            FROM pg_constraint 
            WHERE conrelid = 'investor_profiles'::regclass 
            AND contype = 'c'
            AND conname LIKE 'chk_%';
        """)
        
        new_constraints = cur.fetchall()
        for constraint in new_constraints:
            print(f"  ✓ {constraint[0]}: {constraint[1]}")
        
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