"""
Modèle pour les tokens de réinitialisation de mot de passe
"""

from app import db
from datetime import datetime, timedelta
import secrets

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    is_used = db.Column(db.Boolean, default=False)
    
    # Relation avec l'utilisateur
    user = db.relationship('User', backref=db.backref('password_reset_tokens', cascade='all, delete-orphan'))
    
    def __init__(self, user_id, expires_in_hours=24):
        """
        Crée un nouveau token de réinitialisation
        
        Args:
            user_id: ID de l'utilisateur
            expires_in_hours: Durée de validité en heures (défaut: 24h)
        """
        self.user_id = user_id
        self.token = secrets.token_urlsafe(32)
        self.expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    def __repr__(self):
        return f'<PasswordResetToken {self.id} - User {self.user_id} - {self.token[:8]}...>'
    
    def is_valid(self):
        """
        Vérifie si le token est encore valide
        
        Returns:
            bool: True si le token est valide, False sinon
        """
        return (
            not self.is_used and 
            self.expires_at > datetime.utcnow()
        )
    
    def mark_as_used(self):
        """Marque le token comme utilisé"""
        self.is_used = True
        self.used_at = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def create_for_user(cls, user_id):
        """
        Crée un nouveau token pour un utilisateur et invalide les anciens
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            PasswordResetToken: Le nouveau token créé
        """
        # Marquer tous les anciens tokens comme utilisés
        old_tokens = cls.query.filter_by(user_id=user_id, is_used=False).all()
        for token in old_tokens:
            token.mark_as_used()
        
        # Créer le nouveau token
        new_token = cls(user_id=user_id)
        db.session.add(new_token)
        db.session.commit()
        
        return new_token
    
    @classmethod
    def get_valid_token(cls, token_string):
        """
        Récupère un token valide par sa chaîne
        
        Args:
            token_string: La chaîne du token
            
        Returns:
            PasswordResetToken|None: Le token s'il est valide, None sinon
        """
        token = cls.query.filter_by(token=token_string).first()
        
        if token and token.is_valid():
            return token
        
        return None
    
    def to_dict(self):
        """Convertit le token en dictionnaire pour l'API"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'token': self.token,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'expires_at': self.expires_at.strftime('%Y-%m-%d %H:%M:%S') if self.expires_at else None,
            'is_used': self.is_used,
            'is_valid': self.is_valid()
        }