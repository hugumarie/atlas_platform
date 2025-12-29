#!/usr/bin/env python3
"""
Script de migration pour générer les actions d'investissement
pour tous les utilisateurs existants.

Ce script doit être exécuté une seule fois lors du déploiement en production.
"""

from app import create_app, db
from app.models.user import User
from app.models.investment_plan import InvestmentPlan
from app.services.investment_actions_service import InvestmentActionsService
from datetime import datetime

def migrate_investment_actions():
    """
    Génère les actions d'investissement du mois courant pour tous les utilisateurs
    qui ont un plan d'investissement actif.
    """
    app = create_app()
    
    with app.app_context():
        print("🚀 Démarrage de la migration des actions d'investissement...")
        print(f"📅 Génération pour le mois: {datetime.utcnow().strftime('%Y-%m')}")
        
        # Récupérer tous les utilisateurs non-admin avec un plan d'investissement
        users_with_plans = db.session.query(User).join(
            InvestmentPlan,
            User.id == InvestmentPlan.user_id
        ).filter(
            User.is_admin == False,
            User.is_prospect == False,  # Utilisateurs convertis uniquement
            InvestmentPlan.is_active == True
        ).all()
        
        # Filtrer pour garder seulement ceux qui ont des lignes avec des montants > 0
        from app.models.investment_plan import InvestmentPlanLine
        filtered_users = []
        
        for user in users_with_plans:
            plan = InvestmentPlan.query.filter_by(user_id=user.id, is_active=True).first()
            if plan:
                lines = InvestmentPlanLine.query.filter_by(plan_id=plan.id).all()
                # Vérifier si au moins une ligne a un montant > 0
                has_valid_lines = any(line.computed_amount > 0 for line in lines)
                if has_valid_lines:
                    filtered_users.append(user)
        
        users_with_plans = filtered_users
        
        print(f"👥 {len(users_with_plans)} utilisateurs trouvés avec des plans d'investissement")
        
        success_count = 0
        error_count = 0
        total_actions_created = 0
        
        for i, user in enumerate(users_with_plans, 1):
            try:
                print(f"📋 [{i}/{len(users_with_plans)}] Traitement: {user.email}")
                
                # Générer les actions pour le mois courant
                result = InvestmentActionsService.generate_monthly_actions(
                    user_id=user.id,
                    force_current=True
                )
                
                if result['success']:
                    created = result['created_count']
                    existing = result['existing_count']
                    total_actions_created += created
                    
                    if created > 0:
                        print(f"   ✅ {created} nouvelles actions créées, {existing} déjà existantes")
                    else:
                        print(f"   ℹ️ {existing} actions déjà existantes")
                    
                    success_count += 1
                else:
                    print(f"   ❌ Erreur: {result['error']}")
                    error_count += 1
                    
            except Exception as e:
                print(f"   💥 Exception: {str(e)}")
                error_count += 1
        
        print(f"\n📊 Résultats de la migration:")
        print(f"   ✅ Succès: {success_count} utilisateurs")
        print(f"   ❌ Erreurs: {error_count} utilisateurs")
        print(f"   📋 Total actions créées: {total_actions_created}")
        
        if error_count == 0:
            print(f"\n🎉 Migration terminée avec succès!")
        else:
            print(f"\n⚠️ Migration terminée avec {error_count} erreurs")
        
        # Statistiques finales
        from app.models.investment_action import InvestmentAction
        total_pending = InvestmentAction.query.filter_by(status='pending').count()
        print(f"📈 Total actions pending dans le système: {total_pending}")
        
        return success_count, error_count, total_actions_created

def reset_yearly_savings_for_existing_users():
    """
    Remet à 0 l'épargne annuelle réalisée pour tous les utilisateurs existants
    pour qu'ils puissent commencer avec une barre d'épargne à 0.
    """
    app = create_app()
    
    with app.app_context():
        print("🔄 Remise à zéro de l'épargne annuelle pour les utilisateurs existants...")
        
        # Note: Cette fonction est conceptuelle car l'épargne annuelle est calculée
        # dynamiquement à partir des actions validées. Pour remettre à 0, il faudrait
        # soit marquer les anciennes actions comme 'reset' ou implémenter une logique
        # de date de début pour le calcul d'épargne.
        
        print("ℹ️ L'épargne annuelle est calculée automatiquement à partir des actions validées.")
        print("ℹ️ Les nouveaux utilisateurs commenceront avec 0€ d'épargne car aucune action n'est validée.")

if __name__ == "__main__":
    print("=" * 60)
    print("    MIGRATION ACTIONS D'INVESTISSEMENT - PRODUCTION")
    print("=" * 60)
    
    # Exécuter la migration
    success, errors, actions_created = migrate_investment_actions()
    
    # Remise à zéro conceptuelle
    reset_yearly_savings_for_existing_users()
    
    print("\n" + "=" * 60)
    print("                    MIGRATION TERMINÉE")
    print("=" * 60)
    
    if errors == 0:
        exit(0)  # Succès
    else:
        exit(1)  # Erreurs détectées