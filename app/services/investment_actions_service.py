"""
Service pour la gestion des actions d'investissement récurrentes.
"""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, or_
from app import db
from app.models.investment_action import InvestmentAction
from app.models.investment_plan import InvestmentPlan, InvestmentPlanLine
from app.models.user import User
import os


class InvestmentActionsService:
    """Service principal pour gérer les actions d'investissement mensuelles."""
    
    @staticmethod
    def is_test_mode():
        """Vérifie si le mode test est activé."""
        return os.getenv('ACTIONS_TEST_MODE', '0') == '1'
    
    @staticmethod
    def is_test_user(user):
        """Vérifie si l'utilisateur est un utilisateur de test."""
        test_emails = ['admin@gmail.com', 'hugues.marie925@gmail.com', 'test.client@gmail.com']
        return user.email in test_emails
    
    @staticmethod
    def get_target_month(user, force_current=False):
        """
        Détermine le mois cible pour les actions.
        
        Args:
            user: Utilisateur concerné
            force_current: Force l'utilisation du mois courant
            
        Returns:
            str: Mois au format YYYY-MM
        """
        now = datetime.utcnow()
        
        # Si force_current est activé, utiliser le mois courant
        if force_current:
            return now.strftime('%Y-%m')
        
        # Pour tous les utilisateurs, utiliser le mois courant comme mois cible
        return now.strftime('%Y-%m')
    
    @staticmethod
    def generate_monthly_actions(user_id, year_month=None, force_current=False):
        """
        Génère les actions mensuelles pour un utilisateur.
        Fonction idempotente - ne crée pas de doublons.
        
        Args:
            user_id: ID de l'utilisateur
            year_month: Mois cible (optionnel, auto-déterminé si None)
            force_current: Force l'utilisation du mois courant
            
        Returns:
            dict: Résultat avec statistiques
        """
        try:
            # Récupérer l'utilisateur
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'Utilisateur non trouvé'}
            
            # Déterminer le mois cible
            if not year_month:
                year_month = InvestmentActionsService.get_target_month(user, force_current)
            
            # Récupérer le plan d'investissement de l'utilisateur
            investment_plan = InvestmentPlan.query.filter_by(user_id=user_id).first()
            if not investment_plan:
                return {'success': False, 'error': 'Aucun plan d\'investissement trouvé'}
            
            # Récupérer les lignes du plan
            plan_lines = InvestmentPlanLine.query.filter_by(plan_id=investment_plan.id).all()
            if not plan_lines:
                return {'success': False, 'error': 'Aucune ligne dans le plan d\'investissement'}
            
            created_actions = []
            existing_actions = []
            
            for line in plan_lines:
                # Vérifier si l'action existe déjà (idempotence)
                existing_action = InvestmentAction.query.filter_by(
                    user_id=user_id,
                    plan_line_id=line.id,
                    year_month=year_month
                ).first()
                
                if existing_action:
                    existing_actions.append(existing_action)
                    continue
                
                # Calculer le montant basé sur le pourcentage ou montant fixe
                expected_amount = 0.0
                support_type = line.support_envelope
                
                # Nouveau modèle avec pourcentages
                if hasattr(line, 'percentage') and line.percentage and hasattr(line, 'computed_amount'):
                    expected_amount = line.computed_amount
                # Ancien modèle avec montants fixes
                elif hasattr(line, 'monthly_amount') and line.monthly_amount:
                    expected_amount = line.monthly_amount
                # Support type alternatif
                elif hasattr(line, 'envelope_type'):
                    support_type = line.envelope_type
                
                # Créer une nouvelle action
                action = InvestmentAction(
                    user_id=user_id,
                    plan_line_id=line.id,
                    year_month=year_month,
                    support_type=support_type,
                    label=line.description or f"Investissement {support_type}",
                    expected_amount=expected_amount,
                    status='pending'
                )
                
                db.session.add(action)
                created_actions.append(action)
            
            # Sauvegarder les nouvelles actions
            if created_actions:
                db.session.commit()
            
            return {
                'success': True,
                'year_month': year_month,
                'created_count': len(created_actions),
                'existing_count': len(existing_actions),
                'total_count': len(created_actions) + len(existing_actions),
                'created_actions': [
                    {
                        'id': action.id,
                        'support_type': action.support_type,
                        'expected_amount': action.expected_amount
                    }
                    for action in created_actions
                ]
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Erreur lors de la génération: {str(e)}'}
    
    @staticmethod
    def update_action_status(action_id, status, realized_amount=None):
        """
        Met à jour le statut d'une action et le patrimoine de l'utilisateur.
        
        Args:
            action_id: ID de l'action
            status: Nouveau statut ('done', 'adjusted', 'skipped')
            realized_amount: Montant réalisé (si status = 'adjusted')
            
        Returns:
            dict: Résultat de la mise à jour
        """
        try:
            action = InvestmentAction.query.get(action_id)
            if not action:
                return {'success': False, 'error': 'Action non trouvée'}
            
            # Récupérer l'utilisateur et son profil
            from app.models.user import User
            user = User.query.get(action.user_id)
            if not user or not user.investor_profile:
                return {'success': False, 'error': 'Profil utilisateur non trouvé'}
            
            # Marquer l'action selon le statut
            actual_amount = 0
            if status == 'done':
                action.mark_as_done()
                actual_amount = action.expected_amount
            elif status == 'adjusted':
                if realized_amount is None:
                    return {'success': False, 'error': 'Montant requis pour le statut adjusted'}
                action.mark_as_adjusted(realized_amount)
                actual_amount = realized_amount
            elif status == 'skipped':
                action.mark_as_skipped()
                actual_amount = 0
            else:
                return {'success': False, 'error': f'Statut invalide: {status}'}
            
            # Mettre à jour le patrimoine si montant > 0
            if actual_amount > 0:
                InvestmentActionsService._update_user_patrimony(user.investor_profile, action.support_type, actual_amount)
                
                # Recalculer tous les totaux patrimoniaux après mise à jour
                from app.services.patrimony_calculation_engine import PatrimonyCalculationEngine
                PatrimonyCalculationEngine.calculate_and_save_all(
                    user.investor_profile, 
                    force_recalculate=True, 
                    save_to_db=True
                )
                print(f"🔄 Recalcul patrimonial effectué après validation action")
            
            db.session.commit()
            
            return {
                'success': True,
                'action_id': action_id,
                'new_status': action.status,
                'realized_amount': action.realized_amount,
                'patrimony_updated': actual_amount > 0
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Erreur lors de la mise à jour: {str(e)}'}
    
    @staticmethod
    def _update_user_patrimony(investor_profile, support_type, amount):
        """
        Met à jour le patrimoine de l'utilisateur selon le type de support.
        
        Args:
            investor_profile: Profil investisseur
            support_type: Type de support (PEA, PER, etc.)
            amount: Montant à ajouter
        """
        # Mapper les types de support vers les champs du profil
        support_mapping = {
            'PEA': 'pea_value',
            'PER': 'per_value',
            'Assurance Vie': 'life_insurance_value',
            'CTO': 'cto_value',
            'PEE': 'pee_value',
            'SCPI': 'scpi_value',
            'Private Equity': 'private_equity_value',
            'Livret A': 'livret_a_value',
            'LDDS': 'ldds_value',
            'PEL/CEL': 'pel_cel_value'
        }
        
        field_name = support_mapping.get(support_type)
        if field_name and hasattr(investor_profile, field_name):
            current_value = getattr(investor_profile, field_name) or 0
            new_value = current_value + amount
            setattr(investor_profile, field_name, new_value)
            
            # Mettre à jour le flag "has_" correspondant
            has_field_name = f"has_{field_name.replace('_value', '')}"
            if hasattr(investor_profile, has_field_name):
                setattr(investor_profile, has_field_name, new_value > 0)
            
            print(f"📈 Patrimoine mis à jour: {support_type} {current_value}€ → {new_value}€ (+{amount}€)")
        else:
            # Support non mappé, ajouter aux liquidités par défaut
            current_savings = investor_profile.current_savings or 0
            investor_profile.current_savings = current_savings + amount
            print(f"📈 Ajouté aux liquidités: {current_savings}€ → {current_savings + amount}€ (+{amount}€)")
    
    @staticmethod
    def calculate_days_until_next_actions():
        """
        Calcule le nombre de jours jusqu'au dernier jour du mois prochain.
        
        Returns:
            int: Nombre de jours restants
        """
        from datetime import datetime, date
        from dateutil.relativedelta import relativedelta
        
        today = date.today()
        
        # Calculer le mois prochain
        next_month = today + relativedelta(months=1)
        
        # Calculer le dernier jour du mois prochain de façon sûre
        # On passe au mois suivant, puis on recule d'un jour
        first_day_month_after = date(next_month.year, next_month.month, 1)
        last_day_next_month = (first_day_month_after + relativedelta(months=1)) - relativedelta(days=1)
        
        # Calculer la différence en jours
        days_remaining = (last_day_next_month - today).days
        
        return max(0, days_remaining)
    
    @staticmethod
    def get_dashboard_data(user_id, year_month=None):
        """
        Récupère les données pour le dashboard.
        
        Args:
            user_id: ID de l'utilisateur
            year_month: Mois cible (optionnel)
            
        Returns:
            dict: Données pour le dashboard
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'Utilisateur non trouvé'}
            
            if not year_month:
                year_month = InvestmentActionsService.get_target_month(user)
            
            # Récupérer TOUTES les actions pending (tous mois confondus)
            all_pending_actions = InvestmentAction.query.filter_by(
                user_id=user_id,
                status='pending'
            ).order_by(InvestmentAction.year_month.asc()).all()
            
            # Récupérer les actions du mois spécifique pour les stats
            actions = InvestmentAction.get_monthly_actions(user_id, year_month)
            pending_actions = all_pending_actions
            
            # Calculer les statistiques
            monthly_stats = InvestmentAction.calculate_monthly_stats(user_id, year_month)
            
            # Statistiques annuelles
            current_year = datetime.utcnow().year
            yearly_stats = InvestmentAction.calculate_yearly_stats(user_id, current_year)
            
            # Calculer les jours jusqu'aux prochaines actions
            days_until_next_actions = InvestmentActionsService.calculate_days_until_next_actions()
            
            # Déterminer le mois courant pour marquer les actions en retard
            current_month = datetime.utcnow().strftime('%Y-%m')
            
            # Calculer l'épargne annuelle réalisée
            yearly_savings = InvestmentActionsService.calculate_yearly_savings_realized(user_id, current_year)
            
            return {
                'success': True,
                'year_month': year_month,
                'actions': [
                    {
                        'id': action.id,
                        'support_type': action.support_type,
                        'label': action.label,
                        'expected_amount': action.expected_amount,
                        'realized_amount': action.realized_amount,
                        'status': action.status,
                        'is_pending': action.is_pending,
                        'completion_rate': action.completion_rate
                    }
                    for action in actions
                ],
                'pending_actions': [
                    {
                        'id': action.id,
                        'support_type': action.support_type,
                        'label': action.label,
                        'expected_amount': action.expected_amount,
                        'year_month': action.year_month,
                        'is_overdue': action.year_month < current_month
                    }
                    for action in pending_actions
                ],
                'monthly_stats': monthly_stats,
                'yearly_stats': yearly_stats,
                'days_until_next_actions': days_until_next_actions,
                'yearly_savings': yearly_savings
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Erreur lors de la récupération des données: {str(e)}'}
    
    @staticmethod
    def calculate_yearly_savings_realized(user_id, year):
        """
        Calcule l'épargne annuelle réalisée basée sur les actions validées.
        
        Args:
            user_id: ID de l'utilisateur
            year: Année de calcul
            
        Returns:
            float: Montant total épargné dans l'année
        """
        try:
            # Récupérer toutes les actions done/adjusted pour l'année
            year_start = f"{year}-01"
            year_end = f"{year}-12"
            
            realized_actions = InvestmentAction.query.filter(
                InvestmentAction.user_id == user_id,
                InvestmentAction.year_month >= year_start,
                InvestmentAction.year_month <= year_end,
                InvestmentAction.status.in_(['done', 'adjusted'])
            ).all()
            
            total_realized = sum(
                action.realized_amount or action.expected_amount 
                for action in realized_actions
            )
            
            return float(total_realized)
            
        except Exception as e:
            print(f"❌ Erreur calcul épargne annuelle: {str(e)}")
            return 0.0
    
    @staticmethod
    def auto_generate_for_dashboard(user_id):
        """
        Génère automatiquement les actions pour le dashboard si nécessaire.
        Génère les actions du mois courant pour tous les utilisateurs.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            dict: Résultat de la génération
        """
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'error': 'Utilisateur non trouvé'}
        
        # Vérifier que l'utilisateur a un plan d'investissement
        from app.models.investment_plan import InvestmentPlan
        investment_plan = InvestmentPlan.query.filter_by(user_id=user_id).first()
        if not investment_plan:
            return {'success': False, 'error': 'Aucun plan d\'investissement trouvé'}
        
        # Générer pour le mois courant pour tous les utilisateurs
        return InvestmentActionsService.generate_monthly_actions(
            user_id=user_id
        )
    
    @staticmethod
    def simulate_historical_actions(user_id, start_month="2024-10"):
        """
        Simule des actions depuis octobre 2024 pour les tests.
        Crée toutes les actions mensuelles comme pending.
        
        Args:
            user_id: ID de l'utilisateur de test
            start_month: Premier mois à générer (YYYY-MM)
            
        Returns:
            dict: Résultat de la simulation
        """
        try:
            from datetime import datetime
            from dateutil.relativedelta import relativedelta
            
            user = User.query.get(user_id)
            if not user or not InvestmentActionsService.is_test_user(user):
                return {'success': False, 'error': 'Utilisateur non autorisé'}
            
            # Récupérer le plan d'investissement
            investment_plan = InvestmentPlan.query.filter_by(user_id=user_id).first()
            if not investment_plan:
                return {'success': False, 'error': 'Aucun plan d\'investissement trouvé'}
            
            # Parser la date de début
            start_date = datetime.strptime(start_month, '%Y-%m')
            current_date = datetime.utcnow()
            
            created_count = 0
            months_generated = []
            
            # Générer pour chaque mois depuis le début jusqu'au mois courant
            month_date = start_date
            while month_date <= current_date:
                month_str = month_date.strftime('%Y-%m')
                
                # Générer les actions pour ce mois
                result = InvestmentActionsService.generate_monthly_actions(
                    user_id=user_id,
                    year_month=month_str,
                    force_current=True
                )
                
                if result['success']:
                    created_count += result['created_count']
                    if result['created_count'] > 0:
                        months_generated.append(month_str)
                
                # Passer au mois suivant
                month_date += relativedelta(months=1)
            
            return {
                'success': True,
                'total_created': created_count,
                'months_generated': months_generated,
                'message': f"{created_count} actions créées depuis {start_month}"
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Erreur simulation: {str(e)}'}