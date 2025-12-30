"""
Routes de gestion des paiements Stripe pour l'onboarding Atlas
"""

from flask import Blueprint, request, jsonify, redirect, url_for, flash, current_app, render_template
from flask_login import login_required, current_user
import stripe
import logging
from app.services.stripe_service import stripe_service
from app.models.user import User
from app import db

# Configuration du logging
logger = logging.getLogger(__name__)

# Blueprint pour les routes Stripe
stripe_bp = Blueprint('stripe', __name__, url_prefix='/onboarding/stripe')

@stripe_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Crée une session de checkout Stripe pour l'abonnement"""
    try:
        # Vérifier l'authentification manuellement pour retourner du JSON
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': 'Utilisateur non connecté'}), 401
            
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Données JSON manquantes'}), 400
            
        plan_type = data.get('plan_type')
        
        if not plan_type:
            return jsonify({'success': False, 'error': 'Plan type requis'}), 400
        
        if plan_type.lower() not in ['initia', 'optima', 'maxima']:
            return jsonify({'success': False, 'error': f'Plan type invalide: {plan_type}'}), 400
            
        # Vérification spéciale pour MAXIMA qui n'est pas encore disponible
        if plan_type.lower() == 'maxima':
            return jsonify({
                'success': False, 
                'error': 'Le plan MAXIMA n\'est pas encore disponible. Veuillez nous contacter directement.'
            }), 400
        
        logger.info(f"Création session checkout pour {current_user.email} - Plan: {plan_type}")
        
        # Créer la session Stripe
        session = stripe_service.create_checkout_session(current_user, plan_type)
        
        logger.info(f"Session Stripe créée: {session.id}")
        
        return jsonify({
            'success': True,
            'checkout_url': session.url,
            'session_id': session.id
        })
        
    except Exception as e:
        logger.error(f"Erreur création checkout session: {str(e)}")
        logger.exception("Traceback complet:")
        return jsonify({
            'success': False,
            'error': f'Erreur lors de la création de la session de paiement: {str(e)}'
        }), 500

@stripe_bp.route('/success')
@login_required
def payment_success():
    """Page de succès après paiement Stripe"""
    session_id = request.args.get('session_id')
    
    if session_id:
        try:
            # Vérifier la session Stripe
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid':
                # Debug: voir le contenu de la session
                print(f"🔍 Session payment_status: {session.payment_status}")
                print(f"🔍 Session metadata: {getattr(session, 'metadata', 'NO METADATA')}")
                print(f"🔍 Session customer: {getattr(session, 'customer', 'NO CUSTOMER')}")
                print(f"🔍 Session subscription: {getattr(session, 'subscription', 'NO SUBSCRIPTION')}")
                
                # Traiter le paiement manuellement si le webhook a échoué
                success = stripe_service.handle_successful_payment(session)
                
                if success:
                    flash('Votre abonnement Atlas a été activé avec succès !', 'success')
                    logger.info(f"Abonnement activé manuellement pour session {session_id}")
                else:
                    flash('Paiement validé, activation en cours...', 'info')
                    logger.warning(f"Échec activation manuelle pour session {session_id}")
                    print(f"❌ Échec activation pour session {session_id}")
                
                # Afficher la page de célébration avant le dashboard
                return render_template('onboarding/payment_success.html')
            else:
                flash('Le paiement n\'est pas encore confirmé. Veuillez patienter.', 'warning')
                return redirect(url_for('onboarding.plan_selection'))
                
        except stripe.error.StripeError as e:
            logger.error(f"Erreur vérification session: {str(e)}")
            flash('Erreur lors de la vérification du paiement.', 'error')
    
    return redirect(url_for('platform_investor.dashboard'))

@stripe_bp.route('/cancel')
@login_required
def payment_cancel():
    """Page d'annulation après paiement Stripe"""
    flash('Le paiement a été annulé. Vous pouvez réessayer quand vous le souhaitez.', 'info')
    return redirect(url_for('onboarding.plan_selection'))

@stripe_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Endpoint pour recevoir les webhooks Stripe"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    if not sig_header:
        logger.error("Signature Stripe manquante")
        return jsonify({'error': 'Signature manquante'}), 400
    
    try:
        # Traiter le webhook
        success = stripe_service.handle_webhook(payload, sig_header)
        
        if success:
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'error': 'Erreur traitement webhook'}), 400
            
    except Exception as e:
        logger.error(f"Erreur webhook: {str(e)}")
        return jsonify({'error': 'Erreur serveur'}), 500

@stripe_bp.route('/config')
@login_required
def stripe_config():
    """Endpoint pour récupérer la configuration Stripe publique"""
    return jsonify({
        'publishableKey': stripe_service.get_publishable_key()
    })

@stripe_bp.route('/test-success')
def test_success():
    """Test de la page de félicitations sans paiement"""
    return render_template('onboarding/payment_success.html')

@stripe_bp.route('/portal', methods=['POST'])
@login_required
def customer_portal():
    """Redirige vers le portail client Stripe pour gérer l'abonnement"""
    try:
        if not current_user.subscription or not current_user.subscription.stripe_customer_id:
            return jsonify({
                'success': False, 
                'error': 'Aucun abonnement Stripe trouvé'
            }), 400
        
        # Créer une session du portail client
        session = stripe.billing_portal.Session.create(
            customer=current_user.subscription.stripe_customer_id,
            return_url=url_for('platform_investor.profile', _external=True)
        )
        
        return jsonify({
            'success': True,
            'url': session.url
        })
        
    except stripe.error.StripeError as e:
        logger.error(f"Erreur portail client: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Impossible d\'accéder au portail de gestion'
        }), 500

@stripe_bp.route('/subscription-status')
@login_required
def subscription_status():
    """Récupère le statut de l'abonnement depuis Stripe"""
    try:
        status = stripe_service.get_subscription_status(current_user)
        
        if status:
            return jsonify({
                'success': True,
                'subscription': status
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Aucun abonnement trouvé'
            }), 404
            
    except Exception as e:
        logger.error(f"Erreur statut abonnement: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erreur lors de la récupération du statut'
        }), 500