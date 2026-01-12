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
from app.models.investment_plan import InvestmentPlan, InvestmentPlanLine, AVAILABLE_ENVELOPES
from app.models.compte_rendu import CompteRendu
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
from app.services.user_deletion_service import UserDeletionService
from app.services.digitalocean_storage import get_spaces_service

platform_admin_bp = Blueprint('platform_admin', __name__, url_prefix='/plateforme/admin')

@platform_admin_bp.route('/dashboard')
@login_required
def dashboard():
    print("*** ROUTE PLATFORM/ADMIN/DASHBOARD EXECUTEE ***")
    """
    Dashboard administrateur moderne avec vraies couleurs Atlas.
    """
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('site_pages.index'))
    
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    # === STATISTIQUES DE BASE ===
    total_users = User.query.filter_by(is_admin=False, is_prospect=False).count()
    total_prospects = User.query.filter_by(is_prospect=True).count()
    active_subscriptions = Subscription.query.filter_by(status='active').count()
    completed_profiles = InvestorProfile.query.count()
    
    # === MRR SIMPLIFIÉ ===
    try:
        mrr_query = db.session.query(func.sum(Subscription.price)).filter(
            Subscription.status == 'active'
        ).scalar()
        real_mrr = float(mrr_query) if mrr_query else 0.0
        
        initia_subs = Subscription.query.filter_by(status='active', tier='initia').count()
        optima_subs = Subscription.query.filter_by(status='active', tier='optima').count()
    except Exception as e:
        print(f"Erreur MRR: {e}")
        real_mrr = active_subscriptions * 25.0  # Fallback
        initia_subs = active_subscriptions
        optima_subs = 0
    
    # === CROISSANCE CE MOIS ===
    try:
        debut_mois = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        nouveaux_ce_mois = User.query.filter(
            User.is_admin == False,
            User.is_prospect == False,
            User.date_created >= debut_mois
        ).count()

        # Nom du mois actuel
        mois_actuel = datetime.now().strftime('%B %Y')
        mois_fr = {
            'January': 'Janvier', 'February': 'Février', 'March': 'Mars',
            'April': 'Avril', 'May': 'Mai', 'June': 'Juin',
            'July': 'Juillet', 'August': 'Août', 'September': 'Septembre',
            'October': 'Octobre', 'November': 'Novembre', 'December': 'Décembre'
        }
        for en, fr in mois_fr.items():
            mois_actuel = mois_actuel.replace(en, fr)
    except Exception as e:
        print(f"Erreur croissance: {e}")
        nouveaux_ce_mois = 0
        mois_actuel = "Janvier 2026"
    
    # === PATRIMOINE MOYEN ===
    try:
        avg_query = db.session.query(func.avg(InvestorProfile.calculated_patrimoine_total_net)).filter(
            InvestorProfile.calculated_patrimoine_total_net.isnot(None),
            InvestorProfile.calculated_patrimoine_total_net > 0
        ).scalar()
        avg_patrimoine = float(avg_query) if avg_query else 0.0
    except Exception as e:
        print(f"Erreur patrimoine: {e}")
        avg_patrimoine = 0.0

    # === TOTAL ENCOURS CONSEILLÉS (Placements + Crypto) ===
    try:
        # Somme des placements financiers + crypto de tous les clients
        total_encours = 0.0

        # Récupérer les profils investisseurs des vrais clients uniquement
        all_profiles = db.session.query(InvestorProfile).join(User).filter(
            User.is_admin == False,
            User.is_prospect == False
        ).all()

        print(f"🔍 Calcul encours conseillés pour {len(all_profiles)} clients")

        for profile in all_profiles:
            # Utiliser les colonnes calculées déjà sauvegardées en base
            placements = float(profile.calculated_total_placements or 0)
            crypto = float(profile.calculated_total_cryptomonnaies or 0)

            profile_encours = placements + crypto
            total_encours += profile_encours

            if profile_encours > 0:
                print(f"  - User {profile.user_id}: Placements={placements:,.0f}€ + Crypto={crypto:,.0f}€ = {profile_encours:,.0f}€")

        print(f"✅ Total encours conseillés: {total_encours:,.0f}€")

    except Exception as e:
        print(f"❌ Erreur calcul encours: {e}")
        import traceback
        traceback.print_exc()
        total_encours = 0.0

    stats = {
        'total_users': total_users,
        'total_prospects': total_prospects,
        'active_subscriptions': active_subscriptions,
        'completed_profiles': completed_profiles,
        'real_mrr': real_mrr,
        'initia_subs': initia_subs,
        'optima_subs': optima_subs,
        'nouveaux_ce_mois': nouveaux_ce_mois,
        'mois_actuel': mois_actuel,
        'avg_patrimoine': avg_patrimoine,
        'total_encours': total_encours
    }
    
    # Utilisateurs récents
    recent_users = User.query.filter_by(is_admin=False, is_prospect=False)\
        .order_by(User.date_created.desc()).limit(8).all()
    
    recent_prospects = User.query.filter_by(is_prospect=True)\
        .order_by(User.date_created.desc()).limit(5).all()
    
    return render_template('platform/admin/dashboard.html', 
                         stats=stats, 
                         recent_users=recent_users, 
                         recent_prospects=recent_prospects)

