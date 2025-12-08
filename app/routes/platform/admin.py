"""
Routes pour l'interface administrateur de la plateforme.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.investor_profile import InvestorProfile
from app.models.subscription import Subscription
from app.models.apprentissage import Apprentissage
from sqlalchemy import or_
from flask import jsonify
import requests
import time
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from app.services.credit_calculation import CreditCalculationService
from app.services.patrimoine_calculation import PatrimoineCalculationService

platform_admin_bp = Blueprint('platform_admin', __name__, url_prefix='/plateforme/admin')

@platform_admin_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard administrateur avec statistiques générales.
    """
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('site_pages.index'))
    
    # Statistiques générales - utilisateurs avec compte (is_prospect=False)
    total_users = User.query.filter_by(is_admin=False, is_prospect=False).count()
    active_subscriptions = Subscription.query.filter_by(status='active').count()
    trial_subscriptions = Subscription.query.filter_by(status='trial').count()
    completed_profiles = InvestorProfile.query.count()
    
    # Revenus mensuel récurrent (MRR)
    mrr = active_subscriptions * 20  # 20€ par abonnement
    
    stats = {
        'total_users': total_users,
        'active_subscriptions': active_subscriptions,
        'trial_subscriptions': trial_subscriptions,
        'completed_profiles': completed_profiles,
        'conversion_rate': round((completed_profiles / total_users * 100), 1) if total_users > 0 else 0,
        'mrr': mrr
    }
    
    # Derniers utilisateurs inscrits - utilisateurs avec compte
    recent_users = User.query.filter_by(is_admin=False, is_prospect=False).order_by(User.date_created.desc()).limit(5).all()
    
    return render_template('platform/admin/dashboard.html', stats=stats, recent_users=recent_users)

@platform_admin_bp.route('/utilisateurs')
@login_required
def users():
    """
    CRM interne - Gestion des utilisateurs et clients.
    """
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('site_pages.index'))
    
    # Paramètres de filtrage et pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '', type=str)
    status_filter = request.args.get('status', '', type=str)
    tier_filter = request.args.get('tier', '', type=str)
    
    # Query de base - utilisateurs avec compte (is_prospect=False)
    query = User.query.filter_by(is_admin=False, is_prospect=False)
    
    # Filtres
    if search:
        query = query.filter(
            or_(
                User.first_name.contains(search),
                User.last_name.contains(search),
                User.email.contains(search)
            )
        )
    
    if status_filter:
        query = query.join(Subscription).filter(Subscription.status == status_filter)
    
    if tier_filter:
        query = query.join(Subscription).filter(Subscription.tier == tier_filter)
    
    # Pagination
    users = query.order_by(User.date_created.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Statistiques rapides - utilisateurs avec compte
    user_base_query = User.query.filter_by(is_admin=False, is_prospect=False)
    stats = {
        'total_users': user_base_query.count(),
        'active_users': user_base_query.join(Subscription).filter(Subscription.status == 'active').count(),
        'trial_users': user_base_query.join(Subscription).filter(Subscription.status == 'trial').count(),
        'users_with_profile': user_base_query.join(InvestorProfile).count()
    }
    
    return render_template('platform/admin/users.html', 
                         users=users, 
                         stats=stats,
                         search=search,
                         status_filter=status_filter,
                         tier_filter=tier_filter)

def generate_debug_data(profile):
    """Génère les données de debug pour les calculs patrimoniaux."""
    try:
        from app.services.patrimoine_calculation import PatrimoineCalculationService
        
        debug_data = {}
        
        # Debug liquidités - utiliser les valeurs déjà calculées
        debug_data['liquidites'] = {
            'livret_a': profile.livret_a_value if hasattr(profile, 'livret_a_value') and profile.livret_a_value else 0,
            'ldds': profile.ldds_value if hasattr(profile, 'ldds_value') and profile.ldds_value else 0,
            'pel_cel': profile.pel_cel_value if hasattr(profile, 'pel_cel_value') and profile.pel_cel_value else 0,
            'autres_livrets': profile.autres_livrets_value if hasattr(profile, 'autres_livrets_value') and profile.autres_livrets_value else 0,
            'personnalisees': len(profile.liquidites_personnalisees_data) if profile.liquidites_personnalisees_data else 0,
            'total_calcule': profile.calculated_total_liquidites or 0,
            'total_db': profile.calculated_total_liquidites or 0
        }
        
        # Debug placements - utiliser les valeurs déjà calculées
        debug_data['placements'] = {
            'pea': profile.pea_value if hasattr(profile, 'pea_value') and profile.pea_value else 0,
            'per': profile.per_value if hasattr(profile, 'per_value') and profile.per_value else 0,
            'life_insurance': profile.life_insurance_value if hasattr(profile, 'life_insurance_value') and profile.life_insurance_value else 0,
            'pee': profile.pee_value if hasattr(profile, 'pee_value') and profile.pee_value else 0,
            'scpi': profile.scpi_value if hasattr(profile, 'scpi_value') and profile.scpi_value else 0,
            'cto': profile.cto_value if hasattr(profile, 'cto_value') and profile.cto_value else 0,
            'private_equity': profile.private_equity_value if hasattr(profile, 'private_equity_value') and profile.private_equity_value else 0,
            'crowdfunding': profile.crowdfunding_value if hasattr(profile, 'crowdfunding_value') and profile.crowdfunding_value else 0,
            'personnalises': len(profile.placements_personnalises_data) if profile.placements_personnalises_data else 0,
            'total_calcule': profile.calculated_total_placements or 0,
            'total_db': profile.calculated_total_placements or 0
        }
        
        # Debug immobilier - utiliser les valeurs déjà calculées
        debug_data['immobilier'] = {
            'nb_biens': len(profile.immobilier_data) if profile.immobilier_data else 0,
            'total_calcule': profile.calculated_total_immobilier_net or 0,
            'total_db': profile.calculated_total_immobilier_net or 0
        }
        
        # Debug cryptomonnaies - utiliser les valeurs déjà calculées pour éviter double appel API
        debug_data['cryptomonnaies'] = {
            'nb_cryptos': len(profile.cryptomonnaies_data) if profile.cryptomonnaies_data else 0,
            'total_calcule': profile.calculated_total_cryptomonnaies or 0,  # Utiliser la valeur déjà calculée
            'total_db': profile.calculated_total_cryptomonnaies or 0
        }
        
        # Debug autres biens - utiliser les valeurs déjà calculées
        debug_data['autres_biens'] = {
            'nb_biens': len(profile.autres_biens_data) if profile.autres_biens_data else 0,
            'total_calcule': profile.calculated_total_autres_biens or 0,
            'total_db': profile.calculated_total_autres_biens or 0
        }
        
        # Debug crédits - utiliser les valeurs déjà calculées
        debug_data['credits'] = {
            'nb_credits': len(profile.credits_data) if profile.credits_data else 0,
            'total_calcule': profile.calculated_total_credits_consommation or 0,
            'total_db': profile.calculated_total_credits_consommation or 0
        }
        
        # Calculs finaux
        total_actifs_calcule = (
            debug_data['liquidites']['total_calcule'] +
            debug_data['placements']['total_calcule'] +
            debug_data['immobilier']['total_calcule'] +
            debug_data['cryptomonnaies']['total_calcule'] +
            debug_data['autres_biens']['total_calcule']
        )
        
        debug_data['totaux_finaux'] = {
            'total_actifs_calcule': total_actifs_calcule,
            'total_actifs_db': profile.calculated_total_actifs or 0,
            'patrimoine_net_calcule': total_actifs_calcule - debug_data['credits']['total_calcule'],
            'patrimoine_net_db': profile.calculated_patrimoine_total_net or 0,
            'difference_actifs': total_actifs_calcule - (profile.calculated_total_actifs or 0),
            'difference_patrimoine': (total_actifs_calcule - debug_data['credits']['total_calcule']) - (profile.calculated_patrimoine_total_net or 0)
        }
        
        debug_data['meta'] = {
            'last_calculation': profile.last_calculation_date.isoformat() if profile.last_calculation_date else None,
            'user_id': profile.user_id,
            'profile_id': profile.id
        }
        
        return debug_data
        
    except Exception as e:
        return None

@platform_admin_bp.route('/utilisateur/<int:user_id>')
@login_required
def user_detail(user_id):
    """
    Page de détail d'un utilisateur avec toutes ses données patrimoniales.
    """
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('site_pages.index'))
    
    # Récupérer l'utilisateur - exclut les prospects non convertis
    user = User.query.filter_by(id=user_id, is_admin=False, is_prospect=False).first()
    if not user:
        flash('Utilisateur introuvable.', 'error')
        return redirect(url_for('platform_admin.users'))
    
    
    # Mode édition activé par paramètre URL
    edit_mode = request.args.get('edit') == 'true'
    
    # Les données crypto sont maintenant enrichies directement par le service Binance
    
    # Lecture seule - pas de recalcul des crédits
    
    # Recalcul complet des totaux patrimoniaux
    if user.investor_profile:
        try:
            from app.services.patrimoine_calculation_service import PatrimoineCalculationService
            totaux = PatrimoineCalculationService.calculate_and_save_all_totaux(
                user.investor_profile, 
                save_to_db=True
            )
            
            # Refresh pour avoir les nouvelles valeurs
            db.session.refresh(user.investor_profile)
            
            print(f"✅ Totaux recalculés:")
            print(f"  - Total Autres Biens: {totaux['autres_biens']}€")
            print(f"  - Total Actifs (ÉPARGNE & PATRIMOINE): {totaux['total_actifs']}€")
            
        except Exception as e:
            print(f"Erreur recalcul patrimoine: {e}")
    
    debug_data = None
    
    return render_template('platform/admin/user_detail.html', 
                         user=user, 
                         edit_mode=edit_mode,
                         debug_data=debug_data)

