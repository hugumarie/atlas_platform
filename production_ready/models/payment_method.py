"""
Modèle PaymentMethod pour gérer les moyens de paiement des utilisateurs.
Stocke les informations de cartes de crédit de manière sécurisée.
"""

from app import db
from datetime import datetime
from enum import Enum

class CardType(Enum):
    """Énumération des types de cartes supportées."""
    VISA = "visa"
    MASTERCARD = "mastercard"
    AMEX = "amex"
    DISCOVER = "discover"

class PaymentMethod(db.Model):
    """
    Modèle représentant un moyen de paiement d'un utilisateur.
    
    Attributes:
        id (int): Identifiant unique du moyen de paiement
        user_id (int): Référence vers l'utilisateur
        method_type (str): Type de méthode de paiement
        provider (str): Fournisseur de paiement
        provider_id (str): ID chez le fournisseur
        is_default (bool): Si c'est le moyen de paiement par défaut
        is_active (bool): Si le moyen de paiement est actif
        created_date (datetime): Date de création
    """
    
    __tablename__ = 'payment_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Informations du moyen de paiement
    method_type = db.Column(db.String(50), nullable=False)  # card, paypal, etc.
    provider = db.Column(db.String(100), nullable=True)  # stripe, paypal, etc.
    provider_id = db.Column(db.String(255), nullable=True)  # ID chez le fournisseur
    
    # Statuts
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Métadonnées
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        """
        Initialise un nouveau moyen de paiement.
        """
        super().__init__(**kwargs)
        
        # Si c'est le premier moyen de paiement de l'utilisateur, le mettre par défaut
        if not PaymentMethod.query.filter_by(user_id=self.user_id).first():
            self.is_default = True
    
    def get_display_name(self):
        """
        Retourne le nom d'affichage du moyen de paiement.
        
        Returns:
            str: Nom d'affichage du moyen de paiement
        """
        if self.method_type == 'card':
            return f"Carte {self.provider or 'bancaire'}"
        elif self.method_type == 'paypal':
            return "PayPal"
        elif self.method_type == 'sepa':
            return "Virement SEPA"
        else:
            return self.method_type.title()
    
    def set_as_default(self):
        """
        Définit ce moyen de paiement comme le défaut pour l'utilisateur.
        """
        # Retirer le statut par défaut des autres moyens de paiement
        PaymentMethod.query.filter_by(user_id=self.user_id, is_default=True).update({'is_default': False})
        
        # Définir celui-ci comme défaut
        self.is_default = True
        db.session.commit()
    
    def deactivate(self):
        """
        Désactive le moyen de paiement.
        """
        self.is_active = False
        
        # Si c'était le moyen par défaut, en choisir un autre
        if self.is_default:
            other_method = PaymentMethod.query.filter_by(
                user_id=self.user_id, 
                is_active=True,
                id=db.not_(self.id)
            ).first()
            
            if other_method:
                other_method.is_default = True
            
            self.is_default = False
        
        db.session.commit()
    
    def __repr__(self):
        return f'<PaymentMethod {self.get_display_name()}>'