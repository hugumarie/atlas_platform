"""
Modèle pour les comptes rendus de rendez-vous
"""

from app import db
from datetime import datetime

class CompteRendu(db.Model):
    __tablename__ = 'comptes_rendus'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    titre = db.Column(db.String(200))
    date_rdv = db.Column(db.Date, nullable=False)
    type_rdv = db.Column(db.String(50))  # RDV invest, RDV suivi, Contact
    prochaine_action = db.Column(db.String(50))  # Autre invest, Suivi classique
    contenu = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relation avec l'utilisateur
    user = db.relationship('User', backref=db.backref('comptes_rendus', cascade='all, delete-orphan', order_by='CompteRendu.date_rdv.desc()'))
    
    def __repr__(self):
        return f'<CompteRendu {self.id} - User {self.user_id} - {self.date_rdv}>'
    
    def to_dict(self):
        """Convertit le compte rendu en dictionnaire pour l'API"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'titre': self.titre,
            'date_rdv': self.date_rdv.strftime('%Y-%m-%d') if self.date_rdv else None,
            'date_rdv_formatted': self.date_rdv.strftime('%d/%m/%Y') if self.date_rdv else None,
            'type_rdv': self.type_rdv,
            'prochaine_action': self.prochaine_action,
            'contenu': self.contenu,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
    
    def get_preview(self, max_lines=4):
        """Retourne un aperçu du contenu (HTML tronqué)"""
        if not self.contenu:
            return "Aucun contenu"
        
        # Si c'est du HTML, on prend les premiers caractères et on ajoute ...
        content = self.contenu.strip()
        if len(content) > 200:
            # Tronquer le HTML proprement
            import re
            # Supprimer les tags HTML pour compter les caractères de texte
            text_only = re.sub(r'<[^>]+>', '', content)
            if len(text_only) > 150:
                # Tronquer et fermer les tags ouverts
                truncated = content[:200] + '...'
                return truncated
        
        return content