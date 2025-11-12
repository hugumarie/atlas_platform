"""
Routes d'authentification pour l'inscription, connexion et déconnexion.
Gère également l'activation des abonnements.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.subscription import Subscription
from app.models.portfolio import Portfolio

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Gère l'inscription des nouveaux utilisateurs.
    """
    if current_user.is_authenticated:
        return redirect(url_for('investor.dashboard'))
    
    if request.method == 'POST':
        # Récupération des données du formulaire
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Validation des données
        if not all([email, password, first_name, last_name]):
            flash('Tous les champs obligatoires doivent être remplis.', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères.', 'error')
            return render_template('auth/register.html')
        
        # Vérification si l'utilisateur existe déjà
        if User.query.filter_by(email=email).first():
            flash('Un compte avec cet email existe déjà.', 'error')
            return render_template('auth/register.html')
        
        try:
            # Création du nouvel utilisateur
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone or None
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.flush()  # Pour obtenir l'ID utilisateur
            
            # Création de l'abonnement d'essai
            subscription = Subscription(user_id=user.id)
            db.session.add(subscription)
            
            # Création du portefeuille
            portfolio = Portfolio(user_id=user.id)
            db.session.add(portfolio)
            
            db.session.commit()
            
            # Connexion automatique
            login_user(user)
            user.update_last_login()
            
            flash('Compte créé avec succès! Vous bénéficiez de 7 jours d\'essai gratuit.', 'success')
            return redirect(url_for('investor.questionnaire'))
            
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de la création du compte. Veuillez réessayer.', 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Gère la connexion des utilisateurs.
    """
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('investor.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        if not email or not password:
            flash('Veuillez saisir votre email et mot de passe.', 'error')
            return render_template('auth/login.html')
        
        # Vérification des identifiants admin
        if email == 'admin@gmail.com' and password == 'admin':
            # Création ou récupération du compte admin
            admin_user = User.query.filter_by(email=email).first()
            if not admin_user:
                admin_user = User(
                    email=email,
                    first_name='Admin',
                    last_name='Système',
                    is_admin=True
                )
                admin_user.set_password(password)
                db.session.add(admin_user)
                db.session.commit()
            
            login_user(admin_user, remember=remember_me)
            admin_user.update_last_login()
            return redirect(url_for('admin.dashboard'))
        
        # Vérification des identifiants utilisateur
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Votre compte est désactivé.', 'error')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember_me)
            user.update_last_login()
            
            # Redirection selon le type d'utilisateur
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                # Vérifier si le questionnaire a été complété
                if not user.investor_profile:
                    return redirect(url_for('investor.questionnaire'))
                return redirect(url_for('investor.dashboard'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Déconnecte l'utilisateur actuel.
    """
    logout_user()
    flash('Vous avez été déconnecté avec succès.', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/activate-subscription')
@login_required
def activate_subscription():
    """
    Active l'abonnement après la période d'essai (simulation).
    """
    if current_user.is_admin:
        flash('Les administrateurs n\'ont pas d\'abonnement.', 'info')
        return redirect(url_for('admin.dashboard'))
    
    subscription = current_user.subscription
    
    if not subscription:
        flash('Aucun abonnement trouvé.', 'error')
        return redirect(url_for('investor.dashboard'))
    
    if subscription.is_active():
        if subscription.is_trial():
            # Simulation de l'activation de l'abonnement
            subscription.activate_subscription()
            flash('Abonnement activé avec succès! Votre carte sera débitée de 20€ par mois.', 'success')
        else:
            flash('Votre abonnement est déjà actif.', 'info')
    else:
        flash('Impossible d\'activer l\'abonnement.', 'error')
    
    return redirect(url_for('investor.dashboard'))