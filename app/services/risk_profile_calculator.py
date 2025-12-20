"""
Service de calcul du profil de risque basé sur le questionnaire.
Analyse les 5 réponses et détermine le profil d'investisseur.
"""

class RiskProfileCalculator:
    """Service pour calculer le profil de risque d'un investisseur."""
    
    RISK_PROFILES = {
        'prudent': {
            'name': 'Prudent',
            'description': 'Vous privilégiez la sécurité et acceptez des rendements plus modestes.',
            'min_score': 5,
            'max_score': 8
        },
        'modéré': {
            'name': 'Modéré', 
            'description': 'Vous recherchez un équilibre entre sécurité et performance.',
            'min_score': 9,
            'max_score': 12
        },
        'dynamique': {
            'name': 'Dynamique',
            'description': 'Vous acceptez une volatilité plus importante pour un potentiel de gain supérieur.',
            'min_score': 13,
            'max_score': 25
        }
    }
    
    # Questions du questionnaire avec leurs scores
    QUESTION_SCORES = {
        # Question 1: Quelle baisse de valeur de votre portefeuille accepteriez-vous ?
        'baisse_acceptable': {
            '0-5%': 1,
            '5-10%': 2,
            '10-20%': 3,
            '20-30%': 4,
            'plus_30%': 5
        },
        
        # Question 2: Quel est votre horizon de placement principal ?
        'horizon_placement': {
            'moins_1_an': 1,
            '1-3_ans': 2,
            '3-5_ans': 3,
            '5-10_ans': 4,
            'plus_10_ans': 5
        },
        
        # Question 3: Avez-vous besoin d'une liquidité immédiate ?
        'besoin_liquidite': {
            'oui_immédiat': 1,
            'oui_partiel': 2,
            'peut_être': 3,
            'non_probable': 4,
            'non_jamais': 5
        },
        
        # Question 4: Quelle est votre expérience des marchés financiers ?
        'experience_marches': {
            'aucune': 1,
            'faible': 2,
            'moyenne': 3,
            'bonne': 4,
            'excellente': 5
        },
        
        # Question 5: Comment réagiriez-vous si vos placements baissaient fortement ?
        'attitude_volatilite': {
            'vendre_pertes': 1,
            'attendre_remontee': 3,
            'investir_plus': 5
        }
    }
    
    @classmethod
    def calculate_profile(cls, responses):
        """
        Calcule le profil de risque basé sur les réponses du questionnaire.
        
        Args:
            responses (dict): Dictionnaire contenant les réponses aux questions
            
        Returns:
            dict: Profil calculé avec score et métadonnées
        """
        total_score = 0
        scored_responses = {}
        
        # Pour le moment, on retourne toujours 'modéré' comme demandé
        # TODO: Implémenter le barème correct quand fourni
        
        # Calcul temporaire du score (non utilisé pour le moment)
        for question, answer in responses.items():
            if question in cls.QUESTION_SCORES:
                question_scores = cls.QUESTION_SCORES[question]
                score = question_scores.get(answer, 3)  # Score par défaut si réponse non trouvée
                total_score += score
                scored_responses[question] = {'answer': answer, 'score': score}
        
        # Pour le moment, retourne toujours 'modéré' 
        calculated_profile = 'modéré'
        
        # Logique future pour déterminer le profil basé sur le score total
        # profile_key = cls._determine_profile_from_score(total_score)
        
        return {
            'profile': calculated_profile,
            'score': total_score,
            'max_possible_score': 25,
            'responses': scored_responses,
            'metadata': cls.RISK_PROFILES.get(calculated_profile, cls.RISK_PROFILES['modéré'])
        }
    
    @classmethod
    def _determine_profile_from_score(cls, total_score):
        """
        Détermine le profil basé sur le score total.
        Sera utilisé quand le barème correct sera fourni.
        """
        for profile_key, profile_data in cls.RISK_PROFILES.items():
            if profile_data['min_score'] <= total_score <= profile_data['max_score']:
                return profile_key
        
        # Par défaut, retourner modéré
        return 'modéré'
    
    @classmethod
    def get_profile_display_info(cls, profile_key):
        """Retourne les informations d'affichage pour un profil donné."""
        return cls.RISK_PROFILES.get(profile_key, cls.RISK_PROFILES['modéré'])
    
    @classmethod
    def validate_responses(cls, responses):
        """
        Valide que toutes les réponses requises sont présentes.
        
        Args:
            responses (dict): Dictionnaire des réponses
            
        Returns:
            tuple: (bool, list) - (est_valide, liste_erreurs)
        """
        required_questions = list(cls.QUESTION_SCORES.keys())
        missing_questions = []
        
        for question in required_questions:
            if question not in responses or not responses[question]:
                missing_questions.append(question)
        
        is_valid = len(missing_questions) == 0
        return is_valid, missing_questions