@platform_admin_bp.route('/assistant-ia')
@login_required
def rag_management():
    """
    Interface de gestion de l'assistant IA et du système RAG.
    """
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('site_pages.index'))
    
    return render_template('platform/admin/rag_management.html')

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
    
    # Calcul automatique avec le nouveau service central
    if user.investor_profile:
        try:
            from app.services.patrimony_calculation_engine import PatrimonyCalculationEngine
            
            # Recalcul complet avec le nouveau service
            totaux = PatrimonyCalculationEngine.calculate_and_save_all(
                user.investor_profile,
                force_recalculate=True,
                save_to_db=True
            )
            
            # Refresh complet pour avoir les nouvelles valeurs crypto
            db.session.refresh(user.investor_profile)
            db.session.refresh(user)
            
            # Recharger l'utilisateur complet depuis la base
            user = User.query.get(user_id)
            
            print(f"🔄 Données crypto après refresh: {user.investor_profile.cryptomonnaies_data[:2] if user.investor_profile.cryptomonnaies_data else 'None'}")
            
        except Exception as e:
            print(f"❌ Erreur nouveau service patrimonial: {e}")
            import traceback
            traceback.print_exc()
    
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
        
        # Section 6: QUESTIONNAIRE DE RISQUE DÉTAILLÉ (template admin a déjà les bonnes valeurs)
        
        # Q1: Tolérance au risque (valeurs directes du template admin)
        profile.tolerance_risque = request.form.get('tolerance_risque', '').strip() or 'moderee'
        
        # Q2: Horizon de placement (pas de mapping nécessaire)
        profile.horizon_placement = request.form.get('horizon_placement', '').strip() or 'moyen'
        
        # Q3: Besoin de liquidité (valeurs directes du template admin)
        profile.besoin_liquidite = request.form.get('besoin_liquidite', '').strip() or 'long_terme'
        
        # Q4: Expérience (mapping pour cohérence avec l'algorithme)
        experience_form = request.form.get('experience_investissement', '').strip() or 'intermediaire'
        if experience_form == 'confirme':
            profile.experience_investissement = 'confirme'  # Sans accent pour l'algorithme
        elif experience_form == 'debutant':
            profile.experience_investissement = 'debutant'
        elif experience_form == 'intermediaire':
            profile.experience_investissement = 'intermediaire'
        else:
            profile.experience_investissement = 'intermediaire'  # Défaut
        
        # Q5: Attitude face à la volatilité (pas de mapping nécessaire)
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
        
        # CALCUL DU PROFIL DE RISQUE SELON LE NOUVEL ALGORITHME
        try:
            print(f"🎯 [ADMIN] Calcul du profil de risque pour User {user_id}:")
            print(f"   - Tolerance risque: {profile.tolerance_risque}")
            print(f"   - Horizon placement: {profile.horizon_placement}")
            print(f"   - Besoin liquidité: {profile.besoin_liquidite}")
            print(f"   - Experience investissement: {profile.experience_investissement}")
            print(f"   - Attitude volatilité: {profile.attitude_volatilite}")
            
            # Calcul du profil de risque avec la nouvelle méthode
            calculated_profile = profile.calculate_risk_profile()
            profile.calculated_risk_profile = calculated_profile
            
            print(f"✅ [ADMIN] Profil calculé: {calculated_profile}")
            
            # Maintenir l'ancien champ pour compatibilité
            if calculated_profile:
                if calculated_profile == 'PRUDENT':
                    profile.risk_tolerance = 'conservateur'
                elif calculated_profile == 'EQUILIBRE':
                    profile.risk_tolerance = 'modéré'
                elif calculated_profile == 'DYNAMIQUE':
                    profile.risk_tolerance = 'dynamique'
            
        except Exception as risk_calc_error:
            print(f"❌ [ADMIN] Erreur calcul profil de risque User {user_id}: {risk_calc_error}")
            # En cas d'erreur, garder les valeurs par défaut
            profile.calculated_risk_profile = None
            profile.risk_tolerance = 'modéré'
        
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
        
        # NOUVEAU: Recalcul patrimonial complet avec le service central
        try:
            from app.services.patrimony_calculation_engine import PatrimonyCalculationEngine
            
            # Recalculer TOUS les totaux patrimoniaux avec le nouveau service
            totaux = PatrimonyCalculationEngine.calculate_and_save_all(
                profile,
                force_recalculate=True,
                save_to_db=True
            )
            
            print(f"🔄 Totaux patrimoniaux recalculés après édition")
            
        except Exception as calc_error:
            print(f"❌ Erreur recalcul totaux après édition: {calc_error}")
            import traceback
            traceback.print_exc()
        
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
    
    # Récupérer les tokens d'invitation pour ce prospect
    from app.models.invitation_token import InvitationToken
    invitation_tokens = InvitationToken.query.filter_by(prospect_id=prospect_id).order_by(InvitationToken.created_at.desc()).all()
    
    return render_template('platform/admin/prospect_detail.html', 
                         prospect=prospect, 
                         edit_mode=edit_mode,
                         invitation_tokens=invitation_tokens)

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
    Envoie une invitation au prospect pour créer son compte via Mailjet.
    Utilise le nouveau système de tokens sécurisés.
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
        
        # Importer les nouveaux modèles
        from app.models.invitation_token import InvitationToken
        from app.services.email_service import MailerSendService
        
        # Invalider les anciens tokens actifs pour ce prospect
        old_tokens = InvitationToken.query.filter_by(
            prospect_id=prospect_id, 
            status='active'
        ).all()
        
        for old_token in old_tokens:
            old_token.mark_as_expired()
        
        # Créer un nouveau token sécurisé
        invitation_token = InvitationToken(prospect_id=prospect_id, expiry_days=7)
        db.session.add(invitation_token)
        db.session.flush()  # Pour obtenir l'ID du token
        
        # Construire l'URL d'invitation
        invitation_url = url_for('onboarding.invitation_signup', 
                                token=invitation_token.token, 
                                _external=True)
        
        # Créer le contenu de l'email d'invitation avec le nouveau design
        email_html = f"""
<!doctype html>
<html lang="fr">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <meta name="x-apple-disable-message-reformatting" />
    <title>Atlas</title>
  </head>

  <body style="margin:0;padding:0;background:#f2f4f5;">
    <!-- Preheader -->
    <div style="display:none;max-height:0;overflow:hidden;opacity:0;color:transparent;">
      Créez votre compte Atlas et accédez à votre espace personnel.
    </div>

    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" 
style="background:#f2f4f5;">
      <tr>
        <td align="center" style="padding:28px 16px;">
          <table role="presentation" width="640" cellpadding="0" cellspacing="0" 
style="max-width:640px;background:#fff;border-radius:18px;overflow:hidden;">

            <!-- Header -->
            <tr>
              <td align="center" style="background:#137C8B;padding:18px;">
                <div 
style="font-family:Arial,sans-serif;font-size:22px;font-weight:700;color:#ffffff;">
                  Atlas
                </div>
              </td>
            </tr>

            <!-- Body -->
            <tr>
              <td style="padding:34px;">
                <div 
style="font-family:Arial,sans-serif;font-size:18px;line-height:28px;color:#3a3a3a;">

                  <div style="margin-bottom:20px;font-size:20px;font-weight:700;">
                    🧭 Vous êtes à un pas de rejoindre Atlas
                  </div>

                  <div style="margin-bottom:16px;font-weight:700;">
                    Bonjour {prospect.first_name},
                  </div>

                  <div style="margin-bottom:22px;">
                    Vous avez été invité(e) à créer votre compte afin d'accéder à votre 
<strong>espace personnel Atlas</strong> et choisir la formule qui vous correspond.
                  </div>

                  <!-- Button -->
                  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:22px 
0 28px 0;">
                    <tr>
                      <td align="center">
                        <!--[if mso]>
                        <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" 
href="{invitation_url}" style="height:54px;v-text-anchor:middle;width:320px;" 
arcsize="50%" stroke="f" fillcolor="#137C8B">
                          <w:anchorlock/>
                          <center 
style="color:#ffffff;font-family:Arial,sans-serif;font-size:18px;font-weight:bold;">
                            ✨ Créer mon compte Atlas
                          </center>
                        </v:roundrect>
                        <![endif]-->
                        <!--[if !mso]><!-- -->
                        <a href="{invitation_url}"
                          style="display:inline-block;background:#137C8B;color:#ffffff;text-decor
ation:none;font-family:Arial,sans-serif;font-size:18px;font-weight:700;padding:16px 
28px;border-radius:999px;">
                          ✨ Créer mon compte Atlas
                        </a>
                        <!--<![endif]-->
                      </td>
                    </tr>
                  </table>

                  <div style="margin-bottom:12px;font-weight:700;">
                    📋 Prochaines étapes :
                  </div>

                  <ol style="margin:0 0 22px 18px;padding:0;font-size:18px;line-height:28px;">
                    <li>Créer votre <strong>mot de passe sécurisé</strong></li>
                    <li>Choisir votre formule (<strong>INITIA</strong> ou 
<strong>OPTIMA</strong>)</li>
                    <li>Accéder à votre <strong>tableau de bord</strong> et à votre 
<strong>accompagnement Atlas</strong></li>
                  </ol>

                  <div style="margin-bottom:18px;">
                    <strong>⏰ Important :</strong> Cette invitation reste valable <strong>7 
jours</strong>.
                  </div>

                  <div style="margin-bottom:26px;">
                    Si vous avez la moindre question, vous pouvez nous écrire à :
                    <a href="mailto:contact@atlas-invest.fr" 
style="color:#137C8B;font-weight:700;text-decoration:none;">
                      contact@atlas-invest.fr
                    </a>
                  </div>  

                  <div style="font-family:Arial,sans-serif;font-size:18px;line-height:28px;color:#3a3a3a;margi
n-top:28px;">
                    À tout de suite dans votre espace client,
                  </div>
                  <div style="font-family:Arial,sans-serif;font-size:18px;line-height:28px;color:#3a3a3a;font-weigh
t:700;margin-bottom:20px;">
                    L'équipe Atlas
                  </div>

                </div>
              </td>
            </tr>

            <!-- Footer -->
            <tr>
              <td style="padding:0 34px 30px 34px;">
                <a href="https://atlas-invest.fr" 
style="font-family:Arial,sans-serif;color:#137C8B;text-decoration:underline;">
                  https://atlas-invest.fr
                </a>

                <div style="margin-top:12px;">
                  <img src="https://atlas-invest.fr/static/img/logo-atlas.png" alt="Atlas" style="height:32px;width:auto;vertical-align:middle;margin-right:12px;">
                  <span style="display:inline-block;background:#137C8B;color:#ffffff;font-family:Arial,
sans-serif;font-size:14px;font-weight:700;padding:10px 14px;border-radius:10px;vertical-align:middle;">
                    Atlas – le conseil financier clair et indépendant
                  </span>
                </div>

                <div 
style="margin-top:20px;font-family:Arial,sans-serif;font-size:12px;color:#8a8a8a;">
                  Cet email a été envoyé automatiquement, merci de ne pas y répondre.
                </div>
              </td>
            </tr>

          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
        """
        
        email_text = f"""
        Bonjour {prospect.first_name},
        
        Bienvenue chez Atlas Finance !
        
        Vous avez été invité(e) à créer votre compte client pour accéder à notre plateforme de gestion patrimoniale.
        
        Cliquez sur ce lien pour créer votre compte : {invitation_url}
        
        Prochaines étapes :
        1. Créez votre mot de passe sécurisé
        2. Choisissez votre formule (Initia ou Optima)  
        3. Accédez à votre tableau de bord personnalisé
        
        Cette invitation est valide pendant 7 jours.
        
        À bientôt sur Atlas Invest !
        L'équipe Atlas Invest
        """
        
        # Envoyer l'email d'invitation via MailerSend
        try:
            # Utiliser le token depuis les variables d'environnement
            api_token = os.getenv('MAILERSEND_API_TOKEN')
            if not api_token:
                print("⚠️ MAILERSEND_API_TOKEN non configuré")
                return jsonify({'success': False, 'message': 'Configuration email manquante'}), 500
            
            mailer = MailerSendService(api_token)
            
            email_sent = mailer.send_email(
                to_email=prospect.email,
                to_name=f"{prospect.first_name} {prospect.last_name}",
                subject="🚀 Créez votre compte Atlas",
                html_content=email_html,
                text_content=email_text,
                from_email="noreply@atlas-invest.fr",
                from_name="Atlas"
            )
            
            email_result = {'success': email_sent}
        except Exception as e:
            print(f"❌ Erreur envoi email MailerSend: {e}")
            email_result = {'success': False, 'error': str(e)}
        
        if email_result['success']:
            # Mettre à jour le statut du prospect
            prospect.prospect_status = 'contacté'
            print(f"✅ Invitation envoyée avec succès à {prospect.email}")
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Invitation envoyée avec succès à {prospect.email}',
                'invitation_url': invitation_url,
                'token_expires_in_hours': invitation_token.get_remaining_hours(),
                'email_sent': True,
                'show_link': True  # Pour afficher le lien dans l'interface admin
            })
        else:
            # Email échoué mais token créé
            print(f"❌ Erreur envoi email: {email_result.get('error', 'Erreur inconnue')}")
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Token créé mais erreur email: {email_result.get("error", "Erreur inconnue")}',
                'invitation_url': invitation_url,
                'token_expires_in_hours': invitation_token.get_remaining_hours(),
                'email_sent': False,
                'show_link': True,
                'email_error': email_result.get('error')
            })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur lors de la création de l'invitation: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'Erreur lors de la création de l\'invitation: {str(e)}'
        }), 500




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
            
            # 🔧 CALCULS AVEC VRAIES FORMULES D'AMORTISSEMENT (comme côté utilisateur)
            credit_details = CreditCalculationService.calculate_credit_details(
                principal=montant_initial,
                annual_rate=taux_annuel,
                duration_months=duree_mois,
                start_date=start_date,
                current_date=date.today()
            )
            
            # Utiliser les valeurs calculées avec les vraies formules
            mensualite = credit_details['monthly_payment']
            capital_restant = credit_details['remaining_capital']
            capital_rembourse = credit_details['capital_repaid']
            cout_global = credit_details['total_cost']
            
            # Mise à jour des données avec TOUS les champs nécessaires
            credits_data[i]['mensualite'] = round(mensualite, 2)
            credits_data[i]['montant_restant'] = round(capital_restant, 2)  # Champ attendu par le template
            credits_data[i]['capital_restant'] = round(capital_restant, 2)  # Champ alternatif
            credits_data[i]['capital_rembourse'] = round(capital_rembourse, 2)  # Nouveau champ
            credits_data[i]['cout_global'] = round(cout_global, 2)  # Nouveau champ
            credits_data[i]['calculated_with_real_formulas'] = True  # Marqueur
            
            print(f"🚗 ADMIN - Crédit {credit_data.get('description', 'N/A')}: Capital restant CORRIGÉ {capital_restant:.0f}€ (formule d'amortissement)")
            print(f"   → Capital remboursé: {capital_rembourse:.0f}€, Coût global: {cout_global:.0f}€")
            
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
        
        # 🔧 UTILISER LES VRAIES FORMULES D'AMORTISSEMENT POUR L'API ADMIN
        if data.get('date_debut'):
            try:
                start_date = CreditCalculationService._parse_date(data['date_debut'])
                credit_details = CreditCalculationService.calculate_credit_details(
                    principal=float(data['montant_initial']),
                    annual_rate=float(data['taux_interet']),
                    duration_months=int(data['duree_mois']),
                    start_date=start_date
                )
                remaining_capital = credit_details['remaining_capital']
                capital_rembourse = credit_details['capital_repaid']
                total_cost = credit_details['total_cost']
            except Exception:
                # Fallback en cas d'erreur
                remaining_capital = float(data['montant_initial'])
                capital_rembourse = 0
                total_cost = 0
        else:
            # Pas de date de début, utiliser calcul simple
            remaining_capital = float(data['montant_initial'])
            capital_rembourse = 0
            total_cost = (monthly_payment * int(data['duree_mois'])) - float(data['montant_initial'])
        
        return jsonify({
            'success': True,
            'monthly_payment': monthly_payment,
            'remaining_capital': remaining_capital,
            'capital_rembourse': capital_rembourse if 'capital_rembourse' in locals() else 0,
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
    """Créer une nouvelle formation avec DigitalOcean Spaces"""
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('site_pages.index'))
    
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            nom = request.form.get('nom', '').strip()
            description = request.form.get('description', '').strip()
            categorie = request.form.get('categorie', '').strip() or None
            ordre = int(request.form.get('ordre', 0))
            actif = 'actif' in request.form
            
            if not nom:
                flash('Le nom de la formation est obligatoire.', 'error')
                return render_template('platform/admin/apprentissage_form.html', categories=Apprentissage.CATEGORIES)
            
            # Obtenir le service DigitalOcean Spaces
            spaces_service = get_spaces_service()
            
            # Variables pour les fichiers
            image_url = None
            image_key = None
            pdf_url = None
            pdf_key = None
            pdf_original_name = None
            storage_type = 'digitalocean' if spaces_service else 'local'
            
            print(f"🚀 Début création formation '{nom}' - Storage: {storage_type}")
            
            # Gestion de l'image
            if 'image' in request.files:
                image_file = request.files['image']
                if image_file and image_file.filename and image_file.filename.strip():
                    print(f"🖼️ Processing image: {image_file.filename}")
                    if image_file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        if spaces_service:
                            # Upload vers DigitalOcean Spaces
                            print("📤 Upload image vers DigitalOcean...")
                            image_file.seek(0)  # Reset file pointer
                            result = spaces_service.upload_file(
                                file=image_file,
                                folder_path='apprentissages/images'
                            )
                            if result['success']:
                                image_url = result['url']
                                image_key = result['key']
                                print(f"✅ Image uploadée: {image_url}")
                            else:
                                print(f"❌ Erreur upload image: {result['error']}")
                                flash(f'Erreur upload image: {result["error"]}', 'error')
                                return render_template('platform/admin/apprentissage_form.html', categories=Apprentissage.CATEGORIES)
                        else:
                            # Fallback local si DigitalOcean non disponible
                            upload_dir = os.path.join('app', 'static', 'uploads', 'apprentissages')
                            os.makedirs(upload_dir, exist_ok=True)
                            file_extension = os.path.splitext(image_file.filename)[1]
                            image_filename = f"{uuid.uuid4().hex}{file_extension}"
                            image_path = os.path.join(upload_dir, image_filename)
                            image_file.save(image_path)
                            image_key = image_filename
                            storage_type = 'local'
                            print(f"✅ Image sauvée localement: {image_filename}")
                    else:
                        flash('Format d\'image non supporté. Utilisez PNG, JPG, JPEG ou GIF.', 'error')
                        return render_template('platform/admin/apprentissage_form.html', categories=Apprentissage.CATEGORIES)
            
            # Gestion du PDF
            if 'fichier_pdf' in request.files:
                pdf_file = request.files['fichier_pdf']
                if pdf_file and pdf_file.filename:
                    print(f"📄 Processing PDF: {pdf_file.filename}")
                    if pdf_file.filename.lower().endswith('.pdf'):
                        pdf_original_name = pdf_file.filename
                        
                        if spaces_service:
                            # Upload vers DigitalOcean Spaces
                            print("📤 Upload PDF vers DigitalOcean...")
                            pdf_file.seek(0)  # Reset file pointer
                            result = spaces_service.upload_file(
                                file=pdf_file,
                                folder_path='apprentissages/pdfs'
                            )
                            if result['success']:
                                pdf_url = result['url']
                                pdf_key = result['key']
                                print(f"✅ PDF uploadé: {pdf_url}")
                            else:
                                print(f"❌ Erreur upload PDF: {result['error']}")
                                flash(f'Erreur upload PDF: {result["error"]}', 'error')
                                return render_template('platform/admin/apprentissage_form.html', categories=Apprentissage.CATEGORIES)
                        else:
                            # Fallback local si DigitalOcean non disponible
                            upload_dir = os.path.join('app', 'static', 'uploads', 'apprentissages')
                            os.makedirs(upload_dir, exist_ok=True)
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            safe_filename = "".join(c for c in pdf_original_name if c.isalnum() or c in '._-')
                            pdf_filename = f"{timestamp}_{safe_filename}"
                            pdf_path = os.path.join(upload_dir, pdf_filename)
                            pdf_file.save(pdf_path)
                            pdf_key = pdf_filename
                            storage_type = 'local'
                            print(f"✅ PDF sauvé localement: {pdf_filename}")
                    else:
                        flash('Seuls les fichiers PDF sont autorisés.', 'error')
                        return render_template('platform/admin/apprentissage_form.html', categories=Apprentissage.CATEGORIES)
            
            # Création de la formation
            print("💾 Création formation en base de données...")
            apprentissage = Apprentissage(
                nom=nom,
                description=description if description else None,
                categorie=categorie,
                image=image_key,
                image_url=image_url,
                fichier_pdf=pdf_key,
                fichier_pdf_url=pdf_url,
                fichier_pdf_original=pdf_original_name,
                storage_type=storage_type,
                ordre=ordre,
                actif=actif
            )
            
            db.session.add(apprentissage)
            db.session.commit()
            
            print(f"✅ Formation '{nom}' créée avec succès (ID: {apprentissage.id})")
            flash(f'Formation "{nom}" créée avec succès.', 'success')
            return redirect(url_for('platform_admin.apprentissages'))
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur création formation: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Erreur lors de la création de la formation: {str(e)}', 'error')
            return render_template('platform/admin/apprentissage_form.html', categories=Apprentissage.CATEGORIES)
    
    return render_template('platform/admin/apprentissage_form.html', categories=Apprentissage.CATEGORIES)


@platform_admin_bp.route('/apprentissages/<int:id>/modifier', methods=['GET', 'POST'])
@login_required
def apprentissage_edit(id):
    """Modifier une formation existante avec support DigitalOcean Spaces"""
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('site_pages.index'))
    
    apprentissage = Apprentissage.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            nom = request.form.get('nom', '').strip()
            description = request.form.get('description', '').strip()
            categorie = request.form.get('categorie', '').strip() or None
            ordre = int(request.form.get('ordre', 0))
            actif = 'actif' in request.form
            
            if not nom:
                flash('Le nom de la formation est obligatoire.', 'error')
                return render_template('platform/admin/apprentissage_form.html', apprentissage=apprentissage, categories=Apprentissage.CATEGORIES)
            
            # Obtenir le service DigitalOcean Spaces
            spaces_service = get_spaces_service()
            
            print(f"🔄 Modification formation '{nom}' (ID: {id})")
            
            # Gestion de l'image (si nouveau fichier uploadé)
            if 'image' in request.files:
                image_file = request.files['image']
                if image_file and image_file.filename and image_file.filename.strip():
                    print(f"🖼️ Remplacement image: {image_file.filename}")
                    if image_file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        
                        # Supprimer l'ancienne image si elle existe
                        if apprentissage.storage_type == 'digitalocean' and spaces_service and apprentissage.image:
                            print(f"🗑️ Suppression ancienne image: {apprentissage.image}")
                            spaces_service.delete_file(apprentissage.image)
                        elif apprentissage.storage_type == 'local' and apprentissage.image:
                            old_path = os.path.join('app', 'static', 'uploads', 'apprentissages', apprentissage.image)
                            if os.path.exists(old_path):
                                os.remove(old_path)
                        
                        # Upload nouvelle image
                        if spaces_service:
                            image_file.seek(0)
                            result = spaces_service.upload_file(
                                file=image_file,
                                folder_path='apprentissages/images'
                            )
                            if result['success']:
                                apprentissage.image = result['key']
                                apprentissage.image_url = result['url']
                                apprentissage.storage_type = 'digitalocean'
                                print(f"✅ Nouvelle image uploadée: {result['url']}")
                            else:
                                flash(f'Erreur upload image: {result["error"]}', 'error')
                                return render_template('platform/admin/apprentissage_form.html', apprentissage=apprentissage, categories=Apprentissage.CATEGORIES)
                        else:
                            # Fallback local
                            upload_dir = os.path.join('app', 'static', 'uploads', 'apprentissages')
                            os.makedirs(upload_dir, exist_ok=True)
                            file_extension = os.path.splitext(image_file.filename)[1]
                            image_filename = f"{uuid.uuid4().hex}{file_extension}"
                            image_path = os.path.join(upload_dir, image_filename)
                            image_file.save(image_path)
                            apprentissage.image = image_filename
                            apprentissage.image_url = None
                            apprentissage.storage_type = 'local'
                    else:
                        flash('Format d\'image non supporté. Utilisez PNG, JPG, JPEG ou GIF.', 'error')
                        return render_template('platform/admin/apprentissage_form.html', apprentissage=apprentissage, categories=Apprentissage.CATEGORIES)
            
            # Gestion du PDF (si nouveau fichier uploadé)  
            if 'fichier_pdf' in request.files:
                pdf_file = request.files['fichier_pdf']
                if pdf_file and pdf_file.filename:
                    print(f"📄 Remplacement PDF: {pdf_file.filename}")
                    if pdf_file.filename.lower().endswith('.pdf'):
                        
                        # Supprimer l'ancien PDF s'il existe
                        if apprentissage.storage_type == 'digitalocean' and spaces_service and apprentissage.fichier_pdf:
                            print(f"🗑️ Suppression ancien PDF: {apprentissage.fichier_pdf}")
                            spaces_service.delete_file(apprentissage.fichier_pdf)
                        elif apprentissage.storage_type == 'local' and apprentissage.fichier_pdf:
                            old_path = os.path.join('app', 'static', 'uploads', 'apprentissages', apprentissage.fichier_pdf)
                            if os.path.exists(old_path):
                                os.remove(old_path)
                        
                        # Upload nouveau PDF
                        pdf_original_name = pdf_file.filename
                        
                        if spaces_service:
                            pdf_file.seek(0)
                            result = spaces_service.upload_file(
                                file=pdf_file,
                                folder_path='apprentissages/pdfs'
                            )
                            if result['success']:
                                apprentissage.fichier_pdf = result['key']
                                apprentissage.fichier_pdf_url = result['url']
                                apprentissage.fichier_pdf_original = pdf_original_name
                                apprentissage.storage_type = 'digitalocean'
                                print(f"✅ Nouveau PDF uploadé: {result['url']}")
                            else:
                                flash(f'Erreur upload PDF: {result["error"]}', 'error')
                                return render_template('platform/admin/apprentissage_form.html', apprentissage=apprentissage, categories=Apprentissage.CATEGORIES)
                        else:
                            # Fallback local
                            upload_dir = os.path.join('app', 'static', 'uploads', 'apprentissages')
                            os.makedirs(upload_dir, exist_ok=True)
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            safe_filename = "".join(c for c in pdf_original_name if c.isalnum() or c in '._-')
                            pdf_filename = f"{timestamp}_{safe_filename}"
                            pdf_path = os.path.join(upload_dir, pdf_filename)
                            pdf_file.save(pdf_path)
                            apprentissage.fichier_pdf = pdf_filename
                            apprentissage.fichier_pdf_url = None
                            apprentissage.fichier_pdf_original = pdf_original_name
                            apprentissage.storage_type = 'local'
                    else:
                        flash('Seuls les fichiers PDF sont autorisés.', 'error')
                        return render_template('platform/admin/apprentissage_form.html', apprentissage=apprentissage, categories=Apprentissage.CATEGORIES)
            
            # Mise à jour des autres champs
            apprentissage.nom = nom
            apprentissage.description = description if description else None
            apprentissage.categorie = categorie
            apprentissage.ordre = ordre
            apprentissage.actif = actif
            
            db.session.commit()
            
            print(f"✅ Formation '{nom}' mise à jour avec succès")
            flash(f'Formation "{nom}" mise à jour avec succès.', 'success')
            return redirect(url_for('platform_admin.apprentissages'))
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur modification formation: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Erreur lors de la mise à jour de la formation: {str(e)}', 'error')
            return render_template('platform/admin/apprentissage_form.html', apprentissage=apprentissage, categories=Apprentissage.CATEGORIES)
    
    return render_template('platform/admin/apprentissage_form.html', apprentissage=apprentissage, categories=Apprentissage.CATEGORIES)


