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
        card_type (str): Type de carte (visa, mastercard, etc.)
        last_four_digits (str): 4 derniers chiffres de la carte
        expiry_month (int): Mois d'expiration
        expiry_year (int): Année d'expiration
        cardholder_name (str): Nom du porteur de la carte
        is_default (bool): Si c'est le moyen de paiement par défaut
        is_active (bool): Si le moyen de paiement est actif
        created_date (datetime): Date de création
        last_used_date (datetime): Date de dernière utilisation
    """
    
    __tablename__ = 'payment_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Informations de la carte
    card_type = db.Column(db.String(20), nullable=False)  # visa, mastercard, etc.
    last_four_digits = db.Column(db.String(4), nullable=False)
    expiry_month = db.Column(db.Integer, nullable=False)
    expiry_year = db.Column(db.Integer, nullable=False)
    cardholder_name = db.Column(db.String(100), nullable=False)
    
    # Statuts
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Métadonnées
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_date = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, **kwargs):
        """
        Initialise un nouveau moyen de paiement.
        """
        super().__init__(**kwargs)
        
        # Si c'est le premier moyen de paiement de l'utilisateur, le mettre par défaut
        if not PaymentMethod.query.filter_by(user_id=self.user_id).first():
            self.is_default = True
    
    def get_masked_number(self):
        """
        Retourne le numéro de carte masqué.
        
        Returns:
            str: Numéro masqué (ex: "**** **** **** 1234")
        """
        return f"**** **** **** {self.last_four_digits}"
    
    def get_card_type_display(self):
        """
        Retourne le nom d'affichage du type de carte.
        
        Returns:
            str: Nom du type de carte
        """
        type_names = {
            CardType.VISA.value: "Visa",
            CardType.MASTERCARD.value: "Mastercard",
            CardType.AMEX.value: "American Express",
            CardType.DISCOVER.value: "Discover"
        }
        return type_names.get(self.card_type, self.card_type.title())
    
    def get_expiry_display(self):
        """
        Retourne la date d'expiration formatée.
        
        Returns:
            str: Date d'expiration (ex: "12/25")
        """
        return f"{self.expiry_month:02d}/{str(self.expiry_year)[-2:]}"
    
    def is_expired(self):
        """
        Vérifie si la carte est expirée.
        
        Returns:
            bool: True si la carte est expirée
        """
        now = datetime.utcnow()
        return (self.expiry_year < now.year or 
                (self.expiry_year == now.year and self.expiry_month < now.month))
    
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
    
    @staticmethod
    def detect_card_type(card_number):
        """
        Détecte le type de carte basé sur le numéro.
        
        Args:
            card_number (str): Numéro de carte complet
            
        Returns:
            str: Type de carte détecté
        """
        # Supprimer tous les espaces et caractères non-numériques
        card_number = ''.join(filter(str.isdigit, card_number))
        
        # Règles de détection simplifiées
        if card_number.startswith('4'):
            return CardType.VISA.value
        elif card_number.startswith(('5', '2')):
            return CardType.MASTERCARD.value
        elif card_number.startswith(('34', '37')):
            return CardType.AMEX.value
        elif card_number.startswith('6'):
            return CardType.DISCOVER.value
        else:
            return CardType.VISA.value  # Par défaut
    
    def __repr__(self):
        return f'<PaymentMethod {self.get_card_type_display()} ****{self.last_four_digits}>'