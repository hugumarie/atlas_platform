"""
Blueprint pour la plateforme applicative.
"""

from flask import Blueprint

platform_bp = Blueprint('platform', __name__, url_prefix='/plateforme')