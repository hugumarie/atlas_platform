#!/usr/bin/env python3
"""
Script de migration pour unifier les modèles Prospect et User.
Transfère toutes les données de la table prospects vers la table users
avec user_type='prospect'.

IMPORTANT: Ce script n'est utile que pour la migration initiale.
Une fois la migration effectuée et vérifiée, ce fichier peut être supprimé.
"""

import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au path pour importer l'app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.prospect import Prospect

def migrate_prospects_to_users():
    """
    Migre tous les prospects existants vers la table users unifiée.
    """
    app = create_app()
    
    with app.app_context():
        try:
            print("Début de la migration des prospects vers users...")
            
            # Récupérer tous les prospects existants
            prospects = Prospect.query.all()
            print(f"Trouvé {len(prospects)} prospects à migrer")
            
            migrated_count = 0
            skipped_count = 0
            
            for prospect in prospects:
                # Vérifier si un utilisateur avec le même email existe déjà
                existing_user = User.query.filter_by(email=prospect.email).first()
                
                if existing_user:
                    print(f"Utilisateur existant trouvé pour {prospect.email}, mise à jour des champs prospect...")
                    
                    # Mettre à jour l'utilisateur existant avec les données prospect
                    existing_user.user_type = 'prospect'
                    existing_user.prospect_source = prospect.source
                    existing_user.prospect_status = prospect.status
                    existing_user.prospect_notes = prospect.notes
                    existing_user.appointment_requested = prospect.appointment_requested
                    existing_user.appointment_status = prospect.appointment_status
                    existing_user.assigned_to = prospect.assigned_to
                    existing_user.last_contact = prospect.last_contact
                    
                    # Copier les informations de contact si nécessaires
                    if not existing_user.first_name:
                        existing_user.first_name = prospect.first_name
                    if not existing_user.last_name:
                        existing_user.last_name = prospect.last_name
                    if not existing_user.phone:
                        existing_user.phone = prospect.phone
                    
                    skipped_count += 1
                    
                else:
                    # Créer un nouvel utilisateur de type prospect
                    new_user = User(
                        email=prospect.email,
                        first_name=prospect.first_name,
                        last_name=prospect.last_name,
                        phone=prospect.phone,
                        is_admin=False,
                        is_active=True,
                        date_created=prospect.date_created,
                        
                        # Champs spécifiques aux prospects
                        user_type='prospect',
                        prospect_source=prospect.source,
                        prospect_status=prospect.status,
                        prospect_notes=prospect.notes,
                        appointment_requested=prospect.appointment_requested,
                        appointment_status=prospect.appointment_status,
                        assigned_to=prospect.assigned_to,
                        last_contact=prospect.last_contact
                    )
                    
                    # Mot de passe temporaire (sera changé lors de la première connexion)
                    new_user.set_password('TempPassword123!')
                    
                    db.session.add(new_user)
                    migrated_count += 1
                    
                    print(f"Créé utilisateur prospect: {prospect.email}")
            
            # Sauvegarder les changements
            db.session.commit()
            
            print(f"\nMigration terminée avec succès!")
            print(f"- {migrated_count} nouveaux utilisateurs prospects créés")
            print(f"- {skipped_count} utilisateurs existants mis à jour")
            print(f"- Total: {len(prospects)} prospects traités")
            
            # Afficher un résumé des utilisateurs
            total_users = User.query.count()
            prospect_users = User.query.filter_by(user_type='prospect').count()
            client_users = User.query.filter_by(user_type='client').count()
            
            print(f"\nRésumé de la base de données:")
            print(f"- Total utilisateurs: {total_users}")
            print(f"- Prospects: {prospect_users}")
            print(f"- Clients: {client_users}")
            
        except Exception as e:
            print(f"Erreur lors de la migration: {e}")
            db.session.rollback()
            sys.exit(1)

def verify_migration():
    """
    Vérifie que la migration s'est bien déroulée.
    """
    app = create_app()
    
    with app.app_context():
        prospects_count = Prospect.query.count()
        prospect_users_count = User.query.filter_by(user_type='prospect').count()
        
        print(f"\nVérification:")
        print(f"- Prospects dans table prospects: {prospects_count}")
        print(f"- Utilisateurs prospects dans table users: {prospect_users_count}")
        
        if prospects_count == prospect_users_count:
            print("✅ Migration vérifiée avec succès!")
        else:
            print("⚠️  Différence détectée, vérification manuelle recommandée")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Migration des prospects vers users')
    parser.add_argument('--verify', action='store_true', help='Vérifier la migration')
    parser.add_argument('--dry-run', action='store_true', help='Simulation sans modification')
    
    args = parser.parse_args()
    
    if args.verify:
        verify_migration()
    elif args.dry_run:
        print("Mode simulation - aucune modification ne sera effectuée")
        # TODO: Implémenter le mode dry-run si nécessaire
    else:
        migrate_prospects_to_users()
        verify_migration()