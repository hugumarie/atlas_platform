#!/usr/bin/env python3
"""
Migration pour ajouter les champs Stripe aux modèles User et Subscription existants.
À exécuter une seule fois avant le déploiement de l'intégration Stripe.
"""

from app import create_app, db
from sqlalchemy import text

def migrate_stripe_fields():
    """Ajoute les champs Stripe aux tables existantes"""
    
    app = create_app()
    
    with app.app_context():
        print("🔄 Migration des champs Stripe...")
        
        try:
            # 1. Ajouter les champs Stripe à la table users
            print("📝 Ajout des champs Stripe à la table 'users'...")
            
            # Vérifier si les colonnes existent déjà
            result = db.session.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'stripe_customer_id';
            """))
            
            if not result.fetchone():
                # Ajouter stripe_customer_id
                db.session.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN stripe_customer_id VARCHAR(100) UNIQUE;
                """))
                print("  ✅ Champ stripe_customer_id ajouté")
            else:
                print("  ℹ️ Champ stripe_customer_id déjà présent")
            
            # Vérifier subscription_date
            result = db.session.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'subscription_date';
            """))
            
            if not result.fetchone():
                # Ajouter subscription_date
                db.session.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN subscription_date TIMESTAMP;
                """))
                print("  ✅ Champ subscription_date ajouté")
            else:
                print("  ℹ️ Champ subscription_date déjà présent")
                
            # 2. Ajouter les champs Stripe à la table subscriptions
            print("📝 Ajout des champs Stripe à la table 'subscriptions'...")
            
            stripe_fields = [
                ('stripe_subscription_id', 'VARCHAR(100) UNIQUE'),
                ('stripe_customer_id', 'VARCHAR(100)'),
                ('current_period_start', 'TIMESTAMP'),
                ('current_period_end', 'TIMESTAMP'),
                ('canceled_at', 'TIMESTAMP'),
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            ]
            
            for field_name, field_type in stripe_fields:
                # Vérifier si la colonne existe
                result = db.session.execute(text(f"""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'subscriptions' AND column_name = '{field_name}';
                """))
                
                if not result.fetchone():
                    # Ajouter la colonne
                    db.session.execute(text(f"""
                        ALTER TABLE subscriptions 
                        ADD COLUMN {field_name} {field_type};
                    """))
                    print(f"  ✅ Champ {field_name} ajouté")
                else:
                    print(f"  ℹ️ Champ {field_name} déjà présent")
            
            # Commiter les changements
            db.session.commit()
            print("\n✅ Migration des champs Stripe terminée avec succès !")
            
            # 3. Afficher un résumé des tables modifiées
            print("\n📊 Résumé de la migration :")
            
            # Compter les utilisateurs
            user_count = db.session.execute(text("SELECT COUNT(*) FROM users;")).scalar()
            print(f"   👥 {user_count} utilisateurs dans la base")
            
            # Compter les abonnements
            sub_count = db.session.execute(text("SELECT COUNT(*) FROM subscriptions;")).scalar()
            print(f"   💳 {sub_count} abonnements dans la base")
            
            print("\n🎯 Les modèles sont maintenant prêts pour l'intégration Stripe !")
            
        except Exception as e:
            print(f"❌ Erreur lors de la migration : {str(e)}")
            db.session.rollback()
            return False
            
        return True

def verify_stripe_fields():
    """Vérifie que les champs Stripe ont été correctement ajoutés"""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 Vérification des champs Stripe...")
        
        try:
            # Vérifier les champs users
            users_fields = db.session.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name IN ('stripe_customer_id', 'subscription_date')
                ORDER BY column_name;
            """)).fetchall()
            
            print(f"📋 Champs Stripe dans 'users' : {[field[0] for field in users_fields]}")
            
            # Vérifier les champs subscriptions
            sub_fields = db.session.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'subscriptions' AND column_name LIKE '%stripe%' OR column_name IN ('current_period_start', 'current_period_end', 'canceled_at', 'updated_at')
                ORDER BY column_name;
            """)).fetchall()
            
            print(f"📋 Champs Stripe dans 'subscriptions' : {[field[0] for field in sub_fields]}")
            
            return len(users_fields) >= 2 and len(sub_fields) >= 6
            
        except Exception as e:
            print(f"❌ Erreur lors de la vérification : {str(e)}")
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("    MIGRATION STRIPE - ATLAS")
    print("=" * 60)
    
    # Exécuter la migration
    success = migrate_stripe_fields()
    
    if success:
        # Vérifier que tout s'est bien passé
        if verify_stripe_fields():
            print("\n🎉 Migration et vérification réussies !")
            exit(0)
        else:
            print("\n⚠️ Migration effectuée mais vérification échouée")
            exit(1)
    else:
        print("\n❌ Échec de la migration")
        exit(1)