@platform_admin_bp.route('/utilisateur/<int:user_id>/modifier', methods=['POST'])
@login_required
def update_user_data(user_id):
    """
    Modifier les données complètes d'un utilisateur depuis l'admin (questionnaire étendu).
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    user = User.query.filter_by(id=user_id, is_admin=False, is_prospect=False).first()
    if not user:
        return jsonify({'success': False, 'message': 'Utilisateur introuvable'}), 404
    
    # Récupérer les données du formulaire HTML directement
    try:
        # Mise à jour des informations personnelles
        user.first_name = request.form.get('first_name', '').strip()
        user.last_name = request.form.get('last_name', '').strip()
        
        # Créer ou mettre à jour le profil investisseur
        if not user.investor_profile:
            from app.models.investor_profile import InvestorProfile
            profile = InvestorProfile(user_id=user.id)
            db.session.add(profile)
        else:
            profile = user.investor_profile
        
        # Section 1: IDENTITÉ
        profile.civilite = request.form.get('civilite', '').strip() or None
        date_naissance_str = request.form.get('date_naissance', '').strip()
        if date_naissance_str:
            from datetime import datetime
            try:
                profile.date_naissance = datetime.strptime(date_naissance_str, '%Y-%m-%d').date()
            except ValueError:
                profile.date_naissance = None
        profile.lieu_naissance = request.form.get('lieu_naissance', '').strip() or None
        profile.nationalite = request.form.get('nationalite', '').strip() or None
        profile.pays_residence = request.form.get('pays_residence', '').strip() or None
        profile.pays_residence_fiscal = request.form.get('pays_residence_fiscal', '').strip() or None
        profile.family_situation = request.form.get('family_situation', '').strip() or None
        
        # Mise à jour du téléphone utilisateur
        user.phone = request.form.get('phone', '').strip() or None
        
        # Section 2: REVENUS
        profile.professional_situation = request.form.get('professional_situation', '').strip() or None
        profile.professional_situation_other = request.form.get('professional_situation_other', '').strip() or None
        profile.metier = request.form.get('metier', '').strip() or None
        
        
        try:
            profile.monthly_net_income = float(request.form.get('monthly_net_income', 0) or 0)
        except ValueError:
            profile.monthly_net_income = 0.0
            
        try:
            profile.impots_mensuels = float(request.form.get('impots_mensuels', 0) or 0)
        except ValueError:
            profile.impots_mensuels = 0.0
            
        # Traitement des revenus complémentaires (nouveau format)
        income_names = request.form.getlist('revenu_complementaire_name[]')
        income_amounts = request.form.getlist('revenu_complementaire_amount[]')
        
        complementary_incomes = []
        for name, amount in zip(income_names, income_amounts):
            if name and name.strip() and amount and amount.strip():
                try:
                    amount_float = float(amount.strip())
                    if amount_float >= 0:  # Permettre 0 aussi
                        complementary_incomes.append({
                            'name': name.strip(),
                            'amount': amount_float
                        })
                except ValueError:
                    continue
        
        profile.set_revenus_complementaires_data(complementary_incomes)
        
        # Calculer le total pour maintenir la compatibilité avec l'ancien champ
        total_complementaires = sum(income['amount'] for income in complementary_incomes)
        profile.revenus_complementaires = total_complementaires
        
        # Traitement des charges mensuelles (nouveau format)
        charge_names = request.form.getlist('charge_mensuelle_name[]')
        charge_amounts = request.form.getlist('charge_mensuelle_amount[]')
        
        monthly_charges = []
        for name, amount in zip(charge_names, charge_amounts):
            if name and name.strip() and amount and amount.strip():
                try:
                    amount_float = float(amount.strip())
                    if amount_float >= 0:  # Permettre 0 aussi
                        monthly_charges.append({
                            'name': name.strip(),
                            'amount': amount_float
                        })
                except ValueError:
                    continue
        
        profile.set_charges_mensuelles_data(monthly_charges)
        
        # Calculer le total pour maintenir la compatibilité avec l'ancien champ
        total_charges = sum(charge['amount'] for charge in monthly_charges)
        profile.charges_mensuelles = total_charges
        
        # Cryptomonnaies traités plus loin dans la fonction
        
        # Traitement des liquidités personnalisées
        liquidite_names = request.form.getlist('liquidite_personnalisee_name[]')
        liquidite_amounts = request.form.getlist('liquidite_personnalisee_amount[]')
        
        liquidites_personnalisees = []
        for name, amount in zip(liquidite_names, liquidite_amounts):
            if name and name.strip() and amount and amount.strip():
                try:
                    amount_float = float(amount.strip())
                    if amount_float > 0:
                        liquidites_personnalisees.append({
                            'name': name.strip(),
                            'amount': amount_float
                        })
                except ValueError:
                    continue
        
        profile.set_liquidites_personnalisees_data(liquidites_personnalisees)
        
        # Traitement des placements personnalisés
        placement_names = request.form.getlist('placement_personnalise_name[]')
        placement_amounts = request.form.getlist('placement_personnalise_amount[]')
        
        placements_personnalises = []
        for name, amount in zip(placement_names, placement_amounts):
            if name and name.strip() and amount and amount.strip():
                try:
                    amount_float = float(amount.strip())
                    if amount_float > 0:
                        placements_personnalises.append({
                            'name': name.strip(),
                            'amount': amount_float
                        })
                except ValueError:
                    continue
        
        profile.set_placements_personnalises_data(placements_personnalises)
        
        try:
            profile.monthly_savings_capacity = float(request.form.get('monthly_savings_capacity', 0) or 0)
        except ValueError:
            profile.monthly_savings_capacity = 0.0
        
        # Section 3: PATRIMOINE
        try:
            profile.current_savings = float(request.form.get('current_savings', 0) or 0)
        except ValueError:
            profile.current_savings = 0.0
        
        # Liquidités - Section 1
        # Livret A
        try:
            profile.livret_a_value = float(request.form.get('livret_a_value', 0) or 0)
        except ValueError:
            profile.livret_a_value = 0.0
        profile.has_livret_a = profile.livret_a_value > 0
        
        # Livret LDDS
        try:
            profile.ldds_value = float(request.form.get('ldds_value', 0) or 0)
        except ValueError:
            profile.ldds_value = 0.0
        profile.has_ldds = profile.ldds_value > 0
            
        # LEP - Pas dans le formulaire, on garde la valeur existante
        
        # PEL/CEL
        try:
            profile.pel_cel_value = float(request.form.get('pel_cel_value', 0) or 0)
        except ValueError:
            profile.pel_cel_value = 0.0
        profile.has_pel_cel = profile.pel_cel_value > 0
            
        # Compte Courant - Pas dans le formulaire, on garde la valeur existante
        
        # PEL, CEL, Autres livrets - Pas dans le formulaire, on garde les valeurs existantes
        
        # Placements financiers - Section 2
        # PEA
        try:
            profile.pea_value = float(request.form.get('pea_value', 0) or 0)
        except ValueError:
            profile.pea_value = 0.0
        profile.has_pea = profile.pea_value > 0
        
        # PER
        try:
            profile.per_value = float(request.form.get('per_value', 0) or 0)
        except ValueError:
            profile.per_value = 0.0
        profile.has_per = profile.per_value > 0
        
        # PEE
        try:
            profile.pee_value = float(request.form.get('pee_value', 0) or 0)
        except ValueError:
            profile.pee_value = 0.0
        profile.has_pee = profile.pee_value > 0
        
        # Assurance Vie
        try:
            profile.life_insurance_value = float(request.form.get('life_insurance_value', 0) or 0)
        except ValueError:
            profile.life_insurance_value = 0.0
        profile.has_life_insurance = profile.life_insurance_value > 0
        
        # CTO
        try:
            profile.cto_value = float(request.form.get('cto_value', 0) or 0)
        except ValueError:
            profile.cto_value = 0.0
        profile.has_cto = profile.cto_value > 0
        
        # Private Equity
        try:
            profile.private_equity_value = float(request.form.get('private_equity_value', 0) or 0)
        except ValueError:
            profile.private_equity_value = 0.0
        profile.has_private_equity = profile.private_equity_value > 0
        
        # Crowdfunding - Pas dans le formulaire, on garde la valeur existante
        
        # SCPI
        try:
            profile.scpi_value = float(request.form.get('scpi_value', 0) or 0)
        except ValueError:
            profile.scpi_value = 0.0
        profile.has_scpi = profile.scpi_value > 0
        
        # Immobilier et Autres Biens - Traités plus bas dans le formulaire avec détails (lignes 440-474)
        
        # Section 4: OBJECTIFS
        profile.objectif_constitution_epargne = request.form.get('objectif_constitution_epargne') == 'on'
        profile.objectif_retraite = request.form.get('objectif_retraite') == 'on'
        profile.objectif_transmission = request.form.get('objectif_transmission') == 'on'
        profile.objectif_defiscalisation = request.form.get('objectif_defiscalisation') == 'on'
        profile.objectif_immobilier = request.form.get('objectif_immobilier') == 'on'
        
        # Investment goals (format pour compatibilité)
        goals = []
        if profile.objectif_constitution_epargne:
            goals.append("constitution_epargne")
        if profile.objectif_retraite:
            goals.append("retraite")
        if profile.objectif_transmission:
            goals.append("transmission")
        if profile.objectif_defiscalisation:
            goals.append("defiscalisation")
        if profile.objectif_immobilier:
            goals.append("immobilier")
        profile.investment_goals = ", ".join(goals)
        
        # Section 5: PROFIL DE RISQUE
        profile.profil_risque_connu = request.form.get('profil_risque_connu') == 'on'
        profile.profil_risque_choisi = request.form.get('profil_risque_choisi', '').strip() or None
        # Compatibilité avec valeur par défaut pour éviter NOT NULL constraint
        profile.risk_tolerance = profile.profil_risque_choisi or 'modéré'
        
        # Valeurs par défaut pour éviter NOT NULL constraint
        profile.investment_experience = request.form.get('experience_investissement', '').strip() or 'intermediaire'
        profile.investment_horizon = request.form.get('horizon_placement', '').strip() or 'moyen'
        
        # Section 6: QUESTIONNAIRE DE RISQUE DÉTAILLÉ
        profile.tolerance_risque = request.form.get('tolerance_risque', '').strip() or 'moderee'
        profile.horizon_placement = request.form.get('horizon_placement', '').strip() or 'moyen'  
        profile.besoin_liquidite = request.form.get('besoin_liquidite', '').strip() or 'long_terme'
        profile.experience_investissement = request.form.get('experience_investissement', '').strip() or 'intermediaire'
        profile.attitude_volatilite = request.form.get('attitude_volatilite', '').strip() or 'attendre'
        
        # Ancien questionnaire (pour compatibilité)
        profile.question_1_reponse = request.form.get('question_1_reponse', '').strip() or None
        profile.question_2_reponse = request.form.get('question_2_reponse', '').strip() or None
        profile.question_3_reponse = request.form.get('question_3_reponse', '').strip() or None
        profile.question_4_reponse = request.form.get('question_4_reponse', '').strip() or None
        profile.question_5_reponse = request.form.get('question_5_reponse', '').strip() or None
        profile.synthese_profil_risque = request.form.get('synthese_profil_risque', '').strip() or None
        
        # Nouveaux objectifs d'investissement étendus
        profile.objectif_premiers_pas = request.form.get('objectif_premiers_pas') == 'on'
        profile.objectif_constituer_capital = request.form.get('objectif_constituer_capital') == 'on'
        profile.objectif_diversifier = request.form.get('objectif_diversifier') == 'on'
        profile.objectif_optimiser_rendement = request.form.get('objectif_optimiser_rendement') == 'on'
        profile.objectif_preparer_retraite = request.form.get('objectif_preparer_retraite') == 'on'
        profile.objectif_securite_financiere = request.form.get('objectif_securite_financiere') == 'on'
        profile.objectif_projet_immobilier = request.form.get('objectif_projet_immobilier') == 'on'
        profile.objectif_revenus_complementaires = request.form.get('objectif_revenus_complementaires') == 'on'
        profile.objectif_transmettre_capital = request.form.get('objectif_transmettre_capital') == 'on'
        profile.objectif_proteger_famille = request.form.get('objectif_proteger_famille') == 'on'
        
        # Nouvelles questions de profil de risque détaillées
        profile.tolerance_risque = request.form.get('tolerance_risque', '').strip() or None
        profile.horizon_placement = request.form.get('horizon_placement', '').strip() or None
        profile.besoin_liquidite = request.form.get('besoin_liquidite', '').strip() or None
        profile.experience_investissement = request.form.get('experience_investissement', '').strip() or None
        profile.attitude_volatilite = request.form.get('attitude_volatilite', '').strip() or None
        
        # Traitement des données complexes JSONB
        
        # Immobilier détaillé
        immobilier_data = []
        bien_types = request.form.getlist('bien_type[]')
        bien_descriptions = request.form.getlist('bien_description[]')
        bien_valeurs = request.form.getlist('bien_valeur[]')
        bien_surfaces = request.form.getlist('bien_surface[]')
        credit_checkboxes = request.form.getlist('bien_has_credit[]') or []
        credit_montants = request.form.getlist('credit_montant[]')
        credit_taegs = request.form.getlist('credit_taeg[]')
        credit_tags = request.form.getlist('credit_tag[]')
        credit_durees = request.form.getlist('credit_duree[]')
        credit_dates = request.form.getlist('credit_date[]')
        
        for i in range(len(bien_types)):
            if bien_types[i].strip():
                bien_data = {
                    'type': bien_types[i].strip(),
                    'description': bien_descriptions[i].strip() if i < len(bien_descriptions) else '',
                    'valeur': float(bien_valeurs[i] or 0) if i < len(bien_valeurs) else 0,
                    'surface': float(bien_surfaces[i] or 0) if i < len(bien_surfaces) else 0,
                    'has_credit': str(i) in credit_checkboxes if credit_checkboxes else False,
                    'credit_montant': float(credit_montants[i] or 0) if i < len(credit_montants) else 0,
                    'credit_taeg': float(credit_taegs[i] or 0) if i < len(credit_taegs) else 0,
                    'credit_tag': float(credit_tags[i] or 0) if i < len(credit_tags) else 0,
                    'credit_duree': int(credit_durees[i] or 0) if i < len(credit_durees) else 0,
                    'credit_date': credit_dates[i].strip() if i < len(credit_dates) else ''
                }
                immobilier_data.append(bien_data)
        
        profile.set_immobilier_data(immobilier_data)
        
        # Calcul des totaux immobilier et mise à jour des champs de résumé
        total_immobilier_value = sum(bien.get('valeur', 0) for bien in immobilier_data)
        profile.immobilier_value = total_immobilier_value
        profile.has_immobilier = total_immobilier_value > 0
        
        # Compatibilité anciens champs
        profile.has_real_estate = profile.has_immobilier
        profile.real_estate_value = profile.immobilier_value
        
        # Cryptomonnaies détaillées - PRÉSERVER les calculated_value existants
        crypto_data = []
        crypto_symbols = request.form.getlist('crypto_symbol[]')
        crypto_quantities = request.form.getlist('crypto_quantity[]')
        
        # Récupérer les données existantes pour préserver les calculated_value
        existing_crypto_data = profile.cryptomonnaies_data or []
        existing_crypto_dict = {c.get('symbol'): c for c in existing_crypto_data}
        
        for i in range(len(crypto_symbols)):
            if crypto_symbols[i].strip():
                symbol = crypto_symbols[i].strip()
                quantity = float(crypto_quantities[i] or 0) if i < len(crypto_quantities) else 0
                
                # Préserver les données enrichies existantes si disponibles
                existing_crypto = existing_crypto_dict.get(symbol, {})
                crypto_item = {
                    'symbol': symbol,
                    'quantity': quantity
                }
                
                # Préserver calculated_value et current_price si ils existent
                if 'calculated_value' in existing_crypto:
                    crypto_item['calculated_value'] = existing_crypto['calculated_value']
                if 'current_price' in existing_crypto:
                    crypto_item['current_price'] = existing_crypto['current_price']
                
                crypto_data.append(crypto_item)
        
        profile.set_cryptomonnaies_data(crypto_data)
        
        # Autres biens détaillés
        autres_biens_data = []
        autre_bien_names = request.form.getlist('autre_bien_name[]')
        autre_bien_descriptions = request.form.getlist('autre_bien_description[]')
        autre_bien_valeurs = request.form.getlist('autre_bien_valeur[]')
        
        for i in range(len(autre_bien_names)):
            if autre_bien_names[i].strip():
                autres_biens_data.append({
                    'name': autre_bien_names[i].strip(),
                    'description': autre_bien_descriptions[i].strip() if i < len(autre_bien_descriptions) else '',
                    'valeur': float(autre_bien_valeurs[i] or 0) if i < len(autre_bien_valeurs) else 0
                })
        
        profile.set_autres_biens_data(autres_biens_data)
        
        # Crédits détaillés (complémentaire au modèle Credit) - GESTION AMÉLIORÉE
        credits_data = []
        credit_ids = request.form.getlist('credit_conso_id[]')
        credit_descriptions = request.form.getlist('credit_conso_description[]')
        credit_montants_initiaux = request.form.getlist('credit_conso_montant_initial[]')
        credit_taux = request.form.getlist('credit_conso_taux[]')
        credit_durees_credit = request.form.getlist('credit_conso_duree[]')
        credit_dates_depart = request.form.getlist('credit_conso_date_depart[]')
        
        # Vérifier que tous les arrays ont la même longueur
        arrays = [credit_ids, credit_descriptions, credit_montants_initiaux, credit_taux, credit_durees_credit, credit_dates_depart]
        max_length = max(len(arr) for arr in arrays) if any(arrays) else 0
        
        # Créer un mapping des crédits existants par ID/index pour préserver les calculs
        existing_credits = profile.credits_data.copy() if profile.credits_data else []
        existing_by_index = {i: credit for i, credit in enumerate(existing_credits)}
        
        
        for i in range(max_length):
            description = credit_descriptions[i].strip() if i < len(credit_descriptions) else ''
            
            # Ne traiter que les crédits avec une description
            if description:
                credit_id = credit_ids[i] if i < len(credit_ids) else str(i)
                
                
                # Données de base du formulaire
                new_credit = {
                    'id': credit_id,
                    'description': description,
                    'montant_initial': float(credit_montants_initiaux[i] or 0) if i < len(credit_montants_initiaux) else 0,
                    'taux': float(credit_taux[i] or 0) if i < len(credit_taux) else 0,
                    'duree': int(credit_durees_credit[i] or 0) if i < len(credit_durees_credit) else 0,
                    'date_depart': credit_dates_depart[i].strip() if i < len(credit_dates_depart) else ''
                }
                
                # Chercher le crédit existant correspondant
                existing_match = None
                if i < len(existing_credits):
                    existing = existing_credits[i]
                    # Match par position ET similarité des données
                    if (existing.get('description') == new_credit['description'] and
                        abs(existing.get('montant_initial', 0) - new_credit['montant_initial']) < 0.01):
                        existing_match = existing
                
                # Préserver les données calculées existantes ou calculer si nouveau
                if existing_match and not any([ 
                    existing_match.get('taux') != new_credit['taux'],
                    existing_match.get('duree') != new_credit['duree'],
                    existing_match.get('date_depart') != new_credit['date_depart']
                ]):
                    # Aucun changement dans les paramètres de calcul - préserver
                    new_credit.update({
                        'mensualite': existing_match.get('mensualite', 0),
                        'capital_restant': existing_match.get('capital_restant', new_credit['montant_initial']),
                        'montant_restant': existing_match.get('montant_restant', new_credit['montant_initial'])
                    })
                else:
                    # Nouveaux paramètres - sera recalculé par calculate_and_save_credits_data
                    pass
                
                credits_data.append(new_credit)
        
        # CORRECTION: Ne pas écraser - directement calculer et sauvegarder avec les nouvelles données
        # Mettre à jour temporairement les données pour le calcul
        profile.credits_data_json = credits_data
        
        # Calculer automatiquement les mensualités et capital restant (qui va sauvegarder correctement)
        calculate_and_save_credits_data(profile)
        
        db.session.commit()
        
        # NOUVEAU: Recalcul local après sauvegarde (lecture DB uniquement)
        try:
            from app.services.local_portfolio_service import LocalPortfolioService
            
            # Recalculer tous les totaux avec les nouvelles données
            LocalPortfolioService.update_user_calculated_totals(profile, save_to_db=True)
            
        except Exception as calc_error:
            print(f"Erreur lors du recalcul des totaux patrimoniaux: {calc_error}")
        
        # Vérification des données après sauvegarde
        db.session.refresh(profile)
        
        # Redirection vers la vue normale après modification
        flash('Profil utilisateur mis à jour avec succès.', 'success')
        return redirect(url_for('platform_admin.user_detail', user_id=user.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la mise à jour: {str(e)}', 'error')
        return redirect(url_for('platform_admin.user_detail', user_id=user.id, edit='true'))

@platform_admin_bp.route('/clients')
@login_required  
def clients():
    """
    Redirection vers la nouvelle page utilisateurs.
    """
    return redirect(url_for('platform_admin.users'))

# Ancienne fonction clients pour compatibilité
def old_clients():
    # Paramètres de recherche
    search = request.args.get('search', '')
    
    # Construction de la requête
    query = User.query.filter_by(is_admin=False)
    
    if search:
        query = query.filter(
            db.or_(
                User.first_name.contains(search),
                User.last_name.contains(search),
                User.email.contains(search)
            )
        )
    
    # Récupération des clients avec pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    clients = query.order_by(User.date_created.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('platform/admin/clients.html', clients=clients, search=search)

@platform_admin_bp.route('/clients/<int:client_id>')
@login_required
def client_detail(client_id):
    """
    Redirection vers la nouvelle page de détail utilisateur.
    """
    return redirect(url_for('platform_admin.user_detail', user_id=client_id))

@platform_admin_bp.route('/prospects')
@login_required
def prospects():
    """
    CRM - Gestion des prospects (leads) provenant du site vitrine.
    """
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('site_pages.index'))
    
    # Paramètres de filtrage et pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '', type=str)
    status_filter = request.args.get('status', '', type=str)
    source_filter = request.args.get('source', '', type=str)
    
    # Query de base - prospects sans compte (is_prospect=True)
    query = User.query.filter_by(is_prospect=True)
    
    # Filtres
    if search:
        query = query.filter(
            or_(
                User.first_name.contains(search),
                User.last_name.contains(search),
                User.email.contains(search),
                User.phone.contains(search)
            )
        )
    
    if status_filter:
        query = query.filter(User.prospect_status == status_filter)
    
    if source_filter:
        query = query.filter(User.prospect_source == source_filter)
    
    # Pagination
    prospects = query.order_by(User.date_created.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Statistiques rapides
    stats = {
        'total_prospects': User.query.filter_by(is_prospect=True).count(),
        'new_prospects': User.query.filter_by(is_prospect=True, prospect_status='nouveau').count(),
        'qualified_prospects': User.query.filter_by(is_prospect=True, prospect_status='qualifié').count(),
        'converted_prospects': User.query.filter_by(is_prospect=False, prospect_status='converti').count(),
        'appointment_pending': User.query.filter_by(is_prospect=True, appointment_status='en_attente').count()
    }
    
    return render_template('platform/admin/prospects.html', 
                         prospects=prospects, 
                         stats=stats,
                         search=search,
                         status_filter=status_filter,
                         source_filter=source_filter)

@platform_admin_bp.route('/prospect/<int:prospect_id>')
@login_required
def prospect_detail(prospect_id):
    """
    Page de détail d'un prospect avec formulaire de modification.
    """
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('site_pages.index'))
    
    # Récupérer le prospect (utilisateur de type prospect)
    prospect = User.query.filter_by(id=prospect_id, is_prospect=True).first()
    if not prospect:
        flash('Prospect introuvable.', 'error')
        return redirect(url_for('platform_admin.prospects'))
    
    # Mode édition activé par paramètre URL
    edit_mode = request.args.get('edit') == 'true'
    
    return render_template('platform/admin/prospect_detail.html', 
                         prospect=prospect, 
                         edit_mode=edit_mode)

@platform_admin_bp.route('/prospect/<int:prospect_id>/modifier', methods=['POST'])
@login_required
def update_prospect(prospect_id):
    """
    Modifier les données d'un prospect depuis l'admin.
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    prospect = User.query.filter_by(id=prospect_id, is_prospect=True).first()
    if not prospect:
        return jsonify({'success': False, 'message': 'Prospect introuvable'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'Aucune donnée reçue'}), 400
    
    try:
        # Mise à jour des informations du prospect
        prospect.first_name = data.get('first_name', prospect.first_name).strip()
        prospect.last_name = data.get('last_name', prospect.last_name).strip()
        prospect.email = data.get('email', prospect.email).strip()
        prospect.phone = data.get('phone', prospect.phone).strip()
        prospect.prospect_status = data.get('status', prospect.prospect_status)
        prospect.prospect_source = data.get('source', prospect.prospect_source)
        prospect.assigned_to = data.get('assigned_to', prospect.assigned_to)
        prospect.appointment_status = data.get('appointment_status', prospect.appointment_status)
        prospect.prospect_notes = data.get('notes', prospect.prospect_notes)
        
        # Mise à jour de la date de dernier contact si le statut change
        if 'status' in data or 'notes' in data:
            prospect.update_last_contact()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Prospect mis à jour avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur lors de la mise à jour: {str(e)}'}), 500

