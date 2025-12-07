"""
Modèle pour les formations/apprentissages
"""

from app import db
from datetime import datetime

class Apprentissage(db.Model):
    __tablename__ = 'apprentissages'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    fichier_pdf = db.Column(db.String(255), nullable=True)  # chemin vers le fichier PDF
    fichier_pdf_original = db.Column(db.String(255), nullable=True)  # nom original du PDF
    image = db.Column(db.String(255), nullable=True)  # chemin vers l'image de la formation
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    actif = db.Column(db.Boolean, default=True)  # pour désactiver sans supprimer
    ordre = db.Column(db.Integer, default=0)  # pour ordonner les formations
    
    def __repr__(self):
        return f'<Apprentissage {self.nom}>'
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id': self.id,
            'nom': self.nom,
            'description': self.description,
            'fichier_pdf': self.fichier_pdf,
            'image': self.image,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None,
            'date_modification': self.date_modification.isoformat() if self.date_modification else None,
            'actif': self.actif,
            'ordre': self.ordre
        }