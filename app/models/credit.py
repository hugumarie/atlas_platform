"""
Modèle Credit pour gérer les crédits en cours des utilisateurs.
Permet de suivre les emprunts immobiliers, consommation, etc.
"""

from app import db
from datetime import datetime

class Credit(db.Model):
    """
    Modèle représentant un crédit en cours d'un utilisateur.
    
    Attributes:
        id (int): Identifiant unique du crédit
        user_id (int): Référence vers l'utilisateur
        investor_profile_id (int): Référence vers le profil investisseur
        type_credit (str): Type de crédit (immobilier, consommation, auto, etc.)
        designation (str): Description du crédit
        montant_initial (float): Montant emprunté initialement
        montant_restant (float): Capital restant dû
        mensualite (float): Mensualité à payer
        taux_interet (float): Taux d'intérêt annuel
        duree_mois (int): Durée totale en mois
        date_souscription (datetime): Date de souscription du crédit
        date_fin_prevue (datetime): Date de fin prévue
        organisme (str): Nom de l'organisme prêteur
        date_created (datetime): Date de création de l'enregistrement
        last_updated (datetime): Dernière mise à jour
    """
    
    __tablename__ = 'credits'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    investor_profile_id = db.Column(db.Integer, db.ForeignKey('investor_profiles.id'), nullable=False)
    
    # Informations sur le crédit
    type_credit = db.Column(db.String(30), nullable=False)  # immobilier, consommation, auto, travaux
    designation = db.Column(db.String(100), nullable=False)  # Description du crédit
    montant_initial = db.Column(db.Float, nullable=False)
    montant_restant = db.Column(db.Float, nullable=False)
    mensualite = db.Column(db.Float, nullable=False)
    taux_interet = db.Column(db.Float, nullable=True)  # Taux annuel en %
    duree_mois = db.Column(db.Integer, nullable=True)  # Durée totale en mois
    
    # Dates
    date_souscription = db.Column(db.Date, nullable=True)
    date_fin_prevue = db.Column(db.Date, nullable=True)
    
    # Organisme
    organisme = db.Column(db.String(100), nullable=True)
    
    # Métadonnées
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_pourcentage_rembourse(self):
        """
        Calcule le pourcentage remboursé du crédit.
        
        Returns:
            float: Pourcentage remboursé (0-100)
        """
        if not self.montant_initial or self.montant_initial == 0:
            return 0.0
            
        rembourse = self.montant_initial - (self.montant_restant or 0.0)
        return round((rembourse / self.montant_initial) * 100, 1)
    
    def get_mois_restants(self):
        """
        Calcule le nombre de mois restants approximatif.
        
        Returns:
            int: Nombre de mois restants
        """
        if not self.mensualite or self.mensualite == 0 or not self.montant_restant:
            return 0
            
        return int(self.montant_restant / self.mensualite)
    
    def get_cout_total_interets(self):
        """
        Calcule le coût total des intérêts sur la durée restante.
        
        Returns:
            float: Coût total des intérêts
        """
        if not self.duree_mois or not self.mensualite:
            return 0.0
            
        total_mensualites = self.mensualite * self.duree_mois
        return total_mensualites - self.montant_initial
    
    def __repr__(self):
        return f'<Credit {self.type_credit} - {self.designation}>'


# Ajouter la relation dans InvestorProfile
# Cette partie sera ajoutée via une migration ou modification du modèle InvestorProfile