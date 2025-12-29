#!/usr/bin/env python3
"""
Script de test complet pour simuler un upload de formation avec fichiers
"""

import sys
import os
import io
import uuid
from datetime import datetime
sys.path.append('.')

from app import create_app, db
from app.models.apprentissage import Apprentissage
from app.models.user import User
from werkzeug.datastructures import FileStorage

def create_test_files():
    """Crée des fichiers de test en mémoire"""
    # Créer un PDF de test
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Formation Test) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000200 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
294
%%EOF"""

    # Créer une image PNG de test (1x1 pixel transparent)
    png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0bIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'

    return pdf_content, png_content

def test_file_upload():
    """Test complet d'upload de fichiers"""
    print("=== TEST COMPLET D'UPLOAD DE FORMATION ===\n")
    
    app = create_app()
    with app.app_context():
        # 1. Créer les fichiers de test
        pdf_content, png_content = create_test_files()
        print("1. Fichiers de test créés")
        
        # 2. Simuler le processus d'upload (comme dans la route admin)
        try:
            print("\n2. Simulation du processus d'upload...")
            
            # Données du formulaire
            nom = f"Formation Test Upload {datetime.now().strftime('%H%M%S')}"
            description = "Test d'upload complet avec fichiers"
            ordre = 999
            actif = True
            
            # Simulation des fichiers uploadés
            upload_dir = os.path.join('app', 'static', 'uploads', 'apprentissages')
            
            # Gestion de l'image
            image_filename = None
            if png_content:
                image_filename = f"{uuid.uuid4().hex}.png"
                image_path = os.path.join(upload_dir, image_filename)
                with open(image_path, 'wb') as f:
                    f.write(png_content)
                print(f"   ✅ Image sauvegardée: {image_filename}")
            
            # Gestion du PDF
            pdf_filename = None
            pdf_original_name = None
            if pdf_content:
                pdf_original_name = "formation_test.pdf"
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                pdf_filename = f"{timestamp}_{pdf_original_name}"
                pdf_path = os.path.join(upload_dir, pdf_filename)
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_content)
                print(f"   ✅ PDF sauvegardé: {pdf_filename}")
            
            # Création de la formation
            apprentissage = Apprentissage(
                nom=nom,
                description=description,
                image=image_filename,
                fichier_pdf=pdf_filename,
                fichier_pdf_original=pdf_original_name,
                ordre=ordre,
                actif=actif
            )
            
            db.session.add(apprentissage)
            db.session.commit()
            print(f"   ✅ Formation créée avec ID: {apprentissage.id}")
            
            # 3. Vérifier que les fichiers existent
            print(f"\n3. Vérification des fichiers...")
            if image_filename:
                img_path = os.path.join(upload_dir, image_filename)
                exists = os.path.exists(img_path)
                size = os.path.getsize(img_path) if exists else 0
                print(f"   Image: {'✅' if exists else '❌'} ({size} bytes)")
            
            if pdf_filename:
                pdf_path = os.path.join(upload_dir, pdf_filename)
                exists = os.path.exists(pdf_path)
                size = os.path.getsize(pdf_path) if exists else 0
                print(f"   PDF: {'✅' if exists else '❌'} ({size} bytes)")
            
            # 4. Test de récupération depuis la DB
            print(f"\n4. Vérification base de données...")
            formation_db = Apprentissage.query.get(apprentissage.id)
            if formation_db:
                print(f"   ✅ Formation trouvée: {formation_db.nom}")
                print(f"   ✅ Image: {formation_db.image}")
                print(f"   ✅ PDF: {formation_db.fichier_pdf}")
                print(f"   ✅ PDF original: {formation_db.fichier_pdf_original}")
            
            # 5. Nettoyer (supprimer la formation de test)
            print(f"\n5. Nettoyage...")
            if image_filename:
                try:
                    os.remove(os.path.join(upload_dir, image_filename))
                    print(f"   🗑️ Image supprimée")
                except:
                    pass
            
            if pdf_filename:
                try:
                    os.remove(os.path.join(upload_dir, pdf_filename))
                    print(f"   🗑️ PDF supprimé")
                except:
                    pass
            
            db.session.delete(apprentissage)
            db.session.commit()
            print(f"   🗑️ Formation supprimée de la DB")
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == "__main__":
    test_file_upload()