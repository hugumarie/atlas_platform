"""
Modèle pour les actions d'investissement mensuelles à réaliser par les utilisateurs.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app import db


class InvestmentAction(db.Model):
    """
    Actions d'investissement récurrentes générées chaque mois pour chaque utilisateur.
    
    Chaque action correspond à une ligne du plan d'investissement d'un utilisateur
    pour un mois donné, avec le montant attendu et le suivi de réalisation.
    """
    __tablename__ = 'investment_actions'
    
    id = Column(Integer, primary_key=True)
    
    # Relations
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    plan_line_id = Column(Integer, ForeignKey('investment_plan_lines.id'), nullable=False)
    
    # Période cible (format YYYY-MM, ex: "2024-12")
    year_month = Column(String(7), nullable=False)
    
    # Détails de l'investissement
    support_type = Column(String(50), nullable=False)  # PEA, CTO, Assurance Vie, etc.
    label = Column(String(200), nullable=True)  # Description/nom de l'investissement
    
    # Montants
    expected_amount = Column(Float, nullable=False, default=0.0)  # Montant attendu
    realized_amount = Column(Float, nullable=True, default=0.0)   # Montant réellement investi
    
    # Statut de l'action
    # pending: en attente de réalisation
    # done: réalisé avec le montant attendu
    # adjusted: réalisé avec un montant différent
    # skipped: reporté/non fait ce mois-ci
    status = Column(String(20), nullable=False, default='pending')
    
    # Horodatage
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    answered_at = Column(DateTime, nullable=True)  # Date de réponse de l'utilisateur
    
    # Relations
    user = relationship("User", backref="investment_actions")
    plan_line = relationship("InvestmentPlanLine", backref="actions")
    
    # Index unique pour éviter les doublons
    __table_args__ = (
        Index('idx_unique_action', 'user_id', 'plan_line_id', 'year_month', unique=True),
        Index('idx_user_year_month', 'user_id', 'year_month'),
        Index('idx_status_year_month', 'status', 'year_month'),
    )
    
    def __repr__(self):
        return f"<InvestmentAction {self.user_id} - {self.support_type} - {self.year_month} - {self.expected_amount}€>"
    
    @property
    def is_pending(self):
        """Retourne True si l'action est en attente de réalisation."""
        return self.status == 'pending'
    
    @property
    def is_completed(self):
        """Retourne True si l'action a été réalisée (done ou adjusted)."""
        return self.status in ['done', 'adjusted']
    
    @property
    def actual_amount(self):
        """Retourne le montant réellement investi, ou 0 si pas encore fait."""
        if self.status in ['done', 'adjusted']:
            return self.realized_amount or 0.0
        return 0.0
    
    @property
    def completion_rate(self):
        """Retourne le taux de réalisation (montant réalisé / montant attendu)."""
        if not self.expected_amount or self.expected_amount <= 0:
            return 0.0
        if not self.is_completed:
            return 0.0
        return min(100.0, (self.actual_amount / self.expected_amount) * 100)
    
    def mark_as_done(self):
        """Marque l'action comme réalisée avec le montant attendu."""
        self.status = 'done'
        self.realized_amount = self.expected_amount
        self.answered_at = datetime.utcnow()
    
    def mark_as_adjusted(self, amount):
        """Marque l'action comme réalisée avec un montant personnalisé."""
        self.status = 'adjusted'
        self.realized_amount = float(amount)
        self.answered_at = datetime.utcnow()
    
    def mark_as_skipped(self):
        """Marque l'action comme reportée/non réalisée."""
        self.status = 'skipped'
        self.realized_amount = 0.0
        self.answered_at = datetime.utcnow()
    
    @classmethod
    def get_monthly_actions(cls, user_id, year_month):
        """Récupère toutes les actions d'un utilisateur pour un mois donné."""
        return cls.query.filter_by(
            user_id=user_id,
            year_month=year_month
        ).order_by(cls.expected_amount.desc()).all()
    
    @classmethod
    def get_pending_actions(cls, user_id, year_month):
        """Récupère les actions en attente pour un utilisateur et un mois donné."""
        return cls.query.filter_by(
            user_id=user_id,
            year_month=year_month,
            status='pending'
        ).order_by(cls.expected_amount.desc()).all()
    
    @classmethod
    def calculate_monthly_stats(cls, user_id, year_month):
        """Calcule les statistiques mensuelles d'un utilisateur."""
        actions = cls.get_monthly_actions(user_id, year_month)
        
        if not actions:
            return {
                'total_expected': 0.0,
                'total_realized': 0.0,
                'completion_rate': 0.0,
                'pending_count': 0,
                'completed_count': 0
            }
        
        total_expected = sum(action.expected_amount for action in actions)
        total_realized = sum(action.actual_amount for action in actions)
        pending_count = len([a for a in actions if a.is_pending])
        completed_count = len([a for a in actions if a.is_completed])
        
        completion_rate = 0.0
        if total_expected > 0:
            completion_rate = min(100.0, (total_realized / total_expected) * 100)
        
        return {
            'total_expected': total_expected,
            'total_realized': total_realized,
            'completion_rate': completion_rate,
            'pending_count': pending_count,
            'completed_count': completed_count
        }
    
    @classmethod
    def calculate_yearly_stats(cls, user_id, year):
        """Calcule les statistiques annuelles d'un utilisateur."""
        from sqlalchemy import and_, func
        
        actions = cls.query.filter(
            and_(
                cls.user_id == user_id,
                cls.year_month.like(f"{year}-%")
            )
        ).all()
        
        if not actions:
            return {
                'total_expected': 0.0,
                'total_realized': 0.0,
                'completion_rate': 0.0,
                'months_with_actions': 0
            }
        
        total_expected = sum(action.expected_amount for action in actions)
        total_realized = sum(action.actual_amount for action in actions)
        
        # Nombre de mois avec des actions
        months_with_actions = len(set(action.year_month for action in actions))
        
        completion_rate = 0.0
        if total_expected > 0:
            completion_rate = min(100.0, (total_realized / total_expected) * 100)
        
        return {
            'total_expected': total_expected,
            'total_realized': total_realized,
            'completion_rate': completion_rate,
            'months_with_actions': months_with_actions
        }