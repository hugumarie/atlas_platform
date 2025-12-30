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
    
    def __init__(self, safe_mode=None):
        """
        Initialise le service Stripe
        
        Args:
            safe_mode (bool): Si True, n'exige pas les variables Stripe (pour migrations/tests)
        """
        self.safe_mode = safe_mode if safe_mode is not None else os.getenv('STRIPE_SAFE_MODE', 'false').lower() == 'true'
        self._initialized = False
        
        # Initialisation différée seulement si pas en mode safe
        if not self.safe_mode:
            self.load_config()
        else:
            self._setup_safe_mode()
        
    def _setup_safe_mode(self):
        """Configure le service en mode safe (sans Stripe) pour les migrations/tests"""
        self.publishable_key = None
        self.secret_key = None 
        self.webhook_secret = None
        self.price_mapping = {}
        self.success_url = 'https://atlas-invest.fr/plateforme/dashboard'
        self.cancel_url = 'https://atlas-invest.fr/onboarding/plan'
        self._initialized = True
        logger.info("StripeService initialisé en mode SAFE (sans Stripe)")
        
    def load_config(self):
        """Charge la configuration Stripe depuis les variables d'environnement"""
        try:
            # Forcer le rechargement du .env
            from dotenv import load_dotenv
            load_dotenv(override=True)
            
            # Configuration de Stripe - priorité aux variables d'environnement système
            self.secret_key = os.getenv('STRIPE_SECRET_KEY')
            
            # Si pas de clé secrète et pas en mode safe, passer en mode safe
            if not self.secret_key:
                if not self.safe_mode:
                    logger.warning("STRIPE_SECRET_KEY manquante - activation du mode SAFE")
                    self.safe_mode = True
                    self._setup_safe_mode()
                    return
                else:
                    raise ValueError("Configuration Stripe incomplète: STRIPE_SECRET_KEY manquante")
            
            # Configuration complète Stripe
            stripe.api_key = self.secret_key
            
            # Clés et IDs
            self.publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
            self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
            
            # Price IDs pour les plans
            self.price_mapping = {
                'initia': os.getenv('STRIPE_PRICE_INITIA'),
                'optima': os.getenv('STRIPE_PRICE_OPTIMA')
            }
            
            # URLs - adaptation automatique selon l'environnement
            base_url = os.getenv('SITE_URL', 'https://atlas-invest.fr')
            self.success_url = os.getenv('STRIPE_SUCCESS_URL', f'{base_url}/plateforme/dashboard')
            self.cancel_url = os.getenv('STRIPE_CANCEL_URL', f'{base_url}/onboarding/plan')
            
            self._initialized = True
            logger.info("Configuration Stripe chargée (Production)")
            
        except Exception as e:
            if self.safe_mode:
                logger.warning(f"Erreur configuration Stripe en mode safe: {e}")
                self._setup_safe_mode()
            else:
                logger.error(f"Erreur configuration Stripe: {e}")
                raise
    
    def _check_stripe_available(self):
        """Vérifie si Stripe est disponible (pas en mode safe)"""
        if self.safe_mode or not self._initialized:
            raise RuntimeError("Stripe non disponible - service en mode SAFE ou non initialisé")
        return True
    
    def get_publishable_key(self):
        """Retourne la clé publique Stripe"""
        if self.safe_mode:
            logger.warning("get_publishable_key appelé en mode SAFE")
            return None
        return self.publishable_key
    
    def get_or_create_customer(self, user):
        """Récupère ou crée un client Stripe pour l'utilisateur"""
        if self.safe_mode:
            logger.warning("get_or_create_customer appelé en mode SAFE - retour None")
            return None
            
        try:
            self._check_stripe_available()
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
            # Debug des métadonnées
            print(f"🔍 Session type: {type(session)}")
            print(f"🔍 Session keys: {list(session.keys()) if hasattr(session, 'keys') else 'No keys'}")
            print(f"🔍 Metadata: {getattr(session, 'metadata', 'No metadata')}")
            
            metadata = getattr(session, 'metadata', {})
            user_id = metadata.get('atlas_user_id') if metadata else None
            plan_type = metadata.get('plan_type') if metadata else None
            
            if not user_id or not plan_type:
                logger.error("Métadonnées manquantes dans la session")
                return False
            
            user = User.query.get(int(user_id))
            if not user:
                logger.error(f"Utilisateur {user_id} non trouvé")
                return False
            
            # Récupérer l'abonnement Stripe
            subscription_id = getattr(session, 'subscription', None)
            if not subscription_id:
                logger.error("Pas d'abonnement dans la session")
                # Essayer de trouver l'abonnement via le customer
                customer_id = getattr(session, 'customer', None)
                if customer_id:
                    subscriptions = stripe.Subscription.list(customer=customer_id, limit=1)
                    if subscriptions.data:
                        subscription_id = subscriptions.data[0].id
                        logger.info(f"Abonnement trouvé via customer: {subscription_id}")
                    else:
                        logger.warning("Aucun abonnement trouvé - création manuelle")
                        # Créer un abonnement "simulé" pour compatibilité
                        subscription = Subscription(
                            user_id=user.id,
                            tier=plan_type,
                            status='active',
                            stripe_customer_id=customer_id,
                            start_date=datetime.utcnow(),
                            current_period_start=datetime.utcnow(),
                            current_period_end=datetime.utcnow() + timedelta(days=30)
                        )
                        db.session.add(subscription)
                        
                        # Marquer l'utilisateur comme non-prospect
                        user.is_prospect = False
                        user.subscription_date = datetime.utcnow()
                        
                        db.session.commit()
                        logger.info(f"Abonnement manuel créé pour {user.email}")
                        return True
                else:
                    logger.error("Pas de customer dans la session")
                    return False
            
            stripe_subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Créer ou mettre à jour l'abonnement local
            if user.subscription:
                subscription = user.subscription
                subscription.tier = plan_type
                subscription.status = 'active'
                subscription.stripe_subscription_id = subscription_id
                subscription.stripe_customer_id = getattr(session, 'customer', None)
            else:
                subscription = Subscription(
                    user_id=user.id,
                    tier=plan_type,
                    status='active',
                    stripe_subscription_id=subscription_id,
                    stripe_customer_id=getattr(session, 'customer', None),
                    start_date=datetime.utcnow()
                )
                db.session.add(subscription)
                
            # Mettre à jour les dates
            try:
                if hasattr(stripe_subscription, 'current_period_start') and stripe_subscription.current_period_start:
                    subscription.current_period_start = datetime.fromtimestamp(stripe_subscription.current_period_start)
                else:
                    subscription.current_period_start = datetime.utcnow()
                    
                if hasattr(stripe_subscription, 'current_period_end') and stripe_subscription.current_period_end:
                    subscription.current_period_end = datetime.fromtimestamp(stripe_subscription.current_period_end)
                else:
                    subscription.current_period_end = datetime.utcnow() + timedelta(days=30)
                    
                subscription.updated_at = datetime.utcnow()
            except Exception as e:
                logger.error(f"Erreur dates abonnement: {e}")
                # Valeurs par défaut
                subscription.current_period_start = datetime.utcnow()
                subscription.current_period_end = datetime.utcnow() + timedelta(days=30)
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
            print(f"🔍 Erreur détaillée: {e}")
            print(f"🔍 Type erreur: {type(e)}")
            import traceback
            traceback.print_exc()
            
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
            user.subscription.status = 'cancelled'
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
                subscription.status = 'cancelled'
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
    
    def change_subscription_plan(self, user, new_plan_tier):
        """
        Change le plan d'abonnement d'un utilisateur avec facturation proratisée
        
        Args:
            user: Utilisateur avec abonnement existant
            new_plan_tier: Nouveau plan ('initia', 'optima', 'ultima')
            
        Returns:
            dict: Résultat de l'opération avec succès/erreur
        """
        try:
            self._check_stripe_available()
            
            if not user.subscription or not user.subscription.stripe_subscription_id:
                return {
                    'success': False, 
                    'error': 'Aucun abonnement Stripe trouvé pour cet utilisateur'
                }
            
            # Vérifier que le nouveau plan est valide et disponible
            new_price_id = self.price_mapping.get(new_plan_tier.lower())
            if not new_price_id or new_price_id == 'TO_BE_PROVIDED':
                if new_plan_tier.lower() == 'ultima':
                    return {
                        'success': False,
                        'error': 'Le plan ULTIMA nécessite un devis personnalisé. Veuillez nous contacter.'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Plan {new_plan_tier} non configuré ou indisponible'
                    }
            
            # Prix des plans pour référence
            tier_prices = {
                'initia': 25.00,
                'optima': 50.00,
                'ultima': 99.99  # Prix de base, mais sur devis
            }
            
            # Récupérer l'abonnement Stripe actuel
            current_subscription = stripe.Subscription.retrieve(
                user.subscription.stripe_subscription_id
            )
            
            # Déterminer si c'est un upgrade ou downgrade
            current_plan = user.subscription.tier
            current_price = tier_prices.get(current_plan, 25.00)
            new_price = tier_prices.get(new_plan_tier.lower(), 25.00)
            
            is_upgrade = new_price > current_price
            
            # Modifier l'abonnement dans Stripe avec proration automatique
            updated_subscription = stripe.Subscription.modify(
                user.subscription.stripe_subscription_id,
                items=[{
                    'id': current_subscription['items']['data'][0].id,
                    'price': new_price_id,
                }],
                proration_behavior='always_invoice',  # Facturation immédiate de la différence
                metadata={
                    'plan_type': new_plan_tier.lower(),
                    'company': 'ATLAS INVEST',
                    'change_date': datetime.utcnow().isoformat(),
                    'previous_plan': current_plan
                }
            )
            
            # Mettre à jour l'abonnement local
            user.subscription.tier = new_plan_tier.lower()
            user.subscription.price = new_price
            user.subscription.updated_at = datetime.utcnow()
            
            # Mettre à jour les dates basées sur l'abonnement Stripe mis à jour
            if hasattr(updated_subscription, 'current_period_start'):
                user.subscription.current_period_start = datetime.fromtimestamp(
                    updated_subscription.current_period_start
                )
            if hasattr(updated_subscription, 'current_period_end'):
                user.subscription.current_period_end = datetime.fromtimestamp(
                    updated_subscription.current_period_end
                )
            
            db.session.commit()
            
            # Calculer le montant de la proration
            proration_amount = 0
            if is_upgrade:
                # Pour un upgrade, calculer la différence proratisée
                days_remaining = (user.subscription.current_period_end - datetime.utcnow()).days
                daily_diff = (new_price - current_price) / 30
                proration_amount = daily_diff * days_remaining
            
            logger.info(f"Plan changé avec succès pour {user.email}: {current_plan} → {new_plan_tier}")
            
            return {
                'success': True,
                'message': f'Plan changé avec succès vers {new_plan_tier.upper()}',
                'previous_plan': current_plan,
                'new_plan': new_plan_tier.lower(),
                'is_upgrade': is_upgrade,
                'proration_amount': round(proration_amount, 2) if is_upgrade else 0,
                'new_monthly_price': new_price
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe lors du changement de plan: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur de facturation: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Erreur générale lors du changement de plan: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Erreur lors du changement de plan: {str(e)}'
            }
    
    def get_customer_payment_methods(self, user):
        """
        Récupère les moyens de paiement d'un utilisateur depuis Stripe
        
        Args:
            user: Utilisateur avec stripe_customer_id
            
        Returns:
            list: Liste des moyens de paiement ou None si erreur
        """
        try:
            self._check_stripe_available()
            
            if not user.stripe_customer_id:
                logger.info(f"Pas de customer Stripe pour {user.email}")
                return []
            
            # Récupérer les moyens de paiement depuis Stripe
            payment_methods = stripe.PaymentMethod.list(
                customer=user.stripe_customer_id,
                type="card"  # On se concentre sur les cartes pour l'instant
            )
            
            # Récupérer le customer pour connaître le moyen de paiement par défaut
            customer = stripe.Customer.retrieve(user.stripe_customer_id)
            default_payment_method_id = getattr(customer, 'invoice_settings', {}).get('default_payment_method')
            
            # Formater les données pour l'affichage
            formatted_methods = []
            for pm in payment_methods.data:
                card = pm.card
                formatted_methods.append({
                    'id': pm.id,
                    'type': 'card',
                    'card_type': card.brand.lower(),  # visa, mastercard, amex, etc.
                    'last4': card.last4,
                    'exp_month': f"{card.exp_month:02d}",
                    'exp_year': card.exp_year,
                    'cardholder_name': getattr(pm.billing_details, 'name', '') or user.get_full_name(),
                    'is_default': pm.id == default_payment_method_id,
                    'created': pm.created
                })
            
            # Trier par défaut d'abord, puis par date de création
            formatted_methods.sort(key=lambda x: (not x['is_default'], -x['created']))
            
            logger.info(f"Récupérés {len(formatted_methods)} moyens de paiement pour {user.email}")
            return formatted_methods
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe récupération moyens de paiement: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erreur générale récupération moyens de paiement: {str(e)}")
            return None
    
    def create_setup_intent(self, user):
        """
        Crée un SetupIntent pour ajouter un nouveau moyen de paiement
        
        Args:
            user: Utilisateur
            
        Returns:
            dict: SetupIntent client_secret ou None si erreur
        """
        try:
            self._check_stripe_available()
            
            # S'assurer que l'utilisateur a un customer Stripe
            customer = self.get_or_create_customer(user)
            
            # Créer le SetupIntent
            setup_intent = stripe.SetupIntent.create(
                customer=customer.id,
                payment_method_types=['card'],
                usage='off_session',  # Pour les paiements futurs
                metadata={
                    'atlas_user_id': str(user.id)
                }
            )
            
            logger.info(f"SetupIntent créé pour {user.email}: {setup_intent.id}")
            return {
                'success': True,
                'client_secret': setup_intent.client_secret,
                'setup_intent_id': setup_intent.id
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur création SetupIntent: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur de configuration paiement: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Erreur générale création SetupIntent: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur lors de l\'ajout du moyen de paiement: {str(e)}'
            }
    
    def set_default_payment_method(self, user, payment_method_id):
        """
        Définit un moyen de paiement comme par défaut
        
        Args:
            user: Utilisateur
            payment_method_id: ID du moyen de paiement Stripe
            
        Returns:
            dict: Résultat de l'opération
        """
        try:
            self._check_stripe_available()
            
            if not user.stripe_customer_id:
                return {
                    'success': False,
                    'error': 'Aucun customer Stripe trouvé'
                }
            
            # Mettre à jour le customer avec le nouveau moyen de paiement par défaut
            stripe.Customer.modify(
                user.stripe_customer_id,
                invoice_settings={
                    'default_payment_method': payment_method_id
                }
            )
            
            logger.info(f"Moyen de paiement par défaut mis à jour pour {user.email}: {payment_method_id}")
            return {
                'success': True,
                'message': 'Moyen de paiement par défaut mis à jour'
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur mise à jour moyen de paiement par défaut: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur Stripe: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Erreur générale mise à jour moyen de paiement par défaut: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur: {str(e)}'
            }
    
    def remove_payment_method(self, user, payment_method_id):
        """
        Supprime un moyen de paiement
        
        Args:
            user: Utilisateur
            payment_method_id: ID du moyen de paiement à supprimer
            
        Returns:
            dict: Résultat de l'opération
        """
        try:
            self._check_stripe_available()
            
            # Vérifier que le moyen de paiement appartient bien à cet utilisateur
            if not user.stripe_customer_id:
                return {
                    'success': False,
                    'error': 'Aucun customer Stripe trouvé'
                }
            
            # Récupérer TOUS les moyens de paiement du customer pour vérifier le nombre
            all_payment_methods = stripe.PaymentMethod.list(
                customer=user.stripe_customer_id,
                type="card"
            )
            
            # Vérifier qu'il y a plus d'un moyen de paiement
            if len(all_payment_methods.data) <= 1:
                return {
                    'success': False,
                    'error': 'Impossible de supprimer votre unique moyen de paiement. Ajoutez une autre carte avant de supprimer celle-ci.'
                }
            
            # Récupérer le moyen de paiement pour vérifier qu'il appartient au customer
            payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
            if payment_method.customer != user.stripe_customer_id:
                return {
                    'success': False,
                    'error': 'Moyen de paiement non autorisé'
                }
            
            # Vérifier si c'est le moyen de paiement par défaut
            customer = stripe.Customer.retrieve(user.stripe_customer_id)
            default_payment_method_id = getattr(customer, 'invoice_settings', {}).get('default_payment_method')
            
            is_default = payment_method_id == default_payment_method_id
            
            # Détacher le moyen de paiement du customer (= le supprimer)
            stripe.PaymentMethod.detach(payment_method_id)
            
            # Si c'était le moyen de paiement par défaut, définir un autre comme par défaut
            if is_default and len(all_payment_methods.data) > 1:
                # Trouver un autre moyen de paiement pour le définir par défaut
                remaining_methods = stripe.PaymentMethod.list(
                    customer=user.stripe_customer_id,
                    type="card"
                )
                
                if remaining_methods.data:
                    new_default = remaining_methods.data[0].id
                    stripe.Customer.modify(
                        user.stripe_customer_id,
                        invoice_settings={
                            'default_payment_method': new_default
                        }
                    )
                    logger.info(f"Nouveau moyen de paiement par défaut défini: {new_default}")
            
            logger.info(f"Moyen de paiement supprimé pour {user.email}: {payment_method_id}")
            return {
                'success': True,
                'message': 'Moyen de paiement supprimé avec succès' + 
                          (' et nouveau moyen par défaut défini automatiquement' if is_default else '')
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur suppression moyen de paiement: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur Stripe: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Erreur générale suppression moyen de paiement: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur: {str(e)}'
            }

# Instance globale du service - initialisée en mode safe par défaut
stripe_service = StripeService(safe_mode=True)

def initialize_stripe_service():
    """
    Force la réinitialisation du service Stripe avec la vraie configuration
    À appeler après que l'application Flask soit configurée
    """
    global stripe_service
    try:
        # Forcer le rechargement du .env
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        # Vérifier si on a les clés Stripe
        secret_key = os.getenv('STRIPE_SECRET_KEY')
        if secret_key and secret_key.startswith('sk_'):
            print(f"🔐 Clés Stripe trouvées, réinitialisation du service...")
            stripe_service = StripeService(safe_mode=False)
            print(f"✅ StripeService réinitialisé avec succès (safe_mode: {stripe_service.safe_mode})")
        else:
            print(f"⚠️ Pas de clés Stripe valides, service en mode SAFE")
            
    except Exception as e:
        print(f"❌ Erreur réinitialisation StripeService: {e}")
        logger.error(f"Erreur réinitialisation StripeService: {e}")