"""
Routes d'authentification pour la plateforme.
Inscription avec paiement obligatoire, connexion sécurisée.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.subscription import Subscription
from app.models.portfolio import Portfolio
import re

platform_auth_bp = Blueprint('platform_auth', __name__, url_prefix='/plateforme')

def validate_password(password):
    """
    Valide la complexité du mot de passe.
    Doit contenir : 8+ caractères, 1 majuscule, 1 chiffre, 1 caractère spécial
    """
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    
    if not re.search(r'[A-Z]', password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    
    if not re.search(r'[0-9]', password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        return False, "Le mot de passe doit contenir au moins un caractère spécial (!@#$%^&*...)"
    
    return True, "Mot de passe valide"

@platform_auth_bp.route('/inscription', methods=['GET', 'POST'])
def register():
    """
    Inscription avec paiement obligatoire.
    """
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('platform_admin.dashboard'))
        return redirect(url_for('platform_investor.dashboard'))
    
    if request.method == 'POST':
        # Récupération des données du formulaire
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Données de paiement (simulation)
        card_number = request.form.get('card_number', '').strip()
        card_expiry = request.form.get('card_expiry', '').strip()
        card_cvv = request.form.get('card_cvv', '').strip()
        card_name = request.form.get('card_name', '').strip()
        
        # Validation des données
        if not all([email, password, password_confirm, first_name, last_name, card_number, card_expiry, card_cvv, card_name]):
            flash('Tous les champs obligatoires doivent être remplis.', 'error')
            return render_template('platform/auth/register.html')
        
        # Validation du mot de passe
        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message, 'error')
            return render_template('platform/auth/register.html')
        
        # Vérification de la confirmation du mot de passe
        if password != password_confirm:
            flash('Les mots de passe ne correspondent pas.', 'error')
            return render_template('platform/auth/register.html')
        
        # Vérification si l'utilisateur existe déjà
        if User.query.filter_by(email=email).first():
            flash('Un compte avec cet email existe déjà.', 'error')
            return render_template('platform/auth/register.html')
        
        # Validation de la carte de paiement (simulation)
        if not validate_payment_card(card_number, card_expiry, card_cvv):
            flash('Informations de carte de paiement invalides.', 'error')
            return render_template('platform/auth/register.html')
        
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
            
            # Création de l'abonnement actif (payé)
            subscription = Subscription(
                user_id=user.id,
                status='active',  # Directement actif après paiement
                payment_method='card_simulation'
            )
            subscription.activate_subscription()  # Configure les dates
            db.session.add(subscription)
            
            # Création du portefeuille
            portfolio = Portfolio(user_id=user.id)
            db.session.add(portfolio)
            
            db.session.commit()
            
            # Connexion automatique
            login_user(user)
            user.update_last_login()
            
            flash('Compte créé avec succès ! Paiement de 20€ effectué. Bienvenue !', 'success')
            return redirect(url_for('platform_investor.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de la création du compte. Veuillez réessayer.', 'error')
            return render_template('platform/auth/register.html')
    
    return render_template('platform/auth/register.html')

def validate_payment_card(card_number, expiry, cvv):
    """
    Validation simulée de la carte de paiement.
    En production, ici on ferait appel à Stripe.
    """
    # Simulation : on accepte toute carte avec des critères basiques
    card_number = re.sub(r'[^0-9]', '', card_number)  # Supprime espaces et tirets
    
    # Vérification de la longueur (16 chiffres pour Visa/Mastercard)
    if len(card_number) not in [15, 16]:  # 15 pour Amex, 16 pour Visa/MC
        return False
    
    # Vérification du format d'expiration (MM/YY)
    if not re.match(r'^(0[1-9]|1[0-2])\/[0-9]{2}$', expiry):
        return False
    
    # Vérification du CVV (3 ou 4 chiffres)
    if not re.match(r'^[0-9]{3,4}$', cvv):
        return False
    
    return True

@platform_auth_bp.route('/connexion', methods=['GET', 'POST'])
def login():
    """
    Connexion à la plateforme.
    """
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('platform_admin.dashboard'))
        return redirect(url_for('platform_investor.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        if not email or not password:
            flash('Veuillez saisir votre email et mot de passe.', 'error')
            return render_template('platform/auth/login.html')
        
        # Vérification des identifiants admin
        if email == 'admin@gmail.com' and password == 'admin':
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
            
            # Hook supprimé - pas de recalcul automatique à la connexion
            
            return redirect(url_for('platform_admin.dashboard'))
        
        # Vérification des identifiants utilisateur
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Votre compte est désactivé.', 'error')
                return render_template('platform/auth/login.html')
            
            # Vérification accès plateforme
            if not user.can_access_platform():
                flash('Votre abonnement a expiré. Veuillez renouveler votre abonnement.', 'error')
                return render_template('platform/auth/login.html')
            
            login_user(user, remember=remember_me)
            user.update_last_login()
            
            # Hook supprimé - pas de recalcul automatique à la connexion
            
            # Nouveau flow : vérifier si l'onboarding est terminé
            if not user.has_completed_onboarding():
                # Si l'onboarding n'est pas terminé, rediriger vers sélection de plan
                flash('Veuillez compléter votre inscription en sélectionnant un plan.', 'info')
                return redirect(url_for('onboarding.plan_selection'))
            
            # Redirection selon le profil - dashboard si onboarding terminé
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('platform_investor.dashboard'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')
    
    return render_template('platform/auth/login.html')

@platform_auth_bp.route('/deconnexion')
@login_required
def logout():
    """
    Déconnexion de la plateforme.
    """
    logout_user()
    return redirect(url_for('site_pages.index'))