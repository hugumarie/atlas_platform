#!/usr/bin/env python3
"""
Migration pour corriger les valeurs de profil de risque en production.
Mappe les anciennes valeurs brutes vers les valeurs attendues par l'algorithme.

SÉCURISÉ : Fait une sauvegarde avant modification et permet rollback.
"""

from app import create_app, db
from app.models.investor_profile import InvestorProfile
import json
from datetime import datetime

def backup_profiles():
    """Sauvegarde les profils avant modification"""
    app = create_app()
    with app.app_context():
        profiles = InvestorProfile.query.all()
        backup_data = []
        
        for profile in profiles:
            backup_data.append({
                'user_id': profile.user_id,
                'tolerance_risque': profile.tolerance_risque,
                'horizon_placement': profile.horizon_placement,
                'besoin_liquidite': profile.besoin_liquidite,
                'experience_investissement': profile.experience_investissement,
                'attitude_volatilite': profile.attitude_volatilite,
                'calculated_risk_profile': profile.calculated_risk_profile
            })
        
        # Sauvegarder dans un fichier avec timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"backup_risk_profiles_{timestamp}.json"
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Sauvegarde créée: {backup_file}")
        return backup_file

def fix_risk_profile_values():
    """Corrige les valeurs de profil de risque"""
    
    print("🔄 Début de la migration des profils de risque...")
    
    # Créer une sauvegarde
    backup_file = backup_profiles()
    
    app = create_app()
    with app.app_context():
        try:
            profiles = InvestorProfile.query.all()
            print(f"📊 {len(profiles)} profils à vérifier")
            
            fixed_count = 0
            
            for profile in profiles:
                changed = False
                user_id = profile.user_id
                
                # 1. Fix tolerance_risque mapping
                old_tolerance = profile.tolerance_risque
                if profile.tolerance_risque in ['5', '6']:
                    profile.tolerance_risque = 'faible'
                    changed = True
                elif profile.tolerance_risque == '15':
                    profile.tolerance_risque = 'moderee'
                    changed = True
                elif profile.tolerance_risque == '30':
                    profile.tolerance_risque = 'elevee'
                    changed = True
                
                # 2. Fix besoin_liquidite mapping
                old_liquidite = profile.besoin_liquidite
                if profile.besoin_liquidite == 'oui':
                    profile.besoin_liquidite = 'court_terme'
                    changed = True
                elif profile.besoin_liquidite == 'non':
                    profile.besoin_liquidite = 'long_terme'
                    changed = True
                
                # 3. Fix experience_investissement mapping (enlever accents)
                old_experience = profile.experience_investissement
                if profile.experience_investissement == 'débutant':
                    profile.experience_investissement = 'debutant'
                    changed = True
                elif profile.experience_investissement == 'intermédiaire':
                    profile.experience_investissement = 'intermediaire'
                    changed = True
                elif profile.experience_investissement == 'confirmé':
                    profile.experience_investissement = 'confirme'
                    changed = True
                
                # 4. Fix attitude_volatilite mapping
                old_attitude = profile.attitude_volatilite
                if profile.attitude_volatilite in ['accepter_moderement', 'accepter_modérément']:
                    profile.attitude_volatilite = 'attendre'  # Mapping vers valeur la plus proche
                    changed = True
                elif profile.attitude_volatilite in ['accepter_fortement']:
                    profile.attitude_volatilite = 'investir_plus'
                    changed = True
                
                # 5. Recalculer le profil si des changements ont été faits
                if changed or not profile.calculated_risk_profile:
                    try:
                        new_profile = profile.calculate_risk_profile()
                        old_calculated = profile.calculated_risk_profile
                        profile.calculated_risk_profile = new_profile
                        
                        print(f"  User {user_id}:")
                        if old_tolerance != profile.tolerance_risque:
                            print(f"    tolerance: {old_tolerance} → {profile.tolerance_risque}")
                        if old_liquidite != profile.besoin_liquidite:
                            print(f"    liquidite: {old_liquidite} → {profile.besoin_liquidite}")
                        if old_experience != profile.experience_investissement:
                            print(f"    experience: {old_experience} → {profile.experience_investissement}")
                        if old_attitude != profile.attitude_volatilite:
                            print(f"    attitude: {old_attitude} → {profile.attitude_volatilite}")
                        print(f"    profil calculé: {old_calculated} → {new_profile}")
                        
                        fixed_count += 1
                        
                    except Exception as e:
                        print(f"  ❌ Erreur calcul User {user_id}: {e}")
            
            # Commit toutes les modifications
            db.session.commit()
            print(f"\n✅ Migration terminée: {fixed_count} profils corrigés")
            print(f"💾 Sauvegarde disponible: {backup_file}")
            
        except Exception as e:
            print(f"\n❌ Erreur durant la migration: {e}")
            db.session.rollback()
            print("🔙 Rollback effectué, aucune modification appliquée")
            raise

