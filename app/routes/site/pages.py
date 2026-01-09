"""
Routes pour les pages du site vitrine.
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app import db
from app.models.user import User
from app.services.email_service import MailerSendService
import re
import os

site_pages_bp = Blueprint('site_pages', __name__, url_prefix='/site')

@site_pages_bp.route('/')
@site_pages_bp.route('/accueil')
def index():
    """Page d'accueil du site vitrine."""
    return render_template('site/index_exact.html')

@site_pages_bp.route('/nouveau')
def new_design():
    """Nouveau design Qlower style."""
    return render_template('site/index_new.html')

@site_pages_bp.route('/a-propos')
def about():
    """Page à propos."""
    return render_template('site/about.html')

@site_pages_bp.route('/tarifs')
def pricing():
    """Page tarifs."""
    return render_template('site/pricing.html')

@site_pages_bp.route('/contact')
def contact():
    """Page contact."""
    return render_template('site/contact.html')

@site_pages_bp.route('/solutions')
def solutions():
    """Page nos solutions."""
    return render_template('site/solutions.html')

@site_pages_bp.route('/cgu')
def cgu():
    """Page CGU."""
    return render_template('site/cgu.html')

@site_pages_bp.route('/confidentialite')
def privacy():
    """Page confidentialité."""
    return render_template('site/privacy.html')

@site_pages_bp.route('/cookies')
def cookies():
    """Page cookies."""
    return render_template('site/cookies.html')

@site_pages_bp.route('/mentions-legales')
def legal():
    """Page mentions légales."""
    return render_template('site/legal.html')

@site_pages_bp.route('/api/prospect', methods=['POST'])
def create_prospect():
    """
    API pour créer un nouveau prospect depuis le formulaire de prise de RDV.
    """
    try:
        data = request.get_json()
        
        # Validation des données
        if not data or not all(k in data for k in ['firstName', 'lastName', 'email', 'phone']):
            return jsonify({'error': 'Données manquantes'}), 400
        
        # Validation de l'email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'error': 'Email invalide'}), 400
        
        # Vérification si l'utilisateur/prospect existe déjà
        existing_user = User.query.filter_by(email=data['email'].strip().lower()).first()
        if existing_user:
            if existing_user.is_prospect_type():
                return jsonify({
                    'success': True,
                    'message': 'Prospect déjà enregistré',
                    'prospect_id': existing_user.id,
                    'cal_url': 'https://app.cal.com/atlas-finance/30min'
                })
            else:
                # C'est déjà un client
                return jsonify({
                    'success': True,
                    'message': 'Vous êtes déjà client, connectez-vous à votre espace',
                    'prospect_id': existing_user.id,
                    'cal_url': 'https://app.cal.com/atlas-finance/30min'
                })
        
        # Création du nouveau prospect (utilisateur de type prospect)
        prospect = User(
            first_name=data['firstName'].strip(),
            last_name=data['lastName'].strip(),
            email=data['email'].strip().lower(),
            phone=data['phone'].strip(),
            is_admin=False,
            is_active=True,
            
            # Champs spécifiques aux prospects
            user_type='prospect',
            is_prospect=True,  # CRITIQUE : Marquer comme prospect
            prospect_source='site_vitrine',
            prospect_status='nouveau',
            appointment_requested=True,
            appointment_status='en_attente'
        )
        
        # Mot de passe temporaire (sera changé lors de la création du compte)
        prospect.set_password('TempPassword123!')
        
        db.session.add(prospect)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Prospect créé avec succès',
            'prospect_id': prospect.id,
            'cal_url': 'https://cal.com/atlas-finance/30min'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@site_pages_bp.route('/invitation/<token>')
def invitation_signup(token):
    """
    Page d'inscription via invitation pour les prospects.
    """
    prospect = User.query.filter_by(invitation_token=token, user_type='prospect').first()
    
    if not prospect or not prospect.is_invitation_valid():
        flash('Cette invitation est invalide ou a expiré.', 'error')
        return redirect(url_for('site_pages.index'))
    
    return render_template('site/invitation_signup.html', prospect=prospect, token=token)

