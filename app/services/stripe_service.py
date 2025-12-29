"""
Service de gestion des paiements Stripe pour Atlas
Gestion des abonnements récurrents en production
"""

import stripe
import os
from flask import current_app
from dotenv import load_dotenv
from app import db
from app.models.user import User
from app.models.subscription import Subscription
from datetime import datetime, timedelta
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

class StripeService:
    """Service principal pour les interactions avec Stripe"""
    
    def __init__(self):
        self.load_config()
        
    def load_config(self):
        """Charge la configuration Stripe depuis .env.stripe"""
        # Charger les variables d'environnement Stripe
        load_dotenv('.env.stripe')
        
        # Configuration de Stripe
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        
        # Clés et IDs
        self.publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
        self.secret_key = os.getenv('STRIPE_SECRET_KEY')
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        # Price IDs pour les plans
        self.price_mapping = {
            'initia': os.getenv('STRIPE_PRICE_INITIA'),
            'optima': os.getenv('STRIPE_PRICE_OPTIMA'),
            'maxima': os.getenv('STRIPE_PRICE_MAXIMA')
        }
        
        # URLs
        self.success_url = os.getenv('STRIPE_SUCCESS_URL', 'https://www.atlas-invest.fr/plateforme/dashboard')
        self.cancel_url = os.getenv('STRIPE_CANCEL_URL', 'https://www.atlas-invest.fr/onboarding/plan')
        
        logger.info("Configuration Stripe chargée (Production)")
    
    def get_publishable_key(self):
        """Retourne la clé publique Stripe"""
        return self.publishable_key
    
    def get_or_create_customer(self, user):
        """Récupère ou crée un client Stripe pour l'utilisateur"""
        try:
            # Vérifier si l'utilisateur a déjà un ID client
            if user.stripe_customer_id:
                try:
                    customer = stripe.Customer.retrieve(user.stripe_customer_id)
                    return customer
                except stripe.error.StripeError:
                    # Client introuvable, en créer un nouveau
                    user.stripe_customer_id = None
            
            # Créer un nouveau client
            customer = stripe.Customer.create(
                email=user.email,
                name=user.get_full_name(),
                metadata={
                    'atlas_user_id': str(user.id),
                    'atlas_user_type': user.user_type
                }
            )
            
            # Sauvegarder l'ID client
            user.stripe_customer_id = customer.id
            db.session.commit()
            
            logger.info(f"Client Stripe créé pour {user.email}: {customer.id}")
            return customer
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur création client Stripe: {str(e)}")
            raise Exception(f"Impossible de créer le client Stripe: {str(e)}")
    
    def create_checkout_session(self, user, plan_type):
        """Crée une session de checkout Stripe"""
        try:
            # Récupérer ou créer le client
            customer = self.get_or_create_customer(user)
            
            # Récupérer l'ID du prix
            price_id = self.price_mapping.get(plan_type.lower())
            if not price_id or price_id == 'TO_BE_PROVIDED':
                raise ValueError(f"Plan {plan_type} non configuré ou indisponible")
            
            # Créer la session de checkout
            session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                customer_update={
                    'address': 'auto'
                },
                automatic_tax={
                    'enabled': True,
                },
                allow_promotion_codes=True,
                success_url=f"{self.success_url}?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=self.cancel_url,
                subscription_data={
                    'description': f'Abonnement Atlas Invest - Plan {plan_type.upper()}',
                    'metadata': {
                        'plan_type': plan_type,
                        'company': 'ATLAS INVEST'
                    }
                },
                metadata={
                    'atlas_user_id': str(user.id),
                    'plan_type': plan_type
                }
            )
            
            logger.info(f"Session checkout créée pour {user.email}: {session.id}")
            return session
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur création session checkout: {str(e)}")
            raise Exception(f"Impossible de créer la session de paiement: {str(e)}")
    
    def handle_successful_payment(self, session):
        """Traite un paiement réussi"""
        try:
            user_id = session['metadata'].get('atlas_user_id')
            plan_type = session['metadata'].get('plan_type')
            
            if not user_id or not plan_type:
                logger.error("Métadonnées manquantes dans la session")
                return False
            
            user = User.query.get(int(user_id))
            if not user:
                logger.error(f"Utilisateur {user_id} non trouvé")
                return False
            
            # Récupérer l'abonnement Stripe
            subscription_id = session['subscription']
            stripe_subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Créer ou mettre à jour l'abonnement local
            if user.subscription:
                subscription = user.subscription
                subscription.tier = plan_type
                subscription.status = 'active'
                subscription.stripe_subscription_id = subscription_id
                subscription.stripe_customer_id = session['customer']
            else:
                subscription = Subscription(
                    user_id=user.id,
                    tier=plan_type,
                    status='active',
                    stripe_subscription_id=subscription_id,
                    stripe_customer_id=session['customer'],
                    start_date=datetime.utcnow()
                )
                db.session.add(subscription)
                
            # Mettre à jour les dates
            subscription.current_period_start = datetime.fromtimestamp(stripe_subscription.current_period_start)
            subscription.current_period_end = datetime.fromtimestamp(stripe_subscription.current_period_end)
            subscription.updated_at = datetime.utcnow()
            
            # Marquer l'utilisateur comme non-prospect
            user.is_prospect = False
            user.subscription_date = datetime.utcnow()
            
            db.session.commit()
            
            # Envoyer l'email de bienvenue
            try:
                from app.services.email_service import send_welcome_email
                send_welcome_email(user)
            except Exception as e:
                logger.error(f"Erreur envoi email de bienvenue: {e}")
            
            logger.info(f"Abonnement activé pour {user.email}: plan {plan_type}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur traitement paiement réussi: {str(e)}")
            db.session.rollback()
            return False
    
    def cancel_subscription(self, user):
        """Annule l'abonnement d'un utilisateur"""
        try:
            if not user.subscription or not user.subscription.stripe_subscription_id:
                raise ValueError("Aucun abonnement Stripe trouvé")
            
            # Annuler dans Stripe
            stripe.Subscription.modify(
                user.subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )
            
            # Mettre à jour le statut local
            user.subscription.status = 'canceled'
            user.subscription.canceled_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Abonnement annulé pour {user.email}")
            return True
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur annulation abonnement: {str(e)}")
            raise Exception(f"Impossible d'annuler l'abonnement: {str(e)}")
    
    def get_subscription_status(self, user):
        """Récupère le statut de l'abonnement depuis Stripe"""
        try:
            if not user.subscription or not user.subscription.stripe_subscription_id:
                return None
            
            subscription = stripe.Subscription.retrieve(user.subscription.stripe_subscription_id)
            return {
                'status': subscription.status,
                'current_period_end': datetime.fromtimestamp(subscription.current_period_end),
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'plan': subscription.items.data[0].price.nickname or 'Plan Atlas'
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur récupération statut: {str(e)}")
            return None
    
    def handle_webhook(self, payload, sig_header):
        """Traite les webhooks Stripe"""
        try:
            # Vérifier la signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            
            # Traiter l'événement
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                if session['mode'] == 'subscription':
                    return self.handle_successful_payment(session)
            
            elif event['type'] == 'customer.subscription.updated':
                subscription = event['data']['object']
                return self.handle_subscription_updated(subscription)
            
            elif event['type'] == 'customer.subscription.deleted':
                subscription = event['data']['object']
                return self.handle_subscription_deleted(subscription)
            
            elif event['type'] == 'invoice.payment_failed':
                invoice = event['data']['object']
                return self.handle_payment_failed(invoice)
            
            logger.info(f"Événement webhook traité: {event['type']}")
            return True
            
        except stripe.error.SignatureVerificationError:
            logger.error("Signature webhook invalide")
            return False
        except Exception as e:
            logger.error(f"Erreur traitement webhook: {str(e)}")
            return False
    
    def handle_subscription_updated(self, stripe_subscription):
        """Traite la mise à jour d'un abonnement"""
        try:
            # Trouver l'utilisateur via l'ID client Stripe
            user = User.query.filter_by(
                stripe_customer_id=stripe_subscription['customer']
            ).first()
            
            if user and user.subscription:
                subscription = user.subscription
                subscription.status = stripe_subscription['status']
                subscription.current_period_start = datetime.fromtimestamp(
                    stripe_subscription['current_period_start']
                )
                subscription.current_period_end = datetime.fromtimestamp(
                    stripe_subscription['current_period_end']
                )
                subscription.updated_at = datetime.utcnow()
                
                db.session.commit()
                logger.info(f"Abonnement mis à jour pour {user.email}")
            
            return True
        except Exception as e:
            logger.error(f"Erreur mise à jour abonnement: {str(e)}")
            return False
    
    def handle_subscription_deleted(self, stripe_subscription):
        """Traite la suppression d'un abonnement"""
        try:
            user = User.query.filter_by(
                stripe_customer_id=stripe_subscription['customer']
            ).first()
            
            if user and user.subscription:
                subscription = user.subscription
                subscription.status = 'canceled'
                subscription.canceled_at = datetime.utcnow()
                subscription.updated_at = datetime.utcnow()
                
                db.session.commit()
                logger.info(f"Abonnement supprimé pour {user.email}")
            
            return True
        except Exception as e:
            logger.error(f"Erreur suppression abonnement: {str(e)}")
            return False
    
    def handle_payment_failed(self, invoice):
        """Traite un échec de paiement"""
        try:
            user = User.query.filter_by(
                stripe_customer_id=invoice['customer']
            ).first()
            
            if user:
                # Marquer le statut comme problématique
                if user.subscription:
                    user.subscription.status = 'past_due'
                    user.subscription.updated_at = datetime.utcnow()
                
                db.session.commit()
                logger.warning(f"Échec de paiement pour {user.email}")
            
            return True
        except Exception as e:
            logger.error(f"Erreur traitement échec paiement: {str(e)}")
            return False

# Instance globale du service
stripe_service = StripeService()