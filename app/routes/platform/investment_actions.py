"""
Routes pour la gestion des actions d'investissement.
"""

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app.services.investment_actions_service import InvestmentActionsService
from app import db
import json

investment_actions_bp = Blueprint('investment_actions', __name__, url_prefix='/plateforme/actions')


@investment_actions_bp.route('/api/generate', methods=['POST'])
@login_required
def api_generate_actions():
    """
    API pour générer les actions d'investissement pour un mois.
    """
    try:
        data = request.get_json() or {}
        year_month = data.get('year_month')
        force_current = data.get('force_current', False)
        
        result = InvestmentActionsService.generate_monthly_actions(
            user_id=current_user.id,
            year_month=year_month,
            force_current=force_current
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur lors de la génération: {str(e)}'
        }), 500


@investment_actions_bp.route('/api/update/<int:action_id>', methods=['POST'])
@login_required
def api_update_action(action_id):
    """
    API pour mettre à jour le statut d'une action.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Données manquantes'}), 400
        
        status = data.get('status')
        realized_amount = data.get('realized_amount')
        
        if not status:
            return jsonify({'success': False, 'error': 'Statut requis'}), 400
        
        # Vérifier que l'action appartient à l'utilisateur actuel
        from app.models.investment_action import InvestmentAction
        action = InvestmentAction.query.filter_by(id=action_id, user_id=current_user.id).first()
        if not action:
            return jsonify({'success': False, 'error': 'Action non trouvée'}), 404
        
        result = InvestmentActionsService.update_action_status(
            action_id=action_id,
            status=status,
            realized_amount=realized_amount
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur lors de la mise à jour: {str(e)}'
        }), 500


@investment_actions_bp.route('/api/dashboard-data')
@login_required
def api_dashboard_data():
    """
    API pour récupérer les données du dashboard d'actions.
    """
    try:
        year_month = request.args.get('year_month')
        
        result = InvestmentActionsService.get_dashboard_data(
            user_id=current_user.id,
            year_month=year_month
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur lors de la récupération: {str(e)}'
        }), 500


@investment_actions_bp.route('/api/auto-generate', methods=['POST'])
@login_required
def api_auto_generate():
    """
    API pour la génération automatique en mode test.
    """
    try:
        result = InvestmentActionsService.auto_generate_for_dashboard(current_user.id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur lors de la génération automatique: {str(e)}'
        }), 500


@investment_actions_bp.route('/test')
@login_required
def test_page():
    """
    Page de test pour le module d'actions.
    """
    # Générer automatiquement si mode test
    auto_result = InvestmentActionsService.auto_generate_for_dashboard(current_user.id)
    
    # Récupérer les données
    dashboard_data = InvestmentActionsService.get_dashboard_data(current_user.id)
    
    return render_template('platform/investment_actions/test.html', 
                         auto_result=auto_result,
                         dashboard_data=dashboard_data)


@investment_actions_bp.route('/api/yearly-savings')
@login_required
def api_yearly_savings():
    """
    API pour récupérer les données d'épargne annuelle mises à jour.
    """
    try:
        from datetime import datetime
        
        current_year = datetime.utcnow().year
        yearly_savings = InvestmentActionsService.calculate_yearly_savings_realized(current_user.id, current_year)
        
        # Récupérer l'objectif annuel depuis le profil investisseur
        yearly_objective = 12000  # Valeur par défaut
        if current_user.investor_profile and hasattr(current_user.investor_profile, 'yearly_savings_capacity'):
            yearly_objective = current_user.investor_profile.yearly_savings_capacity or 12000
        
        return jsonify({
            'success': True,
            'yearly_savings': yearly_savings,
            'yearly_objective': yearly_objective,
            'percentage': (yearly_savings / yearly_objective * 100) if yearly_objective > 0 else 0
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur lors du calcul de l\'épargne: {str(e)}'
        }), 500


@investment_actions_bp.route('/debug')
@login_required
def debug_info():
    """
    Page de debug pour vérifier la configuration.
    """
    debug_data = {
        'test_mode': InvestmentActionsService.is_test_mode(),
        'test_user': InvestmentActionsService.is_test_user(current_user),
        'user_email': current_user.email,
        'target_month': InvestmentActionsService.get_target_month(current_user),
        'target_month_forced': InvestmentActionsService.get_target_month(current_user, force_current=True)
    }
    
    return jsonify(debug_data)