@platform_admin_bp.route('/prospect/<int:prospect_id>/convert', methods=['POST'])
@login_required
def convert_prospect(prospect_id):
    """
    Convertir un prospect en client (utilisateur).
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    prospect = User.query.filter_by(id=prospect_id, is_prospect=True).first()
    if not prospect:
        return jsonify({'success': False, 'message': 'Prospect introuvable'}), 404
    
    try:
        # Convertir le prospect en client (simple changement de type)
        prospect.mark_as_converted()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Prospect converti en client avec succès',
            'user_id': prospect.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur lors de la conversion: {str(e)}'}), 500

@platform_admin_bp.route('/prospect/<int:prospect_id>/invite', methods=['POST'])
@login_required
def invite_prospect(prospect_id):
    """
    Envoie une invitation au prospect pour créer son compte.
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    prospect = User.query.filter_by(id=prospect_id, is_prospect=True).first()
    if not prospect:
        return jsonify({'success': False, 'message': 'Prospect introuvable'}), 404
    
    try:
        # Vérifier si le prospect peut recevoir une invitation
        if prospect.prospect_status == 'converti':
            return jsonify({'success': False, 'message': 'Ce prospect est déjà converti'}), 400
        
        # Générer et envoyer l'invitation
        token = prospect.generate_invitation_token()
        
        # TODO: Envoyer l'email d'invitation ici
        # send_invitation_email(prospect.email, token)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Invitation envoyée avec succès',
            'invitation_url': url_for('site_pages.invitation_signup', token=token, _external=True)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur lors de l\'envoi: {str(e)}'}), 500




