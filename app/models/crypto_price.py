"""
Modèle pour stocker les prix des cryptomonnaies.
Permet d'éviter les appels API répétés et d'avoir un cache local.
"""

from app import db
from datetime import datetime


class CryptoPrice(db.Model):
    """
    Stockage des prix crypto récupérés depuis Binance.
    Mis à jour régulièrement pour éviter les appels API répétés.
    """
    
    __tablename__ = 'crypto_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(50), unique=True, nullable=False, index=True)  # ex: 'bitcoin', 'ethereum'
    price_usd = db.Column(db.Float, nullable=False)  # Prix en USD depuis Binance
    price_eur = db.Column(db.Float, nullable=False)  # Prix converti en EUR
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Dernière mise à jour
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Date de création
    
    def __repr__(self):
        return f'<CryptoPrice {self.symbol}: €{self.price_eur:.2f}>'
    
    @property
    def age_minutes(self):
        """Retourne l'âge des données en minutes."""
        if self.updated_at:
            delta = datetime.utcnow() - self.updated_at
            return int(delta.total_seconds() / 60)
        return 999999
    
    @property
    def is_recent(self, max_age_minutes=5):
        """Vérifie si les données sont récentes (moins de 5 minutes par défaut)."""
        return self.age_minutes <= max_age_minutes
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire."""
        return {
            'symbol': self.symbol,
            'price_usd': self.price_usd,
            'price_eur': self.price_eur,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'age_minutes': self.age_minutes,
            'is_recent': self.is_recent
        }