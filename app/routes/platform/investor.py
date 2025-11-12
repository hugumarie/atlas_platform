"""
Routes pour l'interface investisseur de la plateforme.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, make_response
from flask_login import login_required, current_user
from app import db
from app.models.investor_profile import InvestorProfile
from app.models.portfolio import Portfolio
from app.models.subscription import Subscription, SubscriptionTier
from app.models.payment_method import PaymentMethod
import json
import re
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io

platform_investor_bp = Blueprint('platform_investor', __name__, url_prefix='/plateforme')

@platform_investor_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard principal de l'investisseur.
    """
    if current_user.is_admin:
        return redirect(url_for('platform_admin.dashboard'))
    
    # Vérifier l'abonnement actif
    if not current_user.subscription or not current_user.subscription.is_active():
        flash('Votre abonnement a expiré. Veuillez renouveler.', 'error')
        return redirect(url_for('platform_auth.login'))
    
    # Vérifier si le questionnaire a été complété
    if not current_user.investor_profile:
        flash('Veuillez d\'abord compléter votre profil investisseur.', 'warning')
        return redirect(url_for('platform_investor.questionnaire'))
    
    # Mettre à jour le portefeuille
    if current_user.portfolio:
        current_user.portfolio.update_from_profile()
    
    return render_template('platform/investor/dashboard.html')

@platform_investor_bp.route('/questionnaire', methods=['GET', 'POST'])
@login_required
def questionnaire():
    """
    Questionnaire de profil investisseur.
    """
    if current_user.is_admin:
        return redirect(url_for('platform_admin.dashboard'))
    
    # Vérifier l'abonnement actif
    if not current_user.subscription or not current_user.subscription.is_active():
        flash('Votre abonnement a expiré.', 'error')
        return redirect(url_for('platform_auth.login'))
    
    # Si le profil existe déjà, rediriger vers le dashboard
    if current_user.investor_profile:
        return redirect(url_for('platform_investor.dashboard'))
    
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            profile_data = {
                'user_id': current_user.id,
                'monthly_net_income': float(request.form.get('monthly_net_income', 0)),
                'current_savings': float(request.form.get('current_savings', 0)),
                'monthly_savings_capacity': float(request.form.get('monthly_savings_capacity', 0)),
                'risk_tolerance': request.form.get('risk_tolerance'),
                'investment_experience': request.form.get('investment_experience'),
                'investment_goals': request.form.get('investment_goals'),
                'investment_horizon': request.form.get('investment_horizon'),
                'family_situation': request.form.get('family_situation'),
                'professional_situation': request.form.get('professional_situation'),
                
                # Investissements existants
                'has_real_estate': 'has_real_estate' in request.form,
                'real_estate_value': float(request.form.get('real_estate_value', 0)) if 'has_real_estate' in request.form else 0,
                'has_life_insurance': 'has_life_insurance' in request.form,
                'life_insurance_value': float(request.form.get('life_insurance_value', 0)) if 'has_life_insurance' in request.form else 0,
                'has_pea': 'has_pea' in request.form,
                'pea_value': float(request.form.get('pea_value', 0)) if 'has_pea' in request.form else 0,
                'has_livret_a': 'has_livret_a' in request.form,
                'livret_a_value': float(request.form.get('livret_a_value', 0)) if 'has_livret_a' in request.form else 0,
                'other_investments': request.form.get('other_investments', '')
            }
            
            # Validation des données obligatoires
            required_fields = ['monthly_net_income', 'current_savings', 'monthly_savings_capacity', 
                             'risk_tolerance', 'investment_experience', 'investment_goals', 
                             'investment_horizon', 'family_situation', 'professional_situation']
            
            for field in required_fields:
                if not profile_data.get(field):
                    flash(f'Le champ {field} est obligatoire.', 'error')
                    return render_template('platform/investor/questionnaire.html')
            
            # Création du profil investisseur
            investor_profile = InvestorProfile(**profile_data)
            db.session.add(investor_profile)
            
            # Mise à jour du portefeuille
            if current_user.portfolio:
                current_user.portfolio.update_from_profile()
            
            db.session.commit()
            
            flash('Profil investisseur créé avec succès ! Bienvenue sur votre dashboard.', 'success')
            return redirect(url_for('platform_investor.dashboard'))
            
        except ValueError as e:
            flash('Veuillez vérifier les valeurs numériques saisies.', 'error')
            return render_template('platform/investor/questionnaire.html')
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de la sauvegarde. Veuillez réessayer.', 'error')
            return render_template('platform/investor/questionnaire.html')
    
    return render_template('platform/investor/questionnaire.html')

