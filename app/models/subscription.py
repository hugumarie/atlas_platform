"""
Modèle Subscription pour gérer les abonnements des utilisateurs.
Gère le statut des abonnements et les paiements (simulation avant Stripe).
"""

from app import db
from datetime import datetime, timedelta
from enum import Enum

class SubscriptionStatus(Enum):
    """Énumération des statuts d'abonnement possibles."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRIAL = "trial"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class SubscriptionTier(Enum):
    """Énumération des types de plans d'abonnement."""
    INITIA = "initia"
    OPTIMA = "optima"
    ULTIMA = "ultima"

class Subscription(db.Model):
    """
    Modèle représentant l'abonnement d'un utilisateur à la plateforme.
    
    Attributes:
        id (int): Identifiant unique de l'abonnement
        user_id (int): Référence vers l'utilisateur
        status (str): Statut de l'abonnement
        price (float): Prix mensuel de l'abonnement
        start_date (datetime): Date de début de l'abonnement
        end_date (datetime): Date de fin de l'abonnement
        next_billing_date (datetime): Date du prochain paiement
        payment_method (str): Méthode de paiement (simulation)
        trial_end_date (datetime): Date de fin de période d'essai
        cancelled_date (datetime): Date d'annulation
        created_date (datetime): Date de création
        last_payment_date (datetime): Date du dernier paiement
    """
    
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Informations d'abonnement
    status = db.Column(db.String(20), nullable=False, default=SubscriptionStatus.TRIAL.value)
    tier = db.Column(db.String(20), nullable=False, default=SubscriptionTier.INITIA.value)
    price = db.Column(db.Float, nullable=False, default=20.0)
    
    # Dates importantes
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    next_billing_date = db.Column(db.DateTime, nullable=True)
    trial_end_date = db.Column(db.DateTime, nullable=True)
    cancelled_date = db.Column(db.DateTime, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_payment_date = db.Column(db.DateTime, nullable=True)
    
    # Informations de paiement (simulation)
    payment_method = db.Column(db.String(50), default="simulation")
    
    # Intégration Stripe
    stripe_subscription_id = db.Column(db.String(100), nullable=True, unique=True)
    stripe_customer_id = db.Column(db.String(100), nullable=True)
    current_period_start = db.Column(db.DateTime, nullable=True)
    current_period_end = db.Column(db.DateTime, nullable=True)
    canceled_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, user_id, **kwargs):
        """
        Initialise un nouvel abonnement directement actif (après paiement).
        
        Args:
            user_id (int): ID de l'utilisateur
        """
        super().__init__(user_id=user_id, **kwargs)
        
        # Abonnement directement actif après paiement
        self.start_date = datetime.utcnow()
        self.next_billing_date = datetime.utcnow() + timedelta(days=30)
        self.last_payment_date = datetime.utcnow()
        self.status = SubscriptionStatus.ACTIVE.value
    
    def is_active(self):
        """
        Vérifie si l'abonnement est actif.
        
        Returns:
            bool: True si l'abonnement est actif
        """
        return self.status in [SubscriptionStatus.ACTIVE.value, SubscriptionStatus.TRIAL.value]
    
    def is_trial(self):
        """
        Vérifie si l'utilisateur est en période d'essai.
        
        Returns:
            bool: True si en période d'essai
        """
        return (self.status == SubscriptionStatus.TRIAL.value and 
                self.trial_end_date and 
                datetime.utcnow() < self.trial_end_date)
    
    def days_remaining_trial(self):
        """
        Calcule le nombre de jours restants dans la période d'essai.
        
        Returns:
            int: Nombre de jours restants (0 si pas en essai)
        """
        if not self.is_trial():
            return 0
        
        remaining = self.trial_end_date - datetime.utcnow()
        return max(0, remaining.days)
    
    def activate_subscription(self):
        """
        Active l'abonnement après la période d'essai.
        """
        self.status = SubscriptionStatus.ACTIVE.value
        self.start_date = datetime.utcnow()
        self.next_billing_date = datetime.utcnow() + timedelta(days=30)
        self.last_payment_date = datetime.utcnow()
        db.session.commit()
    
    def cancel_subscription(self, immediate=False):
        """
        Annule l'abonnement.
        
        Args:
            immediate (bool): Si True, annulation immédiate, sinon à la fin de la période
        """
        self.cancelled_date = datetime.utcnow()
        
        if immediate:
            self.status = SubscriptionStatus.CANCELLED.value
            self.end_date = datetime.utcnow()
        else:
            # Annulation à la fin de la période de facturation
            self.end_date = self.next_billing_date
        
        db.session.commit()
    
    def renew_subscription(self):
        """
        Renouvelle l'abonnement pour un mois supplémentaire.
        """
        if self.status == SubscriptionStatus.ACTIVE.value:
            self.last_payment_date = datetime.utcnow()
            self.next_billing_date = datetime.utcnow() + timedelta(days=30)
            db.session.commit()
    
    def get_status_display(self):
        """
        Retourne le statut en français pour l'affichage.
        
        Returns:
            str: Statut traduit en français
        """
        status_translations = {
            SubscriptionStatus.ACTIVE.value: "Actif",
            SubscriptionStatus.INACTIVE.value: "Inactif",
            SubscriptionStatus.TRIAL.value: "Période d'essai",
            SubscriptionStatus.CANCELLED.value: "Annulé",
            SubscriptionStatus.EXPIRED.value: "Expiré"
        }
        return status_translations.get(self.status, self.status)
    
    def get_tier_display(self):
        """
        Retourne le nom d'affichage du plan d'abonnement.
        
        Returns:
            str: Nom du plan en majuscules
        """
        return self.tier.upper() if self.tier else "INITIA"
    
    def get_next_payment_amount(self):
        """
        Calcule le montant du prochain paiement.
        
        Returns:
            float: Montant à payer
        """
        return self.price
    
    def __repr__(self):
        return f'<Subscription {self.user.email} - {self.status}>'