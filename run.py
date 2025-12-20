"""
Point d'entrée principal de l'application Atlas.
Lance l'application de gestion de patrimoine.

RECOMMANDÉ: Utilisez ./start_atlas.sh pour un démarrage complet avec crypto
"""

from app import create_app
import os

# Création de l'instance de l'application
app = create_app()

if __name__ == '__main__':
    print("🚀 Atlas - Démarrage direct")
    print("💡 Pour un démarrage complet avec crypto, utilisez: ./start_atlas.sh")
    print("")
    
    # Configuration pour le développement
    if os.getenv('FLASK_ENV') == 'production':
        print("🌐 Mode PRODUCTION - http://0.0.0.0:5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("🌐 Mode DÉVELOPPEMENT - http://127.0.0.1:5001")
        app.run(debug=True, host='127.0.0.1', port=5001)