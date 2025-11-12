"""
Blueprint pour le site vitrine.
"""

from flask import Blueprint

site_bp = Blueprint('site', __name__, url_prefix='/site')