def calculate_and_save_credits_data(investor_profile):
    """
    Calcule les mensualités et capital restant pour tous les crédits et sauvegarde en base.
    Utilise le service centralisé de calcul pour assurer la cohérence.
    """
    from app.services.credit_calculation import CreditCalculationService
    from datetime import date
    
    # Traitement des crédits dans credits_data_json (format JSONB)
    credits_data = investor_profile.credits_data.copy() if investor_profile.credits_data else []
    
    for i, credit_data in enumerate(credits_data):
        # Récupération des données
        montant_initial = float(credit_data.get('montant_initial', 0))
        taux_annuel = float(credit_data.get('taux', 0))
        duree_annees = int(credit_data.get('duree', 0))
        date_depart = credit_data.get('date_depart', '')
        
        if montant_initial > 0 and duree_annees > 0:
            # Conversion durée en mois
            duree_mois = duree_annees * 12
            
            # Parse de la date
            try:
                if date_depart:
                    if len(date_depart) == 7:  # Format 2025-10
                        year, month = date_depart.split('-')
                        start_date = date(int(year), int(month), 1)
                    else:
                        start_date = date.today()
                else:
                    start_date = date.today()
            except:
                start_date = date.today()
            
            # Calculs avec le service
            mensualite = CreditCalculationService.calculate_monthly_payment(
                montant_initial, taux_annuel, duree_mois
            )
            
            capital_restant = CreditCalculationService.calculate_remaining_capital(
                montant_initial, taux_annuel, duree_mois, start_date
            )
            
            # Mise à jour des données avec TOUS les champs nécessaires
            credits_data[i]['mensualite'] = round(mensualite, 2)
            credits_data[i]['montant_restant'] = round(capital_restant, 2)  # Champ attendu par le template
            credits_data[i]['capital_restant'] = round(capital_restant, 2)  # Champ alternatif
            
        else:
            # Valeurs par défaut si données insuffisantes
            credits_data[i]['mensualite'] = 0
            credits_data[i]['montant_restant'] = montant_initial
            credits_data[i]['capital_restant'] = montant_initial
    
    # Sauvegarder les données mises à jour avec SQL direct (plus fiable pour JSONB)
    import json
    try:
        sql = '''UPDATE investor_profiles 
                 SET credits_data_json = :credits_data 
                 WHERE id = :profile_id'''
        
        db.session.execute(db.text(sql), {
            'credits_data': json.dumps(credits_data),
            'profile_id': investor_profile.id
        })
        db.session.commit()
        pass  # Sauvegarde réussie
    except Exception as e:
        pass  # Erreur lors de la sauvegarde
        db.session.rollback()
    
    return credits_data


