"""
Modèle pour les tokens d'invitation prospect
"""

from app import db
from datetime import datetime, timedelta
import secrets
import string


class InvitationToken(db.Model):
    """
    Modèle pour gérer les tokens d'invitation sécurisés
    """
    __tablename__ = 'invitation_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    prospect_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active', nullable=False)  # active, used, expired
    
    # Relations
    prospect = db.relationship('User', backref='invitation_tokens')
    
    def __init__(self, prospect_id, expiry_days=7):
        """
        Crée un nouveau token d'invitation
        
        Args:
            prospect_id: ID du prospect
            expiry_days: Nombre de jours de validité (défaut: 7)
        """
        self.prospect_id = prospect_id
        self.token = self._generate_secure_token()
        self.expires_at = datetime.utcnow() + timedelta(days=expiry_days)
        self.status = 'active'
    
    def _generate_secure_token(self) -> str:
        """
        Génère un token sécurisé unique
        
        Returns:
            str: Token de 64 caractères
        """
        # Utilise secrets pour la sécurité cryptographique
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(64))
    
    def is_valid(self) -> bool:
        """
        Vérifie si le token est valide (non expiré, non utilisé)
        
        Returns:
            bool: True si valide, False sinon
        """
        now = datetime.utcnow()
        return (
            self.status == 'active' and
            self.used_at is None and
            self.expires_at > now
        )
    
    def mark_as_used(self):
        """
        Marque le token comme utilisé
        """
        self.used_at = datetime.utcnow()
        self.status = 'used'
        db.session.commit()
    
    def mark_as_expired(self):
        """
        Marque le token comme expiré
        """
        self.status = 'expired'
        db.session.commit()
    
    def get_remaining_hours(self) -> int:
        """
        Retourne le nombre d'heures restantes avant expiration
        
        Returns:
            int: Heures restantes (0 si expiré)
        """
        if self.expires_at <= datetime.utcnow():
            return 0
        
        delta = self.expires_at - datetime.utcnow()
        return int(delta.total_seconds() / 3600)
    
    @staticmethod
    def cleanup_expired():
        """
        Nettoie les tokens expirés (marque comme expired)
        À appeler périodiquement via cron
        """
        expired_tokens = InvitationToken.query.filter(
            InvitationToken.expires_at <= datetime.utcnow(),
            InvitationToken.status == 'active'
        ).all()
        
        for token in expired_tokens:
            token.mark_as_expired()
        
        return len(expired_tokens)
    
    def to_dict(self):
        """
        Convertit en dictionnaire pour JSON
        """
        return {
            'id': self.id,
            'token': self.token,
            'prospect_id': self.prospect_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'status': self.status,
            'is_valid': self.is_valid(),
            'remaining_hours': self.get_remaining_hours()
        }
    
    def __repr__(self):
        return f'<InvitationToken {self.token[:8]}... for prospect {self.prospect_id}>'