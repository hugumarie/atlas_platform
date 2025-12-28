"""
Routes pour l'interface investisseur de la plateforme.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, make_response, send_file
from flask_login import login_required, current_user
from app import db
from app.models.investor_profile import InvestorProfile
from app.models.portfolio import Portfolio
from app.models.subscription import Subscription, SubscriptionTier
from app.models.payment_method import PaymentMethod
from app.models.apprentissage import Apprentissage
from app.models.investment_plan import InvestmentPlan, InvestmentPlanLine, AVAILABLE_ENVELOPES
import json
import re
from datetime import datetime, timedelta
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.units import mm
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io

platform_investor_bp = Blueprint('platform_investor', __name__, url_prefix='/plateforme')

@platform_investor_bp.route('/dashboard')
@login_required  
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('platform_admin.dashboard'))
    
    if not current_user.subscription or not current_user.subscription.is_active():
        return redirect(url_for('platform_auth.login'))
    
    if not current_user.investor_profile:
        return redirect(url_for('platform_investor.questionnaire'))
    
    # LECTURE PURE DE LA BASE DE DONNÉES - AUCUN CALCUL
    profile = current_user.investor_profile
    patrimoine_total_net = profile.calculated_patrimoine_total_net
    total_immobilier_net = profile.calculated_total_immobilier_net
    
    patrimoine_repartition = {
        'liquidites': profile.calculated_total_liquidites or 0,
        'placements': profile.calculated_total_placements or 0, 
        'immobilier': profile.calculated_total_immobilier_net or 0,
        'crypto': profile.calculated_total_cryptomonnaies or 0,
        'autres_biens': profile.calculated_total_autres_biens or 0
    }

    investment_plan = InvestmentPlan.query.filter_by(user_id=current_user.id, is_active=True).first()
    
    return render_template('platform/investor/dashboard.html',
                         investment_plan=investment_plan,
                         patrimoine_repartition=patrimoine_repartition, 
                         patrimoine_total_net=patrimoine_total_net,
                         total_immobilier_net=total_immobilier_net)

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
    # Les admins peuvent aussi consulter les formations
    
    # Vérifier les permissions (admins exempts des vérifications d'abonnement)
    if not current_user.is_admin:
        if not current_user.subscription or not current_user.subscription.is_active():
            return redirect(url_for('platform_auth.login'))
        
        if not current_user.investor_profile:
            flash('Veuillez d\'abord compléter votre profil investisseur.', 'warning')
            return redirect(url_for('platform_investor.questionnaire'))
    
    # Récupérer les formations actives depuis la base de données
    apprentissages = Apprentissage.query.filter_by(actif=True).order_by(Apprentissage.ordre, Apprentissage.date_creation.desc()).all()
    
    return render_template('platform/investor/learning.html', apprentissages=apprentissages)

@platform_investor_bp.route('/api/crypto-prices')
@login_required
def get_crypto_prices():
    """API endpoint pour récupérer TOUS les prix crypto depuis la DB uniquement."""
    try:
        from app.models.crypto_price import CryptoPrice
        from datetime import datetime, timedelta
        
        # Récupérer TOUS les prix en base de données (peu importe l'âge)
        crypto_prices = CryptoPrice.query.all()
        
        # Utiliser UNIQUEMENT les prix en base de données, pas d'appel API
        # Les prix sont mis à jour uniquement au démarrage via start_atlas.sh
        print(f"📊 API crypto: {len(crypto_prices)} prix disponibles en base (tous)")
        
        # Convertir TOUS les prix en format compatible avec le frontend
        formatted_prices = {}
        
        for crypto_price in crypto_prices:
            symbol = crypto_price.symbol
            # Retourner tous les symboles, pas seulement un mapping limité
            formatted_prices[symbol] = {
                'eur': round(crypto_price.price_eur, 6),  # Plus de précision pour les petites cryptos
                'price': round(crypto_price.price_eur, 6),
                'symbol': symbol.upper(),
                'updated_at': crypto_price.updated_at.isoformat(),
                'age_minutes': int((datetime.utcnow() - crypto_price.updated_at).total_seconds() / 60)
            }
        
        print(f"✅ Retour de {len(formatted_prices)} prix crypto récents")
        return jsonify(formatted_prices)
        
    except Exception as e:
        print(f"❌ Erreur API crypto prices: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@platform_investor_bp.route('/api/crypto-price/<symbol>')
@login_required
def get_single_crypto_price(symbol):
    """API endpoint pour récupérer le prix d'une crypto spécifique depuis la DB Binance."""
    try:
        from app.services.binance_price_service import BinancePriceService
        
        # Récupérer le prix depuis la DB UNIQUEMENT, sans appel API
        price_eur = BinancePriceService.get_crypto_price_from_db(symbol.lower(), max_age_minutes=1440)  # 24h max
        
        if price_eur is not None:
            return jsonify({
                'success': True,
                'symbol': symbol,
                'price': round(price_eur, 6),
                'currency': 'EUR',
                'source': 'binance_db'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Prix indisponible pour {symbol}'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Erreur serveur'
        }), 500

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
    
    # Recalcul complet des totaux patrimoniaux avec PatrimonyCalculationEngine V2.0
    try:
        from app.services.patrimony_calculation_engine import PatrimonyCalculationEngine
        PatrimonyCalculationEngine.calculate_and_save_all(current_user.investor_profile, force_recalculate=True, save_to_db=True)
        db.session.refresh(current_user.investor_profile)
        db.session.refresh(current_user)
    except Exception as calc_error:
        pass  # En cas d'erreur, on continue sans bloquer l'affichage
    
    # Calcul des valeurs nettes par bien immobilier avec CreditCalculationService
    immobilier_with_calculations = []
    if current_user.investor_profile.immobilier_data:
        from app.services.credit_calculation import CreditCalculationService
        from datetime import datetime, date
        
        for bien in current_user.investor_profile.immobilier_data:
            bien_copy = dict(bien)
            
            # Calculs précis si le bien a un crédit (détection basée sur le montant)
            if bien.get('credit_montant', 0) > 0:
                montant_initial = float(bien.get('credit_montant', 0))
                taux_interet = float(bien.get('credit_taeg', 2.5))
                duree_annees = int(bien.get('credit_duree', 25))
                duree_mois = duree_annees * 12
                
                # Parse de la date de début
                date_debut_str = bien.get('credit_date', '')
                try:
                    if date_debut_str:
                        if '-' in date_debut_str and len(date_debut_str) >= 7:
                            date_debut = datetime.strptime(date_debut_str[:7] + '-01', '%Y-%m-%d').date()
                        else:
                            date_debut = date.today()
                    else:
                        date_debut = date.today()
                except (ValueError, TypeError):
                    date_debut = date.today()
                
                # Calculs précis avec CreditCalculationService
                mensualite = CreditCalculationService.calculate_monthly_payment(
                    principal=montant_initial,
                    annual_rate=taux_interet,
                    duration_months=duree_mois
                )
                
                # 🔧 CALCULS AVEC VRAIES FORMULES D'AMORTISSEMENT
                credit_details = CreditCalculationService.calculate_credit_details(
                    principal=montant_initial,
                    annual_rate=taux_interet,
                    duration_months=duree_mois,
                    start_date=date_debut,
                    current_date=date.today()
                )
                
                capital_restant = credit_details['remaining_capital']
                capital_rembourse = credit_details['capital_repaid']
                cout_global = credit_details['total_cost']
                
                valeur_nette = bien.get('valeur', 0) - capital_restant
                
                # Ajouter les calculs au bien avec vraies formules
                bien_copy['calculated_mensualite'] = round(mensualite, 0)
                bien_copy['calculated_capital_restant'] = round(capital_restant, 0)
                bien_copy['calculated_capital_rembourse'] = round(capital_rembourse, 0)
                bien_copy['calculated_cout_global'] = round(cout_global, 0)
                bien_copy['calculated_valeur_nette'] = round(valeur_nette, 0)
                bien_copy['calculated_with_real_formulas'] = True
            else:
                # Pas de crédit = valeur nette = valeur totale
                bien_copy['calculated_mensualite'] = 0
                bien_copy['calculated_capital_restant'] = 0
                bien_copy['calculated_valeur_nette'] = bien.get('valeur', 0)
            
            immobilier_with_calculations.append(bien_copy)
    
    return render_template('platform/investor/investor_data.html', 
                         edit_mode=edit_mode,
                         immobilier_with_calculations=immobilier_with_calculations)