@platform_admin_bp.route('/apprentissages/<int:id>/supprimer', methods=['POST'])
@login_required
def apprentissage_delete(id):
    """Supprimer une formation et tous ses fichiers associés"""
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('site_pages.index'))
    
    apprentissage = Apprentissage.query.get_or_404(id)
    nom = apprentissage.nom
    
    try:
        # Initialiser le service DigitalOcean Spaces
        from app.services.digitalocean_storage import get_spaces_service
        spaces_service = get_spaces_service()
        
        files_deleted = []
        errors = []
        
        # 1. Supprimer l'image
        if apprentissage.image:
            if apprentissage.storage_type == 'digitalocean' and spaces_service:
                # Suppression sur DigitalOcean Spaces
                try:
                    result = spaces_service.delete_file(apprentissage.image)
                    if result.get('success', False):
                        files_deleted.append(f"Image: {apprentissage.image} (DigitalOcean)")
                        print(f"✅ Image supprimée sur Spaces: {apprentissage.image}")
                    else:
                        error_detail = result.get('error', 'Erreur inconnue')
                        errors.append(f"Image: {apprentissage.image} (Spaces: {error_detail})")
                        print(f"⚠️ Erreur suppression image Spaces: {error_detail}")
                except Exception as e:
                    errors.append(f"Image Spaces: {e}")
                    print(f"❌ Erreur suppression image Spaces: {e}")
            
            # Toujours essayer de supprimer en local au cas où
            local_image_path = os.path.join('app', 'static', 'uploads', 'apprentissages', apprentissage.image)
            if os.path.exists(local_image_path):
                try:
                    os.remove(local_image_path)
                    files_deleted.append(f"Image: {apprentissage.image} (local)")
                    print(f"✅ Image locale supprimée: {local_image_path}")
                except Exception as e:
                    errors.append(f"Image locale: {e}")
        
        # 2. Supprimer le PDF
        if apprentissage.fichier_pdf:
            if apprentissage.storage_type == 'digitalocean' and spaces_service:
                # Suppression sur DigitalOcean Spaces
                try:
                    result = spaces_service.delete_file(apprentissage.fichier_pdf)
                    if result.get('success', False):
                        files_deleted.append(f"PDF: {apprentissage.fichier_pdf} (DigitalOcean)")
                        print(f"✅ PDF supprimé sur Spaces: {apprentissage.fichier_pdf}")
                    else:
                        error_detail = result.get('error', 'Erreur inconnue')
                        errors.append(f"PDF: {apprentissage.fichier_pdf} (Spaces: {error_detail})")
                        print(f"⚠️ Erreur suppression PDF Spaces: {error_detail}")
                except Exception as e:
                    errors.append(f"PDF Spaces: {e}")
                    print(f"❌ Erreur suppression PDF Spaces: {e}")
            
            # Toujours essayer de supprimer en local au cas où
            local_pdf_path = os.path.join('app', 'static', 'uploads', 'apprentissages', apprentissage.fichier_pdf)
            if os.path.exists(local_pdf_path):
                try:
                    os.remove(local_pdf_path)
                    files_deleted.append(f"PDF: {apprentissage.fichier_pdf} (local)")
                    print(f"✅ PDF local supprimé: {local_pdf_path}")
                except Exception as e:
                    errors.append(f"PDF local: {e}")
        
        # 3. Supprimer de la base de données
        db.session.delete(apprentissage)
        db.session.commit()
        
        # Message de succès détaillé
        success_msg = f'Formation "{nom}" supprimée avec succès.'
        if files_deleted:
            success_msg += f' Fichiers supprimés: {len(files_deleted)}'
        if errors:
            success_msg += f' ⚠️ Erreurs: {len(errors)}'
            
        flash(success_msg, 'success')
        print(f"✅ Formation supprimée: {nom}")
        print(f"   - Fichiers supprimés: {files_deleted}")
        if errors:
            print(f"   - Erreurs: {errors}")
        
    except Exception as e:
        db.session.rollback()
        error_msg = f'Erreur lors de la suppression de la formation: {str(e)}'
        flash(error_msg, 'error')
        print(f"❌ Erreur suppression formation {nom}: {e}")
    
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
        # Retourner TOUS les prix disponibles (pas de mapping limité)
        formatted_prices = {}

        for crypto_price in crypto_prices:
            symbol = crypto_price.symbol
            # Utiliser plus de décimales pour les petites cryptos comme SHIB
            formatted_prices[symbol] = {
                'eur': round(crypto_price.price_eur, 8),  # 8 décimales pour SHIB et autres petites cryptos
                'price': round(crypto_price.price_eur, 8)
            }

        return jsonify(formatted_prices)
        
    except Exception as e:
        return jsonify({'error': 'Erreur serveur'}), 500