@platform_admin_bp.route('/api/credit/calculate', methods=['POST'])
@login_required
def calculate_credit_api():
    """
    API endpoint pour calculer en temps réel les données d'un crédit.
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    try:
        from app.services.credit_calculation import CreditCalculationService
        
        data = request.get_json()
        
        # Validation des données d'entrée
        required_fields = ['montant_initial', 'taux_interet', 'duree_mois']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Champs manquants'}), 400
        
        # Calculs
        monthly_payment = CreditCalculationService.calculate_monthly_payment(
            float(data['montant_initial']),
            float(data['taux_interet']),
            int(data['duree_mois'])
        )
        
        remaining_capital = data['montant_initial']  # Par défaut
        if data.get('date_debut'):
            from datetime import datetime
            try:
                start_date = CreditCalculationService._parse_date(data['date_debut'])
                remaining_capital = CreditCalculationService.calculate_remaining_capital(
                    float(data['montant_initial']),
                    float(data['taux_interet']),
                    int(data['duree_mois']),
                    start_date
                )
            except Exception:
                pass
        
        # Calculs additionnels
        total_cost = CreditCalculationService.calculate_total_cost(
            float(data['montant_initial']),
            float(data['taux_interet']),
            int(data['duree_mois'])
        )
        
        return jsonify({
            'success': True,
            'monthly_payment': monthly_payment,
            'remaining_capital': remaining_capital,
            'total_cost': total_cost
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur de calcul: {str(e)}'}), 500


@platform_admin_bp.route('/api/credit/<int:user_id>/update', methods=['POST'])
@login_required
def update_user_credit_api(user_id):
    """
    API endpoint pour mettre à jour les calculs des crédits d'un utilisateur.
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        investor_profile = user.investor_profile
        
        if not investor_profile:
            return jsonify({'error': 'Profil investisseur non trouvé'}), 404
        
        # Recalcul des données de crédit
        updated_credits = calculate_and_save_credits_data(investor_profile)
        
        return jsonify({
            'success': True,
            'message': 'Calculs mis à jour avec succès',
            'credits_data': updated_credits
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la mise à jour: {str(e)}'}), 500


@platform_admin_bp.route('/api/patrimoine/calculate/<int:user_id>', methods=['POST'])
@login_required
def calculate_patrimoine_totaux(user_id):
    """
    Calcule et sauvegarde tous les totaux patrimoniaux pour un utilisateur.
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        investor_profile = user.investor_profile
        
        if not investor_profile:
            return jsonify({'error': 'Profil investisseur non trouvé'}), 404
        
        # Calcul de tous les totaux patrimoniaux
        totaux = PatrimoineCalculationService.calculate_all_totaux(investor_profile, save_to_db=True)
        
        return jsonify({
            'success': True,
            'message': 'Tous les totaux patrimoniaux ont été calculés et sauvegardés',
            'totaux': totaux
        })
        
    except Exception as e:
        print(f"Erreur calcul patrimoine pour utilisateur {user_id}: {e}")
        return jsonify({'error': f'Erreur lors du calcul: {str(e)}'}), 500


@platform_admin_bp.route('/api/patrimoine/calculate-all', methods=['POST'])
@login_required
def calculate_all_patrimoine():
    """
    Calcule et sauvegarde les totaux patrimoniaux pour tous les utilisateurs.
    """
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    try:
        # Mise à jour pour tous les utilisateurs
        PatrimoineCalculationService.update_all_users_patrimoine()
        
        return jsonify({
            'success': True,
            'message': 'Tous les totaux patrimoniaux ont été recalculés pour tous les utilisateurs'
        })
        
    except Exception as e:
        print(f"Erreur calcul patrimoine global: {e}")
        return jsonify({'error': f'Erreur lors du calcul global: {str(e)}'}), 500


# ==========================================
# ROUTES APPRENTISSAGE / FORMATIONS
# ==========================================

@platform_admin_bp.route('/apprentissages')
@login_required
def apprentissages():
    """Liste de toutes les formations"""
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('site_pages.index'))
    
    apprentissages = Apprentissage.query.order_by(Apprentissage.ordre, Apprentissage.date_creation.desc()).all()
    return render_template('platform/admin/apprentissages.html', apprentissages=apprentissages)


@platform_admin_bp.route('/apprentissages/nouveau', methods=['GET', 'POST'])
@login_required
def apprentissage_create():
    """Créer une nouvelle formation"""
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('site_pages.index'))
    
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            nom = request.form.get('nom', '').strip()
            description = request.form.get('description', '').strip()
            ordre = int(request.form.get('ordre', 0))
            actif = 'actif' in request.form
            
            if not nom:
                flash('Le nom de la formation est obligatoire.', 'error')
                return render_template('platform/admin/apprentissage_form.html')
            
            # Création du dossier uploads si nécessaire
            upload_dir = os.path.join('app', 'static', 'uploads', 'apprentissages')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Gestion de l'image
            image_filename = None
            if 'image' in request.files:
                image_file = request.files['image']
                if image_file and image_file.filename:
                    # Vérifier le type de fichier
                    if image_file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        # Générer un nom unique
                        file_extension = os.path.splitext(image_file.filename)[1]
                        image_filename = f"{uuid.uuid4().hex}{file_extension}"
                        image_path = os.path.join(upload_dir, image_filename)
                        image_file.save(image_path)
                    else:
                        flash('Format d\'image non supporté. Utilisez PNG, JPG ou GIF.', 'error')
                        return render_template('platform/admin/apprentissage_form.html')
            
            # Gestion du PDF
            pdf_filename = None
            pdf_original_name = None
            if 'fichier_pdf' in request.files:
                pdf_file = request.files['fichier_pdf']
                if pdf_file and pdf_file.filename:
                    if pdf_file.filename.lower().endswith('.pdf'):
                        # Conserver le nom original et générer un nom unique pour le stockage
                        pdf_original_name = pdf_file.filename
                        # Créer un nom sécurisé avec timestamp pour éviter les conflits
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        safe_filename = "".join(c for c in pdf_original_name if c.isalnum() or c in '._-')
                        pdf_filename = f"{timestamp}_{safe_filename}"
                        pdf_path = os.path.join(upload_dir, pdf_filename)
                        pdf_file.save(pdf_path)
                    else:
                        flash('Seuls les fichiers PDF sont autorisés.', 'error')
                        return render_template('platform/admin/apprentissage_form.html')
            
            # Création de la formation
            apprentissage = Apprentissage(
                nom=nom,
                description=description if description else None,
                image=image_filename,
                fichier_pdf=pdf_filename,
                fichier_pdf_original=pdf_original_name,
                ordre=ordre,
                actif=actif
            )
            
            db.session.add(apprentissage)
            db.session.commit()
            
            flash(f'Formation "{nom}" créée avec succès.', 'success')
            return redirect(url_for('platform_admin.apprentissages'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création de la formation: {str(e)}', 'error')
            return render_template('platform/admin/apprentissage_form.html')
    
    return render_template('platform/admin/apprentissage_form.html')


@platform_admin_bp.route('/apprentissages/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
def apprentissage_edit(id):
    """Modifier une formation existante"""
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('site_pages.index'))
    
    apprentissage = Apprentissage.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            nom = request.form.get('nom', '').strip()
            description = request.form.get('description', '').strip()
            ordre = int(request.form.get('ordre', 0))
            actif = 'actif' in request.form
            
            if not nom:
                flash('Le nom de la formation est obligatoire.', 'error')
                return render_template('platform/admin/apprentissage_form.html', apprentissage=apprentissage)
            
            # Dossier uploads
            upload_dir = os.path.join('app', 'static', 'uploads', 'apprentissages')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Gestion de l'image
            if 'image' in request.files:
                image_file = request.files['image']
                if image_file and image_file.filename and image_file.filename.strip():
                    if image_file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        try:
                            # Supprimer l'ancienne image
                            if apprentissage.image:
                                old_image_path = os.path.join(upload_dir, apprentissage.image)
                                if os.path.exists(old_image_path):
                                    os.remove(old_image_path)
                            
                            # Sauvegarder la nouvelle image
                            file_extension = os.path.splitext(image_file.filename)[1]
                            image_filename = f"{uuid.uuid4().hex}{file_extension}"
                            image_path = os.path.join(upload_dir, image_filename)
                            
                            image_file.save(image_path)
                            
                            # Vérifier que le fichier existe après sauvegarde
                            if os.path.exists(image_path):
                                apprentissage.image = image_filename
                            else:
                                flash('Erreur: fichier image non sauvegardé', 'error')
                                return render_template('platform/admin/apprentissage_form.html', apprentissage=apprentissage)
                                
                        except Exception as img_error:
                            flash(f'Erreur lors de la sauvegarde de l\'image: {str(img_error)}', 'error')
                            return render_template('platform/admin/apprentissage_form.html', apprentissage=apprentissage)
                    else:
                        flash('Format d\'image non supporté. Utilisez PNG, JPG ou GIF.', 'error')
                        return render_template('platform/admin/apprentissage_form.html', apprentissage=apprentissage)
            
            # Gestion du PDF
            if 'fichier_pdf' in request.files:
                pdf_file = request.files['fichier_pdf']
                if pdf_file and pdf_file.filename:
                    if pdf_file.filename.lower().endswith('.pdf'):
                        # Supprimer l'ancien PDF
                        if apprentissage.fichier_pdf:
                            old_pdf_path = os.path.join(upload_dir, apprentissage.fichier_pdf)
                            if os.path.exists(old_pdf_path):
                                os.remove(old_pdf_path)
                        
                        # Conserver le nom original et générer un nom unique pour le stockage
                        pdf_original_name = pdf_file.filename
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        safe_filename = "".join(c for c in pdf_original_name if c.isalnum() or c in '._-')
                        pdf_filename = f"{timestamp}_{safe_filename}"
                        pdf_path = os.path.join(upload_dir, pdf_filename)
                        pdf_file.save(pdf_path)
                        apprentissage.fichier_pdf = pdf_filename
                        apprentissage.fichier_pdf_original = pdf_original_name
                    else:
                        flash('Seuls les fichiers PDF sont autorisés.', 'error')
                        return render_template('platform/admin/apprentissage_form.html', apprentissage=apprentissage)
            
            # Mise à jour des autres champs
            apprentissage.nom = nom
            apprentissage.description = description if description else None
            apprentissage.ordre = ordre
            apprentissage.actif = actif
            
            db.session.commit()
            
            flash(f'Formation "{nom}" mise à jour avec succès.', 'success')
            return redirect(url_for('platform_admin.apprentissages'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la mise à jour de la formation: {str(e)}', 'error')
            return render_template('platform/admin/apprentissage_form.html', apprentissage=apprentissage)
    
    return render_template('platform/admin/apprentissage_form.html', apprentissage=apprentissage)


@platform_admin_bp.route('/apprentissages/<int:id>/supprimer', methods=['POST'])
@login_required
def apprentissage_delete(id):
    """Supprimer une formation"""
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('site_pages.index'))
    
    apprentissage = Apprentissage.query.get_or_404(id)
    nom = apprentissage.nom
    
    try:
        # Supprimer les fichiers associés
        upload_dir = os.path.join('app', 'static', 'uploads', 'apprentissages')
        
        if apprentissage.image:
            image_path = os.path.join(upload_dir, apprentissage.image)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        if apprentissage.fichier_pdf:
            pdf_path = os.path.join(upload_dir, apprentissage.fichier_pdf)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        
        # Supprimer de la base de données
        db.session.delete(apprentissage)
        db.session.commit()
        
        flash(f'Formation "{nom}" supprimée avec succès.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression de la formation: {str(e)}', 'error')
    
    return redirect(url_for('platform_admin.apprentissages'))


@platform_admin_bp.route('/apprentissages/<int:id>/apercu')
@login_required
def apprentissage_preview(id):
    """Aperçu d'un PDF d'apprentissage"""
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('site_pages.index'))
    
    apprentissage = Apprentissage.query.get_or_404(id)
    
    if not apprentissage.fichier_pdf:
        flash('Aucun fichier PDF associé à cette formation.', 'error')
        return redirect(url_for('platform_admin.apprentissages'))
    
    try:
        pdf_path = os.path.join('app', 'static', 'uploads', 'apprentissages', apprentissage.fichier_pdf)
        return send_file(pdf_path, mimetype='application/pdf')
        
    except FileNotFoundError:
        flash('Fichier PDF introuvable.', 'error')
        return redirect(url_for('platform_admin.apprentissages'))

@platform_admin_bp.route('/api/crypto-prices')
@login_required
def get_crypto_prices():
    """API endpoint pour récupérer les prix crypto depuis la DB uniquement."""
    # Autoriser tous les utilisateurs connectés (pas seulement admin)
    # if not current_user.is_admin:
    #     return jsonify({'error': 'Accès non autorisé'}), 403
    
    try:
        from app.services.global_crypto_service import GlobalCryptoService
        from app.models.crypto_price import CryptoPrice
        
        # Récupérer les prix depuis la DB uniquement
        crypto_prices = CryptoPrice.query.all()
        
        if not crypto_prices:
            return jsonify({'error': 'Aucun prix disponible en base'}), 500
        
        # Convertir en format compatible avec le frontend JavaScript
        formatted_prices = {}
        
        symbol_mapping = {
            'bitcoin': {'symbol': 'BTC', 'name': 'Bitcoin'},
            'ethereum': {'symbol': 'ETH', 'name': 'Ethereum'},
            'binancecoin': {'symbol': 'BNB', 'name': 'BNB'},
            'solana': {'symbol': 'SOL', 'name': 'Solana'},
            'cardano': {'symbol': 'ADA', 'name': 'Cardano'},
            'polkadot': {'symbol': 'DOT', 'name': 'Polkadot'},
            'chainlink': {'symbol': 'LINK', 'name': 'Chainlink'},
            'avalanche-2': {'symbol': 'AVAX', 'name': 'Avalanche'},
            'cosmos': {'symbol': 'ATOM', 'name': 'Cosmos'},
            'stellar': {'symbol': 'XLM', 'name': 'Stellar'},
        }
        
        for crypto_price in crypto_prices:
            symbol = crypto_price.symbol
            if symbol in symbol_mapping:
                formatted_prices[symbol] = {
                    'eur': round(crypto_price.price_eur, 2),
                    'symbol': symbol_mapping[symbol]['symbol'],
                    'name': symbol_mapping[symbol]['name'],
                    'price': round(crypto_price.price_eur, 2)
                }
        
        return jsonify(formatted_prices)
        
    except Exception as e:
        return jsonify({'error': 'Erreur serveur'}), 500