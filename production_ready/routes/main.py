"""
Routes principales de l'application.
Gère la page d'accueil et les pages statiques.
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Page d'accueil de la plateforme.
    Redirige vers le dashboard si l'utilisateur est connecté.
    """
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('investor.dashboard'))
    
    return render_template('main/index.html')

@main_bp.route('/about')
def about():
    """
    Page à propos de la plateforme.
    """
    return render_template('main/about.html')

@main_bp.route('/pricing')
def pricing():
    """
    Page de présentation des tarifs.
    """
    return render_template('main/pricing.html')