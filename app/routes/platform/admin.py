"""
Routes pour l'interface administrateur de la plateforme.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.investor_profile import InvestorProfile
from app.models.subscription import Subscription
from sqlalchemy import or_
from flask import jsonify

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
    
    return render_template('platform/admin/user_detail.html', 
                         user=user, 
                         edit_mode=edit_mode)

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
                    if amount_float > 0:
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
                    if amount_float > 0:
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
        
        # Traitement des cryptomonnaies
        crypto_symbols = request.form.getlist('crypto_symbol[]')
        crypto_quantities = request.form.getlist('crypto_quantity[]')
        
        crypto_investments = []
        for symbol, quantity in zip(crypto_symbols, crypto_quantities):
            if symbol and symbol.strip() and quantity and quantity.strip():
                try:
                    quantity_float = float(quantity.strip())
                    if quantity_float > 0:
                        crypto_investments.append({
                            'symbol': symbol.strip().upper(),
                            'quantity': quantity_float
                        })
                except ValueError:
                    continue
        
        profile.set_cryptos_data(crypto_investments)
        
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
        profile.has_livret_a = request.form.get('has_livret_a') == 'on'
        try:
            profile.livret_a_value = float(request.form.get('livret_a_value', 0) or 0) if profile.has_livret_a else 0.0
        except ValueError:
            profile.livret_a_value = 0.0
        
        # Livret LDDS
        profile.has_ldds = request.form.get('has_ldds') == 'on'
        try:
            profile.ldds_value = float(request.form.get('ldds_value', 0) or 0) if profile.has_ldds else 0.0
        except ValueError:
            profile.ldds_value = 0.0
            
        # LEP
        profile.has_lep = request.form.get('has_lep') == 'on'
        try:
            profile.lep_value = float(request.form.get('lep_value', 0) or 0) if profile.has_lep else 0.0
        except ValueError:
            profile.lep_value = 0.0
            
        # PEL/CEL
        profile.has_pel_cel = request.form.get('has_pel_cel') == 'on'
        try:
            profile.pel_cel_value = float(request.form.get('pel_cel_value', 0) or 0) if profile.has_pel_cel else 0.0
        except ValueError:
            profile.pel_cel_value = 0.0
            
        # Compte Courant
        profile.has_current_account = request.form.get('has_current_account') == 'on'
        try:
            profile.current_account_value = float(request.form.get('current_account_value', 0) or 0) if profile.has_current_account else 0.0
        except ValueError:
            profile.current_account_value = 0.0
        
        # PEL
        profile.has_pel = request.form.get('has_pel') == 'on'
        try:
            profile.pel_value = float(request.form.get('pel_value', 0) or 0) if profile.has_pel else 0.0
        except ValueError:
            profile.pel_value = 0.0
        
        # CEL
        profile.has_cel = request.form.get('has_cel') == 'on'
        try:
            profile.cel_value = float(request.form.get('cel_value', 0) or 0) if profile.has_cel else 0.0
        except ValueError:
            profile.cel_value = 0.0
        
        # Autres livrets
        profile.has_autres_livrets = request.form.get('has_autres_livrets') == 'on'
        try:
            profile.autres_livrets_value = float(request.form.get('autres_livrets_value', 0) or 0) if profile.has_autres_livrets else 0.0
        except ValueError:
            profile.autres_livrets_value = 0.0
        
        # Placements financiers - Section 2
        # PEA
        profile.has_pea = request.form.get('has_pea') == 'on'
        try:
            profile.pea_value = float(request.form.get('pea_value', 0) or 0) if profile.has_pea else 0.0
        except ValueError:
            profile.pea_value = 0.0
        
        # PER
        profile.has_per = request.form.get('has_per') == 'on'
        try:
            profile.per_value = float(request.form.get('per_value', 0) or 0) if profile.has_per else 0.0
        except ValueError:
            profile.per_value = 0.0
        
        # PEE
        profile.has_pee = request.form.get('has_pee') == 'on'
        try:
            profile.pee_value = float(request.form.get('pee_value', 0) or 0) if profile.has_pee else 0.0
        except ValueError:
            profile.pee_value = 0.0
        
        # Assurance Vie
        profile.has_life_insurance = request.form.get('has_life_insurance') == 'on'
        try:
            profile.life_insurance_value = float(request.form.get('life_insurance_value', 0) or 0) if profile.has_life_insurance else 0.0
        except ValueError:
            profile.life_insurance_value = 0.0
        
        # CTO
        profile.has_cto = request.form.get('has_cto') == 'on'
        try:
            profile.cto_value = float(request.form.get('cto_value', 0) or 0) if profile.has_cto else 0.0
        except ValueError:
            profile.cto_value = 0.0
        
        # Private Equity
        profile.has_private_equity = request.form.get('has_private_equity') == 'on'
        try:
            profile.private_equity_value = float(request.form.get('private_equity_value', 0) or 0) if profile.has_private_equity else 0.0
        except ValueError:
            profile.private_equity_value = 0.0
        
        # Crowdfunding
        profile.has_crowdfunding = request.form.get('has_crowdfunding') == 'on'
        try:
            profile.crowdfunding_value = float(request.form.get('crowdfunding_value', 0) or 0) if profile.has_crowdfunding else 0.0
        except ValueError:
            profile.crowdfunding_value = 0.0
            
        # SCPI
        profile.has_scpi = request.form.get('has_scpi') == 'on'
        try:
            profile.scpi_value = float(request.form.get('scpi_value', 0) or 0) if profile.has_scpi else 0.0
        except ValueError:
            profile.scpi_value = 0.0
        
        # Immobilier
        profile.has_immobilier = request.form.get('has_immobilier') == 'on'
        try:
            profile.immobilier_value = float(request.form.get('immobilier_value', 0) or 0) if profile.has_immobilier else 0.0
        except ValueError:
            profile.immobilier_value = 0.0
        
        # Autres Biens
        profile.has_autres_biens = request.form.get('has_autres_biens') == 'on'
        try:
            profile.autres_biens_value = float(request.form.get('autres_biens_value', 0) or 0) if profile.has_autres_biens else 0.0
        except ValueError:
            profile.autres_biens_value = 0.0
        
        # Compatibilité anciens champs
        profile.has_real_estate = profile.has_immobilier
        profile.real_estate_value = profile.immobilier_value
        
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
        profile.investment_experience = request.form.get('investment_experience', '').strip() or 'intermédiaire'
        profile.investment_horizon = request.form.get('investment_horizon', '').strip() or 'moyen'
        
        # Section 6: QUESTIONNAIRE DE RISQUE
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
        
        # Traitement des données complexes JSON
        import json
        
        # Immobilier détaillé
        immobilier_data = []
        bien_types = request.form.getlist('bien_type[]')
        bien_descriptions = request.form.getlist('bien_description[]')
        bien_valeurs = request.form.getlist('bien_valeur[]')
        bien_surfaces = request.form.getlist('bien_surface[]')
        credit_checkboxes = request.form.getlist('credit_checkbox[]') or []
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
                    'has_credit': str(i) in [cb.split('_')[-1] for cb in credit_checkboxes] if credit_checkboxes else False,
                    'credit_montant': float(credit_montants[i] or 0) if i < len(credit_montants) else 0,
                    'credit_taeg': float(credit_taegs[i] or 0) if i < len(credit_taegs) else 0,
                    'credit_tag': float(credit_tags[i] or 0) if i < len(credit_tags) else 0,
                    'credit_duree': int(credit_durees[i] or 0) if i < len(credit_durees) else 0,
                    'credit_date': credit_dates[i].strip() if i < len(credit_dates) else ''
                }
                immobilier_data.append(bien_data)
        
        profile.set_immobilier_data(immobilier_data)
        
        # Cryptomonnaies détaillées
        crypto_data = []
        crypto_symbols = request.form.getlist('crypto_symbol[]')
        crypto_quantities = request.form.getlist('crypto_quantity[]')
        
        for i in range(len(crypto_symbols)):
            if crypto_symbols[i].strip():
                crypto_data.append({
                    'symbol': crypto_symbols[i].strip(),
                    'quantity': float(crypto_quantities[i] or 0) if i < len(crypto_quantities) else 0
                })
        
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
        
        # Crédits détaillés (complémentaire au modèle Credit)
        credits_data = []
        credit_descriptions = request.form.getlist('credit_description[]')
        credit_montants_initiaux = request.form.getlist('credit_montant_initial[]')
        credit_taux = request.form.getlist('credit_taux[]')
        credit_durees_credit = request.form.getlist('credit_duree[]')
        credit_dates_depart = request.form.getlist('credit_date_depart[]')
        
        for i in range(len(credit_descriptions)):
            if credit_descriptions[i].strip():
                credits_data.append({
                    'description': credit_descriptions[i].strip(),
                    'montant_initial': float(credit_montants_initiaux[i] or 0) if i < len(credit_montants_initiaux) else 0,
                    'taux': float(credit_taux[i] or 0) if i < len(credit_taux) else 0,
                    'duree': int(credit_durees_credit[i] or 0) if i < len(credit_durees_credit) else 0,
                    'date_depart': credit_dates_depart[i].strip() if i < len(credit_dates_depart) else ''
                })
        
        profile.set_credits_data(credits_data)
        
        db.session.commit()
        
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