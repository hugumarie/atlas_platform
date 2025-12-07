#!/usr/bin/env python3
"""
Script pour mettre à jour automatiquement tous les calculs patrimoniaux.
Peut être exécuté périodiquement (cron job) pour maintenir les données à jour.
"""

import sys
import os

# Ajouter le répertoire parent au path pour importer l'app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.services.patrimoine_calculation import PatrimoineCalculationService


def main():
    """
    Point d'entrée principal du script de mise à jour.
    """
    print("🚀 Démarrage de la mise à jour des calculs patrimoniaux...")
    
    # Créer le contexte d'application
    app = create_app()
    
    with app.app_context():
        try:
            # Mise à jour de tous les utilisateurs
            PatrimoineCalculationService.update_all_users_patrimoine()
            
            print("✅ Mise à jour terminée avec succès.")
            return 0
            
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour: {e}")
            import traceback
            traceback.print_exc()
            return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)