@site_pages_bp.route('/invitation/<token>/create-account', methods=['POST'])
def create_account_from_invitation(token):
    """
    Activer un compte utilisateur à partir d'une invitation prospect.
    """
    prospect = User.query.filter_by(invitation_token=token, user_type='prospect').first()
    
    if not prospect or not prospect.is_invitation_valid():
        return jsonify({'error': 'Invitation invalide ou expirée'}), 400
    
    try:
        data = request.get_json()
        
        # Validation du mot de passe
        password = data.get('password', '').strip()
        if len(password) < 8:
            return jsonify({'error': 'Le mot de passe doit contenir au moins 8 caractères'}), 400
        
        # Mettre à jour le mot de passe et activer le compte
        prospect.set_password(password)
        prospect.can_create_account = False  # Désactiver l'invitation
        prospect.mark_as_converted()  # Convertir en client
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Compte activé avec succès',
            'redirect_url': url_for('platform_auth.login')
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de l\'activation du compte: {str(e)}'}), 500

@site_pages_bp.route('/api/contact', methods=['POST'])
def send_contact_email():
    """
    API pour envoyer un email de contact via le formulaire.
    """
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = ['nom', 'email', 'sujet', 'message']
        if not data or not all(k in data for k in required_fields):
            return jsonify({'error': 'Données manquantes'}), 400
        
        # Validation de l'email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'error': 'Email invalide'}), 400
        
        # Récupérer l'API token MailerSend
        api_token = os.getenv('MAILERSEND_API_TOKEN')
        if not api_token:
            return jsonify({'error': 'Service d\'email non configuré'}), 500
        
        mailer = MailerSendService(api_token)
        
        # Préparer le contenu de l'email
        nom = data['nom']
        email = data['email']
        telephone = data.get('telephone', 'Non renseigné')
        sujet = data['sujet']
        message = data['message']
        
        # Contenu HTML de l'email
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #137C8B; margin-bottom: 10px;">Nouveau message de contact - Atlas</h1>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="color: #344D59; margin-bottom: 15px;">Informations du contact</h3>
                <p><strong>Nom :</strong> {nom}</p>
                <p><strong>Email :</strong> {email}</p>
                <p><strong>Téléphone :</strong> {telephone}</p>
                <p><strong>Sujet :</strong> {sujet}</p>
            </div>
            
            <div style="background: white; padding: 20px; border-left: 4px solid #137C8B; margin-bottom: 20px;">
                <h3 style="color: #344D59; margin-bottom: 15px;">Message</h3>
                <p style="line-height: 1.6; white-space: pre-line;">{message}</p>
            </div>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #e2e8f0;">
            <p style="font-size: 12px; color: #718096; text-align: center;">
                Atlas Invest - Message reçu depuis le site web
            </p>
        </div>
        """
        
        # Version texte
        text_content = f"""
        Nouveau message de contact - Atlas
        
        Informations du contact:
        Nom: {nom}
        Email: {email}
        Téléphone: {telephone}
        Sujet: {sujet}
        
        Message:
        {message}
        
        ---
        Atlas Invest - Message reçu depuis le site web
        """
        
        # Envoyer l'email
        success = mailer.send_email(
            to_email="contact@atlas-invest.fr",
            to_name="Équipe Atlas",
            subject=f"[Contact Site Web] {sujet} - {nom}",
            html_content=html_content,
            text_content=text_content,
            from_email="noreply@atlas-invest.fr",
            from_name="Site Web Atlas"
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Message envoyé avec succès'
            })
        else:
            return jsonify({'error': 'Erreur lors de l\'envoi du message'}), 500
        
    except Exception as e:
        print(f"Erreur envoi contact: {e}")
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500