# ===== ROUTES PLAN D'INVESTISSEMENT =====

@platform_admin_bp.route('/api/utilisateur/<int:user_id>/plan-investissement')
@login_required
def get_user_investment_plan_api(user_id):
    """
    API pour récupérer le plan d'investissement d'un utilisateur.
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    user = User.query.filter_by(id=user_id, is_admin=False, is_prospect=False).first()
    if not user:
        return jsonify({'success': False, 'message': 'Utilisateur introuvable'}), 404
    
    try:
        # Récupérer ou créer le plan actif
        plan = InvestmentPlan.query.filter_by(user_id=user_id, is_active=True).first()
        if not plan:
            # Créer un plan par défaut
            plan = InvestmentPlan(user_id=user_id, name="Plan principal")
            db.session.add(plan)
            db.session.commit()
        
        # Récupérer le montant mensuel depuis le profil
        monthly_amount = 0
        if user.investor_profile and user.investor_profile.monthly_savings_capacity:
            monthly_amount = user.investor_profile.monthly_savings_capacity
        
        return jsonify({
            'success': True,
            'plan': plan.to_dict(),
            'monthly_amount': monthly_amount,
            'available_envelopes': AVAILABLE_ENVELOPES
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'}), 500



@platform_admin_bp.route('/utilisateur/<int:user_id>/plan-investissement/ligne/<int:line_id>', methods=['DELETE'])
@login_required
def delete_investment_plan_line(user_id, line_id):
    """
    Supprimer une ligne de plan d'investissement.
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    try:
        # Vérifier que la ligne appartient bien au bon utilisateur
        line = InvestmentPlanLine.query.join(InvestmentPlan).filter(
            InvestmentPlanLine.id == line_id,
            InvestmentPlan.user_id == user_id
        ).first()
        
        if not line:
            return jsonify({'success': False, 'message': 'Ligne introuvable'}), 404
        
        db.session.delete(line)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Ligne supprimée avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'}), 500

