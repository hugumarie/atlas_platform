"""
Modèle pour les plans sélectionnés par les utilisateurs
"""

from app import db
from datetime import datetime


class UserPlan(db.Model):
    """
    Modèle pour stocker les sélections de plan pendant l'onboarding
    """
    __tablename__ = 'user_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_type = db.Column(db.String(20), nullable=False)  # 'initia', 'optima'
    selected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Informations du plan au moment de la sélection
    plan_price = db.Column(db.Numeric(10, 2), nullable=True)  # Prix en euros
    plan_currency = db.Column(db.String(3), default='EUR')
    
    # Statut de l'onboarding
    onboarding_step = db.Column(db.String(20), default='plan_selected')  # plan_selected, payment_pending, completed
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relations
    user = db.relationship('User', backref='selected_plans')
    
    # Configurations des plans (données statiques)
    PLAN_CONFIGS = {
        'initia': {
            'name': 'INITIA',
            'price': 25.00,
            'description': 'Pour débuter dans l\'investissement',
            'features': [
                'Analyse de votre situation et de vos objectifs',
                'Mise en place d\'une stratégie d\'investissement',
                'Suivi via votre tableau de bord Atlas',
                'Pilotage de vos investissements',
                'Contenus pédagogiques exclusifs',
                'Accompagnement humain et 100% indépendant'
            ]
        },
        'optima': {
            'name': 'OPTIMA',
            'price': 50.00,
            'description': 'Pour structurer et optimiser son patrimoine existant',
            'features': [
                'Tous les avantages Initia',
                'Optimisation du patrimoine existant',
                'Classes d\'actifs supplémentaires',
                'Réponses prioritaires'
            ]
        }
    }
    
    def __init__(self, user_id, plan_type):
        """
        Crée une nouvelle sélection de plan
        
        Args:
            user_id: ID de l'utilisateur
            plan_type: Type de plan ('initia' ou 'optima')
        """
        self.user_id = user_id
        self.plan_type = plan_type.lower()
        
        # Récupérer le prix depuis la configuration
        if self.plan_type in self.PLAN_CONFIGS:
            self.plan_price = self.PLAN_CONFIGS[self.plan_type]['price']
    
    def get_plan_config(self):
        """
        Retourne la configuration du plan sélectionné
        
        Returns:
            dict: Configuration du plan
        """
        return self.PLAN_CONFIGS.get(self.plan_type, {})
    
    def get_plan_name(self):
        """
        Retourne le nom commercial du plan
        
        Returns:
            str: Nom du plan
        """
        config = self.get_plan_config()
        return config.get('name', self.plan_type.upper())
    
    def get_plan_features(self):
        """
        Retourne la liste des fonctionnalités du plan
        
        Returns:
            list: Liste des fonctionnalités
        """
        config = self.get_plan_config()
        return config.get('features', [])
    
    def mark_as_completed(self):
        """
        Marque l'onboarding comme terminé
        """
        self.onboarding_step = 'completed'
        self.completed_at = datetime.utcnow()
        db.session.commit()
    
    def set_payment_pending(self):
        """
        Marque comme en attente de paiement
        """
        self.onboarding_step = 'payment_pending'
        db.session.commit()
    
    def is_completed(self):
        """
        Vérifie si l'onboarding est terminé
        
        Returns:
            bool: True si terminé, False sinon
        """
        return self.onboarding_step == 'completed' and self.completed_at is not None
    
    @staticmethod
    def get_available_plans():
        """
        Retourne la liste des plans disponibles
        
        Returns:
            dict: Dictionnaire des plans disponibles
        """
        return UserPlan.PLAN_CONFIGS.copy()
    
    @staticmethod
    def get_user_current_plan(user_id):
        """
        Récupère le plan actuel d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            UserPlan: Plan actuel ou None
        """
        return UserPlan.query.filter_by(user_id=user_id).order_by(UserPlan.selected_at.desc()).first()
    
    def to_dict(self):
        """
        Convertit en dictionnaire pour JSON
        """
        config = self.get_plan_config()
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_type': self.plan_type,
            'plan_name': self.get_plan_name(),
            'plan_price': float(self.plan_price) if self.plan_price else None,
            'plan_currency': self.plan_currency,
            'plan_description': config.get('description', ''),
            'plan_features': self.get_plan_features(),
            'selected_at': self.selected_at.isoformat() if self.selected_at else None,
            'onboarding_step': self.onboarding_step,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_completed': self.is_completed()
        }
    
    def __repr__(self):
        return f'<UserPlan {self.user_id} -> {self.plan_type.upper()}>'