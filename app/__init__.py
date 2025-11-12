"""
Application Factory pour la plateforme de gestion de patrimoine.
Initialise Flask et configure les extensions nécessaires.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Initialisation des extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """
    Factory function pour créer l'application Flask.
    
    Returns:
        Flask: Instance de l'application configurée
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'votre-cle-secrete-très-longue-et-complexe'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patrimoine.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
    
    # Initialisation des extensions avec l'app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'platform_auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    
    # Import des modèles
    from app.models.user import User
    from app.models.investor_profile import InvestorProfile
    from app.models.portfolio import Portfolio
    from app.models.subscription import Subscription
    from app.models.credit import Credit
    
    # Configuration du user_loader pour Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Enregistrement des blueprints
    # Site vitrine
    from app.routes.site.pages import site_pages_bp
    app.register_blueprint(site_pages_bp)
    
    # Plateforme
    from app.routes.platform.auth import platform_auth_bp
    from app.routes.platform.investor import platform_investor_bp
    from app.routes.platform.admin import platform_admin_bp
    
    app.register_blueprint(platform_auth_bp)
    app.register_blueprint(platform_investor_bp)
    app.register_blueprint(platform_admin_bp)
    
    # Route racine redirige vers le site vitrine
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('site_pages.index'))
    
    # Création des tables de base de données
    with app.app_context():
        db.create_all()
    
    return app