@platform_admin_bp.route('/utilisateur/<int:user_id>/plan-investissement', methods=['GET'])
@login_required
def user_investment_plan(user_id):
    """
    Page de gestion du plan d'investissement pour un utilisateur.
    """
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('site_pages.index'))
    
    # Récupérer l'utilisateur
    user = User.query.filter_by(id=user_id, is_admin=False, is_prospect=False).first()
    if not user:
        flash('Utilisateur introuvable.', 'error')
        return redirect(url_for('platform_admin.users'))
    
    # Récupérer ou créer le plan d'investissement
    investment_plan = InvestmentPlan.query.filter_by(user_id=user_id, is_active=True).first()
    if not investment_plan:
        investment_plan = InvestmentPlan(
            user_id=user_id,
            name="Plan d'investissement principal",
            is_active=True
        )
        db.session.add(investment_plan)
        db.session.commit()
    
    # Récupérer le montant mensuel depuis le profil investisseur
    monthly_amount = 0
    if user.investor_profile and user.investor_profile.monthly_savings_capacity:
        monthly_amount = user.investor_profile.monthly_savings_capacity
    
    return render_template('platform/admin/user_investment_plan.html', 
                         user=user, 
                         investment_plan=investment_plan,
                         monthly_amount=monthly_amount,
                         available_envelopes=AVAILABLE_ENVELOPES)

@platform_admin_bp.route('/utilisateur/<int:user_id>/plan-investissement/save', methods=['POST'])
@login_required
def save_investment_plan(user_id):
    """
    Sauvegarde le plan d'investissement d'un utilisateur.
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    user = User.query.filter_by(id=user_id, is_admin=False, is_prospect=False).first()
    if not user:
        return jsonify({'success': False, 'message': 'Utilisateur introuvable'}), 404
    
    try:
        data = request.get_json()
        lines_data = data.get('lines', [])
        
        # Validation : vérifier que la somme des pourcentages ne dépasse pas 100%
        total_percentage = sum(float(line.get('percentage', 0)) for line in lines_data)
        if total_percentage > 100:
            return jsonify({
                'success': False, 
                'message': f'La somme des pourcentages ({total_percentage:.1f}%) dépasse 100%'
            }), 400
        
        # Récupérer ou créer le plan
        investment_plan = InvestmentPlan.query.filter_by(user_id=user_id, is_active=True).first()
        if not investment_plan:
            investment_plan = InvestmentPlan(
                user_id=user_id,
                name="Plan d'investissement principal",
                is_active=True
            )
            db.session.add(investment_plan)
            db.session.flush()  # Pour obtenir l'ID
        
        # Supprimer d'abord toutes les actions liées aux anciennes lignes (comme côté user)
        from app.models.investment_action import InvestmentAction
        existing_lines = InvestmentPlanLine.query.filter_by(plan_id=investment_plan.id).all()
        
        # Supprimer les actions liées en premier pour éviter la contrainte FK
        if existing_lines:
            try:
                for line in existing_lines:
                    InvestmentAction.query.filter_by(plan_line_id=line.id).delete()
                db.session.commit()
            except Exception as delete_error:
                db.session.rollback()
                raise Exception(f"Erreur lors de la suppression des actions: {delete_error}")
        
        # Dans une nouvelle transaction, supprimer les anciennes lignes
        try:
            InvestmentPlanLine.query.filter_by(plan_id=investment_plan.id).delete()
            
            # Créer les nouvelles lignes
            for i, line_data in enumerate(lines_data):
                if not line_data.get('support_envelope') or not line_data.get('description'):
                    continue  # Ignorer les lignes incomplètes
                    
                line = InvestmentPlanLine(
                    plan_id=investment_plan.id,
                    support_envelope=line_data.get('support_envelope', ''),
                    description=line_data.get('description', ''),
                    reference=line_data.get('reference', ''),
                    percentage=float(line_data.get('percentage', 0)),
                    order_index=i
                )
                db.session.add(line)
            
            db.session.commit()
            
        except Exception as plan_error:
            db.session.rollback()
            raise Exception(f"Erreur lors de la mise à jour du plan: {plan_error}")
        
        return jsonify({
            'success': True,
            'message': 'Plan d\'investissement sauvegardé avec succès',
            'plan': investment_plan.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur lors de la sauvegarde: {str(e)}'}), 500

@platform_admin_bp.route('/utilisateur/<int:user_id>/supprimer', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """
    Supprime complètement un utilisateur avec annulation Stripe et suppression de toutes ses données.
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    # Récupérer l'utilisateur
    user = User.query.filter_by(id=user_id, is_admin=False).first()
    if not user:
        return jsonify({'success': False, 'message': 'Utilisateur introuvable'}), 404
    
    # Empêcher la suppression d'admin
    if user.is_admin:
        return jsonify({'success': False, 'message': 'Impossible de supprimer un administrateur'}), 400
    
    # Utiliser le service de suppression dédié
    result = UserDeletionService.delete_user_completely(user_id)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 500


