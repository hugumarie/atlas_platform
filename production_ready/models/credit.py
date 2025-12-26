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
    investor_profile_id = db.Column(db.Integer, db.ForeignKey('investor_profiles.id'), nullable=False)
    
    # Informations sur le crédit - mapping avec les vraies colonnes de la table
    type_credit = db.Column(db.String(30), nullable=True)  # immobilier, consommation, auto, travaux
    description = db.Column('description', db.String(100), nullable=True)  # Description du crédit
    montant_initial = db.Column('initial_amount', db.Float, nullable=True)
    montant_restant = db.Column('remaining_amount', db.Float, nullable=True)
    mensualite = db.Column('monthly_payment', db.Float, nullable=True)
    taux_interet = db.Column('interest_rate', db.Float, nullable=True)  # Taux annuel en %
    duree_annees = db.Column('duration_years', db.Integer, nullable=True)  # Durée en années
    
    @property
    def duree_mois(self):
        """Convertit la durée en années vers mois."""
        if self.duree_annees:
            return self.duree_annees * 12
        return 0
    
    @duree_mois.setter
    def duree_mois(self, mois):
        """Convertit les mois en années pour stockage en DB."""
        if mois:
            self.duree_annees = int(mois / 12)
        else:
            self.duree_annees = None
    
    # Dates
    date_souscription = db.Column('start_date', db.Date, nullable=True)
    date_fin_prevue = db.Column('end_date', db.Date, nullable=True)
    
    # Champs calculés automatiquement
    calculated_monthly_payment = db.Column(db.Float, nullable=True)  # Mensualité calculée
    calculated_remaining_capital = db.Column(db.Float, nullable=True)  # Capital restant calculé
    last_calculation_date = db.Column(db.DateTime, nullable=True)  # Date du dernier calcul
    
    # Métadonnées - mapping avec les vraies colonnes
    date_created = db.Column('created_date', db.DateTime, default=datetime.utcnow)
    last_updated = db.Column('updated_date', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    
    def update_calculations(self):
        """
        Met à jour les calculs du crédit en utilisant le service de calcul.
        """
        from app.services.credit_calculation import CreditCalculationService
        
        if not all([self.montant_initial, self.taux_interet, self.duree_mois, self.date_souscription]):
            return
        
        try:
            # Calcul de la mensualité
            self.calculated_monthly_payment = CreditCalculationService.calculate_monthly_payment(
                self.montant_initial, self.taux_interet, self.duree_mois
            )
            
            # Calcul du capital restant
            self.calculated_remaining_capital = CreditCalculationService.calculate_remaining_capital(
                self.montant_initial, self.taux_interet, self.duree_mois, self.date_souscription
            )
            
            # Mise à jour des champs principaux si nécessaire
            if self.mensualite == 0:
                self.mensualite = self.calculated_monthly_payment
            
            self.montant_restant = self.calculated_remaining_capital
            self.last_calculation_date = datetime.utcnow()
            
        except Exception as e:
            print(f"Erreur lors du calcul du crédit {self.id}: {e}")
    
    def get_remaining_capital_display(self):
        """
        Retourne le montant restant à rembourser pour l'affichage.
        Utilise en priorité le calcul automatique.
        """
        if self.calculated_remaining_capital is not None:
            return self.calculated_remaining_capital
        return self.montant_restant or 0.0
    
    def get_monthly_payment_display(self):
        """
        Retourne la mensualité pour l'affichage.
        Utilise en priorité le calcul automatique.
        """
        if self.calculated_monthly_payment is not None:
            return self.calculated_monthly_payment
        return self.mensualite or 0.0
    
    def __repr__(self):
        return f'<Credit {self.type_credit} - {self.designation}>'