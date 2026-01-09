"""
Application Factory pour la plateforme de gestion de patrimoine.
Initialise Flask et configure les extensions nécessaires.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
import click
from dotenv import load_dotenv

# Initialisation des extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """
    Factory function pour créer l'application Flask.
    
    Returns:
        Flask: Instance de l'application configurée
    """
    # Charger les variables d'environnement depuis .env
    load_dotenv()
    
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'votre-cle-secrete-très-longue-et-complexe')
    
    # Configuration PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://huguesmarie:@localhost:5432/atlas_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
    
    # Configuration uploads - Pas de limite de taille
    app.config['MAX_CONTENT_LENGTH'] = None  # Aucune limite de taille
    app.config['UPLOAD_EXTENSIONS'] = ['.pdf', '.png', '.jpg', '.jpeg', '.gif']
    
    # Configuration PostgreSQL avancée
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 120,
        'pool_pre_ping': True
    }
    
    # Configuration anti-cache pour le développement - Templates ET fichiers statiques
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    # Configuration DigitalOcean Spaces
    # Support des deux formats de variables d'environnement
    app.config['DO_SPACES_ACCESS_KEY'] = (
        os.environ.get('DO_SPACES_ACCESS_KEY') or 
        os.environ.get('DIGITALOCEAN_SPACES_KEY')
    )
    app.config['DO_SPACES_SECRET_KEY'] = (
        os.environ.get('DO_SPACES_SECRET_KEY') or 
        os.environ.get('DIGITALOCEAN_SPACES_SECRET')
    )
    app.config['DO_SPACES_REGION'] = 'fra1'
    app.config['DO_SPACES_BUCKET'] = (
        os.environ.get('DO_SPACES_BUCKET') or 
        os.environ.get('DIGITALOCEAN_SPACES_BUCKET') or 
        'atlas-database'
    )
    
    # Configuration DEBUG pour auto-reload du code Python
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
    
    # Initialisation DigitalOcean Spaces
    try:
        access_key = app.config.get('DO_SPACES_ACCESS_KEY')
        secret_key = app.config.get('DO_SPACES_SECRET_KEY')
        
        if access_key and secret_key:
            from app.services.digitalocean_storage import init_spaces_service
            init_spaces_service(
                access_key=access_key,
                secret_key=secret_key
            )
            print("✅ DigitalOcean Spaces initialisé avec succès")
        else:
            print("⚠️ DigitalOcean Spaces non configuré (clés manquantes)")
    except Exception as e:
        print(f"❌ Erreur initialisation DigitalOcean Spaces: {e}")
    
    # Import des modèles
    from app.models.user import User
    from app.models.investor_profile import InvestorProfile
    from app.models.portfolio import Portfolio
    from app.models.subscription import Subscription
    from app.models.credit import Credit
    from app.models.apprentissage import Apprentissage
    from app.models.crypto_price import CryptoPrice
    from app.models.investment_action import InvestmentAction
    
    # Configuration du user_loader pour Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Enregistrement des blueprints
    # Site vitrine
    from app.routes.site.pages import site_pages_bp
    app.register_blueprint(site_pages_bp)
    print(f"✅ Blueprint site_pages enregistré avec {len(site_pages_bp.deferred_functions)} routes")
    
    # Plateforme
    from app.routes.platform.auth import platform_auth_bp
    from app.routes.platform.investor import platform_investor_bp
    from app.routes.platform.admin import platform_admin_bp
    from app.routes.platform.investment_actions import investment_actions_bp
    from app.routes.onboarding import onboarding_bp
    from app.routes.onboarding.stripe_routes import stripe_bp
    
    app.register_blueprint(platform_auth_bp)
    app.register_blueprint(platform_investor_bp)
    app.register_blueprint(platform_admin_bp)
    app.register_blueprint(investment_actions_bp)
    app.register_blueprint(onboarding_bp)
    app.register_blueprint(stripe_bp)
    
    # API crypto intégrée dans les routes admin
    
    # Route racine redirige vers le site vitrine
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('site_pages.index'))
    
    # Route temporaire pour solutions
    @app.route('/site/solutions')
    def solutions_temp():
        from flask import render_template
        return render_template('site/solutions_simple.html')
    
    # Création des tables de base de données
    with app.app_context():
        db.create_all()
        
        # Chargement initial des prix crypto (version silencieuse pour app factory)
        # La version complète avec logs détaillés est dans run.py
        try:
            from app.services.binance_price_service import BinancePriceService
            from app.models.crypto_price import CryptoPrice
            from datetime import datetime, timedelta
            
            # Seulement si pas lancé via run.py (éviter double chargement)
            if not os.environ.get('ATLAS_DIRECT_LAUNCH'):
                # Vérifier si nous avons des prix récents (moins de 30 minutes)
                thirty_minutes_ago = datetime.utcnow() - timedelta(minutes=30)
                recent_prices_count = CryptoPrice.query.filter(
                    CryptoPrice.updated_at >= thirty_minutes_ago
                ).count()
                
                # Si nous n'avons pas suffisamment de prix récents, faire un refresh silencieux
                if recent_prices_count < 40:  # Moins de 40 cryptos avec des prix récents
                    print(f"🔄 Atlas: Chargement des prix crypto...")
                    
                    success = BinancePriceService.update_crypto_prices_in_db()
                    
                    if success:
                        final_count = CryptoPrice.query.filter(
                            CryptoPrice.updated_at >= thirty_minutes_ago
                        ).count()
                        print(f"✅ Atlas: {final_count} prix crypto récupérés")
                    else:
                        print(f"⚠️ Atlas: Échec chargement crypto")
                else:
                    print(f"✅ Atlas: {recent_prices_count} prix crypto disponibles")
                
        except Exception as e:
            print(f"⚠️ Atlas: Erreur initialisation crypto: {e}")
            # Ne pas faire planter l'app si le chargement crypto échoue
        
        # Initialisation du service Stripe après la configuration de l'app
        try:
            from app.services.stripe_service import initialize_stripe_service
            initialize_stripe_service()
        except Exception as e:
            print(f"⚠️ Atlas: Erreur initialisation Stripe: {e}")
    
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