@platform_admin_bp.route('/prospect/<int:prospect_id>/supprimer', methods=['DELETE'])
@login_required
def delete_prospect(prospect_id):
    """
    Supprime complètement un prospect et toutes ses données associées.
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    # Récupérer le prospect
    prospect = User.query.filter_by(id=prospect_id, is_prospect=True).first()
    if not prospect:
        return jsonify({'success': False, 'message': 'Prospect introuvable'}), 404
    
    # Utiliser le service de suppression dédié (fonctionne pour prospects aussi)
    result = UserDeletionService.delete_user_completely(prospect_id)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 500


@platform_admin_bp.route('/utilisateur/<int:user_id>/suivi')
@login_required
def user_tracking(user_id):
    """
    Page de suivi utilisateur avec actions possibles
    """
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('site_pages.index'))
    
    # Récupérer l'utilisateur
    user = User.query.filter_by(id=user_id, is_admin=False).first()
    if not user:
        flash('Utilisateur introuvable.', 'error')
        return redirect(url_for('platform_admin.users'))
    
    # Récupérer les comptes rendus de l'utilisateur
    comptes_rendus = CompteRendu.query.filter_by(user_id=user_id).order_by(CompteRendu.date_rdv.desc()).all()
    
    return render_template('platform/admin/user_tracking.html', user=user, comptes_rendus=comptes_rendus)


@platform_admin_bp.route('/utilisateur/<int:user_id>/envoyer-rdv-email', methods=['POST'])
@login_required
def send_first_appointment_email(user_id):
    """
    Envoie un email pour prendre le premier rendez-vous
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    # Récupérer l'utilisateur
    user = User.query.filter_by(id=user_id, is_admin=False).first()
    if not user:
        return jsonify({'success': False, 'message': 'Utilisateur introuvable'}), 404
    
    try:
        from app.services.email_service import MailerSendService
        
        # Récupérer l'API token depuis les variables d'environnement
        api_token = os.getenv('MAILERSEND_API_TOKEN')
        if not api_token:
            return jsonify({'success': False, 'message': 'Configuration email manquante'}), 500
        
        mailer = MailerSendService(api_token)
        
        # Construire l'URL pour le rendez-vous (Cal.com)
        appointment_url = "https://app.cal.eu/contact-atlas/suivi-patrimonial-atlas"
        
        # Contenu HTML de l'email de première prise de RDV avec couleurs Atlas corrigées
        email_html = f"""
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <meta name="x-apple-disable-message-reformatting" />
  <title>Atlas</title>
</head>

<body style="margin:0;padding:0;background:#f2f4f5;">
  <!-- Preheader -->
  <div style="display:none;max-height:0;overflow:hidden;opacity:0;color:transparent;">
    Votre recommandation d'investissement Atlas est en préparation.
  </div>

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f2f4f5;">
    <tr>
      <td align="center" style="padding:28px 16px;">
        <table role="presentation" width="640" cellpadding="0" cellspacing="0" style="max-width:640px;background:#ffffff;border-radius:18px;overflow:hidden;">

          <!-- Header -->
          <tr>
            <td align="center" style="background:#137C8B;padding:18px;">
              <div style="font-family:Arial,sans-serif;font-size:22px;font-weight:700;color:#ffffff;">
                Atlas
              </div>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:34px;">
              <div style="font-family:Arial,sans-serif;font-size:18px;line-height:28px;color:#3a3a3a;">

                <div style="font-weight:700;margin-bottom:16px;">
                  Bonjour {user.first_name},
                </div>

                <div style="margin-bottom:20px;font-size:20px;font-weight:700;">
                  Ton profil investisseur est bien complété 👍
                </div>

                <div style="margin-bottom:22px;">
                  À partir de ces informations, nous allons analyser ta situation et préparer une première
                  <strong>recommandation d'investissement adaptée</strong> à ton <strong>profil de risque</strong> et à tes <strong>objectifs</strong>.
                </div>

                <div style="margin-bottom:18px;">
                  La prochaine étape est simple 👇
                </div>

                <!-- CTA -->
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:22px 0 26px 0;">
                  <tr>
                    <td align="center">
                      <!--[if mso]>
                      <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" href="{appointment_url}" style="height:74px;v-text-anchor:middle;width:380px;" arcsize="50%" stroke="f" fillcolor="#137C8B">
                        <w:anchorlock/>
                        <center style="color:#ffffff;font-family:Arial,sans-serif;font-size:18px;font-weight:bold;">
                          👉 Choisir un créneau de rendez-vous
                        </center>
                      </v:roundrect>
                      <![endif]-->
                      <!--[if !mso]><!-- -->
                      <a href="{appointment_url}"
                        style="display:inline-block;background:#137C8B;color:#ffffff;text-decoration:none;font-family:Arial,sans-serif;font-size:18px;font-weight:700;padding:18px 30px;border-radius:999px;text-align:center;">
                        👉 Choisir un créneau de rendez-vous<br>
                        <span style="font-size:14px;font-style:italic;font-weight:400;">
                          (téléphonique ou visio – 30 min)
                        </span>
                      </a>
                      <!--<![endif]-->
                    </td>
                  </tr>
                </table>

                <div style="margin-bottom:12px;font-weight:700;">
                  Ce rendez-vous nous permettra de :
                </div>

                <ul style="margin:0 0 22px 18px;padding:0;font-size:18px;line-height:28px;">
                  <li>te présenter la <strong>stratégie retenue</strong></li>
                  <li>t'expliquer les <strong>choix effectués</strong></li>
                  <li>répondre à tes <strong>questions</strong></li>
                  <li>valider les <strong>prochaines étapes</strong></li>
                </ul>

                <div style="margin-bottom:26px;">
                  Les créneaux sont disponibles à partir de <strong>J+2</strong>, le temps pour nous de travailler sur ton dossier.
                </div>

                <div style="font-family:Arial,sans-serif;font-size:18px;line-height:28px;color:#3a3a3a;font-style:italic;">
                  À très vite,
                </div>
                <div style="font-family:Arial,sans-serif;font-size:18px;line-height:28px;color:#3a3a3a;font-weight:700;margin-bottom:20px;">
                  L'équipe Atlas
                </div>

              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:0 34px 30px 34px;">
              <a href="https://atlas-invest.fr" style="font-family:Arial,sans-serif;color:#137C8B;text-decoration:underline;">
                https://atlas-invest.fr
              </a>

              <div style="margin-top:12px;">
                <img src="https://atlas-invest.fr/static/img/logo-atlas.png" alt="Atlas" style="height:32px;width:auto;vertical-align:middle;margin-right:12px;">
                <span style="display:inline-block;background:#137C8B;color:#ffffff;font-family:Arial,sans-serif;font-size:14px;font-weight:700;padding:10px 14px;border-radius:10px;vertical-align:middle;">
                  Atlas – le conseil financier clair et indépendant
                </span>
              </div>

              <div style="margin-top:20px;font-family:Arial,sans-serif;font-size:12px;color:#8a8a8a;">
                Cet email a été envoyé automatiquement, merci de ne pas y répondre.
              </div>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
        """
        
        # Version texte
        email_text = f"""
        Bonjour {user.first_name},
        
        Ton profil investisseur est bien complété !
        
        À partir de ces informations, nous allons analyser ta situation et préparer une première recommandation d'investissement adaptée à ton profil de risque et à tes objectifs.
        
        La prochaine étape est simple : choisir un créneau de rendez-vous.
        
        Lien pour réserver : {appointment_url}
        
        Ce rendez-vous nous permettra de :
        - te présenter la stratégie retenue
        - t'expliquer les choix effectués  
        - répondre à tes questions
        - valider les prochaines étapes
        
        Les créneaux sont disponibles à partir de J+2, le temps pour nous de travailler sur ton dossier.
        
        À très vite,
        L'équipe Atlas
        """
        
        # Envoyer l'email
        success = mailer.send_email(
            to_email=user.email,
            to_name=f"{user.first_name} {user.last_name}",
            subject="🌱 Ton premier investissement commence ici",
            html_content=email_html,
            text_content=email_text
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Email de prise de RDV envoyé avec succès à {user.email}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erreur lors de l\'envoi de l\'email'
            })
            
    except Exception as e:
        print(f"Erreur envoi email RDV: {e}")
        return jsonify({
            'success': False,
            'message': f'Erreur lors de l\'envoi: {str(e)}'
        }), 500


