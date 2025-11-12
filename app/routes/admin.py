"""
Routes pour l'interface administrateur.
Gère la liste des clients et l'administration de la plateforme.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.investor_profile import InvestorProfile
from app.models.subscription import Subscription

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard administrateur avec statistiques générales.
    """
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('main.index'))
    
    # Statistiques générales
    total_users = User.query.filter_by(is_admin=False).count()
    active_subscriptions = Subscription.query.filter_by(status='active').count()
    trial_subscriptions = Subscription.query.filter_by(status='trial').count()
    completed_profiles = InvestorProfile.query.count()
    
    stats = {
        'total_users': total_users,
        'active_subscriptions': active_subscriptions,
        'trial_subscriptions': trial_subscriptions,
        'completed_profiles': completed_profiles,
        'conversion_rate': round((completed_profiles / total_users * 100), 1) if total_users > 0 else 0
    }
    
    # Derniers utilisateurs inscrits
    recent_users = User.query.filter_by(is_admin=False).order_by(User.date_created.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', stats=stats, recent_users=recent_users)

@admin_bp.route('/clients')
@login_required
def clients():
    """
    Liste de tous les clients avec recherche et filtres.
    """
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('main.index'))
    
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
    
    return render_template('admin/clients.html', clients=clients, search=search)

@admin_bp.route('/clients/<int:client_id>')
@login_required
def client_detail(client_id):
    """
    Détails d'un client spécifique.
    """
    if not current_user.is_admin:
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('main.index'))
    
    client = User.query.get_or_404(client_id)
    
    if client.is_admin:
        flash('Impossible d\'afficher les détails d\'un administrateur.', 'error')
        return redirect(url_for('admin.clients'))
    
    return render_template('admin/client_detail.html', client=client)