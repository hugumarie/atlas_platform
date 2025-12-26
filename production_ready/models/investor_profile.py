"""
Modèle InvestorProfile pour stocker les informations financières des investisseurs.
Contient les réponses au questionnaire de profil et les données financières.
"""

from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

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
    professional_situation_other = db.Column(db.String(100), nullable=True)  # Situation pro personnalisée
    
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
    revenus_complementaires_json = db.Column(JSONB, nullable=True)  # Nouveau format JSONB PostgreSQL
    charges_mensuelles = db.Column(db.Float, nullable=True)  # Ancien champ (maintenu pour compatibilité)
    charges_mensuelles_json = db.Column(JSONB, nullable=True)  # Nouveau format JSONB PostgreSQL
    cryptos_json = db.Column(JSONB, nullable=True)  # Cryptomonnaies JSONB (legacy compatibility)
    liquidites_personnalisees_json = db.Column(JSONB, nullable=True)  # Liquidités personnalisées JSONB
    placements_personnalises_json = db.Column(JSONB, nullable=True)  # Placements personnalisés JSONB
    # taux_epargne calculé automatiquement via méthode
    
    # Nouvelles sections JSON pour données complexes
    immobilier_data_json = db.Column(JSONB, nullable=True)  # Données détaillées immobilier
    cryptomonnaies_data_json = db.Column(JSONB, nullable=True)  # Données détaillées crypto avec prix
    autres_biens_data_json = db.Column(JSONB, nullable=True)  # Autres biens détaillés
    credits_data_json = db.Column(JSONB, nullable=True)  # Crédits détaillés (complément du modèle Credit)
    
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
    
    # PEL/CEL combiné
    has_pel_cel = db.Column(db.Boolean, default=False)
    pel_cel_value = db.Column(db.Float, default=0.0)
    
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
    
    has_scpi = db.Column(db.Boolean, default=False)
    scpi_value = db.Column(db.Float, default=0.0)
    
    other_investments = db.Column(db.Text, nullable=True)
    
    # Section 4 - Objectifs d'investissement (étendus)
    objectif_constitution_epargne = db.Column(db.Boolean, default=False)
    objectif_retraite = db.Column(db.Boolean, default=False)
    objectif_transmission = db.Column(db.Boolean, default=False)
    objectif_defiscalisation = db.Column(db.Boolean, default=False)
    objectif_immobilier = db.Column(db.Boolean, default=False)
    
    # Nouveaux objectifs d'investissement
    objectif_premiers_pas = db.Column(db.Boolean, default=False)
    objectif_constituer_capital = db.Column(db.Boolean, default=False)
    objectif_diversifier = db.Column(db.Boolean, default=False)
    objectif_optimiser_rendement = db.Column(db.Boolean, default=False)
    objectif_preparer_retraite = db.Column(db.Boolean, default=False)
    objectif_securite_financiere = db.Column(db.Boolean, default=False)
    objectif_projet_immobilier = db.Column(db.Boolean, default=False)
    objectif_revenus_complementaires = db.Column(db.Boolean, default=False)
    objectif_transmettre_capital = db.Column(db.Boolean, default=False)
    objectif_proteger_famille = db.Column(db.Boolean, default=False)
    
    # Section 5 - Profil de risque
    profil_risque_connu = db.Column(db.Boolean, default=False)
    profil_risque_choisi = db.Column(db.String(20), nullable=True)  # conservateur, modéré, dynamique
    
    # Section 6 - Questions de risque détaillées (nouvelles questions spécifiques)
    tolerance_risque = db.Column(db.String(50), nullable=True)  # faible, moderee, elevee
    horizon_placement = db.Column(db.String(50), nullable=True)  # court, moyen, long
    besoin_liquidite = db.Column(db.String(50), nullable=True)  # court_terme, long_terme
    experience_investissement = db.Column(db.String(50), nullable=True)  # debutant, intermediaire, confirme
    attitude_volatilite = db.Column(db.String(50), nullable=True)  # vendre, attendre, investir_plus
    
    # Anciennes questions (maintenues pour compatibilité)
    question_1_reponse = db.Column(db.String(100), nullable=True)
    question_2_reponse = db.Column(db.String(100), nullable=True)
    question_3_reponse = db.Column(db.String(100), nullable=True)
    question_4_reponse = db.Column(db.String(100), nullable=True)
    question_5_reponse = db.Column(db.String(100), nullable=True)
    synthese_profil_risque = db.Column(db.String(500), nullable=True)  # Synthèse automatique
    
    # Métadonnées
    date_completed = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Colonnes pour les totaux calculés et sauvegardés
    calculated_total_liquidites = db.Column(db.Float, nullable=True, default=0.0)
    calculated_total_placements = db.Column(db.Float, nullable=True, default=0.0)  
    calculated_total_immobilier_net = db.Column(db.Float, nullable=True, default=0.0)
    calculated_total_cryptomonnaies = db.Column(db.Float, nullable=True, default=0.0)
    calculated_total_autres_biens = db.Column(db.Float, nullable=True, default=0.0)
    calculated_total_credits_consommation = db.Column(db.Float, nullable=True, default=0.0)
    calculated_total_actifs = db.Column(db.Float, nullable=True, default=0.0)
    calculated_patrimoine_total_net = db.Column(db.Float, nullable=True, default=0.0)
    last_calculation_date = db.Column(db.DateTime, nullable=True)
    
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
        if self.has_pel_cel:
            total += self.pel_cel_value or 0.0
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
        if self.has_scpi:
            total += self.scpi_value or 0.0
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
        if self.has_pel_cel:
            total += self.pel_cel_value or 0.0
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
        if self.has_scpi:
            total += self.scpi_value or 0.0
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
            
        if self.has_pel_cel and self.pel_cel_value > 0:
            distribution['PEL/CEL'] = self.pel_cel_value
            
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
            
        if self.has_scpi and self.scpi_value > 0:
            distribution['SCPI'] = self.scpi_value
            
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
        
        # PostgreSQL JSONB returns Python objects directly, not JSON strings
        if isinstance(self.revenus_complementaires_json, list):
            return self.revenus_complementaires_json
        
        # Fallback for string JSON data
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
        # PostgreSQL JSONB stores Python objects directly
        self.revenus_complementaires_json = data if data else None
    
    @property
    def charges_mensuelles_data(self):
        """
        Retourne les charges mensuelles sous forme de liste de dictionnaires.
        
        Returns:
            list: Liste des charges mensuelles [{'name': str, 'amount': float}]
        """
        if not self.charges_mensuelles_json:
            return []
        
        # PostgreSQL JSONB returns Python objects directly, not JSON strings
        if isinstance(self.charges_mensuelles_json, list):
            return self.charges_mensuelles_json
        
        # Fallback for string JSON data
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
        # PostgreSQL JSONB stores Python objects directly
        self.charges_mensuelles_json = data if data else None
    
    @property
    def cryptos_data(self):
        """
        Retourne les cryptomonnaies sous forme de liste de dictionnaires.
        
        Returns:
            list: Liste des cryptos [{'symbol': str, 'quantity': float}]
        """
        if not self.cryptos_json:
            return []
        
        # PostgreSQL JSONB returns Python objects directly
        if isinstance(self.cryptos_json, list):
            return self.cryptos_json
        
        # Fallback for string JSON data
        try:
            import json
            return json.loads(self.cryptos_json)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_cryptos_data(self, data):
        """
        Sauvegarde les cryptomonnaies en format JSONB.
        
        Args:
            data (list): Liste des cryptos [{'symbol': str, 'quantity': float}]
        """
        # PostgreSQL JSONB stores Python objects directly
        self.cryptos_json = data if data else None
    
    @property
    def liquidites_personnalisees_data(self):
        """
        Retourne les liquidités personnalisées sous forme de liste de dictionnaires.
        
        Returns:
            list: Liste des liquidités [{'name': str, 'amount': float}]
        """
        if not self.liquidites_personnalisees_json:
            return []
        
        # PostgreSQL JSONB returns Python objects directly
        if isinstance(self.liquidites_personnalisees_json, list):
            return self.liquidites_personnalisees_json
        
        # Fallback for string JSON data
        try:
            import json
            return json.loads(self.liquidites_personnalisees_json)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_liquidites_personnalisees_data(self, data):
        """
        Sauvegarde les liquidités personnalisées en format JSONB.
        
        Args:
            data (list): Liste des liquidités [{'name': str, 'amount': float}]
        """
        # PostgreSQL JSONB stores Python objects directly
        self.liquidites_personnalisees_json = data if data else None
    
    @property
    def placements_personnalises_data(self):
        """
        Retourne les placements personnalisés sous forme de liste de dictionnaires.
        
        Returns:
            list: Liste des placements [{'name': str, 'amount': float}]
        """
        if not self.placements_personnalises_json:
            return []
        
        # PostgreSQL JSONB returns Python objects directly
        if isinstance(self.placements_personnalises_json, list):
            return self.placements_personnalises_json
        
        # Fallback for string JSON data
        try:
            import json
            return json.loads(self.placements_personnalises_json)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_placements_personnalises_data(self, data):
        """
        Sauvegarde les placements personnalisés en format JSONB.
        
        Args:
            data (list): Liste des placements [{'name': str, 'amount': float}]
        """
        # PostgreSQL JSONB stores Python objects directly
        self.placements_personnalises_json = data if data else None
    
    @property
    def immobilier_data(self):
        """
        Retourne les données immobilier détaillées sous forme de liste.
        
        Returns:
            list: Liste des biens immobiliers avec détails complets
        """
        if not self.immobilier_data_json:
            return []
        
        # PostgreSQL JSONB returns Python objects directly
        if isinstance(self.immobilier_data_json, list):
            return self.immobilier_data_json
        
        # Fallback for string JSON data
        try:
            import json
            return json.loads(self.immobilier_data_json)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_immobilier_data(self, data):
        """
        Sauvegarde les données immobilier en format JSONB.
        
        Args:
            data (list): Liste des biens immobiliers détaillés
        """
        # PostgreSQL JSONB stores Python objects directly
        self.immobilier_data_json = data if data else None
    
    @property
    def cryptomonnaies_data(self):
        """
        Retourne les données crypto détaillées avec prix.
        
        Returns:
            list: Liste des cryptomonnaies avec prix et quantités
        """
        if not self.cryptomonnaies_data_json:
            return []
        
        # PostgreSQL JSONB returns Python objects directly
        if isinstance(self.cryptomonnaies_data_json, list):
            return self.cryptomonnaies_data_json
        
        # Fallback for string JSON data
        try:
            import json
            return json.loads(self.cryptomonnaies_data_json)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_cryptomonnaies_data(self, data):
        """
        Sauvegarde les données crypto en format JSONB.
        
        Args:
            data (list): Liste des cryptomonnaies détaillées
        """
        # PostgreSQL JSONB stores Python objects directly
        self.cryptomonnaies_data_json = data if data else None
    
    @property
    def autres_biens_data(self):
        """
        Retourne les autres biens détaillés.
        
        Returns:
            list: Liste des autres biens avec descriptions
        """
        if not self.autres_biens_data_json:
            return []
        
        # PostgreSQL JSONB returns Python objects directly
        if isinstance(self.autres_biens_data_json, list):
            return self.autres_biens_data_json
        
        # Fallback for string JSON data
        try:
            import json
            return json.loads(self.autres_biens_data_json)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_autres_biens_data(self, data):
        """
        Sauvegarde les autres biens en format JSONB.
        
        Args:
            data (list): Liste des autres biens détaillés
        """
        # PostgreSQL JSONB stores Python objects directly
        self.autres_biens_data_json = data if data else None
    
    @property
    def credits_data(self):
        """
        Retourne les données crédits détaillées.
        
        Returns:
            list: Liste des crédits avec calculs
        """
        if not self.credits_data_json:
            return []
        
        # PostgreSQL JSONB returns Python objects directly
        if isinstance(self.credits_data_json, list):
            return self.credits_data_json
        
        # Fallback for string JSON data
        try:
            import json
            return json.loads(self.credits_data_json)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_credits_data(self, data):
        """
        Sauvegarde les données crédits en format JSONB.
        
        Args:
            data (list): Liste des crédits détaillés
        """
        # PostgreSQL JSONB stores Python objects directly
        self.credits_data_json = data if data else None
    
    def __repr__(self):
        return f'<InvestorProfile {self.user.get_full_name()}>'