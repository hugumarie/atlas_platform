"""
Routes pour l'onboarding des prospects
Processus : Invitation → Création compte → Sélection plan → Paiement
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.invitation_token import InvitationToken
from app.models.user_plan import UserPlan
import re

onboarding_bp = Blueprint('onboarding', __name__, url_prefix='/onboarding')


@onboarding_bp.route('/invitation/<token>')
def invitation_signup(token):
    """
    Page d'inscription via invitation pour les prospects.
    Vérifie le token et affiche le formulaire de création de compte.
    """
    # Rechercher le token dans la nouvelle table
    invitation_token = InvitationToken.query.filter_by(token=token).first()
    
    if not invitation_token or not invitation_token.is_valid():
        flash('Cette invitation est invalide ou a expiré.', 'error')
        return redirect(url_for('site_pages.index'))
    
    prospect = invitation_token.prospect
    
    if not prospect or prospect.prospect_status == 'converti':
        flash('Ce prospect a déjà créé son compte.', 'info')
        return redirect(url_for('platform_auth.login'))
    
    return render_template(
        'onboarding/invitation_signup.html', 
        prospect=prospect, 
        token=token,
        token_expires_in_hours=invitation_token.get_remaining_hours()
    )


@onboarding_bp.route('/invitation/<token>/create-account', methods=['POST'])
def create_account_from_invitation(token):
    """
    Créer un compte utilisateur à partir d'une invitation prospect.
    Convertit le prospect en utilisateur actif.
    """
    # Vérifier le token
    invitation_token = InvitationToken.query.filter_by(token=token).first()
    
    if not invitation_token or not invitation_token.is_valid():
        return jsonify({'error': 'Invitation invalide ou expirée'}), 400
    
    prospect = invitation_token.prospect
    
    try:
        data = request.get_json()
        
        # Validation du mot de passe
        password = data.get('password', '').strip()
        password_confirm = data.get('password_confirm', '').strip()
        
        if len(password) < 8:
            return jsonify({'error': 'Le mot de passe doit contenir au moins 8 caractères'}), 400
        
        if password != password_confirm:
            return jsonify({'error': 'Les mots de passe ne correspondent pas'}), 400
        
        # Vérifier la complexité du mot de passe
        if not re.search(r'[A-Z]', password):
            return jsonify({'error': 'Le mot de passe doit contenir au moins une majuscule'}), 400
        
        if not re.search(r'[0-9]', password):
            return jsonify({'error': 'Le mot de passe doit contenir au moins un chiffre'}), 400
        
        # Convertir le prospect en utilisateur actif
        prospect.set_password(password)
        prospect.user_type = 'client'
        prospect.is_prospect = False
        prospect.prospect_status = 'converti'
        prospect.is_active = True
        
        # Marquer le token comme utilisé
        invitation_token.mark_as_used()
        
        db.session.commit()
        
        # Connecter automatiquement l'utilisateur
        login_user(prospect, remember=False)
        
        print(f"✅ Compte créé avec succès pour {prospect.email}")
        
        return jsonify({
            'success': True,
            'message': 'Compte créé avec succès !',
            'redirect_url': url_for('onboarding.plan_selection')
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur création de compte: {str(e)}")
        return jsonify({
            'error': f'Erreur lors de la création du compte: {str(e)}'
        }), 500


@onboarding_bp.route('/plan')
@login_required
def plan_selection():
    """
    Page de sélection du plan d'abonnement.
    Affiche les options Initia et Optima.
    """
    # Vérifier que l'utilisateur est bien un nouveau client
    if current_user.prospect_status != 'converti':
        flash('Accès non autorisé à cette étape.', 'error')
        return redirect(url_for('platform_investor.dashboard'))
    
    # Vérifier s'il a déjà sélectionné un plan
    existing_plan = UserPlan.get_user_current_plan(current_user.id)
    if existing_plan and existing_plan.is_completed():
        flash('Vous avez déjà complété votre onboarding.', 'info')
        return redirect(url_for('platform_investor.dashboard'))
    
    # Récupérer les plans disponibles
    available_plans = UserPlan.get_available_plans()
    
    return render_template(
        'onboarding/plan_selection.html',
        user=current_user,
        plans=available_plans,
        current_plan=existing_plan.plan_type if existing_plan else None
    )


@onboarding_bp.route('/plan/select', methods=['POST'])
@login_required
def select_plan():
    """
    Enregistre la sélection de plan de l'utilisateur.
    """
    if current_user.prospect_status != 'converti':
        return jsonify({'error': 'Accès non autorisé à cette étape'}), 403
    
    try:
        data = request.get_json()
        plan_type = data.get('plan_type', '').lower().strip()
        
        # Validation du type de plan
        available_plans = UserPlan.get_available_plans()
        if plan_type not in available_plans:
            return jsonify({'error': 'Plan sélectionné invalide'}), 400
        
        # Vérifier s'il y a déjà une sélection active
        existing_plan = UserPlan.get_user_current_plan(current_user.id)
        if existing_plan and existing_plan.is_completed():
            return jsonify({'error': 'Vous avez déjà un plan actif'}), 400
        
        # Supprimer l'ancien plan non terminé s'il existe
        if existing_plan and not existing_plan.is_completed():
            db.session.delete(existing_plan)
        
        # Créer la nouvelle sélection de plan
        user_plan = UserPlan(
            user_id=current_user.id,
            plan_type=plan_type
        )
        user_plan.set_payment_pending()
        
        db.session.add(user_plan)
        db.session.commit()
        
        print(f"✅ Plan {plan_type.upper()} sélectionné pour {current_user.email}")
        
        # Stocker temporairement en session pour la page de paiement
        session['selected_plan_id'] = user_plan.id
        session['selected_plan_type'] = plan_type
        
        return jsonify({
            'success': True,
            'message': f'Plan {plan_type.upper()} sélectionné avec succès',
            'plan_name': user_plan.get_plan_name(),
            'plan_price': float(user_plan.plan_price),
            'redirect_url': url_for('onboarding.payment')
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur sélection de plan: {str(e)}")
        return jsonify({
            'error': f'Erreur lors de la sélection du plan: {str(e)}'
        }), 500


@onboarding_bp.route('/payment')
@login_required
def payment():
    """
    Page de paiement (placeholder pour Stripe).
    Prépare les informations pour l'intégration future de Stripe.
    """
    if current_user.prospect_status != 'converti':
        flash('Accès non autorisé à cette étape.', 'error')
        return redirect(url_for('platform_investor.dashboard'))
    
    # Récupérer le plan sélectionné
    plan_id = session.get('selected_plan_id')
    if not plan_id:
        flash('Aucun plan sélectionné. Veuillez d\'abord choisir un plan.', 'warning')
        return redirect(url_for('onboarding.plan_selection'))
    
    user_plan = UserPlan.query.get(plan_id)
    if not user_plan or user_plan.user_id != current_user.id:
        flash('Plan introuvable ou non autorisé.', 'error')
        return redirect(url_for('onboarding.plan_selection'))
    
    return render_template(
        'onboarding/payment.html',
        user=current_user,
        user_plan=user_plan,
        plan_config=user_plan.get_plan_config()
    )


@onboarding_bp.route('/payment/simulate', methods=['POST'])
@login_required
def simulate_payment():
    """
    Simule un paiement réussi (pour les tests en local).
    À remplacer par l'intégration Stripe en production.
    """
    if current_user.prospect_status != 'converti':
        return jsonify({'error': 'Accès non autorisé à cette étape'}), 403
    
    try:
        # Récupérer le plan sélectionné
        plan_id = session.get('selected_plan_id')
        user_plan = UserPlan.query.get(plan_id)
        
        if not user_plan or user_plan.user_id != current_user.id:
            return jsonify({'error': 'Plan introuvable'}), 400
        
        # Marquer l'onboarding comme terminé
        user_plan.mark_as_completed()
        
        # Nettoyer la session
        session.pop('selected_plan_id', None)
        session.pop('selected_plan_type', None)
        
        db.session.commit()
        
        print(f"✅ Onboarding terminé pour {current_user.email} - Plan: {user_plan.plan_type.upper()}")
        
        return jsonify({
            'success': True,
            'message': 'Paiement simulé avec succès ! Bienvenue chez Atlas !',
            'redirect_url': url_for('platform_investor.dashboard')
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur simulation paiement: {str(e)}")
        return jsonify({
            'error': f'Erreur lors du paiement: {str(e)}'
        }), 500


# Route de nettoyage pour les tokens expirés (à appeler via cron)
@onboarding_bp.route('/cleanup-tokens', methods=['POST'])
def cleanup_expired_tokens():
    """
    Nettoie les tokens d'invitation expirés.
    À appeler périodiquement via un cron job.
    """
    try:
        cleaned_count = InvitationToken.cleanup_expired()
        return jsonify({
            'success': True,
            'message': f'{cleaned_count} tokens expirés nettoyés'
        })
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors du nettoyage: {str(e)}'
        }), 500