"""
Modèle Portfolio pour suivre l'évolution du portefeuille des investisseurs.
Permet de traquer les performances et l'évolution dans le temps.
"""

from app import db
from datetime import datetime

class Portfolio(db.Model):
    """
    Modèle représentant le portefeuille d'un investisseur.
    
    Attributes:
        id (int): Identifiant unique du portefeuille
        user_id (int): Référence vers l'utilisateur
        total_value (float): Valeur totale du portefeuille
        cash_amount (float): Montant en liquidités
        invested_amount (float): Montant investi
        monthly_contribution (float): Contribution mensuelle planifiée
        target_allocation (str): Allocation cible en JSON
        last_updated (datetime): Dernière mise à jour
        created_date (datetime): Date de création
    """
    
    __tablename__ = 'portfolios'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Valeurs du portefeuille
    total_value = db.Column(db.Float, default=0.0)
    cash_amount = db.Column(db.Float, default=0.0)
    invested_amount = db.Column(db.Float, default=0.0)
    monthly_contribution = db.Column(db.Float, default=0.0)
    
    # Configuration
    target_allocation = db.Column(db.Text, nullable=True)  # JSON string
    
    # Métadonnées
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    holdings = db.relationship('PortfolioHolding', backref='portfolio', cascade='all, delete-orphan')
    
    def update_from_profile(self):
        """
        Met à jour le portefeuille basé sur le profil investisseur.
        """
        if self.user.investor_profile:
            profile = self.user.investor_profile
            
            self.cash_amount = profile.current_savings
            self.invested_amount = profile.get_total_investments()
            self.total_value = self.cash_amount + self.invested_amount
            self.monthly_contribution = profile.monthly_savings_capacity
            
            db.session.commit()
    
    def get_allocation_percentages(self):
        """
        Calcule les pourcentages d'allocation actuels.
        
        Returns:
            dict: Pourcentages par catégorie
        """
        if self.total_value == 0:
            return {}
        
        allocation = {}
        if self.user.investor_profile:
            distribution = self.user.investor_profile.get_investment_distribution()
            
            for category, value in distribution.items():
                allocation[category] = round((value / self.total_value) * 100, 2)
        
        return allocation
    
    def get_performance_summary(self):
        """
        Calcule un résumé des performances.
        
        Returns:
            dict: Résumé des performances
        """
        return {
            'total_value': self.total_value,
            'cash_percentage': round((self.cash_amount / self.total_value * 100), 2) if self.total_value > 0 else 0,
            'invested_percentage': round((self.invested_amount / self.total_value * 100), 2) if self.total_value > 0 else 0,
            'monthly_contribution': self.monthly_contribution,
            'investment_rate': round((self.invested_amount / self.total_value * 100), 2) if self.total_value > 0 else 0
        }
    
    def __repr__(self):
        return f'<Portfolio {self.user.email} - {self.total_value}€>'

class PortfolioHolding(db.Model):
    """
    Modèle représentant une position dans le portefeuille.
    
    Attributes:
        id (int): Identifiant unique
        portfolio_id (int): Référence vers le portefeuille
        asset_type (str): Type d'actif (action, obligation, immobilier, etc.)
        asset_name (str): Nom de l'actif
        quantity (float): Quantité détenue
        purchase_price (float): Prix d'achat
        current_value (float): Valeur actuelle
        date_acquired (datetime): Date d'acquisition
    """
    
    __tablename__ = 'portfolio_holdings'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    
    # Informations sur l'actif
    asset_type = db.Column(db.String(50), nullable=False)  # livret_a, pea, immobilier, etc.
    asset_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, default=1.0)
    purchase_price = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, nullable=False)
    
    # Métadonnées
    date_acquired = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_performance(self):
        """
        Calcule la performance de cette position.
        
        Returns:
            dict: Performance en valeur absolue et pourcentage
        """
        gain_loss = self.current_value - self.purchase_price
        percentage = (gain_loss / self.purchase_price * 100) if self.purchase_price > 0 else 0
        
        return {
            'gain_loss': gain_loss,
            'percentage': round(percentage, 2),
            'is_positive': gain_loss >= 0
        }
    
    def __repr__(self):
        return f'<PortfolioHolding {self.asset_name} - {self.current_value}€>'