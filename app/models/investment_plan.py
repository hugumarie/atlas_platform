"""
Modèles pour le plan d'investissement mensuel des utilisateurs.
"""

from app import db
from datetime import datetime
from sqlalchemy import Index


class InvestmentPlan(db.Model):
    """
    Plan d'investissement mensuel d'un utilisateur.
    """
    __tablename__ = 'investment_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False, default="Plan principal")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relations  
    lines = db.relationship('InvestmentPlanLine', back_populates='plan', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<InvestmentPlan {self.id}: {self.name} for User {self.user_id}>'
    
    @property
    def total_percentage(self):
        """Calcule le pourcentage total du plan."""
        return sum(line.percentage for line in self.lines if line.percentage)
    
    @property 
    def monthly_investment_amount(self):
        """Récupère le montant d'investissement mensuel depuis le profil utilisateur."""
        if self.user and self.user.investor_profile:
            return self.user.investor_profile.monthly_savings_capacity or 0
        return 0
    
    def validate_percentages(self):
        """Valide que la somme des pourcentages ne dépasse pas 100%."""
        return self.total_percentage <= 100
    
    def to_dict(self):
        """Convertit le plan en dictionnaire pour l'API."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'is_active': self.is_active,
            'total_percentage': self.total_percentage,
            'monthly_investment_amount': self.monthly_investment_amount,
            'lines': [line.to_dict() for line in self.lines],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class InvestmentPlanLine(db.Model):
    """
    Ligne d'investissement dans un plan mensuel.
    """
    __tablename__ = 'investment_plan_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('investment_plans.id'), nullable=False)
    
    # Champs du plan d'investissement
    support_envelope = db.Column(db.String(100), nullable=False)  # PEA, Assurance Vie, CTO, etc.
    description = db.Column(db.String(200), nullable=False)  # ETF World, etc.
    reference = db.Column(db.String(50), nullable=True)  # ISIN, etc.
    percentage = db.Column(db.Float, nullable=False, default=0.0)  # Pourcentage du montant mensuel
    
    # Métadonnées
    order_index = db.Column(db.Integer, nullable=False, default=0)  # Ordre d'affichage
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relations
    plan = db.relationship('InvestmentPlan', back_populates='lines')
    
    # Index pour optimiser les requêtes
    __table_args__ = (
        Index('idx_plan_order', 'plan_id', 'order_index'),
    )
    
    def __repr__(self):
        return f'<InvestmentPlanLine {self.id}: {self.description} ({self.percentage}%)>'
    
    @property
    def computed_amount(self):
        """Calcule le montant en euros pour cette ligne."""
        if self.plan and self.plan.monthly_investment_amount and self.percentage:
            return round((self.plan.monthly_investment_amount * self.percentage / 100), 2)
        return 0.0
    
    def to_dict(self):
        """Convertit la ligne en dictionnaire pour l'API."""
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'support_envelope': self.support_envelope,
            'description': self.description,
            'reference': self.reference,
            'percentage': self.percentage,
            'computed_amount': self.computed_amount,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# Constantes pour les supports/enveloppes disponibles
AVAILABLE_ENVELOPES = [
    ('PEA', 'PEA - Plan d\'Épargne en Actions'),
    ('PER', 'PER - Plan d\'Épargne Retraite'),
    ('Assurance Vie', 'AV - Assurance Vie'),
    ('CTO', 'CTO - Compte-Titres Ordinaire'),
    ('PEE', 'PEE - Plan d\'Épargne Entreprise'),
    ('PERCO', 'PERCO - Plan d\'Épargne Retraite Collectif'),
    ('SCPI', 'SCPI - Société Civile de Placement Immobilier'),
    ('Private Equity', 'PE - Private Equity'),
    ('Crowdfunding', 'CF - Crowdfunding'),
    ('Livret A', 'LA - Livret A'),
    ('LDDS', 'LDDS - Livret de Développement Durable et Solidaire'),
    ('Compte courant', 'CC - Compte courant'),
    ('Autre', 'Autre support')
]