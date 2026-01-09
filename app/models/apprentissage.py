"""
Modèle pour les formations/apprentissages
"""

from app import db
from datetime import datetime

class Apprentissage(db.Model):
    __tablename__ = 'apprentissages'
    
    # Catégories disponibles
    CATEGORIES = [
        ('enveloppes', 'Enveloppes d\'investissement'),
        ('produits', 'Produits d\'investissement'),
        ('strategies', 'Stratégies d\'investissement'),
        ('autres', 'Autres formations')
    ]
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    categorie = db.Column(db.String(100), nullable=True)  # Nouvelle catégorie de formation
    
    # Support legacy (fichiers locaux) + nouveau système (DigitalOcean)
    fichier_pdf = db.Column(db.String(255), nullable=True)  # chemin local OU clé DigitalOcean
    fichier_pdf_original = db.Column(db.String(255), nullable=True)  # nom original du PDF
    fichier_pdf_url = db.Column(db.String(500), nullable=True)  # URL publique DigitalOcean
    
    image = db.Column(db.String(255), nullable=True)  # chemin local OU clé DigitalOcean
    image_url = db.Column(db.String(500), nullable=True)  # URL publique DigitalOcean
    
    # Métadonnées pour DigitalOcean Spaces
    storage_type = db.Column(db.String(20), default='local')  # 'local' ou 'digitalocean'
    
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    actif = db.Column(db.Boolean, default=True)  # pour désactiver sans supprimer
    ordre = db.Column(db.Integer, default=0)  # pour ordonner les formations
    
    def __repr__(self):
        return f'<Apprentissage {self.nom}>'
    
    def get_pdf_url(self):
        """Retourne l'URL du PDF (DigitalOcean ou local)"""
        if self.storage_type == 'digitalocean' and self.fichier_pdf_url:
            return self.fichier_pdf_url
        elif self.fichier_pdf:
            # URL locale
            return f'/static/uploads/apprentissages/{self.fichier_pdf}'
        return None
    
    def get_image_url(self):
        """Retourne l'URL de l'image (DigitalOcean ou locale)"""
        if self.storage_type == 'digitalocean' and self.image_url:
            return self.image_url
        elif self.image:
            # URL locale
            return f'/static/uploads/apprentissages/{self.image}'
        return None
    
    def has_pdf(self):
        """Vérifie si la formation a un PDF"""
        return bool(self.fichier_pdf_url or self.fichier_pdf)
    
    def has_image(self):
        """Vérifie si la formation a une image"""
        return bool(self.image_url or self.image)
    
    def get_categorie_display(self):
        """Retourne le nom affiché de la catégorie"""
        for key, display in self.CATEGORIES:
            if key == self.categorie:
                return display
        return self.categorie or 'Non catégorisée'

    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id': self.id,
            'nom': self.nom,
            'description': self.description,
            'fichier_pdf': self.fichier_pdf,
            'fichier_pdf_url': self.get_pdf_url(),
            'fichier_pdf_original': self.fichier_pdf_original,
            'image': self.image,
            'image_url': self.get_image_url(),
            'storage_type': self.storage_type,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None,
            'date_modification': self.date_modification.isoformat() if self.date_modification else None,
            'actif': self.actif,
            'ordre': self.ordre
        }