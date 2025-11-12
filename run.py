"""
Point d'entrée principal de l'application Flask.
Lance l'application de gestion de patrimoine.
"""

from app import create_app
import os

# Création de l'instance de l'application
app = create_app()

if __name__ == '__main__':
    # Configuration pour le développement
    import os
    if os.getenv('FLASK_ENV') == 'production':
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        app.run(debug=True, host='127.0.0.1', port=5001)