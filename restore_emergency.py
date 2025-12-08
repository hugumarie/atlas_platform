#!/usr/bin/env python3
# Script de restauration d'urgence - À utiliser uniquement en cas de perte de données
import json
import sys
sys.path.append('.')
from app import create_app, db
from app.models.user import User

def restore_from_backup(backup_file):
    app = create_app()
    with app.app_context():
        with open(backup_file, 'r') as f:
            data = json.load(f)
        print(f"Restauration depuis {backup_file}")
        print(f"Date de sauvegarde: {data['backup_date']}")
        print(f"Nombre d'utilisateurs: {len(data['users'])}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        restore_from_backup(sys.argv[1])
    else:
        print("Usage: python restore_emergency.py <backup_file.json>")