@platform_admin_bp.route('/utilisateur/<int:user_id>/envoyer-post-rdv-email', methods=['POST'])
@login_required
def send_post_appointment_email(user_id):
    """
    Envoie un email de suivi après le premier rendez-vous
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    # Récupérer l'utilisateur
    user = User.query.filter_by(id=user_id, is_admin=False).first()
    if not user:
        return jsonify({'success': False, 'message': 'Utilisateur introuvable'}), 404
    
    try:
        from app.services.email_service import MailerSendService
        
        # Récupérer l'API token depuis les variables d'environnement
        api_token = os.getenv('MAILERSEND_API_TOKEN')
        if not api_token:
            return jsonify({'success': False, 'message': 'Configuration email manquante'}), 500
        
        mailer = MailerSendService(api_token)
        
        # URL vers l'espace client (section Mon Plan)
        plan_url = "https://atlas-invest.fr/plateforme/plan-investissement"
        
        # Contenu HTML de l'email post-RDV avec couleurs Atlas corrigées
        email_html = f"""
<!doctype html>
<html lang="fr">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <meta name="x-apple-disable-message-reformatting" />
    <title>Atlas</title>
  </head>

  <body style="margin:0;padding:0;background:#f2f4f5;">
    <!-- Preheader (hidden) -->
    <div style="display:none;max-height:0;overflow:hidden;opacity:0;color:transparent;">
      Les étapes de mise en œuvre de ton investissement sont disponibles dans « Mon Plan ».
    </div>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#f2f4f5;">
      <tr>
        <td align="center" style="padding:28px 16px;">
          <!-- Container -->
          <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="640" style="width:640px;max-width:640px;background:#ffffff;border-radius:18px;overflow:hidden;">
            <!-- Header -->
            <tr>
              <td align="center" style="background:#137C8B;padding:18px 20px;">
                <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:22px;line-height:26px;font-weight:700;color:#ffffff;">
                  Atlas
                </div>
              </td>
            </tr>

            <!-- Body -->
            <tr>
              <td style="padding:34px 34px 16px 34px;">
                <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;color:#3a3a3a;font-size:18px;line-height:28px;">
                  <div style="margin:0 0 16px 0;font-weight:700;">Bonjour {user.first_name},</div>

                  <div style="margin:0 0 16px 0;">Merci pour notre échange.</div>

                  <div style="margin:0 0 22px 0;">
                    Suite à notre rendez-vous, nous avons formalisé les étapes de mise en œuvre de ton investissement.
                  </div>

                  <div style="margin:0 0 20px 0;">
                    <span style="font-weight:700;">👉</span> Tu peux retrouver l'ensemble des éléments concrets, ainsi que les supports d'investissement préconisés,
                    dans la rubrique <span style="font-weight:700;">« Mon Plan »</span> de ton espace client.
                  </div>

                  <!-- Button -->
                  <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="margin:22px 0 26px 0;">
                    <tr>
                      <td align="center">
                        <!--[if mso]>
                          <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" href="{plan_url}" style="height:54px;v-text-anchor:middle;width:320px;" arcsize="50%" stroke="f" fillcolor="#137C8B">
                            <w:anchorlock/>
                            <center style="color:#ffffff;font-family:Arial,sans-serif;font-size:18px;font-weight:bold;">
                              👉 Accéder à mon plan
                            </center>
                          </v:roundrect>
                        <![endif]-->
                        <!--[if !mso]><!-- -->
                        <a href="{plan_url}"
                          style="display:inline-block;background:#137C8B;color:#ffffff;text-decoration:none;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:18px;line-height:22px;font-weight:700;padding:16px 28px;border-radius:999px;">
                          👉 Accéder à mon plan
                        </a>
                        <!--<![endif]-->
                      </td>
                    </tr>
                  </table>

                  <div style="margin:0 0 18px 0;">
                    Pour les prochaines semaines, l'idée est simple : prendre le temps de te familiariser avec ce placement
                    et de comprendre son fonctionnement.
                  </div>

                  <div style="margin:0 0 10px 0;">
                    <span style="font-weight:700;">👉</span> Tu peux t'appuyer sur :
                  </div>

                  <!-- Bullets -->
                  <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="margin:8px 0 20px 0;">
                    <tr>
                      <td style="padding-left:18px;">
                        <ul style="margin:0;padding-left:18px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;color:#3a3a3a;font-size:18px;line-height:28px;">
                          <li><span style="font-weight:700;">ton tableau de bord</span> pour suivre tes avancées</li>
                          <li><span style="font-weight:700;">les ressources pédagogiques</span> disponibles dans ton espace client</li>
                          <li>
                            notre accompagnement, si tu as la moindre question
                            <span style="font-style:italic;">(via WhatsApp pour une réponse rapide)</span>
                          </li>
                        </ul>
                      </td>
                    </tr>
                  </table>

                  <div style="margin:0 0 18px 0;">
                    Nous nous reparlerons dans environ <span style="font-weight:700;">3 mois</span> pour faire le point et, si c'est pertinent,
                    envisager la mise en place d'un autre investissement.
                  </div>

                  <div style="margin:0 0 22px 0;">
                    Atlas s'inscrit dans une logique progressive : on avance étape par étape, au bon rythme.
                  </div>

                  <div style="margin:0 0 6px 0;">À bientôt,</div>
                  <div style="margin:0 0 18px 0;font-weight:700;">L'équipe Atlas</div>
                </div>
              </td>
            </tr>

            <!-- Signature / Footer band -->
            <tr>
              <td style="padding:10px 34px 30px 34px;">
                <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                  <tr>
                    <td style="padding:10px 0 6px 0;">
                      <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:16px;line-height:22px;">
                        <a href="https://atlas-invest.fr" style="color:#137C8B;text-decoration:underline;">https://atlas-invest.fr</a>
                      </div>
                    </td>
                  </tr>

                  <tr>
                    <td style="padding-top:10px;">
                      <img src="https://atlas-invest.fr/static/img/logo-atlas.png" alt="Atlas" style="height:32px;width:auto;vertical-align:middle;margin-right:12px;">
                      <span style="display:inline-block;background:#137C8B;color:#ffffff;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:14px;line-height:18px;font-weight:700;padding:10px 14px;border-radius:10px;vertical-align:middle;">
                        Atlas – le conseil financier clair et indépendant
                      </span>
                    </td>
                  </tr>

                  <tr>
                    <td style="padding-top:22px;">
                      <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:12px;line-height:18px;color:#8a8a8a;">
                        Cet email a été envoyé automatiquement, merci de ne pas y répondre.
                      </div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
          <!-- /Container -->
        </td>
      </tr>
    </table>
  </body>
