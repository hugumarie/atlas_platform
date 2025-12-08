"""
Application Factory pour la plateforme de gestion de patrimoine.
Initialise Flask et configure les extensions nécessaires.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
import click

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
    
    # Configuration PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://huguesmarie:@localhost:5432/atlas_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
    
    # Configuration PostgreSQL avancée
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 120,
        'pool_pre_ping': True
    }
    
    # Configuration anti-cache pour le développement - Templates ET fichiers statiques
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    # Configuration DEBUG pour auto-reload du code Python
    import os
    if os.environ.get('FLASK_ENV') != 'production':
        app.config['DEBUG'] = True
        app.config['ENV'] = 'development'
    
    # Headers anti-cache pour le développement - Templates ET fichiers statiques
    @app.after_request
    def after_request(response):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['Last-Modified'] = '0'
        return response
    
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
    from app.models.apprentissage import Apprentissage
    from app.models.crypto_price import CryptoPrice
    
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
    
    # API crypto intégrée dans les routes admin
    
    # Route racine redirige vers le site vitrine
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('site_pages.index'))
    
    # Création des tables de base de données
    with app.app_context():
        db.create_all()
    
    # Scheduler crypto désactivé - utilisation du cron externe à la place
    # from app.scheduler import start_scheduler
    # start_scheduler(app)
    
    # Ajouter les commandes CLI
    @app.cli.command()
    def refresh_crypto_prices():
        """Refresh les prix crypto depuis Binance (pour cron)."""
        from refresh_crypto_prices import PeriodicCryptoPriceRefresh
        
        click.echo("🔄 Démarrage du refresh des prix crypto...")
        success = PeriodicCryptoPriceRefresh.run_refresh()
        
        if success:
            click.echo("✅ Refresh terminé avec succès")
        else:
            click.echo("❌ Erreur lors du refresh")
    
    return app