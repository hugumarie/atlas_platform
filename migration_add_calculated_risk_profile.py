"""
Migration pour ajouter le champ calculated_risk_profile à la table investor_profiles
"""

from app import create_app, db
from app.models.investor_profile import InvestorProfile
from sqlalchemy import text

def add_calculated_risk_profile_column():
    """Ajoute la colonne calculated_risk_profile si elle n'existe pas"""
    
    app = create_app()
    with app.app_context():
        try:
            # Vérifier si la colonne existe déjà
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'investor_profiles' 
                AND column_name = 'calculated_risk_profile'
            """))
            
            if result.fetchone():
                print("✅ La colonne 'calculated_risk_profile' existe déjà")
                return
            
            # Ajouter la colonne
            print("🔄 Ajout de la colonne 'calculated_risk_profile'...")
            db.session.execute(text("""
                ALTER TABLE investor_profiles 
                ADD COLUMN calculated_risk_profile VARCHAR(20)
            """))
            
            # Calculer le profil pour tous les profils existants qui ont les 5 réponses
            print("🎯 Calcul du profil de risque pour tous les utilisateurs existants...")
            profiles = InvestorProfile.query.filter(
                InvestorProfile.tolerance_risque.isnot(None),
                InvestorProfile.horizon_placement.isnot(None),
                InvestorProfile.besoin_liquidite.isnot(None),
                InvestorProfile.experience_investissement.isnot(None),
                InvestorProfile.attitude_volatilite.isnot(None)
            ).all()
            
            updated_count = 0
            for profile in profiles:
                try:
                    calculated_profile = profile.calculate_risk_profile()
                    if calculated_profile:
                        profile.calculated_risk_profile = calculated_profile
                        updated_count += 1
                        print(f"   ✅ User {profile.user_id}: {calculated_profile}")
                except Exception as e:
                    print(f"   ❌ Erreur pour user {profile.user_id}: {e}")
            
            db.session.commit()
            print(f"✅ Migration terminée ! {updated_count} profils mis à jour")
            
        except Exception as e:
            print(f"❌ Erreur lors de la migration: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    add_calculated_risk_profile_column()