#!/usr/bin/env python3
"""
Script de test pour vérifier le système d'upload des formations
"""

import sys
import os
sys.path.append('.')

from app import create_app, db
from app.models.apprentissage import Apprentissage
from app.models.user import User
from flask_login import login_user
import uuid
from datetime import datetime

def test_upload_system():
    """Test du système d'upload des formations"""
    print("=== TEST DU SYSTÈME D'UPLOAD DES FORMATIONS ===\n")
    
    app = create_app()
    with app.app_context():
        # 1. Vérifier l'état actuel de la base
        formations = Apprentissage.query.all()
        print(f"1. Formations en base: {len(formations)}")
        for f in formations:
            print(f"   - {f.nom} (actif: {f.actif})")
            print(f"     PDF: {f.fichier_pdf} ({f.fichier_pdf_original})")
            print(f"     Image: {f.image}")
        
        # 2. Vérifier les chemins d'upload
        upload_dir = os.path.join('app', 'static', 'uploads', 'apprentissages')
        print(f"\n2. Répertoire d'upload: {upload_dir}")
        print(f"   Existe: {os.path.exists(upload_dir)}")
        print(f"   Writable: {os.access(upload_dir, os.W_OK)}")
        
        if os.path.exists(upload_dir):
            files = os.listdir(upload_dir)
            print(f"   Fichiers présents: {len(files)}")
            for file in files:
                file_path = os.path.join(upload_dir, file)
                size = os.path.getsize(file_path)
                print(f"     - {file} ({size} bytes)")
        
        # 3. Test de création d'une formation
        print(f"\n3. Test de création d'une formation...")
        try:
            test_formation = Apprentissage(
                nom=f"Formation Test {datetime.now().strftime('%H:%M:%S')}",
                description="Formation de test pour vérifier le système d'upload",
                ordre=999,
                actif=True
            )
            
            db.session.add(test_formation)
            db.session.commit()
            print(f"   ✅ Formation créée avec ID: {test_formation.id}")
            
            # Suppression immédiate pour ne pas polluer
            db.session.delete(test_formation)
            db.session.commit()
            print(f"   🗑️ Formation de test supprimée")
            
        except Exception as e:
            print(f"   ❌ Erreur création: {e}")
            db.session.rollback()
        
        # 4. Vérifier la configuration Flask
        print(f"\n4. Configuration Flask:")
        print(f"   UPLOAD_FOLDER: {app.config.get('UPLOAD_FOLDER', 'Non défini')}")
        print(f"   MAX_CONTENT_LENGTH: {app.config.get('MAX_CONTENT_LENGTH', 'Non défini')}")
        
        # 5. Tester l'accès aux fichiers existants
        print(f"\n5. Test d'accès aux fichiers existants:")
        for formation in formations:
            if formation.fichier_pdf:
                pdf_path = os.path.join(upload_dir, formation.fichier_pdf)
                pdf_exists = os.path.exists(pdf_path)
                print(f"   PDF {formation.fichier_pdf}: {'✅' if pdf_exists else '❌'}")
                
            if formation.image:
                img_path = os.path.join(upload_dir, formation.image)
                img_exists = os.path.exists(img_path)
                print(f"   Image {formation.image}: {'✅' if img_exists else '❌'}")

if __name__ == "__main__":
    test_upload_system()