@platform_investor_bp.route('/donnees-investisseur/modifier', methods=['POST'])
@login_required
def update_investor_data():
    """
    Mise à jour complète des données investisseur - COPIE EXACTE de la logique admin.
    """
    print(f"🚀 START UPDATE_INVESTOR_DATA - User: {current_user.id}")
    if current_user.is_admin:
        return redirect(url_for('platform_admin.dashboard'))
    
    if not current_user.subscription or not current_user.subscription.is_active():
        return redirect(url_for('platform_auth.login'))
    
    if not current_user.investor_profile:
        flash('Profil investisseur introuvable.', 'error')
        return redirect(url_for('platform_investor.questionnaire'))
    
    try:
        # Récupération des données du formulaire HTML - COPIE EXACTE ADMIN
        user = current_user
        profile = user.investor_profile
        
        # Mise à jour des informations personnelles
        user.first_name = request.form.get('first_name', '').strip()
        user.last_name = request.form.get('last_name', '').strip()
        
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
            
        # Traitement des revenus complémentaires
        income_names = request.form.getlist('revenu_complementaire_name[]')
        income_amounts = request.form.getlist('revenu_complementaire_amount[]')
        
        complementary_incomes = []
        for name, amount in zip(income_names, income_amounts):
            if name and name.strip() and amount and amount.strip():
                try:
                    amount_float = float(amount.strip())
                    if amount_float >= 0:
                        complementary_incomes.append({
                            'name': name.strip(),
                            'amount': amount_float
                        })
                except ValueError:
                    continue
        
        profile.set_revenus_complementaires_data(complementary_incomes)
        total_complementaires = sum(income['amount'] for income in complementary_incomes)
        profile.revenus_complementaires = total_complementaires
        
        # Traitement des charges mensuelles
        charge_names = request.form.getlist('charge_mensuelle_name[]')
        charge_amounts = request.form.getlist('charge_mensuelle_amount[]')
        
        monthly_charges = []
        for name, amount in zip(charge_names, charge_amounts):
            if name and name.strip() and amount and amount.strip():
                try:
                    amount_float = float(amount.strip())
                    if amount_float >= 0:
                        monthly_charges.append({
                            'name': name.strip(),
                            'amount': amount_float
                        })
                except ValueError:
                    continue
        
        profile.set_charges_mensuelles_data(monthly_charges)
        total_charges = sum(charge['amount'] for charge in monthly_charges)
        profile.charges_mensuelles = total_charges
        
        # Traitement des liquidités personnalisées
        liquidite_names = request.form.getlist('liquidite_personnalisee_name[]')
        liquidite_amounts = request.form.getlist('liquidite_personnalisee_amount[]')
        
        print(f"🔍 DEBUG liquidités personnalisées:")
        print(f"  - liquidite_names: {liquidite_names}")
        print(f"  - liquidite_amounts: {liquidite_amounts}")
        
        liquidites_personnalisees = []
        for name, amount in zip(liquidite_names, liquidite_amounts):
            print(f"  - Traitement: {name} = {amount}")
            if name and name.strip() and amount and amount.strip():
                try:
                    amount_float = float(amount.strip())
                    if amount_float > 0:
                        liquidites_personnalisees.append({
                            'name': name.strip(),
                            'amount': amount_float
                        })
                        print(f"  ✅ Ajouté: {name.strip()} = {amount_float}€")
                except ValueError:
                    print(f"  ❌ Erreur conversion: {amount}")
                    continue
        
        print(f"  📋 liquidites_personnalisees final: {liquidites_personnalisees}")
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
            
        # PEL/CEL
        try:
            profile.pel_cel_value = float(request.form.get('pel_cel_value', 0) or 0)
        except ValueError:
            profile.pel_cel_value = 0.0
        profile.has_pel_cel = profile.pel_cel_value > 0
            
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
        
        # SCPI
        try:
            profile.scpi_value = float(request.form.get('scpi_value', 0) or 0)
        except ValueError:
            profile.scpi_value = 0.0
        profile.has_scpi = profile.scpi_value > 0
        
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
        profile.risk_tolerance = profile.profil_risque_choisi or 'modéré'
        
        # Valeurs par défaut pour éviter NOT NULL constraint
        # investment_experience et experience_investissement sont le même champ - suppression de la duplication
        profile.investment_horizon = request.form.get('horizon_placement', '').strip() or 'moyen'
        
        # MAPPER EXPERIENCE EN PREMIER (avant calculs de risque)
        # Valeurs exactes autorisées par contrainte: débutant, débutante, intermédiaire, intermediaire, confirmé, confirmée, expert, experte
        experience_form = request.form.get('experience_investissement', '').strip()
        print(f"🔍 FORM VALUE: '{experience_form}'")
        
        if experience_form == 'debutant':
            mapped_value = 'débutant'  # Utiliser valeur avec accent
        elif experience_form == 'intermediaire':
            mapped_value = 'intermédiaire'  # Utiliser valeur avec accent
        elif experience_form == 'confirme':
            mapped_value = 'confirmé'  # Utiliser valeur avec accent
        else:
            mapped_value = 'intermédiaire'  # Défaut sûr
        
        profile.experience_investissement = mapped_value
        profile.investment_experience = mapped_value
        print(f"🔍 MAPPED TO: '{mapped_value}'")
        print(f"🔍 PROFILE FIELDS: exp_invest='{profile.experience_investissement}', invest_exp='{profile.investment_experience}'")
        
        # Section 6: QUESTIONNAIRE DE RISQUE DÉTAILLÉ
        profile.tolerance_risque = request.form.get('tolerance_baisse', '').strip() or 'moderee'
        profile.horizon_placement = request.form.get('horizon_placement', '').strip() or 'moyen'  
        profile.besoin_liquidite = request.form.get('besoin_liquidite', '').strip() or 'non'
        profile.attitude_volatilite = request.form.get('attitude_volatilite', '').strip() or 'attendre'
        
        # CALCUL DU PROFIL DE RISQUE AUTOMATIQUE
        try:
            from app.services.risk_profile_calculator import RiskProfileCalculator
            
            # Collecte des réponses au questionnaire
            risk_responses = {
                'baisse_acceptable': profile.tolerance_risque,
                'horizon_placement': profile.horizon_placement,
                'besoin_liquidite': profile.besoin_liquidite, 
                'experience_marches': profile.experience_investissement,
                'attitude_volatilite': profile.attitude_volatilite
            }
            
            # Calcul du profil de risque
            risk_calculation = RiskProfileCalculator.calculate_profile(risk_responses)
            profile.risk_tolerance = risk_calculation['profile']
            
        except Exception as risk_calc_error:
            # En cas d'erreur, garder la valeur par défaut
            profile.risk_tolerance = 'modéré'
        
        # Nouveaux objectifs d'investissement étendus
        profile.objectif_premiers_pas = request.form.get('objectif_premiers_pas') == 'true'
        profile.objectif_constituer_capital = request.form.get('objectif_constituer_capital') == 'true'
        profile.objectif_diversifier = request.form.get('objectif_diversifier') == 'true'
        profile.objectif_optimiser_rendement = request.form.get('objectif_optimiser_rendement') == 'true'
        profile.objectif_preparer_retraite = request.form.get('objectif_preparer_retraite') == 'true'
        profile.objectif_securite_financiere = request.form.get('objectif_securite_financiere') == 'true'
        profile.objectif_projet_immobilier = request.form.get('objectif_projet_immobilier') == 'true'
        profile.objectif_revenus_complementaires = request.form.get('objectif_revenus_complementaires') == 'true'
        profile.objectif_transmettre_capital = request.form.get('objectif_transmettre_capital') == 'true'
        profile.objectif_proteger_famille = request.form.get('objectif_proteger_famille') == 'true'
        
        # Traitement des données complexes JSONB - IMMOBILIER
        immobilier_data = []
        bien_types = request.form.getlist('bien_type[]')
        bien_descriptions = request.form.getlist('bien_description[]')
        bien_valeurs = request.form.getlist('bien_valeur[]')
        bien_surfaces = request.form.getlist('bien_surface[]')
        # Les checkboxes cochées sont envoyées avec leur valeur, les non-cochées ne sont pas envoyées
        # Nous devons utiliser une approche différente pour identifier quels biens ont des crédits
        
        # Récupérer toutes les données des formulaires
        credit_montants = request.form.getlist('credit_montant[]')
        credit_taegs = request.form.getlist('credit_taeg[]')
        credit_durees = request.form.getlist('credit_duree[]')
        credit_dates = request.form.getlist('credit_date[]')
        
        print(f"🏠 Bien types: {bien_types}")
        print(f"🏠 Credit montants: {credit_montants}")
        print(f"🏠 Credit taegs: {credit_taegs}")
        print(f"🏠 Credit durees: {credit_durees}")
        
        for i in range(len(bien_types)):
            if bien_types[i].strip():
                # Détecter si un bien a un crédit en regardant si les champs crédit ont des valeurs
                credit_montant = float(credit_montants[i] or 0) if i < len(credit_montants) else 0
                credit_taeg = float(credit_taegs[i] or 0) if i < len(credit_taegs) else 0
                credit_duree = int(credit_durees[i] or 0) if i < len(credit_durees) else 0
                credit_date = credit_dates[i].strip() if i < len(credit_dates) else ''
                
                # Un bien a un crédit si au moins le montant est > 0
                has_credit = credit_montant > 0
                
                bien_data = {
                    'type': bien_types[i].strip(),
                    'description': bien_descriptions[i].strip() if i < len(bien_descriptions) else '',
                    'valeur': float(bien_valeurs[i] or 0) if i < len(bien_valeurs) else 0,
                    'surface': float(bien_surfaces[i] or 0) if i < len(bien_surfaces) else 0,
                    'has_credit': has_credit,
                    'credit_montant': credit_montant,
                    'credit_taeg': credit_taeg,
                    'credit_duree': credit_duree,
                    'credit_date': credit_date
                }
                
                print(f"🏠 Bien {i}: {bien_data['type']}, has_credit={has_credit}, montant={credit_montant}€, taeg={credit_taeg}%")
                immobilier_data.append(bien_data)
        
        profile.set_immobilier_data(immobilier_data)
        
        # Calcul des totaux immobilier et mise à jour des champs de résumé
        total_immobilier_value = sum(bien.get('valeur', 0) for bien in immobilier_data)
        profile.immobilier_value = total_immobilier_value
        profile.has_immobilier = total_immobilier_value > 0
        profile.has_real_estate = profile.has_immobilier
        profile.real_estate_value = profile.immobilier_value
        
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
        autre_bien_valeurs = request.form.getlist('autre_bien_valeur[]')
        
        print(f"🔍 DEBUG autres_biens - names: {autre_bien_names}")
        print(f"🔍 DEBUG autres_biens - valeurs: {autre_bien_valeurs}")
        
        for i in range(len(autre_bien_names)):
            if autre_bien_names[i].strip():
                valeur = float(autre_bien_valeurs[i] or 0) if i < len(autre_bien_valeurs) else 0
                autres_biens_data.append({
                    'name': autre_bien_names[i].strip(),
                    'valeur': valeur
                })
                print(f"✅ Autre bien ajouté: {autre_bien_names[i]} = {valeur}€")
        
        profile.set_autres_biens_data(autres_biens_data)
        
        # Crédits détaillés
        credits_data = []
        credit_ids = request.form.getlist('credit_conso_id[]')
        credit_descriptions = request.form.getlist('credit_conso_description[]')
        credit_montants_initiaux = request.form.getlist('credit_conso_montant_initial[]')
        credit_montants_restants = request.form.getlist('credit_conso_montant_restant[]')
        credit_mensualites = request.form.getlist('credit_conso_mensualite[]')
        credit_taux = request.form.getlist('credit_conso_taux[]')
        credit_durees_credit = request.form.getlist('credit_conso_duree[]')
        credit_dates_depart = request.form.getlist('credit_conso_date_depart[]')
        
        arrays = [credit_ids, credit_descriptions, credit_montants_initiaux, credit_montants_restants, credit_mensualites, credit_taux, credit_durees_credit, credit_dates_depart]
        max_length = max(len(arr) for arr in arrays) if any(arrays) else 0
        existing_credits = profile.credits_data.copy() if profile.credits_data else []
        
        for i in range(max_length):
            description = credit_descriptions[i].strip() if i < len(credit_descriptions) else ''
            
            if description:
                credit_id = credit_ids[i] if i < len(credit_ids) else str(i)
                
                montant_initial = float(credit_montants_initiaux[i] or 0) if i < len(credit_montants_initiaux) else 0
                taux = float(credit_taux[i] or 0) if i < len(credit_taux) else 0
                duree = int(credit_durees_credit[i] or 0) if i < len(credit_durees_credit) else 0
                mensualite = float(credit_mensualites[i] or 0) if i < len(credit_mensualites) else 0
                date_depart = credit_dates_depart[i].strip() if i < len(credit_dates_depart) else ''
                
                # Calcul du montant restant avec la formule simplifiée si pas déjà renseigné
                montant_restant = float(credit_montants_restants[i] or 0) if i < len(credit_montants_restants) else 0
                
                # Variables pour les nouvelles données calculées
                credit_details = None
                capital_rembourse = 0
                cout_global = 0
                
                # 🔧 DEBUG : Vérifier pourquoi les calculs ne se déclenchent pas
                print(f"🔍 DEBUG crédit {description}:")
                print(f"   - montant_initial: {montant_initial}")
                print(f"   - taux: {taux}")
                print(f"   - duree: {duree}")
                print(f"   - date_depart: '{date_depart}'")
                
                # 🔧 FORCER LE RECALCUL AVEC VRAIES FORMULES POUR TOUS LES CRÉDITS  
                if montant_initial > 0 and taux > 0 and duree > 0 and date_depart:
                    try:
                        from datetime import datetime, date
                        from app.services.credit_calculation import CreditCalculationService
                        
                        # Parse de la date de début
                        if '-' in date_depart and len(date_depart) >= 7:
                            start_date = datetime.strptime(date_depart[:7] + '-01', '%Y-%m-%d').date()
                        else:
                            start_date = date.today()
                        
                        # 🔧 VRAIES FORMULES D'AMORTISSEMENT (comme pour l'immobilier)
                        duree_mois = duree * 12
                        
                        # Calculer les détails complets du crédit
                        credit_details = CreditCalculationService.calculate_credit_details(
                            montant_initial, taux, duree_mois, start_date
                        )
                        
                        # Utiliser les valeurs calculées avec les vraies formules
                        montant_restant = credit_details['remaining_capital']
                        capital_rembourse = credit_details['capital_repaid'] 
                        mensualite_calculee = credit_details['monthly_payment']
                        cout_global = credit_details['total_cost']
                        
                        # Mettre à jour la mensualité si elle n'était pas correcte
                        if abs(mensualite - mensualite_calculee) > 0.1:
                            mensualite = mensualite_calculee
                            
                        print(f"🚗 Crédit {description}: Capital restant CORRIGÉ {montant_restant:.0f}€ (formule d'amortissement)")
                        print(f"   → Capital remboursé: {capital_rembourse:.0f}€")
                        print(f"   → Coût global: {cout_global:.0f}€")
                        
                    except Exception as calc_error:
                        print(f"⚠️ Erreur calcul montant restant crédit {description}: {calc_error}")
                        montant_restant = montant_initial
                
                new_credit = {
                    'id': credit_id,
                    'description': description,
                    'montant_initial': montant_initial,
                    'montant_restant': montant_restant,
                    'mensualite': mensualite,
                    'taux': taux,
                    'duree': duree,
                    'date_depart': date_depart
                }
                
                # Ajouter les nouvelles données calculées si disponibles
                if credit_details and montant_initial > 0:
                    new_credit.update({
                        'capital_restant': credit_details['remaining_capital'],
                        'capital_rembourse': credit_details['capital_repaid'],
                        'cout_global': credit_details['total_cost'],
                        'calculated_with_real_formulas': True
                    })
                credits_data.append(new_credit)
        
        profile.credits_data_json = credits_data
        
        # ============ RECALCUL DES VALEURS NETTES APRÈS SAUVEGARDE ============
        # Recalculer les valeurs nettes des biens immobiliers avec les nouvelles données
        if current_user.investor_profile.immobilier_data:
            from app.services.credit_calculation import CreditCalculationService
            from datetime import datetime, date
            
            immobilier_updated = []
            for bien in current_user.investor_profile.immobilier_data:
                bien_copy = dict(bien)
                
                # Recalculer la valeur nette avec les données fraîches
                if bien.get('credit_montant', 0) > 0:
                    montant_initial = float(bien.get('credit_montant', 0))
                    taux_interet = float(bien.get('credit_taeg', 2.5))
                    duree_annees = int(bien.get('credit_duree', 25))
                    duree_mois = duree_annees * 12
                    
                    # Parse de la date de début
                    date_debut_str = bien.get('credit_date', '')
                    try:
                        if date_debut_str and '-' in date_debut_str and len(date_debut_str) >= 7:
                            date_debut = datetime.strptime(date_debut_str[:7] + '-01', '%Y-%m-%d').date()
                        else:
                            date_debut = date.today()
                    except (ValueError, TypeError):
                        date_debut = date.today()
                    
                    # 🔧 CALCULS PRÉCIS AVEC VRAIES FORMULES D'AMORTISSEMENT
                    credit_details = CreditCalculationService.calculate_credit_details(
                        principal=montant_initial,
                        annual_rate=taux_interet,
                        duration_months=duree_mois,
                        start_date=date_debut,
                        current_date=date.today()
                    )
                    
                    capital_restant = credit_details['remaining_capital']
                    capital_rembourse = credit_details['capital_repaid']
                    mensualite_calculee = credit_details['monthly_payment']
                    cout_global = credit_details['total_cost']
                    
                    valeur_nette = bien.get('valeur', 0) - capital_restant
                    bien_copy['calculated_valeur_nette'] = round(valeur_nette, 0)
                    
                    # Sauvegarder toutes les nouvelles données calculées
                    bien_copy['calculated_capital_restant'] = round(capital_restant, 0)
                    bien_copy['calculated_capital_rembourse'] = round(capital_rembourse, 0) 
                    bien_copy['calculated_mensualite'] = round(mensualite_calculee, 0)
                    bien_copy['calculated_cout_global'] = round(cout_global, 0)
                    bien_copy['calculated_with_real_formulas'] = True
                    
                    print(f"🏠 CORRIGÉ bien {bien.get('type', 'N/A')}: valeur={bien.get('valeur', 0)}€, capital_restant={capital_restant:.0f}€ (vraie formule), valeur_nette={valeur_nette:.0f}€")
                    print(f"   → Capital remboursé: {capital_rembourse:.0f}€, Mensualité: {mensualite_calculee:.0f}€, Coût global: {cout_global:.0f}€")
                else:
                    bien_copy['calculated_valeur_nette'] = bien.get('valeur', 0)
                    print(f"🏠 Bien sans crédit {bien.get('type', 'N/A')}: valeur_nette={bien.get('valeur', 0)}€")
                
                immobilier_updated.append(bien_copy)
            
            # Sauvegarder les valeurs recalculées
            profile.set_immobilier_data(immobilier_updated)
            print(f"✅ Recalcul terminé pour {len(immobilier_updated)} biens immobiliers")

        # Mise à jour du portefeuille
        if current_user.portfolio:
            current_user.portfolio.update_from_profile()
        
        # Récupérer les totaux calculés par JavaScript si disponibles
        js_total_actifs = request.form.get('calculated_total_actifs_js')
        js_patrimoine_net = request.form.get('calculated_patrimoine_net_js')
        js_total_dettes = request.form.get('calculated_total_dettes_js')
        
        print(f"🔍 DEBUG Champs cachés reçus du formulaire:")
        print(f"  - js_total_actifs: {js_total_actifs}")
        print(f"  - js_patrimoine_net: {js_patrimoine_net}")
        print(f"  - js_total_dettes: {js_total_dettes}")
        
        if js_total_actifs and js_patrimoine_net and js_total_dettes:
            print(f"🎯 Utilisation des totaux calculés par JavaScript:")
            print(f"  - Total Actifs JS: {js_total_actifs}€")
            print(f"  - Patrimoine Net JS: {js_patrimoine_net}€")
            print(f"  - Total Dettes JS: {js_total_dettes}€")
            
            # D'abord calculer les totaux individuels avec le service
            from app.services.patrimoine_calculation import PatrimoineCalculationService
            totaux = PatrimoineCalculationService.calculate_all_totaux(profile, save_to_db=False)
            
            # Puis écraser avec les totaux JS qui sont corrects (incluent les cryptos)
            profile.calculated_total_liquidites = totaux['total_liquidites']
            profile.calculated_total_placements = totaux['total_placements']
            profile.calculated_total_autres_biens = totaux['total_autres_biens']
            profile.calculated_total_immobilier_net = totaux['total_immobilier_net']
            profile.calculated_total_cryptomonnaies = totaux['total_cryptomonnaies']
            profile.calculated_total_actifs = float(js_total_actifs)
            profile.calculated_patrimoine_total_net = float(js_patrimoine_net)
            profile.calculated_total_credits_consommation = float(js_total_dettes)
            
        else:
            # Seulement si pas de valeurs JS, utiliser le service de calcul
            print(f"🧮 Pas de totaux JS, calcul via PatrimoineCalculationService...")
            from app.services.patrimoine_calculation import PatrimoineCalculationService
            from datetime import datetime
            totaux = PatrimoineCalculationService.calculate_all_totaux(profile, save_to_db=True)
        
        # FORCER LA SAUVEGARDE DES BONNES VALEURS EN BASE
        if 'totaux' in locals():
            print(f"🔧 FORÇAGE des bonnes valeurs en base:")
            profile.calculated_total_liquidites = totaux['total_liquidites']
            profile.calculated_total_placements = totaux['total_placements'] 
            profile.calculated_total_immobilier_net = totaux['total_immobilier_net']
            profile.calculated_total_autres_biens = totaux['total_autres_biens']
            profile.calculated_total_cryptomonnaies = totaux['total_cryptomonnaies']
            profile.calculated_total_actifs = totaux['total_actifs']
            profile.calculated_total_credits_consommation = totaux['total_credits_consommation']
            profile.calculated_patrimoine_total_net = totaux['patrimoine_total_net']
            print(f"  ✅ Total Liquidités: {totaux['total_liquidites']}€ → SAUVÉ")
            print(f"  ✅ Total Placements: {totaux['total_placements']}€ → SAUVÉ") 
            print(f"  ✅ Total Autres Biens: {totaux['total_autres_biens']}€ → SAUVÉ")
            print(f"  ✅ Total Actifs: {totaux['total_actifs']}€ → SAUVÉ")
            print(f"  ✅ PATRIMOINE NET: {totaux['patrimoine_total_net']}€ → SAUVÉ")
        
        # Sauvegarder les totaux calculés en base
        profile.calculated_total_liquidites = totaux['total_liquidites']
        profile.calculated_total_placements = totaux['total_placements']
        profile.calculated_total_immobilier_net = totaux['total_immobilier_net']
        profile.calculated_total_autres_biens = totaux['total_autres_biens']
        profile.calculated_total_cryptomonnaies = totaux['total_cryptomonnaies']
        profile.calculated_total_credits_consommation = totaux['total_credits_consommation']
        profile.calculated_total_actifs = totaux['total_actifs']
        profile.calculated_patrimoine_total_net = totaux['patrimoine_total_net']
        profile.last_calculation_date = datetime.utcnow()
        
        db.session.commit()
        
        # 🔍 VÉRIFICATION FINALE - Relire les données depuis la base
        print(f"🔍 VÉRIFICATION FINALE après commit:")
        db.session.refresh(profile)
        print(f"  ✅ DB calculated_total_liquidites: {profile.calculated_total_liquidites}€")
        print(f"  ✅ DB calculated_total_placements: {profile.calculated_total_placements}€")
        print(f"  ✅ DB calculated_total_autres_biens: {profile.calculated_total_autres_biens}€")
        print(f"  ✅ DB calculated_total_actifs: {profile.calculated_total_actifs}€")
        print(f"  ✅ DB calculated_patrimoine_total_net: {profile.calculated_patrimoine_total_net}€")
        print(f"  ✅ DB calculated_total_credits_consommation: {profile.calculated_total_credits_consommation}€")
        print(f"🎯 SAUVEGARDE TERMINÉE - Redirection vers visualisation")
        
        flash('Vos données ont été mises à jour avec succès.', 'success')
        return redirect(url_for('platform_investor.investor_data'))
        
    except ValueError as e:
        flash('Veuillez vérifier les valeurs numériques saisies.', 'error')
        return redirect(url_for('platform_investor.investor_data', edit='true'))
    except Exception as e:
        db.session.rollback()
        print(f"🚨 ERREUR SAUVEGARDE PROFIL: {e}")
        print(f"🔍 DEBUG - AVANT COMMIT:")
        print(f"   experience_investissement: '{profile.experience_investissement}'")
        print(f"   investment_experience: '{profile.investment_experience}'")
        import traceback
        traceback.print_exc()
        flash(f'Erreur lors de la mise à jour: {str(e)}', 'error')
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
        # Appel à l'API OpenAI avec Coach Patrimoine - Version simple
        import requests
        from datetime import datetime
        import os
        import json
        
        # Utiliser la clé API depuis les variables d'environnement
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({'error': 'Configuration OpenAI manquante'}), 500
        
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
        
        # Appel direct à l'API OpenAI via requests
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-4o-mini',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message}
            ],
            'max_tokens': 800,
            'temperature': 0.7
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
        else:
            return jsonify({'error': f'Erreur API OpenAI: {response.status_code}'}), 500
        
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
    except Exception as e:
        # En cas d'erreur API, log pour debug mais message user-friendly en production
        import traceback
        error_details = str(e)
        print(f"🚨 Erreur chatbot: {error_details}")
        print(f"🚨 Traceback: {traceback.format_exc()}")
        
        # Message différent selon l'environnement
        flask_env = os.getenv('FLASK_ENV', 'development')
        if flask_env == 'development':
            error_message = f'Erreur technique: {error_details}'
        else:
            error_message = 'Désolé, je rencontre un problème technique. Veuillez réessayer dans quelques instants.'
        
        return jsonify({
            'response': error_message,
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
    """Fonctionnalité PDF temporairement désactivée pour déploiement"""
    flash('La génération de factures PDF est temporairement indisponible.', 'warning')
    return redirect(url_for('platform_investor.profile'))
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


# ==========================================
# ROUTES APPRENTISSAGE / FORMATIONS
# ==========================================

@platform_investor_bp.route('/formation/pdf/<int:id>')
@login_required
def learning_pdf(id):
    """
    Affichage sécurisé d'un PDF d'apprentissage avec lecteur intégré
    """
    # Les admins peuvent aussi consulter les formations
    
    # Vérifier les permissions (admins exempts des vérifications d'abonnement)
    if not current_user.is_admin:
        if not current_user.subscription or not current_user.subscription.is_active():
            flash('Accès non autorisé. Veuillez vous abonner pour accéder aux formations.', 'error')
            return redirect(url_for('platform_auth.login'))
        
        if not current_user.investor_profile:
            flash('Veuillez d\'abord compléter votre profil investisseur.', 'warning')
            return redirect(url_for('platform_investor.questionnaire'))
    
    # Récupérer la formation
    apprentissage = Apprentissage.query.filter_by(id=id, actif=True).first_or_404()
    
    if not apprentissage.fichier_pdf:
        flash('Aucun contenu PDF disponible pour cette formation.', 'error')
        if current_user.is_admin:
            return redirect(url_for('platform_admin.apprentissages'))
        return redirect(url_for('platform_investor.learning'))
    
    try:
        import os
        pdf_path = os.path.join('app', 'static', 'uploads', 'apprentissages', apprentissage.fichier_pdf)
        
        # Vérifier que le fichier existe
        if not os.path.exists(pdf_path):
            flash('Fichier de formation introuvable.', 'error')
            if current_user.is_admin:
                return redirect(url_for('platform_admin.apprentissages'))
            return redirect(url_for('platform_investor.learning'))
        
        # Utiliser le template approprié selon le type d'utilisateur (SÉCURITÉ)
        if current_user.is_admin:
            # Template admin pour maintenir le contexte administrateur
            return render_template('platform/admin/learning_pdf.html', 
                                 apprentissage=apprentissage,
                                 pdf_url=url_for('static', filename=f'uploads/apprentissages/{apprentissage.fichier_pdf}'))
        else:
            # Template utilisateur standard
            return render_template('platform/investor/learning_pdf.html', 
                                 apprentissage=apprentissage,
                                 pdf_url=url_for('static', filename=f'uploads/apprentissages/{apprentissage.fichier_pdf}'))
        
    except Exception as e:
        flash('Erreur lors de l\'accès à la formation.', 'error')
        if current_user.is_admin:
            return redirect(url_for('platform_admin.apprentissages'))
        return redirect(url_for('platform_investor.learning'))


@platform_investor_bp.route('/api/credit/calculate', methods=['POST'])
@login_required
def calculate_credit_api():
    """
    API endpoint pour calculer en temps réel les données d'un crédit - Version utilisateur.
    """
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
        
        # Utiliser le nouveau service de calcul complet
        if data.get('date_debut'):
            try:
                start_date = CreditCalculationService._parse_date(data['date_debut'])
                credit_details = CreditCalculationService.calculate_credit_details(
                    float(data['montant_initial']),
                    float(data['taux_interet']),
                    int(data['duree_mois']),
                    start_date
                )
            except Exception:
                # Fallback en cas d'erreur de parsing de date
                credit_details = {
                    'principal': float(data['montant_initial']),
                    'monthly_payment': monthly_payment,
                    'capital_repaid': 0,
                    'remaining_capital': float(data['montant_initial']),
                    'total_cost': 0,
                    'months_elapsed': 0,
                    'months_remaining': int(data['duree_mois']),
                    'percentage_repaid': 0
                }
        else:
            # Pas de date de début, crédit pas encore démarré
            credit_details = {
                'principal': float(data['montant_initial']),
                'monthly_payment': monthly_payment,
                'capital_repaid': 0,
                'remaining_capital': float(data['montant_initial']),
                'total_cost': float(data['montant_initial']) * int(data['duree_mois']) / 100 * float(data['taux_interet']),
                'months_elapsed': 0,
                'months_remaining': int(data['duree_mois']),
                'percentage_repaid': 0
            }
        
        return jsonify({
            'success': True,
            'credit_details': credit_details
        })
        
    except Exception as e:
        return jsonify({'error': f'Erreur de calcul: {str(e)}'}), 500


@platform_investor_bp.route('/plan-investissement')
@login_required
def investment_plan():
    """
    Page de gestion du plan d'investissement pour l'utilisateur connecté.
    """
    # Récupérer ou créer le plan d'investissement
    investment_plan = InvestmentPlan.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not investment_plan:
        investment_plan = InvestmentPlan(
            user_id=current_user.id,
            name="Mon plan d'investissement",
            is_active=True
        )
        db.session.add(investment_plan)
        db.session.commit()
    
    # Récupérer le montant mensuel depuis le profil investisseur
    monthly_amount = 0
    if current_user.investor_profile and current_user.investor_profile.monthly_savings_capacity:
        monthly_amount = current_user.investor_profile.monthly_savings_capacity
    
    return render_template('platform/investor/investment_plan.html', 
                         investment_plan=investment_plan,
                         monthly_amount=monthly_amount,
                         available_envelopes=AVAILABLE_ENVELOPES)


@platform_investor_bp.route('/plan-investissement/save', methods=['POST'])
@login_required
def save_investment_plan():
    """
    Sauvegarder le plan d'investissement de l'utilisateur connecté.
    """
    try:
        data = request.get_json()
        lines_data = data.get('lines', [])
        
        # Validation : vérifier que la somme des pourcentages ne dépasse pas 100%
        total_percentage = sum(float(line.get('percentage', 0)) for line in lines_data)
        if total_percentage > 100:
            return jsonify({
                'success': False, 
                'message': f'La somme des pourcentages ({total_percentage}%) dépasse 100%'
            }), 400
        
        # Récupérer ou créer le plan
        plan = InvestmentPlan.query.filter_by(user_id=current_user.id, is_active=True).first()
        if not plan:
            plan = InvestmentPlan(user_id=current_user.id, name="Mon plan d'investissement")
            db.session.add(plan)
            db.session.flush()  # Pour obtenir l'ID
        
        # Supprimer toutes les anciennes lignes
        InvestmentPlanLine.query.filter_by(plan_id=plan.id).delete()
        
        # Ajouter les nouvelles lignes
        for index, line_data in enumerate(lines_data):
            if not line_data.get('description', '').strip():
                continue  # Ignorer les lignes vides
                
            line = InvestmentPlanLine(
                plan_id=plan.id,
                support_envelope=line_data.get('support_envelope', ''),
                description=line_data.get('description', ''),
                reference=line_data.get('reference', ''),
                percentage=float(line_data.get('percentage', 0)),
                order_index=index
            )
            db.session.add(line)
        
        # Mettre à jour la date du plan
        plan.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Plan d\'investissement sauvegardé avec succès',
            'plan': plan.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur lors de la sauvegarde: {str(e)}'}), 500