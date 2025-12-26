"""
Routes pour l'interface investisseur.
Gère le dashboard, le profil, le questionnaire et les différentes sections.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.investor_profile import InvestorProfile
from app.models.portfolio import Portfolio
import json

investor_bp = Blueprint('investor', __name__)

@investor_bp.route('/dashboard')
@login_required
def dashboard():
    print("*** ROUTE INVESTOR.PY DASHBOARD EXECUTEE ***")
    """
    Dashboard principal de l'investisseur.
    """
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    # Vérifier si le questionnaire a été complété
    if not current_user.investor_profile:
        flash('Veuillez d\'abord compléter votre profil investisseur.', 'warning')
        return redirect(url_for('investor.questionnaire'))
    
    # Pas de mise à jour automatique du portefeuille
    
    return render_template('investor/dashboard.html')

@investor_bp.route('/questionnaire', methods=['GET', 'POST'])
@login_required
def questionnaire():
    """
    Questionnaire de profil investisseur.
    """
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    # Si le profil existe déjà, rediriger vers le dashboard
    if current_user.investor_profile:
        return redirect(url_for('investor.dashboard'))
    
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            profile_data = {
                'user_id': current_user.id,
                'monthly_net_income': float(request.form.get('monthly_net_income', 0)),
                'current_savings': float(request.form.get('current_savings', 0)),
                'monthly_savings_capacity': float(request.form.get('monthly_savings_capacity', 0)),
                'risk_tolerance': request.form.get('risk_tolerance'),
                'investment_experience': request.form.get('investment_experience'),
                'investment_goals': request.form.get('investment_goals'),
                'investment_horizon': request.form.get('investment_horizon'),
                'family_situation': request.form.get('family_situation'),
                'professional_situation': request.form.get('professional_situation'),
                
                # Investissements existants
                'has_real_estate': 'has_real_estate' in request.form,
                'real_estate_value': float(request.form.get('real_estate_value', 0)),
                'has_life_insurance': 'has_life_insurance' in request.form,
                'life_insurance_value': float(request.form.get('life_insurance_value', 0)),
                'has_pea': 'has_pea' in request.form,
                'pea_value': float(request.form.get('pea_value', 0)),
                'has_livret_a': 'has_livret_a' in request.form,
                'livret_a_value': float(request.form.get('livret_a_value', 0)),
                'other_investments': request.form.get('other_investments', '')
            }
            
            # Validation des données obligatoires
            required_fields = ['monthly_net_income', 'current_savings', 'monthly_savings_capacity', 
                             'risk_tolerance', 'investment_experience', 'investment_goals', 
                             'investment_horizon', 'family_situation', 'professional_situation']
            
            for field in required_fields:
                if not profile_data.get(field):
                    flash(f'Le champ {field} est obligatoire.', 'error')
                    return render_template('investor/questionnaire.html')
            
            # Création du profil investisseur
            investor_profile = InvestorProfile(**profile_data)
            db.session.add(investor_profile)
            
            # Mise à jour du portefeuille
            if current_user.portfolio:
                current_user.portfolio.update_from_profile()
            
            db.session.commit()
            
            flash('Profil investisseur créé avec succès ! Bienvenue sur votre dashboard.', 'success')
            return redirect(url_for('investor.dashboard'))
            
        except ValueError as e:
            flash('Veuillez vérifier les valeurs numériques saisies.', 'error')
            return render_template('investor/questionnaire.html')
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de la sauvegarde. Veuillez réessayer.', 'error')
            return render_template('investor/questionnaire.html')
    
    return render_template('investor/questionnaire.html')

@investor_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Gestion du profil utilisateur.
    """
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        try:
            # Mise à jour des informations de base
            current_user.first_name = request.form.get('first_name', '').strip()
            current_user.last_name = request.form.get('last_name', '').strip()
            current_user.phone = request.form.get('phone', '').strip() or None
            
            # Gestion du changement de mot de passe
            new_password = request.form.get('new_password', '').strip()
            if new_password:
                if len(new_password) < 6:
                    flash('Le nouveau mot de passe doit contenir au moins 6 caractères.', 'error')
                    return render_template('investor/profile.html')
                current_user.set_password(new_password)
            
            db.session.commit()
            flash('Profil mis à jour avec succès.', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de la mise à jour du profil.', 'error')
    
    return render_template('investor/profile.html')

@investor_bp.route('/learning')
@login_required
def learning():
    """
    Section apprentissage et formations.
    """
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    if not current_user.investor_profile:
        flash('Veuillez d\'abord compléter votre profil investisseur.', 'warning')
        return redirect(url_for('investor.questionnaire'))
    
    # Données fictives pour les formations
    courses = [
        {
            'id': 1,
            'title': 'Les bases de l\'investissement',
            'description': 'Comprendre les fondamentaux de l\'investissement et les différents types de placements.',
            'duration': '45 min',
            'level': 'Débutant',
            'thumbnail': '/static/img/course1.jpg',
            'completed': False
        },
        {
            'id': 2,
            'title': 'Diversification de portefeuille',
            'description': 'Apprendre à répartir ses investissements pour optimiser le rapport rendement/risque.',
            'duration': '60 min',
            'level': 'Intermédiaire',
            'thumbnail': '/static/img/course2.jpg',
            'completed': False
        },
        {
            'id': 3,
            'title': 'PEA et optimisation fiscale',
            'description': 'Tout savoir sur le Plan d\'Épargne en Actions et l\'optimisation fiscale.',
            'duration': '50 min',
            'level': 'Intermédiaire',
            'thumbnail': '/static/img/course3.jpg',
            'completed': False
        }
    ]
    
    return render_template('investor/learning.html', courses=courses)

@investor_bp.route('/assistant')
@login_required
def assistant():
    """
    Assistant financier IA (chat).
    """
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    if not current_user.investor_profile:
        flash('Veuillez d\'abord compléter votre profil investisseur.', 'warning')
        return redirect(url_for('investor.questionnaire'))
    
    return render_template('investor/assistant.html')

@investor_bp.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    """
    API pour l'assistant financier (simulation).
    """
    if current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Message vide'}), 400
    
    # Simulation de réponses de l'assistant IA
    responses = {
        'salut': 'Bonjour ! Je suis votre assistant financier personnel. Comment puis-je vous aider aujourd\'hui ?',
        'investissement': 'Basé sur votre profil, je recommande une diversification entre PEA actions (60%), assurance-vie (30%) et livrets (10%). Souhaitez-vous en savoir plus ?',
        'risque': 'Votre profil de risque semble modéré. Cela signifie un équilibre entre sécurité et potentiel de rendement. Voulez-vous ajuster votre allocation ?',
        'épargne': f'Avec votre capacité d\'épargne mensuelle, vous pourriez constituer un capital intéressant sur le long terme. Avez-vous des objectifs particuliers ?',
        'pea': 'Le PEA est excellent pour les actions européennes avec des avantages fiscaux après 5 ans. C\'est un pilier important de votre stratégie.',
        'default': 'C\'est une excellente question ! Basé sur votre profil investisseur, je peux vous donner des conseils personnalisés. Pouvez-vous être plus spécifique sur ce qui vous intéresse ?'
    }
    
    # Logique simple de correspondance
    user_message_lower = user_message.lower()
    response = responses['default']
    
    for keyword, resp in responses.items():
        if keyword in user_message_lower:
            response = resp
            break
    
    return jsonify({
        'response': response,
        'timestamp': '2024-01-01 12:00:00'  # En production, utiliser datetime.now()
    })

@investor_bp.route('/api/portfolio-data')
@login_required
def portfolio_data():
    """
    API pour récupérer les données du portefeuille pour les graphiques.
    """
    if current_user.is_admin or not current_user.investor_profile:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    profile = current_user.investor_profile
    distribution = profile.get_investment_distribution()
    
    return jsonify({
        'distribution': distribution,
        'total_value': profile.current_savings,
        'monthly_income': profile.monthly_net_income,
        'monthly_savings': profile.monthly_savings_capacity,
        'risk_score': profile.get_risk_score()
    })