def verify_migration():
    """Vérifie que la migration s'est bien passée"""
    app = create_app()
    with app.app_context():
        profiles = InvestorProfile.query.all()
        print(f"\n🔍 Vérification post-migration ({len(profiles)} profils):")
        
        valid_tolerance = ['faible', 'moderee', 'elevee']
        valid_liquidite = ['court_terme', 'long_terme']
        valid_experience = ['debutant', 'intermediaire', 'confirme']
        valid_attitude = ['vendre', 'attendre', 'investir_plus']
        valid_calculated = ['PRUDENT', 'EQUILIBRE', 'DYNAMIQUE']
        
        all_valid = True
        
        for profile in profiles:
            user_id = profile.user_id
            issues = []
            
            if profile.tolerance_risque and profile.tolerance_risque not in valid_tolerance:
                issues.append(f"tolerance_risque invalide: {profile.tolerance_risque}")
            
            if profile.besoin_liquidite and profile.besoin_liquidite not in valid_liquidite:
                issues.append(f"besoin_liquidite invalide: {profile.besoin_liquidite}")
            
            if profile.experience_investissement and profile.experience_investissement not in valid_experience:
                issues.append(f"experience_investissement invalide: {profile.experience_investissement}")
            
            if profile.attitude_volatilite and profile.attitude_volatilite not in valid_attitude:
                issues.append(f"attitude_volatilite invalide: {profile.attitude_volatilite}")
            
            if profile.calculated_risk_profile and profile.calculated_risk_profile not in valid_calculated:
                issues.append(f"calculated_risk_profile invalide: {profile.calculated_risk_profile}")
            
            if issues:
                print(f"  ❌ User {user_id}: {', '.join(issues)}")
                all_valid = False
            else:
                # Test du calcul
                try:
                    if all([profile.tolerance_risque, profile.horizon_placement, profile.besoin_liquidite, 
                           profile.experience_investissement, profile.attitude_volatilite]):
                        calculated = profile.calculate_risk_profile()
                        if calculated != profile.calculated_risk_profile:
                            print(f"  ⚠️  User {user_id}: calcul incohérent {profile.calculated_risk_profile} vs {calculated}")
                            all_valid = False
                        else:
                            print(f"  ✅ User {user_id}: {profile.calculated_risk_profile}")
                    else:
                        print(f"  ℹ️  User {user_id}: données incomplètes")
                except Exception as e:
                    print(f"  ❌ User {user_id}: erreur calcul {e}")
                    all_valid = False
        
        if all_valid:
            print(f"\n✅ Migration validée : tous les profils sont corrects")
        else:
            print(f"\n⚠️  Migration partiellement réussie : vérifier les erreurs ci-dessus")

if __name__ == "__main__":
    print("🚀 Migration des valeurs de profil de risque")
    print("=" * 50)
    
    # Lancer la migration
    fix_risk_profile_values()
    
    # Vérifier le résultat
    verify_migration()
    
    print("\n" + "=" * 50)
    print("📖 Instructions:")
    print("1. Vérifiez les logs ci-dessus")
    print("2. Testez quelques profils utilisateurs")
    print("3. En cas de problème, restaurez depuis le backup JSON")