</html>
        """
        
        # Version texte
        email_text = f"""
        Bonjour {user.first_name},
        
        Merci pour notre échange.
        
        Suite à notre rendez-vous, nous avons formalisé les étapes de mise en œuvre de ton investissement.
        
        Tu peux retrouver l'ensemble des éléments concrets, ainsi que les supports d'investissement préconisés, dans la rubrique « Mon Plan » de ton espace client.
        
        Lien vers ton plan : {plan_url}
        
        Pour les prochaines semaines, l'idée est simple : prendre le temps de te familiariser avec ce placement et de comprendre son fonctionnement.
        
        Tu peux t'appuyer sur :
        - ton tableau de bord pour suivre tes avancées
        - les ressources pédagogiques disponibles dans ton espace client
        - notre accompagnement, si tu as la moindre question (via WhatsApp pour une réponse rapide)
        
        Nous nous reparlerons dans environ 3 mois pour faire le point et, si c'est pertinent, envisager la mise en place d'un autre investissement.
        
        Atlas s'inscrit dans une logique progressive : on avance étape par étape, au bon rythme.
        
        À bientôt,
        L'équipe Atlas
        """
        
        # Envoyer l'email
        success = mailer.send_email(
            to_email=user.email,
            to_name=f"{user.first_name} {user.last_name}",
            subject="🎯 Ton plan d'investissement est en place",
            html_content=email_html,
            text_content=email_text
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Email de suivi post-RDV envoyé avec succès à {user.email}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erreur lors de l\'envoi de l\'email'
            })
            
    except Exception as e:
        print(f"Erreur envoi email post-RDV: {e}")
        return jsonify({
            'success': False,
            'message': f'Erreur lors de l\'envoi: {str(e)}'
        }), 500


@platform_admin_bp.route('/utilisateur/<int:user_id>/envoyer-email-generique-suivi', methods=['POST'])
@login_required
def send_generic_follow_up_email(user_id):
    """
    Envoie un email de suivi générique après n'importe quel rendez-vous
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    # Récupérer l'utilisateur
    user = User.query.filter_by(id=user_id, is_admin=False).first()
    if not user:
        return jsonify({'success': False, 'message': 'Utilisateur introuvable'}), 404
    
    try:
        from app.services.email_service import MailerSendService
        
        # Récupérer l'API token depuis les variables d'environnement
        api_token = os.getenv('MAILERSEND_API_TOKEN')
        if not api_token:
            return jsonify({'success': False, 'message': 'Configuration email manquante'}), 500
        
        mailer = MailerSendService(api_token)
        
        # URL vers l'espace client principal
        dashboard_url = "https://atlas-invest.fr/plateforme/dashboard"
        
        # Contenu HTML de l'email générique de suivi avec couleurs Atlas
        email_html = f"""
<!doctype html>
<html lang="fr">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <meta name="x-apple-disable-message-reformatting" />
    <title>Atlas</title>
  </head>

  <body style="margin:0;padding:0;background:#f2f4f5;">
    <!-- Preheader (hidden) -->
    <div style="display:none;max-height:0;overflow:hidden;opacity:0;color:transparent;">
      Votre accompagnement Atlas se poursuit.
    </div>

    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#f2f4f5;">
      <tr>
        <td align="center" style="padding:28px 16px;">
          <!-- Container -->
          <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="640" style="width:640px;max-width:640px;background:#ffffff;border-radius:18px;overflow:hidden;">

            <!-- Header -->
            <tr>
              <td align="center" style="background:#268190;padding:18px 20px;">
                <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:22px;line-height:26px;font-weight:700;color:#ffffff;">
                  Atlas
                </div>
              </td>
            </tr>

            <!-- Body -->
            <tr>
              <td style="padding:28px 26px 10px 26px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:14px;line-height:1.6;color:#111827;">

                <p style="margin:0 0 14px 0;">Bonjour {user.first_name},</p>

                <p style="margin:0 0 14px 0;">
                  Merci pour notre échange et pour <strong>la confiance que vous accordez à Atlas</strong>.
                </p>

                <p style="margin:0 0 14px 0;">
                  👉 Votre accompagnement Atlas se poursuit, vous pouvez consulter à tout moment votre <strong>espace client</strong> pour :
                </p>

                <ul style="margin:0 0 18px 18px;padding:0;">
                  <li style="margin:0 0 8px 0;">suivre l'évolution de <strong>votre patrimoine</strong></li>
                  <li style="margin:0 0 8px 0;">consulter votre <strong>plan d'investissement</strong></li>
                  <li style="margin:0 0 8px 0;">accéder aux <strong>ressources pédagogiques</strong></li>
                </ul>

                <!-- CTA -->
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:18px 0 22px 0;">
                  <tr>
                    <td align="center">
                      <a href="{dashboard_url}" target="_blank"
                        style="display:inline-block;background:#268190;color:#ffffff;text-decoration:none;font-weight:700;
                               padding:14px 22px;border-radius:12px;font-size:14px;">
                        👉 Accéder à mon espace Atlas
                      </a>
                    </td>
                  </tr>
                </table>

                <p style="margin:0 0 14px 0;">
                  Si vous avez la moindre question ou si vous souhaitez ajuster un point de votre stratégie, nous restons à votre disposition.
                </p>

                <p style="margin:0;">
                  À très bientôt,<br />
                  <strong>L'équipe Atlas</strong>
                </p>

              </td>
            </tr>

            <!-- Signature / Footer band -->
            <tr>
              <td style="padding:10px 34px 30px 34px;">
                <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
                  <tr>
                    <td style="padding:10px 0 6px 0;">
                      <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:16px;line-height:22px;">
                        <a href="https://atlas-invest.fr" style="color:#3f7f88;text-decoration:underline;">https://atlas-invest.fr</a>
                      </div>
                    </td>
                  </tr>

                  <tr>
                    <td style="padding-top:10px;">
                      <img src="https://atlas-invest.fr/static/img/logo-atlas.png" alt="Atlas" style="height:32px;width:auto;vertical-align:middle;margin-right:12px;">
                      <span style="display:inline-block;background:#3f7f88;color:#ffffff;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:14px;line-height:18px;font-weight:700;padding:10px 14px;border-radius:10px;vertical-align:middle;">
                        Atlas – le conseil financier clair et indépendant
                      </span>
                    </td>
                  </tr>

                  <tr>
                    <td style="padding-top:22px;">
                      <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;font-size:12px;line-height:18px;color:#8a8a8a;">
                        Cet email a été envoyé automatiquement, merci de ne pas y répondre.
                      </div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
          <!-- /Container -->
        </td>
      </tr>
    </table>
  </body>
</html>
        """
        
        # Version texte
        email_text = f"""
        Bonjour {user.first_name},

        Merci pour notre échange et pour la confiance que vous accordez à Atlas.

        Votre accompagnement Atlas se poursuit, vous pouvez consulter à tout moment votre espace client pour :
        - suivre l'évolution de votre patrimoine
        - consulter votre plan d'investissement
        - accéder aux ressources pédagogiques

        Lien vers votre espace Atlas : {dashboard_url}

        Si vous avez la moindre question ou si vous souhaitez ajuster un point de votre stratégie, nous restons à votre disposition.

        À très bientôt,
        L'équipe Atlas
        """

        # Envoyer l'email
        success = mailer.send_email(
            to_email=user.email,
            to_name=f"{user.first_name} {user.last_name}",
            subject="Suite à notre échange – votre accompagnement Atlas",
            html_content=email_html,
            text_content=email_text
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Email de suivi générique envoyé avec succès à {user.email}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erreur lors de l\'envoi de l\'email'
            })
            
    except Exception as e:
        print(f"Erreur envoi email générique: {e}")
        return jsonify({
            'success': False,
            'message': f'Erreur lors de l\'envoi: {str(e)}'
        }), 500


@platform_admin_bp.route('/utilisateur/<int:user_id>/compte-rendu', methods=['POST'])
@login_required
def create_compte_rendu(user_id):
    """
    Créer un compte rendu de rendez-vous
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    # Récupérer l'utilisateur
    user = User.query.filter_by(id=user_id, is_admin=False).first()
    if not user:
        return jsonify({'success': False, 'message': 'Utilisateur introuvable'}), 404
    
    try:
        data = request.get_json()
        date_rdv_str = data.get('date_rdv')
        titre = data.get('titre', '').strip()
        type_rdv = data.get('type_rdv', '').strip()
        prochaine_action = data.get('prochaine_action', '').strip()
        contenu = data.get('contenu', '').strip()

        if not date_rdv_str:
            return jsonify({'success': False, 'message': 'Date du rendez-vous requise'}), 400

        if not contenu:
            return jsonify({'success': False, 'message': 'Contenu du compte rendu requis'}), 400

        # Convertir la date
        from datetime import datetime
        try:
            date_rdv = datetime.strptime(date_rdv_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': 'Format de date invalide'}), 400

        # Créer le compte rendu
        compte_rendu = CompteRendu(
            user_id=user_id,
            titre=titre if titre else None,
            date_rdv=date_rdv,
            type_rdv=type_rdv if type_rdv else None,
            prochaine_action=prochaine_action if prochaine_action else None,
            contenu=contenu
        )
        
        db.session.add(compte_rendu)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Compte rendu créé avec succès',
            'compte_rendu': compte_rendu.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Erreur création compte rendu: {e}")
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la création: {str(e)}'
        }), 500


@platform_admin_bp.route('/compte-rendu/<int:compte_rendu_id>')
@login_required
def get_compte_rendu(compte_rendu_id):
    """
    Récupérer un compte rendu complet
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403

    compte_rendu = CompteRendu.query.get_or_404(compte_rendu_id)

    return jsonify({
        'success': True,
        'compte_rendu': compte_rendu.to_dict()
    })


@platform_admin_bp.route('/compte-rendu/<int:compte_rendu_id>/update', methods=['PUT'])
@login_required
def update_compte_rendu(compte_rendu_id):
    """
    Mettre à jour un compte rendu
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403

    compte_rendu = CompteRendu.query.get_or_404(compte_rendu_id)

    try:
        data = request.get_json()

        # Mise à jour des champs
        if 'date_rdv' in data:
            date_rdv_str = data.get('date_rdv')
            if date_rdv_str:
                from datetime import datetime
                try:
                    compte_rendu.date_rdv = datetime.strptime(date_rdv_str, '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'success': False, 'message': 'Format de date invalide'}), 400

        if 'titre' in data:
            compte_rendu.titre = data.get('titre', '').strip() or None

        if 'type_rdv' in data:
            compte_rendu.type_rdv = data.get('type_rdv', '').strip() or None

        if 'prochaine_action' in data:
            compte_rendu.prochaine_action = data.get('prochaine_action', '').strip() or None

        if 'contenu' in data:
            contenu = data.get('contenu', '').strip()
            if not contenu:
                return jsonify({'success': False, 'message': 'Contenu du compte rendu requis'}), 400
            compte_rendu.contenu = contenu

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Compte rendu mis à jour avec succès',
            'compte_rendu': compte_rendu.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        print(f"Erreur mise à jour compte rendu: {e}")
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la mise à jour: {str(e)}'
        }), 500


@platform_admin_bp.route('/compte-rendu/<int:compte_rendu_id>/delete', methods=['DELETE'])
@login_required
def delete_compte_rendu(compte_rendu_id):
    """
    Supprimer un compte rendu
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403

    compte_rendu = CompteRendu.query.get_or_404(compte_rendu_id)

    try:
        db.session.delete(compte_rendu)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Compte rendu supprimé avec succès'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Erreur suppression compte rendu: {e}")
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la suppression: {str(e)}'
        }), 500