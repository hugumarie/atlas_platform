"""
Modèle InvestorProfile pour stocker les informations financières des investisseurs.
Contient les réponses au questionnaire de profil et les données financières.
"""

from app import db
from datetime import datetime

class InvestorProfile(db.Model):
    """
    Modèle représentant le profil d'investisseur d'un utilisateur.
    
    Attributes:
        id (int): Identifiant unique du profil
        user_id (int): Référence vers l'utilisateur
        monthly_net_income (float): Salaire net mensuel
        current_savings (float): Épargne actuelle totale
        monthly_savings_capacity (float): Capacité d'épargne mensuelle
        risk_tolerance (str): Tolérance au risque (conservateur, modéré, dynamique)
        investment_experience (str): Expérience en investissement
        investment_goals (str): Objectifs d'investissement
        investment_horizon (str): Horizon de placement
        family_situation (str): Situation familiale
        professional_situation (str): Situation professionnelle
        has_real_estate (bool): Possède de l'immobilier
        real_estate_value (float): Valeur immobilière
        has_life_insurance (bool): Possède une assurance vie
        life_insurance_value (float): Valeur assurance vie
        has_pea (bool): Possède un PEA
        pea_value (float): Valeur du PEA
        has_livret_a (bool): Possède un Livret A
        livret_a_value (float): Valeur du Livret A
        other_investments (str): Autres investissements
        date_completed (datetime): Date de complétion du questionnaire
        last_updated (datetime): Dernière mise à jour
    """
    
    __tablename__ = 'investor_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Informations financières de base
    monthly_net_income = db.Column(db.Float, nullable=False)
    current_savings = db.Column(db.Float, nullable=False)
    monthly_savings_capacity = db.Column(db.Float, nullable=False)
    
    # Profil de risque et objectifs
    risk_tolerance = db.Column(db.String(20), nullable=False)  # conservateur, modéré, dynamique
    investment_experience = db.Column(db.String(20), nullable=False)  # débutant, intermédiaire, expérimenté
    investment_goals = db.Column(db.Text, nullable=False)
    investment_horizon = db.Column(db.String(20), nullable=False)  # court, moyen, long terme
    
    # Situation personnelle
    family_situation = db.Column(db.String(20), nullable=False)  # célibataire, en couple, famille
    professional_situation = db.Column(db.String(30), nullable=False)  # salarié, indépendant, retraité
    
    # Section 1 - Identité
    civilite = db.Column(db.String(10), nullable=True)  # M., Mme
    date_naissance = db.Column(db.Date, nullable=True)
    lieu_naissance = db.Column(db.String(100), nullable=True)  # Lieu de naissance
    nationalite = db.Column(db.String(50), nullable=True)
    pays_residence = db.Column(db.String(50), nullable=True)
    pays_residence_fiscal = db.Column(db.String(50), nullable=True)  # Pays de résidence fiscal
    
    # Section 2 - Revenus étendus
    metier = db.Column(db.String(100), nullable=True)  # Métier/profession
    revenus_complementaires = db.Column(db.Float, nullable=True)  # Ancien champ (maintenu pour compatibilité)
    revenus_complementaires_json = db.Column(db.Text, nullable=True)  # Nouveau format JSON
    charges_mensuelles = db.Column(db.Float, nullable=True)  # Ancien champ (maintenu pour compatibilité)
    charges_mensuelles_json = db.Column(db.Text, nullable=True)  # Nouveau format JSON
    cryptos_json = db.Column(db.Text, nullable=True)  # Cryptomonnaies JSON
    liquidites_personnalisees_json = db.Column(db.Text, nullable=True)  # Liquidités personnalisées JSON
    placements_personnalises_json = db.Column(db.Text, nullable=True)  # Placements personnalisés JSON
    # taux_epargne calculé automatiquement via méthode
    
    # Investissements actuels - Section 3 Patrimoine
    has_real_estate = db.Column(db.Boolean, default=False)
    real_estate_value = db.Column(db.Float, default=0.0)
    
    # Nouveau: Immobilier et autres biens
    has_immobilier = db.Column(db.Boolean, default=False)
    immobilier_value = db.Column(db.Float, default=0.0)
    
    has_autres_biens = db.Column(db.Boolean, default=False)
    autres_biens_value = db.Column(db.Float, default=0.0)
    
    has_life_insurance = db.Column(db.Boolean, default=False)
    life_insurance_value = db.Column(db.Float, default=0.0)
    
    has_pea = db.Column(db.Boolean, default=False)
    pea_value = db.Column(db.Float, default=0.0)
    
    has_livret_a = db.Column(db.Boolean, default=False)
    livret_a_value = db.Column(db.Float, default=0.0)
    
    has_ldds = db.Column(db.Boolean, default=False)
    ldds_value = db.Column(db.Float, default=0.0)
    
    has_pel = db.Column(db.Boolean, default=False)
    pel_value = db.Column(db.Float, default=0.0)
    
    has_cel = db.Column(db.Boolean, default=False)
    cel_value = db.Column(db.Float, default=0.0)
    
    has_autres_livrets = db.Column(db.Boolean, default=False)
    autres_livrets_value = db.Column(db.Float, default=0.0)
    
    has_per = db.Column(db.Boolean, default=False)
    per_value = db.Column(db.Float, default=0.0)
    
    has_pee = db.Column(db.Boolean, default=False)
    pee_value = db.Column(db.Float, default=0.0)
    
    has_cto = db.Column(db.Boolean, default=False)
    cto_value = db.Column(db.Float, default=0.0)
    
    has_private_equity = db.Column(db.Boolean, default=False)
    private_equity_value = db.Column(db.Float, default=0.0)
    
    has_crowdfunding = db.Column(db.Boolean, default=False)
    crowdfunding_value = db.Column(db.Float, default=0.0)
    
    other_investments = db.Column(db.Text, nullable=True)
    
    # Section 4 - Objectifs d'investissement
    objectif_constitution_epargne = db.Column(db.Boolean, default=False)
    objectif_retraite = db.Column(db.Boolean, default=False)
    objectif_transmission = db.Column(db.Boolean, default=False)
    objectif_defiscalisation = db.Column(db.Boolean, default=False)
    objectif_immobilier = db.Column(db.Boolean, default=False)
    
    # Section 5 - Profil de risque
    profil_risque_connu = db.Column(db.Boolean, default=False)
    profil_risque_choisi = db.Column(db.String(20), nullable=True)  # conservateur, modéré, dynamique
    
    # Section 6 - Questions de risque détaillées
    question_1_reponse = db.Column(db.String(100), nullable=True)
    question_2_reponse = db.Column(db.String(100), nullable=True)
    question_3_reponse = db.Column(db.String(100), nullable=True)
    question_4_reponse = db.Column(db.String(100), nullable=True)
    question_5_reponse = db.Column(db.String(100), nullable=True)
    synthese_profil_risque = db.Column(db.String(500), nullable=True)  # Synthèse automatique
    
    # Métadonnées
    date_completed = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    credits = db.relationship('Credit', backref='investor_profile', cascade='all, delete-orphan')
    
    def get_total_investments(self):
        """
        Calcule la valeur totale des investissements.
        
        Returns:
            float: Valeur totale des investissements
        """
        total = 0.0
        if self.has_livret_a:
            total += self.livret_a_value or 0.0
        if self.has_ldds:
            total += self.ldds_value or 0.0
        if self.has_pel:
            total += self.pel_value or 0.0
        if self.has_cel:
            total += self.cel_value or 0.0
        if self.has_autres_livrets:
            total += self.autres_livrets_value or 0.0
        if self.has_pea:
            total += self.pea_value or 0.0
        if self.has_per:
            total += self.per_value or 0.0
        if self.has_pee:
            total += self.pee_value or 0.0
        if self.has_life_insurance:
            total += self.life_insurance_value or 0.0
        if self.has_cto:
            total += self.cto_value or 0.0
        if self.has_private_equity:
            total += self.private_equity_value or 0.0
        if self.has_crowdfunding:
            total += self.crowdfunding_value or 0.0
        return total
    
    def get_taux_epargne(self):
        """
        Calcule le taux d'épargne automatiquement.
        
        Returns:
            float: Taux d'épargne en pourcentage (0-100)
        """
        if not self.monthly_net_income or self.monthly_net_income == 0:
            return 0.0
        
        capacity = self.monthly_savings_capacity or 0.0
        return round((capacity / self.monthly_net_income) * 100, 1)
    
    def get_total_patrimoine(self):
        """
        Calcule le patrimoine total (liquidités + placements + immobilier + autres biens).
        
        Returns:
            float: Patrimoine total
        """
        total = 0.0
        
        # Liquidités
        if self.has_livret_a:
            total += self.livret_a_value or 0.0
        if self.has_ldds:
            total += self.ldds_value or 0.0
        if self.has_pel:
            total += self.pel_value or 0.0
        if self.has_cel:
            total += self.cel_value or 0.0
        if self.has_autres_livrets:
            total += self.autres_livrets_value or 0.0
            
        # Placements financiers
        if self.has_pea:
            total += self.pea_value or 0.0
        if self.has_per:
            total += self.per_value or 0.0
        if self.has_pee:
            total += self.pee_value or 0.0
        if self.has_life_insurance:
            total += self.life_insurance_value or 0.0
        if self.has_cto:
            total += self.cto_value or 0.0
        if self.has_private_equity:
            total += self.private_equity_value or 0.0
        if self.has_crowdfunding:
            total += self.crowdfunding_value or 0.0
            
        # Immobilier
        if self.has_real_estate:
            total += self.real_estate_value or 0.0
        if self.has_immobilier:
            total += self.immobilier_value or 0.0
            
        # Autres biens
        if self.has_autres_biens:
            total += self.autres_biens_value or 0.0
            
        return total
    
    def get_patrimoine_net(self):
        """
        Calcule le patrimoine net (patrimoine total - crédits).
        
        Returns:
            float: Patrimoine net
        """
        total_patrimoine = self.get_total_patrimoine()
        
        # Soustraire les crédits si le modèle Credit existe
        total_credits = 0.0
        if hasattr(self, 'credits'):
            for credit in self.credits:
                total_credits += credit.montant_restant or 0.0
                
        return total_patrimoine - total_credits
    
    def calculate_profil_risque_from_questions(self):
        """
        Calcule le profil de risque basé sur les réponses aux questions.
        
        Returns:
            str: Profil de risque calculé
        """
        if not all([self.question_1_reponse, self.question_2_reponse, self.question_3_reponse, 
                   self.question_4_reponse, self.question_5_reponse]):
            return None
            
        # TODO: Implémenter la logique de calcul du profil de risque
        # basée sur les réponses aux questions
        score = 0
        
        # Exemple de logique de scoring
        # Question 1: Horizon de placement
        if "long terme" in (self.question_1_reponse or "").lower():
            score += 2
        elif "moyen terme" in (self.question_1_reponse or "").lower():
            score += 1
            
        # Question 2: Tolérance aux fluctuations
        if "acceptable" in (self.question_2_reponse or "").lower():
            score += 2
        elif "modérée" in (self.question_2_reponse or "").lower():
            score += 1
            
        # Questions 3-5: Ajouter logique similaire
        
        if score >= 8:
            return "dynamique"
        elif score >= 4:
            return "modéré"
        else:
            return "conservateur"
    
    def get_investment_distribution(self):
        """
        Retourne la répartition des investissements pour les graphiques.
        
        Returns:
            dict: Dictionnaire avec les catégories et leurs valeurs
        """
        distribution = {}
        
        if self.has_livret_a and self.livret_a_value > 0:
            distribution['Livret A'] = self.livret_a_value
            
        if self.has_ldds and self.ldds_value > 0:
            distribution['Livret de développement durable et solidaire (LDDS)'] = self.ldds_value
            
        if self.has_pel and self.pel_value > 0:
            distribution['Plan d\'Épargne Logement (PEL)'] = self.pel_value
            
        if self.has_cel and self.cel_value > 0:
            distribution['Compte d\'Épargne Logement (CEL)'] = self.cel_value
            
        if self.has_autres_livrets and self.autres_livrets_value > 0:
            distribution['Autres livrets'] = self.autres_livrets_value
        
        if self.has_pea and self.pea_value > 0:
            distribution['Plan d\'Épargne en Actions (PEA)'] = self.pea_value
        
        if self.has_per and self.per_value > 0:
            distribution['Plan d\'Épargne Retraite (PER)'] = self.per_value
            
        if self.has_pee and self.pee_value > 0:
            distribution['Plan d\'Épargne Entreprise (PEE/PERCO)'] = self.pee_value
        
        if self.has_life_insurance and self.life_insurance_value > 0:
            distribution['Assurance Vie'] = self.life_insurance_value
            
        if self.has_cto and self.cto_value > 0:
            distribution['Compte Titres Ordinaire (CTO)'] = self.cto_value
            
        if self.has_private_equity and self.private_equity_value > 0:
            distribution['Private Equity (PE)'] = self.private_equity_value
            
        if self.has_crowdfunding and self.crowdfunding_value > 0:
            distribution['Crowdfunding'] = self.crowdfunding_value
            
        if self.has_real_estate and self.real_estate_value > 0:
            distribution['Immobilier'] = self.real_estate_value
            
        if self.has_immobilier and self.immobilier_value > 0:
            distribution['Immobilier'] += self.immobilier_value or 0.0
            
        if self.has_autres_biens and self.autres_biens_value > 0:
            distribution['Autres biens'] = self.autres_biens_value
        
        return distribution
    
    def get_risk_score(self):
        """
        Calcule un score de risque basé sur le profil.
        
        Returns:
            int: Score de risque de 1 à 10
        """
        score = 5  # Score de base
        
        # Ajustement selon la tolérance au risque
        if self.risk_tolerance == 'conservateur':
            score = 3
        elif self.risk_tolerance == 'modéré':
            score = 5
        elif self.risk_tolerance == 'dynamique':
            score = 8
        
        # Ajustement selon l'expérience
        if self.investment_experience == 'débutant':
            score = max(1, score - 2)
        elif self.investment_experience == 'expérimenté':
            score = min(10, score + 1)
        
        return score
    
    @property
    def revenus_complementaires_data(self):
        """
        Retourne les revenus complémentaires sous forme de liste de dictionnaires.
        
        Returns:
            list: Liste des revenus complémentaires [{'name': str, 'amount': float}]
        """
        if not self.revenus_complementaires_json:
            return []
        
        try:
            import json
            return json.loads(self.revenus_complementaires_json)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_revenus_complementaires_data(self, data):
        """
        Sauvegarde les revenus complémentaires en format JSON.
        
        Args:
            data (list): Liste des revenus [{'name': str, 'amount': float}]
        """
        if data:
            import json
            self.revenus_complementaires_json = json.dumps(data)
        else:
            self.revenus_complementaires_json = None
    
    @property
    def charges_mensuelles_data(self):
        """
        Retourne les charges mensuelles sous forme de liste de dictionnaires.
        
        Returns:
            list: Liste des charges mensuelles [{'name': str, 'amount': float}]
        """
        if not self.charges_mensuelles_json:
            return []
        
        try:
            import json
            return json.loads(self.charges_mensuelles_json)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_charges_mensuelles_data(self, data):
        """
        Sauvegarde les charges mensuelles en format JSON.
        
        Args:
            data (list): Liste des charges [{'name': str, 'amount': float}]
        """
        if data:
            import json
            self.charges_mensuelles_json = json.dumps(data)
        else:
            self.charges_mensuelles_json = None
    
    @property
    def cryptos_data(self):
        """
        Retourne les cryptomonnaies sous forme de liste de dictionnaires.
        
        Returns:
            list: Liste des cryptos [{'symbol': str, 'quantity': float}]
        """
        if not self.cryptos_json:
            return []
        
        try:
            import json
            return json.loads(self.cryptos_json)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_cryptos_data(self, data):
        """
        Sauvegarde les cryptomonnaies en format JSON.
        
        Args:
            data (list): Liste des cryptos [{'symbol': str, 'quantity': float}]
        """
        if data:
            import json
            self.cryptos_json = json.dumps(data)
        else:
            self.cryptos_json = None
    
    @property
    def liquidites_personnalisees_data(self):
        """
        Retourne les liquidités personnalisées sous forme de liste de dictionnaires.
        
        Returns:
            list: Liste des liquidités [{'name': str, 'amount': float}]
        """
        if not self.liquidites_personnalisees_json:
            return []
        
        try:
            import json
            return json.loads(self.liquidites_personnalisees_json)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_liquidites_personnalisees_data(self, data):
        """
        Sauvegarde les liquidités personnalisées en format JSON.
        
        Args:
            data (list): Liste des liquidités [{'name': str, 'amount': float}]
        """
        if data:
            import json
            self.liquidites_personnalisees_json = json.dumps(data)
        else:
            self.liquidites_personnalisees_json = None
    
    @property
    def placements_personnalises_data(self):
        """
        Retourne les placements personnalisés sous forme de liste de dictionnaires.
        
        Returns:
            list: Liste des placements [{'name': str, 'amount': float}]
        """
        if not self.placements_personnalises_json:
            return []
        
        try:
            import json
            return json.loads(self.placements_personnalises_json)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_placements_personnalises_data(self, data):
        """
        Sauvegarde les placements personnalisés en format JSON.
        
        Args:
            data (list): Liste des placements [{'name': str, 'amount': float}]
        """
        if data:
            import json
            self.placements_personnalises_json = json.dumps(data)
        else:
            self.placements_personnalises_json = None
    
    def __repr__(self):
        return f'<InvestorProfile {self.user.get_full_name()}>'