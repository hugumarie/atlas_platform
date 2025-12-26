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
from app.models.investor_profile import InvestorProfile
import re
import secrets
import uuid
from datetime import datetime, timedelta

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
        
        # Si l'utilisateur connecté a déjà un abonnement actif, le rediriger vers le dashboard
        if current_user.subscription and current_user.subscription.is_active():
            return redirect(url_for('platform_investor.dashboard'))
        
        # Si c'est un prospect connecté sans abonnement, il peut rester sur cette page pour souscrire
    
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
            # Vérifier s'il s'agit d'un prospect existant qui paie maintenant
            existing_prospect = User.query.filter_by(email=email, is_prospect=True).first()
            
            if existing_prospect:
                # Un prospect existant qui paie son abonnement
                user = existing_prospect
                if not user.password_hash:  # S'il n'a pas encore de mot de passe
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                user.phone = phone or None
            else:
                # Création d'un nouvel utilisateur directement client (car il paie)
                user = User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone or None,
                    is_prospect=False,  # Devient directement client car il paie
                    user_type='client'
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
            
            # Convertir le prospect en client maintenant qu'il a payé
            if user.is_prospect:
                user.mark_as_converted()
            
            # Création du portefeuille
            portfolio = Portfolio(user_id=user.id)
            db.session.add(portfolio)
            
            db.session.commit()
            
            # Connexion automatique
            login_user(user)
            user.update_last_login()
            
            flash('Compte créé avec succès ! Paiement de 20€ effectué. Bienvenue !', 'success')
            return redirect(url_for('platform_investor.questionnaire'))
            
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
            
            # Vérification que l'utilisateur a un abonnement actif (sauf pour les prospects qui viennent de créer leur compte)
            if not user.subscription or not user.subscription.is_active():
                if user.is_prospect:
                    # Pour les prospects sans abonnement, les connecter et rediriger vers le dashboard avec popup
                    login_user(user, remember=remember_me)
                    user.update_last_login()
                    return redirect(url_for('platform_investor.dashboard'))
                else:
                    flash('Votre abonnement a expiré. Veuillez renouveler votre abonnement.', 'error')
                    return render_template('platform/auth/login.html')
            
            login_user(user, remember=remember_me)
            user.update_last_login()
            
            # Hook supprimé - pas de recalcul automatique à la connexion
            
            # Redirection selon le profil
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif not user.investor_profile:
                return redirect(url_for('platform_investor.questionnaire'))
            else:
                return redirect(url_for('platform_investor.dashboard'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')
    
    return render_template('platform/auth/login.html')

@platform_auth_bp.route('/inscription-invitation', methods=['GET', 'POST'])
def signup():
    """
    Création de compte pour prospects invités.
    """
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('platform_admin.dashboard'))
        return redirect(url_for('platform_investor.dashboard'))
    
    token = request.args.get('token') or request.form.get('token')
    
    # Si un token est fourni, vérifier s'il correspond à un prospect
    prospect_data = None
    if token:
        # Rechercher le prospect avec ce token d'invitation
        from app.models.user import User
        prospect = User.query.filter_by(invitation_token=token).first()
        
        # Vérifier si l'invitation est encore valide (gestion des timezones)
        is_valid = False
        if prospect and prospect.invitation_expires_at:
            try:
                # Convertir en naive datetime pour comparaison
                expires_naive = prospect.invitation_expires_at.replace(tzinfo=None) if prospect.invitation_expires_at.tzinfo else prospect.invitation_expires_at
                is_valid = expires_naive > datetime.utcnow()
            except:
                # En cas d'erreur, considérer comme expiré
                is_valid = False
        
        if prospect and is_valid:
            prospect_data = {
                'email': prospect.email,
                'first_name': prospect.first_name,
                'last_name': prospect.last_name,
                'phone': prospect.phone
            }
        elif prospect:
            flash('Ce lien d\'invitation a expiré. Veuillez contacter notre équipe.', 'error')
            return redirect(url_for('platform_auth.login'))
    
    if request.method == 'POST':
        # Récupération des données du formulaire
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        accept_terms = request.form.get('accept_terms') == 'on'
        
        # Validation des données
        if not all([email, password, password_confirm, first_name, last_name, accept_terms]):
            flash('Tous les champs obligatoires doivent être remplis et les conditions acceptées.', 'error')
            return render_template('platform/auth/signup.html', 
                                 token=token, email=email, first_name=first_name, 
                                 last_name=last_name, phone=phone)
        
        # Validation du mot de passe
        if len(password) < 8:
            flash('Le mot de passe doit contenir au moins 8 caractères.', 'error')
            return render_template('platform/auth/signup.html', 
                                 token=token, email=email, first_name=first_name, 
                                 last_name=last_name, phone=phone)
        
        # Vérification de la confirmation du mot de passe
        if password != password_confirm:
            flash('Les mots de passe ne correspondent pas.', 'error')
            return render_template('platform/auth/signup.html', 
                                 token=token, email=email, first_name=first_name, 
                                 last_name=last_name, phone=phone)
        
        # Vérification si l'utilisateur existe déjà
        existing_user = User.query.filter_by(email=email).first()
        # Autoriser la création si c'est un prospect avec token valide OU si aucun utilisateur n'existe
        if existing_user and not existing_user.is_prospect_type():  # Si c'est un client existant (pas prospect)
            flash('Un compte avec cet email existe déjà.', 'error')
            return render_template('platform/auth/signup.html', 
                                 token=token, email=email, first_name=first_name, 
                                 last_name=last_name, phone=phone)
        
        # Si c'est un prospect avec token, vérifier que le token correspond
        if existing_user and existing_user.is_prospect_type() and token:
            if not existing_user.invitation_token or existing_user.invitation_token != token:
                flash('Lien d\'invitation invalide pour cet email.', 'error')
                return render_template('platform/auth/signup.html', 
                                     token=token, email=email, first_name=first_name, 
                                     last_name=last_name, phone=phone)
        
        try:
            # Si c'est un prospect existant avec token, on met à jour ses données
            if token and existing_user and existing_user.invitation_token == token:
                user = existing_user
                user.first_name = first_name
                user.last_name = last_name
                user.phone = phone or None
                user.set_password(password)
                user.is_active = True
                # IMPORTANT: On garde is_prospect = True jusqu'à ce qu'il ait un abonnement payant
                # user.prospect_status reste 'contacté' ou similaire, pas 'converti'
                user.invitation_token = None  # Nettoyer le token
                user.invitation_expires_at = None
            else:
                # Création d'un nouvel utilisateur (qui reste prospect tant qu'il n'a pas payé)
                user = User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone or None,
                    is_active=True,
                    is_prospect=True,  # Nouveau utilisateur reste prospect
                    prospect_status='nouveau'
                )
                user.set_password(password)
                db.session.add(user)
            
            db.session.flush()  # Pour obtenir l'ID utilisateur
            
            # Ne pas créer d'abonnement automatiquement
            # Le prospect doit choisir et payer un plan pour devenir client
            # Suppression de la création automatique d'abonnement trial
            
            # Ne pas créer de profil investisseur automatiquement
            # Le profil sera créé quand le prospect deviendra client payant
            
            db.session.commit()
            
            # Connexion automatique
            login_user(user)
            user.update_last_login()
            
            flash('Compte créé avec succès ! Bienvenue sur Atlas !', 'success')
            
            # Redirection vers la page de choix de plan
            return redirect(url_for('platform_auth.choose_plan'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la création du compte: {str(e)}")
            flash('Erreur lors de la création du compte. Veuillez réessayer.', 'error')
            return render_template('platform/auth/signup.html', 
                                 token=token, email=email, first_name=first_name, 
                                 last_name=last_name, phone=phone)
    
    # GET request - afficher le formulaire
    if prospect_data:
        return render_template('platform/auth/signup.html', 
                             token=token, **prospect_data)
    else:
        return render_template('platform/auth/signup.html', token=token)

@platform_auth_bp.route('/choisir-plan')
@login_required
def choose_plan():
    """
    Page de choix de plan pour les prospects.
    """
    if not current_user.is_prospect_type():
        return redirect(url_for('platform_investor.dashboard'))
    
    return render_template('platform/auth/choose_plan.html')

@platform_auth_bp.route('/paiement', methods=['GET', 'POST'])
def payment():
    """
    Page de simulation de paiement pour abonnement.
    """
    # Pour les prospects GET, afficher la page de paiement
    if current_user.is_authenticated and current_user.is_prospect_type() and request.method == 'GET':
        plan = request.args.get('plan', 'initia')
        return render_template('platform/auth/payment.html', selected_plan=plan)
    
    if request.method == 'POST':
        print("🚀 POST PAIEMENT REÇU")
        print(f"🔍 Utilisateur connecté: {current_user.is_authenticated}")
        print(f"🔍 Email: {current_user.email if current_user.is_authenticated else 'anonyme'}")
        print(f"🔍 Est prospect: {current_user.is_prospect_type() if current_user.is_authenticated else 'N/A'}")
        
        # Récupération des données du formulaire
        selected_plan = request.form.get('selected_plan', 'initia')
        card_number = request.form.get('card_number', '').replace(' ', '')
        card_expiry = request.form.get('card_expiry', '')
        card_cvv = request.form.get('card_cvv', '')
        card_name = request.form.get('card_name', '').strip()
        
        print(f"📋 Données reçues:")
        print(f"   - Plan: {selected_plan}")
        print(f"   - Carte: {card_number[:4]}****{card_number[-4:] if len(card_number) >= 4 else ''}")
        print(f"   - Expiry: {card_expiry}")
        print(f"   - CVV: {'***' if card_cvv else 'vide'}")
        print(f"   - Nom: {card_name}")
        
        # Validation simplifiée - accepter tout paiement pour la démo
        if not all([card_number, card_expiry, card_cvv, card_name]):
            print("❌ VALIDATION ÉCHOUÉE - champs manquants")
            flash('Tous les champs de paiement sont requis.', 'error')
            return render_template('platform/auth/payment.html')
        
        print("✅ VALIDATION OK - traitement du paiement...")
        
        try:
            # Si l'utilisateur est connecté et est un prospect
            print("🔄 Vérification authentification...")
            if current_user.is_authenticated and current_user.is_prospect_type():
                print(f"✅ Utilisateur prospect authentifié: {current_user.email}")
                user = current_user
                
                # Création de l'abonnement
                subscription = Subscription(
                    user_id=user.id,
                    status='active',
                    payment_method='card_simulation'
                )
                
                # Configuration selon le plan choisi
                if selected_plan == 'optima':
                    subscription.tier = 'optima'
                    subscription.monthly_price = 49.99
                else:
                    subscription.tier = 'initia' 
                    subscription.monthly_price = 24.99
                
                subscription.activate_subscription()
                db.session.add(subscription)
                
                # CONVERSION PROSPECT → CLIENT
                print(f"🔄 Conversion prospect {user.email} en client...")
                
                # Marquer le paiement comme complété
                user.payment_completed = True
                user.plan_selected = True
                
                # Convertir le prospect en client (crée automatiquement le profil investisseur)
                user.mark_as_converted()
                
                print(f"✅ {user.email} est maintenant un client avec abonnement {selected_plan.upper()}")
                
                db.session.commit()
                
                # Message de confirmation personnalisé
                plan_name = 'INITIA' if selected_plan == 'initia' else 'OPTIMA'
                plan_price = '24,99€' if selected_plan == 'initia' else '49,99€'
                
                flash(f'🎉 Paiement de {plan_price} validé ! Bienvenue sur Atlas {plan_name} !', 'success')
                print(f"🎉 Redirection vers dashboard pour {user.email}")
                
                return redirect(url_for('platform_investor.dashboard') + f'?payment_success=1&plan={selected_plan}')
                
            else:
                # Utilisateur non connecté - rediriger vers connexion
                print("❌ Utilisateur non authentifié ou pas prospect")
                print(f"   - Authentifié: {current_user.is_authenticated}")
                if current_user.is_authenticated:
                    print(f"   - Email: {current_user.email}")
                    print(f"   - Est prospect: {current_user.is_prospect_type()}")
                flash('Veuillez vous connecter pour finaliser votre paiement.', 'error')
                return redirect(url_for('platform_auth.login'))
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ ERREUR PAIEMENT: {str(e)}")
            print(f"❌ Type d'erreur: {type(e).__name__}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            flash('Erreur lors du traitement du paiement. Veuillez réessayer.', 'error')
            return render_template('platform/auth/payment.html')
    
    # GET request - afficher la page de paiement
    plan = request.args.get('plan', 'initia')
    return render_template('platform/auth/payment.html', selected_plan=plan)

@platform_auth_bp.route('/test-login-prospect')
def test_login_prospect():
    """
    Route de test pour se connecter automatiquement comme prospect.
    """
    # Prendre le premier prospect disponible
    from flask_login import login_user
    prospect = User.query.filter_by(is_prospect=True).first()
    if prospect:
        login_user(prospect)
        flash(f'Connecté automatiquement comme prospect: {prospect.email}', 'success')
        print(f"🧪 Test login prospect: {prospect.email}")
        return redirect(url_for('platform_auth.choose_plan'))
    else:
        flash('Aucun prospect trouvé', 'error')
        return redirect(url_for('platform_auth.login'))

@platform_auth_bp.route('/deconnexion')
@login_required
def logout():
    """
    Déconnexion de la plateforme.
    """
    logout_user()
    return redirect(url_for('site_pages.index'))