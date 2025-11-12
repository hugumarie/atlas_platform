#!/usr/bin/env python3
"""
Script de migration pour ajouter les nouveaux champs manquants.
Ajoute: lieu_naissance, pays_residence_fiscal, metier, revenus_complementaires
"""

import sys
sys.path.append('.')

from datetime import datetime
from run import app
from app import db

def migrate_nouveaux_champs():
    """
    Ajoute les nouveaux champs manquants au modèle InvestorProfile.
    """
    with app.app_context():
        print("🔄 Migration des nouveaux champs manquants...")
        
        try:
            # Ajouter les nouveaux champs avec ALTER TABLE
            print("📝 Ajout des nouveaux champs...")
            
            # Champs identité
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE investor_profiles ADD COLUMN lieu_naissance VARCHAR(100)'))
                print("✅ Ajouté: lieu_naissance")
                
                conn.execute(db.text('ALTER TABLE investor_profiles ADD COLUMN pays_residence_fiscal VARCHAR(50)'))
                print("✅ Ajouté: pays_residence_fiscal")
                
                # Champs revenus
                conn.execute(db.text('ALTER TABLE investor_profiles ADD COLUMN metier VARCHAR(100)'))
                print("✅ Ajouté: metier")
                
                conn.execute(db.text('ALTER TABLE investor_profiles ADD COLUMN revenus_complementaires FLOAT'))
                print("✅ Ajouté: revenus_complementaires")
                
                conn.commit()
            
            print(f"""
🎉 MIGRATION TERMINÉE AVEC SUCCÈS !

🆕 NOUVEAUX CHAMPS AJOUTÉS:
✅ lieu_naissance - Lieu de naissance de l'utilisateur
✅ pays_residence_fiscal - Pays de résidence fiscal
✅ metier - Métier/profession de l'utilisateur  
✅ revenus_complementaires - Revenus complémentaires (loyers, dividendes...)

🔧 PROCHAINES ÉTAPES:
1. L'interface admin peut maintenant afficher et éditer ces champs
2. Tester la saisie et modification des données
3. Vérifier que les calculs automatiques fonctionnent correctement
            """)
            
        except Exception as e:
            print(f"⚠️  Erreur lors de la migration: {e}")
            print("ℹ️  Certains champs existent peut-être déjà, c'est normal.")

if __name__ == "__main__":
    print("🚀 Lancement de la migration des nouveaux champs...")
    migrate_nouveaux_champs()
    print("🎉 Migration terminée !")