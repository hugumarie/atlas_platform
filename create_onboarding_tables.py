"""
Script pour créer les tables nécessaires au système d'onboarding
À exécuter en local pour ajouter les nouvelles tables
"""

from app import create_app, db

# Importer les nouveaux modèles pour que SQLAlchemy les reconnaisse
from app.models.invitation_token import InvitationToken
from app.models.user_plan import UserPlan

def create_onboarding_tables():
    """
    Crée les nouvelles tables pour l'onboarding
    """
    app = create_app()
    
    with app.app_context():
        print("🔄 Création des tables d'onboarding...")
        
        # Créer les nouvelles tables seulement
        try:
            # Créer la table invitation_tokens
            db.create_all()
            
            print("✅ Tables créées avec succès :")
            print("  - invitation_tokens")
            print("  - user_plans")
            
            # Vérifier que les tables existent
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'invitation_tokens' in existing_tables:
                print("✅ Table 'invitation_tokens' confirmée")
            else:
                print("❌ Table 'invitation_tokens' non trouvée")
                
            if 'user_plans' in existing_tables:
                print("✅ Table 'user_plans' confirmée")
            else:
                print("❌ Table 'user_plans' non trouvée")
            
            print("\n🎯 Système d'onboarding prêt !")
            print("📝 Nouvelles fonctionnalités disponibles :")
            print("  - Tokens d'invitation sécurisés")
            print("  - Sélection de plans")
            print("  - Workflow complet prospect → client")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création des tables : {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    create_onboarding_tables()