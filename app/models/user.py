"""
Modèle User pour la gestion des utilisateurs de la plateforme.
Gère l'authentification et les informations de base des utilisateurs.
"""

from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    """
    Modèle représentant un utilisateur de la plateforme.
    
    Attributes:
        id (int): Identifiant unique de l'utilisateur
        email (str): Email de l'utilisateur (unique)
        password_hash (str): Hash du mot de passe
        first_name (str): Prénom de l'utilisateur
        last_name (str): Nom de famille de l'utilisateur
        phone (str): Numéro de téléphone (optionnel)
        profile_picture (str): Chemin vers la photo de profil
        is_admin (bool): Indique si l'utilisateur est administrateur
        is_active (bool): Statut actif du compte
        date_created (datetime): Date de création du compte
        last_login (datetime): Dernière connexion
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Champs pour la gestion des prospects et clients unifiés
    user_type = db.Column(db.String(20), default='client', nullable=False)  # 'prospect', 'client'
    is_prospect = db.Column(db.Boolean, default=False, nullable=False)  # True = prospect qui n'a pas créé de compte, False = utilisateur avec compte
    prospect_source = db.Column(db.String(50), nullable=True)  # site_vitrine, recommandation, etc.
    prospect_status = db.Column(db.String(20), default='nouveau', nullable=True)  # nouveau, contacté, qualifié, converti
    prospect_notes = db.Column(db.Text, nullable=True)
    appointment_requested = db.Column(db.Boolean, default=False, nullable=False)
    appointment_status = db.Column(db.String(20), default='en_attente', nullable=True)  # en_attente, confirmé, terminé, annulé
    assigned_to = db.Column(db.String(100), nullable=True)  # Conseiller assigné
    last_contact = db.Column(db.DateTime, nullable=True)
    
    # Système d'invitation pour prospects
    invitation_token = db.Column(db.String(255), nullable=True, unique=True)
    invitation_sent_at = db.Column(db.DateTime, nullable=True)
    invitation_expires_at = db.Column(db.DateTime, nullable=True)
    can_create_account = db.Column(db.Boolean, default=False, nullable=False)
    
    # Intégration Stripe
    stripe_customer_id = db.Column(db.String(100), nullable=True, unique=True)
    subscription_date = db.Column(db.DateTime, nullable=True)
    
    # Relations
    investor_profile = db.relationship('InvestorProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    subscription = db.relationship('Subscription', backref='user', uselist=False, cascade='all, delete-orphan')
    portfolio = db.relationship('Portfolio', backref='user', uselist=False, cascade='all, delete-orphan')
    payment_methods = db.relationship('PaymentMethod', backref='user', cascade='all, delete-orphan')
    investment_plans = db.relationship('InvestmentPlan', backref='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """
        Définit le mot de passe de l'utilisateur en le hashant.
        
        Args:
            password (str): Mot de passe en clair
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Vérifie si le mot de passe fourni correspond au hash stocké.
        
        Args:
            password (str): Mot de passe en clair à vérifier
            
        Returns:
            bool: True si le mot de passe est correct, False sinon
        """
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """
        Retourne le nom complet de l'utilisateur.
        
        Returns:
            str: Prénom et nom de famille
        """
        return f"{self.first_name} {self.last_name}"
    
    def get_profile_picture_url(self):
        """
        Retourne l'URL de la photo de profil ou une image par défaut.
        
        Returns:
            str: URL vers la photo de profil
        """
        if self.profile_picture:
            return f"/static/uploads/{self.profile_picture}"
        return "/static/img/default-avatar.svg"
    
    def update_last_login(self):
        """
        Met à jour la date de dernière connexion.
        """
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def can_access_platform(self):
        """
        Vérifie si l'utilisateur peut accéder à la plateforme.
        Permet l'accès aux clients récents (24h) même sans abonnement actif.
        """
        # Admin a toujours accès
        if self.is_admin:
            return True
            
        # Vérifier si c'est un client récent (webhook Stripe peut avoir échoué)
        from datetime import datetime, timedelta, timezone
        now = datetime.now(timezone.utc)
        if self.date_created.tzinfo is None:
            user_created = self.date_created.replace(tzinfo=timezone.utc)
        else:
            user_created = self.date_created.astimezone(timezone.utc)
        
        recent_client = (self.user_type == 'client' and 
                       not self.is_prospect and 
                       user_created > now - timedelta(hours=24))
        
        # Si client récent, autoriser l'accès
        if recent_client:
            return True
            
        # Sinon, vérifier l'abonnement
        return self.subscription and self.subscription.is_active()
    
    def has_completed_onboarding(self):
        """
        Vérifie si l'utilisateur a complété le processus d'onboarding.
        
        Returns:
            bool: True si l'onboarding est terminé (plan sélectionné + paiement), False sinon
        """
        # Admin a toujours l'onboarding "complet"
        if self.is_admin:
            return True
            
        # Un utilisateur a terminé l'onboarding s'il a un abonnement actif
        return self.subscription is not None and self.subscription.is_active()
    
    def is_prospect_type(self):
        """
        Vérifie si l'utilisateur est un prospect (ancienne méthode).
        
        Returns:
            bool: True si l'utilisateur est un prospect, False sinon
        """
        return self.user_type == 'prospect'
    
    def is_client(self):
        """
        Vérifie si l'utilisateur est un client.
        
        Returns:
            bool: True si l'utilisateur est un client, False sinon
        """
        return self.user_type == 'client'
    
    def get_status_badge_class(self):
        """
        Retourne la classe CSS pour le badge de statut prospect.
        
        Returns:
            str: Classe CSS du badge
        """
        if not self.is_prospect_type():
            return 'bg-success'  # Client
        
        status_classes = {
            'nouveau': 'bg-primary',
            'contacté': 'bg-warning',
            'qualifié': 'bg-info',
            'converti': 'bg-success',
            'perdu': 'bg-danger'
        }
        return status_classes.get(self.prospect_status, 'bg-secondary')
    
    def get_appointment_status_badge_class(self):
        """
        Retourne la classe CSS pour le badge de statut RDV.
        
        Returns:
            str: Classe CSS du badge
        """
        status_classes = {
            'en_attente': 'bg-warning',
            'confirmé': 'bg-info',
            'terminé': 'bg-success',
            'annulé': 'bg-danger'
        }
        return status_classes.get(self.appointment_status, 'bg-secondary')
    
    def update_last_contact(self):
        """
        Met à jour la date de dernier contact pour les prospects.
        """
        if self.is_prospect_type():
            self.last_contact = datetime.utcnow()
            db.session.commit()
    
    def mark_as_converted(self):
        """
        Marque le prospect comme converti en client.
        """
        if self.is_prospect_type():
            self.user_type = 'client'
            self.prospect_status = 'converti'
            self.is_prospect = False  # Le prospect devient un utilisateur avec compte
            self.update_last_contact()
    
    def generate_invitation_token(self):
        """
        Génère un token d'invitation unique et sécurisé.
        
        Returns:
            str: Token d'invitation
        """
        import secrets
        from datetime import timedelta
        
        self.invitation_token = secrets.token_urlsafe(32)
        self.invitation_sent_at = datetime.utcnow()
        self.invitation_expires_at = datetime.utcnow() + timedelta(days=7)
        self.can_create_account = True
        
        return self.invitation_token
    
    def is_invitation_valid(self):
        """
        Vérifie si l'invitation est encore valide.
        
        Returns:
            bool: True si l'invitation est valide, False sinon
        """
        if not self.invitation_token or not self.invitation_expires_at:
            return False
        
        try:
            # Gérer le problème de timezone pour la comparaison
            now_utc = datetime.utcnow()
            expires_at = self.invitation_expires_at
            if expires_at.tzinfo is not None:
                expires_at = expires_at.replace(tzinfo=None)
            
            return (
                self.can_create_account and 
                now_utc < expires_at and
                self.is_prospect_type()
            )
        except Exception as e:
            print(f"Erreur dans is_invitation_valid: {e}")
            return False
    
    def get_invitation_status(self):
        """
        Retourne le statut de l'invitation.
        
        Returns:
            str: Statut de l'invitation
        """
        try:
            if not self.invitation_token:
                return 'non_envoyée'
            
            if not self.can_create_account:
                return 'utilisée'
            
            # Gérer le problème de timezone pour la comparaison
            if not self.invitation_expires_at:
                return 'expirée'
            
            now_utc = datetime.utcnow()
            expires_at = self.invitation_expires_at
            if expires_at.tzinfo is not None:
                expires_at = expires_at.replace(tzinfo=None)
            
            if now_utc > expires_at:
                return 'expirée'
            
            return 'valide'
        except Exception as e:
            print(f"Erreur dans get_invitation_status: {e}")
            return 'erreur'
    
    def __repr__(self):
        return f'<User {self.email}>'