@platform_investor_bp.route('/profil', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Gestion du profil utilisateur.
    """
    if current_user.is_admin:
        return redirect(url_for('platform_admin.dashboard'))
    
    if not current_user.subscription or not current_user.subscription.is_active():
        return redirect(url_for('platform_auth.login'))
    
    if request.method == 'POST':
        try:
            # Mise à jour des informations de base
            current_user.first_name = request.form.get('first_name', '').strip()
            current_user.last_name = request.form.get('last_name', '').strip()
            current_user.phone = request.form.get('phone', '').strip() or None
            
            # Gestion du changement de mot de passe
            new_password = request.form.get('new_password', '').strip()
            if new_password:
                password_confirm = request.form.get('new_password_confirm', '').strip()
                
                if new_password != password_confirm:
                    flash('Les nouveaux mots de passe ne correspondent pas.', 'error')
                    return render_template('platform/investor/profile.html')
                
                # Validation de la complexité du mot de passe
                from app.routes.platform.auth import validate_password
                is_valid, message = validate_password(new_password)
                if not is_valid:
                    flash(message, 'error')
                    return render_template('platform/investor/profile.html')
                
                current_user.set_password(new_password)
                flash('Mot de passe mis à jour avec succès.', 'success')
            
            db.session.commit()
            flash('Profil mis à jour avec succès.', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de la mise à jour du profil.', 'error')
    
    return render_template('platform/investor/profile.html')

@platform_investor_bp.route('/formation')
@login_required
def learning():
    """
    Section apprentissage et formations.
    """
    if current_user.is_admin:
        return redirect(url_for('platform_admin.dashboard'))
    
    if not current_user.subscription or not current_user.subscription.is_active():
        return redirect(url_for('platform_auth.login'))
    
    if not current_user.investor_profile:
        flash('Veuillez d\'abord compléter votre profil investisseur.', 'warning')
        return redirect(url_for('platform_investor.questionnaire'))
    
    # Données fictives pour les formations
    courses = [
        {
            'id': 1,
            'title': 'Les bases de l\'investissement',
            'description': 'Comprendre les fondamentaux de l\'investissement et les différents types de placements.',
            'duration': '45 min',
            'level': 'Débutant',
            'thumbnail': '/static/img/course1.jpg',
            'completed': False
        },
        {
            'id': 2,
            'title': 'Diversification de portefeuille',
            'description': 'Apprendre à répartir ses investissements pour optimiser le rapport rendement/risque.',
            'duration': '60 min',
            'level': 'Intermédiaire',
            'thumbnail': '/static/img/course2.jpg',
            'completed': False
        },
        {
            'id': 3,
            'title': 'PEA et optimisation fiscale',
            'description': 'Tout savoir sur le Plan d\'Épargne en Actions et l\'optimisation fiscale.',
            'duration': '50 min',
            'level': 'Intermédiaire',
            'thumbnail': '/static/img/course3.jpg',
            'completed': False
        }
    ]
    
    return render_template('platform/investor/learning.html', courses=courses)

@platform_investor_bp.route('/formations')
@login_required
def formations():
    """
    Section formations détaillées avec layout étendu.
    """
    if current_user.is_admin:
        return redirect(url_for('platform_admin.dashboard'))
    
    if not current_user.subscription or not current_user.subscription.is_active():
        return redirect(url_for('platform_auth.login'))
    
    if not current_user.investor_profile:
        flash('Veuillez d\'abord compléter votre profil investisseur.', 'warning')
        return redirect(url_for('platform_investor.questionnaire'))
    
    # Données détaillées pour les formations
    formations = [
        {
            'id': 1,
            'title': 'Les bases de l\'investissement',
            'description': 'Comprendre les fondamentaux de l\'investissement et les différents types de placements disponibles sur le marché financier pour débuter sereinement.',
            'duration': '45 min',
            'completed': False
        },
        {
            'id': 2,
            'title': 'Diversification de portefeuille',
            'description': 'Apprendre à répartir ses investissements pour optimiser le rapport rendement/risque et minimiser les pertes potentielles grâce aux bonnes pratiques.',
            'duration': '60 min',
            'completed': True
        },
        {
            'id': 3,
            'title': 'PEA et optimisation fiscale',
            'description': 'Tout savoir sur le Plan d\'Épargne en Actions et les stratégies d\'optimisation fiscale pour maximiser vos gains et réduire votre imposition.',
            'duration': '50 min',
            'completed': False
        },
        {
            'id': 4,
            'title': 'Assurance Vie stratégique',
            'description': 'Comprendre l\'assurance vie, ses avantages fiscaux et comment l\'utiliser efficacement dans votre stratégie patrimoniale globale.',
            'duration': '55 min',
            'completed': False
        },
        {
            'id': 5,
            'title': 'Investissement immobilier',
            'description': 'Découvrir les différentes stratégies d\'investissement immobilier et leurs avantages fiscaux spécifiques pour développer votre patrimoine.',
            'duration': '75 min',
            'completed': False
        },
        {
            'id': 6,
            'title': 'Cryptomonnaies et DeFi',
            'description': 'Introduction aux cryptomonnaies, blockchain et à la finance décentralisée pour diversifier intelligemment votre portefeuille moderne.',
            'duration': '65 min',
            'completed': False
        }
    ]
    
    return render_template('platform/investor/formations.html', formations=formations)

@platform_investor_bp.route('/donnees-investisseur')
@login_required
def investor_data():
    """
    Page des données investisseur (profil financier) en mode visualisation.
    """
    if current_user.is_admin:
        return redirect(url_for('platform_admin.dashboard'))
    
    if not current_user.subscription or not current_user.subscription.is_active():
        return redirect(url_for('platform_auth.login'))
    
    if not current_user.investor_profile:
        flash('Veuillez d\'abord compléter votre profil investisseur.', 'warning')
        return redirect(url_for('platform_investor.questionnaire'))
    
    # Vérifier si on est en mode édition
    edit_mode = request.args.get('edit') == 'true'
    
    return render_template('platform/investor/investor_data.html', edit_mode=edit_mode)

@platform_investor_bp.route('/donnees-investisseur/modifier', methods=['POST'])
@login_required
def update_investor_data():
    """
    Mise à jour des données investisseur.
    """
    if current_user.is_admin:
        return redirect(url_for('platform_admin.dashboard'))
    
    if not current_user.subscription or not current_user.subscription.is_active():
        return redirect(url_for('platform_auth.login'))
    
    if not current_user.investor_profile:
        flash('Profil investisseur introuvable.', 'error')
        return redirect(url_for('platform_investor.questionnaire'))
    
    try:
        profile = current_user.investor_profile
        
        # Mise à jour des données financières
        profile.monthly_net_income = float(request.form.get('monthly_net_income', 0))
        profile.current_savings = float(request.form.get('current_savings', 0))
        profile.monthly_savings_capacity = float(request.form.get('monthly_savings_capacity', 0))
        profile.family_situation = request.form.get('family_situation', profile.family_situation)
        
        # Mise à jour du profil d'investissement
        profile.risk_tolerance = request.form.get('risk_tolerance', profile.risk_tolerance)
        profile.investment_experience = request.form.get('investment_experience', profile.investment_experience)
        profile.investment_horizon = request.form.get('investment_horizon', profile.investment_horizon)
        profile.professional_situation = request.form.get('professional_situation', profile.professional_situation)
        profile.investment_goals = request.form.get('investment_goals', profile.investment_goals)
        
        # Mise à jour des investissements existants
        profile.has_livret_a = 'has_livret_a' in request.form
        profile.livret_a_value = float(request.form.get('livret_a_value', 0)) if profile.has_livret_a else 0
        
        profile.has_pea = 'has_pea' in request.form
        profile.pea_value = float(request.form.get('pea_value', 0)) if profile.has_pea else 0
        
        profile.has_per = 'has_per' in request.form
        profile.per_value = float(request.form.get('per_value', 0)) if profile.has_per else 0
        
        profile.has_life_insurance = 'has_life_insurance' in request.form
        profile.life_insurance_value = float(request.form.get('life_insurance_value', 0)) if profile.has_life_insurance else 0
        
        profile.has_current_account = 'has_current_account' in request.form
        profile.current_account_value = float(request.form.get('current_account_value', 0)) if profile.has_current_account else 0
        
        # Mise à jour du portefeuille
        if current_user.portfolio:
            current_user.portfolio.update_from_profile()
        
        db.session.commit()
        flash('Vos données investisseur ont été mises à jour avec succès.', 'success')
        return redirect(url_for('platform_investor.investor_data'))
        
    except ValueError as e:
        flash('Veuillez vérifier les valeurs numériques saisies.', 'error')
        return redirect(url_for('platform_investor.investor_data', edit='true'))
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la mise à jour. Veuillez réessayer.', 'error')
        return redirect(url_for('platform_investor.investor_data', edit='true'))

@platform_investor_bp.route('/assistant')
@login_required
def assistant():
    """
    Assistant financier IA (chat).
    """
    if current_user.is_admin:
        return redirect(url_for('platform_admin.dashboard'))
    
    if not current_user.subscription or not current_user.subscription.is_active():
        return redirect(url_for('platform_auth.login'))
    
    if not current_user.investor_profile:
        flash('Veuillez d\'abord compléter votre profil investisseur.', 'warning')
        return redirect(url_for('platform_investor.questionnaire'))
    
    return render_template('platform/investor/assistant.html')

@platform_investor_bp.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    """
    API pour l'assistant financier Coach Patrimoine via OpenAI.
    """
    if current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    if not current_user.subscription or not current_user.subscription.is_active():
        return jsonify({'error': 'Abonnement expiré'}), 403
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Message vide'}), 400
    
    try:
        # Appel à l'API OpenAI avec Coach Patrimoine
        from openai import OpenAI
        from datetime import datetime
        import os
        
        # Utiliser la clé API depuis les variables d'environnement en production
        api_key = os.getenv('OPENAI_API_KEY', "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")
        client = OpenAI(api_key=api_key)
        
        # Instructions complètes de Coach Patrimoine
        system_prompt = """Tu es "Coach Patrimoine", un assistant d'éducation financière pour débutants en France.
Objectif: expliquer clairement, simplement, sans jargon, et guider l'utilisateur pas à pas (épargne, PEA, assurance-vie, ETF, PER, immobilier, livret A, budget).
Style: phrases courtes, exemples concrets, métaphores simples, check-lists.
Langue: répondre en français par défaut; basculer en anglais si l'utilisateur parle anglais.

Cadre & sécurité:
- Tu fournis de l'information éducative, pas de conseil financier, juridique ou fiscal personnalisé.
- Toujours rappeler: "je ne connais pas ta situation complète". Proposer de consulter un conseiller agréé pour décisions importantes.
- Ne demandes jamais de données sensibles (NIR, IBAN, identités complètes, documents).
- Si l'utilisateur demande une recommandation précise (quel titre acheter), répondre par une méthode simple et diversifiée (ex.: ETF indiciel), expliquer les critères et les risques, sans citer un produit spécifique sauf si l'utilisateur l'a déjà choisi.

Méthode pédagogique standard:
- Budget & épargne: recommander d'épargner au moins 10% des revenus nets chaque mois (si possible).
- Épargne de précaution: constituer 3 à 6 mois de dépenses (selon stabilité des revenus) sur supports sûrs et liquides (Livret A/LDDS).
- Investissement progressif: proposer l'investissement mensuel automatique (DCA) sur des supports diversifiés adaptés au profil de risque.

Exemple neutre de répartition (à adapter au profil utilisateur, toujours comme illustration):
- 60–80% actions globales via ETF indiciels
- 0–20% épargne projet court/moyen terme (monétaire/fonds euros)
- 0–10% crypto maximum et seulement si l'utilisateur comprend la forte volatilité
- enveloppes fiscales françaises (PEA, assurance-vie, PER) selon objectifs

Ton: bienveillant, sans jugement, concret; proposer des micro-actions.

Format de réponse:
- Commencer par un résumé en 2–3 puces.
- Donner les étapes concrètes (1-2-3).
- Ajouter "À retenir" (3 points max).
- Offrir la prochaine micro-action.

Conformité: "Information éducative uniquement. Pas de recommandation personnalisée. Les marchés comportent des risques de perte en capital. Pour tout arbitrage fiscal ou patrimonial important, consulter un professionnel agréé."
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Modèle économique et performant
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
    except Exception as e:
        # En cas d'erreur API, fallback sur message par défaut
        return jsonify({
            'response': 'Désolé, je rencontre un problème technique. Veuillez réessayer dans quelques instants.',
            'timestamp': datetime.now().strftime('%H:%M')
        })

@platform_investor_bp.route('/api/portfolio-data')
@login_required
def portfolio_data():
    """
    API pour récupérer les données du portefeuille pour les graphiques.
    """
    if current_user.is_admin or not current_user.investor_profile:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    if not current_user.subscription or not current_user.subscription.is_active():
        return jsonify({'error': 'Abonnement expiré'}), 403
    
    profile = current_user.investor_profile
    distribution = profile.get_investment_distribution()
    
    return jsonify({
        'distribution': distribution,
        'total_value': profile.current_savings,
        'monthly_income': profile.monthly_net_income,
        'monthly_savings': profile.monthly_savings_capacity,
        'risk_score': profile.get_risk_score()
    })

@platform_investor_bp.route('/profil/changer-plan', methods=['POST'])
@login_required
def change_plan():
    """
    Changement de plan d'abonnement.
    """
    if current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    if not current_user.subscription:
        return jsonify({'success': False, 'message': 'Aucun abonnement trouvé'}), 404
    
    data = request.get_json()
    new_tier = data.get('tier', '').lower()
    
    # Vérifier que le tier est valide
    valid_tiers = ['initia', 'optima', 'ultima']
    if new_tier not in valid_tiers:
        return jsonify({'success': False, 'message': 'Plan invalide'}), 400
    
    # Prix des plans
    tier_prices = {
        'initia': 24.99,
        'optima': 49.99,
        'ultima': 99.99  # Pour ULTIMA, on met un prix de base même si c'est sur devis
    }
    
    try:
        # Mettre à jour l'abonnement
        current_user.subscription.tier = new_tier
        current_user.subscription.price = tier_prices[new_tier]
        current_user.subscription.last_payment_date = datetime.utcnow()
        current_user.subscription.next_billing_date = datetime.utcnow() + timedelta(days=30)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Plan changé avec succès vers {new_tier.upper()}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erreur lors du changement de plan'}), 500

@platform_investor_bp.route('/profil/facture/<int:year>/<int:month>')
@login_required
def generate_invoice(year, month):
    """
    Génère une facture PDF pour le mois et l'année spécifiés.
    """
    if current_user.is_admin:
        return "Accès non autorisé", 403
    
    if not current_user.subscription:
        return "Aucun abonnement trouvé", 404
    
    # Validation des paramètres
    if not (1 <= month <= 12) or not (2020 <= year <= 2030):
        return "Paramètres invalides", 400
    
    # Créer le PDF en mémoire
    buffer = io.BytesIO()
    
    # Configuration du document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=30*mm,
        bottomMargin=30*mm,
        leftMargin=30*mm,
        rightMargin=30*mm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#137C8B')
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#344D59')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6
    )
    
    # Contenu du PDF
    story = []
    
    # Titre
    story.append(Paragraph("ATLAS", title_style))
    story.append(Paragraph("Facture", header_style))
    story.append(Spacer(1, 20))
    
    # Informations de la facture
    month_names = {
        1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
        5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
        9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
    }
    
    invoice_number = f"ATL-{year}-{month:02d}-{current_user.id:04d}"
    invoice_date = datetime(year, month, 1).strftime('%d/%m/%Y')
    
    # Informations générales
    info_data = [
        ['Numéro de facture:', invoice_number],
        ['Date de facturation:', invoice_date],
        ['Période:', f"{month_names[month]} {year}"],
        ['Client:', f"{current_user.first_name} {current_user.last_name}"],
        ['Email:', current_user.email],
    ]
    
    info_table = Table(info_data, colWidths=[60*mm, 80*mm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Détails de la facturation
    story.append(Paragraph("Détails de la facturation", header_style))
    
    # Prix selon le plan
    tier_prices = {
        'initia': 24.99,
        'optima': 49.99,
        'ultima': 99.99
    }
    
    plan_name = current_user.subscription.get_tier_display()
    plan_price = tier_prices.get(current_user.subscription.tier, current_user.subscription.price)
    
    billing_data = [
        ['Description', 'Quantité', 'Prix unitaire', 'Total'],
        [f'Abonnement Atlas - Plan {plan_name}', '1', f'{plan_price:.2f}€', f'{plan_price:.2f}€'],
    ]
    
    billing_table = Table(billing_data, colWidths=[80*mm, 25*mm, 35*mm, 35*mm])
    billing_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#137C8B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(billing_table)
    story.append(Spacer(1, 15))
    
    # Total
    total_data = [
        ['', '', 'Total HT:', f'{plan_price:.2f}€'],
        ['', '', 'TVA (20%):', f'{plan_price * 0.2:.2f}€'],
        ['', '', 'Total TTC:', f'{plan_price * 1.2:.2f}€'],
    ]
    
    total_table = Table(total_data, colWidths=[80*mm, 25*mm, 35*mm, 35*mm])
    total_table.setStyle(TableStyle([
        ('FONTNAME', (2, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (2, -1), (-1, -1), 2, colors.HexColor('#137C8B')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(total_table)
    story.append(Spacer(1, 30))
    
    # Pied de page
    footer_text = """
    <para align=center>
    <b>Atlas - Plateforme Patrimoniale</b><br/>
    Email: contact@atlas-patrimoine.fr<br/>
    Merci de votre confiance !
    </para>
    """
    
    story.append(Paragraph(footer_text, normal_style))
    
    # Construire le PDF
    doc.build(story)
    
    # Préparer la réponse
    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Facture_Atlas_{month_names[month]}_{year}.pdf'
    
    return response

@platform_investor_bp.route('/profil/paiement/ajouter', methods=['POST'])
@login_required
def add_payment_method():
    """
    Ajouter un nouveau moyen de paiement.
    """
    if current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    if not current_user.subscription or not current_user.subscription.is_active():
        return jsonify({'success': False, 'message': 'Abonnement requis'}), 403
    
    data = request.get_json()
    
    try:
        card_number = data.get('card_number', '').replace(' ', '')
        expiry_month = int(data.get('expiry_month', 0))
        expiry_year = int(data.get('expiry_year', 0))
        cardholder_name = data.get('cardholder_name', '').strip()
        set_as_default = data.get('set_as_default', False)
        
        # Validation
        if len(card_number) < 13 or len(card_number) > 19:
            return jsonify({'success': False, 'message': 'Numéro de carte invalide'}), 400
        
        if not (1 <= expiry_month <= 12):
            return jsonify({'success': False, 'message': 'Mois d\'expiration invalide'}), 400
        
        if not (2024 <= expiry_year <= 2035):
            return jsonify({'success': False, 'message': 'Année d\'expiration invalide'}), 400
        
        if not cardholder_name:
            return jsonify({'success': False, 'message': 'Nom du porteur requis'}), 400
        
        # Vérifier si la carte existe déjà
        last_four = card_number[-4:]
        existing_card = PaymentMethod.query.filter_by(
            user_id=current_user.id,
            last_four_digits=last_four
        ).first()
        
        if existing_card:
            return jsonify({'success': False, 'message': 'Cette carte est déjà enregistrée'}), 400
        
        # Créer le nouveau moyen de paiement
        payment_method = PaymentMethod(
            user_id=current_user.id,
            card_type=PaymentMethod.detect_card_type(card_number),
            last_four_digits=last_four,
            expiry_month=expiry_month,
            expiry_year=expiry_year,
            cardholder_name=cardholder_name
        )
        
        db.session.add(payment_method)
        
        # Si demandé ou si c'est la première carte, la mettre par défaut
        if set_as_default or not current_user.payment_methods:
            payment_method.set_as_default()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Carte ajoutée avec succès'
        })
        
    except ValueError:
        return jsonify({'success': False, 'message': 'Données invalides'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erreur lors de l\'ajout'}), 500

@platform_investor_bp.route('/profil/paiement/defaut', methods=['POST'])
@login_required
def set_default_payment():
    """
    Définir un moyen de paiement par défaut.
    """
    if current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    data = request.get_json()
    payment_id = data.get('payment_id')
    
    try:
        payment_method = PaymentMethod.query.filter_by(
            id=payment_id,
            user_id=current_user.id,
            is_active=True
        ).first()
        
        if not payment_method:
            return jsonify({'success': False, 'message': 'Moyen de paiement introuvable'}), 404
        
        payment_method.set_as_default()
        
        return jsonify({
            'success': True,
            'message': 'Moyen de paiement par défaut mis à jour'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erreur lors de la mise à jour'}), 500

@platform_investor_bp.route('/profil/paiement/supprimer', methods=['POST'])
@login_required
def remove_payment_method():
    """
    Supprimer un moyen de paiement.
    """
    if current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    data = request.get_json()
    payment_id = data.get('payment_id')
    
    try:
        payment_method = PaymentMethod.query.filter_by(
            id=payment_id,
            user_id=current_user.id
        ).first()
        
        if not payment_method:
            return jsonify({'success': False, 'message': 'Moyen de paiement introuvable'}), 404
        
        # Désactiver le moyen de paiement
        payment_method.deactivate()
        
        return jsonify({
            'success': True,
            'message': 'Moyen de paiement supprimé'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erreur lors de la suppression'}), 500

@platform_investor_bp.route('/profil/modifier-infos', methods=['POST'])
@login_required
def update_user_info():
    """
    Modifier les informations personnelles de l'utilisateur.
    """
    if current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'Aucune donnée reçue'}), 400
    
    try:
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        phone_raw = data.get('phone', '')
        phone = phone_raw.strip() if phone_raw else None
        
        # Nettoyage des données
        first_name = re.sub(r'[^\w\s\-\'\.]', '', first_name)  # Garder seulement lettres, espaces, tirets, apostrophes, points
        last_name = re.sub(r'[^\w\s\-\'\.]', '', last_name)
        
        # Validation après nettoyage
        if not first_name or not last_name:
            return jsonify({'success': False, 'message': 'Le prénom et le nom sont obligatoires'}), 400
        
        if len(first_name) < 2 or len(first_name) > 50:
            return jsonify({'success': False, 'message': 'Le prénom doit contenir entre 2 et 50 caractères'}), 400
            
        if len(last_name) < 2 or len(last_name) > 50:
            return jsonify({'success': False, 'message': 'Le nom doit contenir entre 2 et 50 caractères'}), 400
        
        # Validation téléphone (optionnel)
        if phone:
            # Format basique pour numéro français (au moins 10 caractères, chiffres et caractères de formatage)
            if not re.match(r'^[0-9\s\-\+\(\)\.]{10,}$', phone):
                return jsonify({'success': False, 'message': 'Format de téléphone invalide'}), 400
        
        # Mise à jour des informations
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.phone = phone
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Informations mises à jour avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erreur lors de la mise à jour'}), 500