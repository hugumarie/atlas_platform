#!/usr/bin/env python3
"""
Analyse complète du problème signalé par l'utilisateur
"""

import sys
import os
sys.path.append('.')

from app import create_app, db
from app.models.apprentissage import Apprentissage
from app.models.user import User

def analyze_formations_issue():
    """Analyse du problème de formations"""
    print("=== ANALYSE COMPLÈTE DU PROBLÈME DE FORMATIONS ===\n")
    
    app = create_app()
    with app.app_context():
        # 1. État actuel des formations en base
        print("1. ÉTAT DE LA BASE DE DONNÉES:")
        formations = Apprentissage.query.all()
        print(f"   Nombre de formations: {len(formations)}")
        
        for formation in formations:
            print(f"\n   📚 {formation.nom}")
            print(f"      ID: {formation.id}")
            print(f"      Description: {formation.description[:50] if formation.description else 'Aucune'}...")
            print(f"      Actif: {'✅ Oui' if formation.actif else '❌ Non'}")
            print(f"      Ordre: {formation.ordre}")
            print(f"      Créé le: {formation.date_creation}")
            print(f"      Modifié le: {formation.date_modification}")
            
            # Vérifier les fichiers
            upload_dir = os.path.join('app', 'static', 'uploads', 'apprentissages')
            
            if formation.fichier_pdf:
                pdf_path = os.path.join(upload_dir, formation.fichier_pdf)
                pdf_exists = os.path.exists(pdf_path)
                pdf_size = os.path.getsize(pdf_path) if pdf_exists else 0
                print(f"      PDF: {formation.fichier_pdf}")
                print(f"           {'✅' if pdf_exists else '❌'} Fichier ({pdf_size} bytes)")
                print(f"           Nom original: {formation.fichier_pdf_original or 'Non défini'}")
            else:
                print(f"      PDF: ❌ Aucun")
                
            if formation.image:
                img_path = os.path.join(upload_dir, formation.image)
                img_exists = os.path.exists(img_path)
                img_size = os.path.getsize(img_path) if img_exists else 0
                print(f"      Image: {formation.image}")
                print(f"             {'✅' if img_exists else '❌'} Fichier ({img_size} bytes)")
            else:
                print(f"      Image: ❌ Aucune")
        
        # 2. Vérifier les routes
        print(f"\n2. VÉRIFICATION DES ROUTES:")
        
        # Routes admin formations
        admin_routes = [
            'platform_admin.apprentissages',
            'platform_admin.apprentissage_create', 
            'platform_admin.apprentissage_edit',
            'platform_admin.apprentissage_delete',
            'platform_admin.apprentissage_preview'
        ]
        
        print(f"   Routes admin disponibles:")
        for route in admin_routes:
            try:
                url = app.url_map._rules_by_endpoint.get(route)
                if url:
                    print(f"      ✅ {route}")
                else:
                    print(f"      ❌ {route}")
            except:
                print(f"      ❌ {route} (erreur)")
        
        # Route formations utilisateur
        user_route = 'platform_investor.formations'
        try:
            url = app.url_map._rules_by_endpoint.get(user_route)
            if url:
                print(f"   ✅ Route utilisateur: {user_route}")
            else:
                print(f"   ❌ Route utilisateur: {user_route}")
        except:
            print(f"   ❌ Route utilisateur: {user_route} (erreur)")
        
        # 3. Identifier les problèmes potentiels
        print(f"\n3. PROBLÈMES POTENTIELS IDENTIFIÉS:")
        issues = []
        
        # La route utilisateur utilise des données statiques au lieu de la DB
        issues.append({
            'type': 'CRITIQUE',
            'description': 'La route /formations côté utilisateur utilise des données statiques au lieu de récupérer les formations depuis la base de données',
            'fichier': 'app/routes/platform/investor.py ligne 290-333',
            'impact': 'Les utilisateurs ne voient pas les vraies formations créées par l\'admin'
        })
        
        # Vérifier si il y a des formations sans fichiers
        formations_sans_fichiers = [f for f in formations if not f.fichier_pdf and not f.image]
        if formations_sans_fichiers:
            issues.append({
                'type': 'ATTENTION',
                'description': f'{len(formations_sans_fichiers)} formation(s) sans fichiers PDF/image',
                'fichier': 'Base de données',
                'impact': 'Ces formations ne peuvent pas être consultées par les utilisateurs'
            })
        
        # Vérifier la colonne fichier_pdf_original qui est parfois None
        formations_sans_nom_original = [f for f in formations if f.fichier_pdf and not f.fichier_pdf_original]
        if formations_sans_nom_original:
            issues.append({
                'type': 'MINEUR',
                'description': f'{len(formations_sans_nom_original)} formation(s) avec PDF mais sans nom original',
                'fichier': 'Base de données - colonne fichier_pdf_original',
                'impact': 'Nom de fichier technique affiché à la place du nom original'
            })
        
        # Affichage des problèmes
        for i, issue in enumerate(issues, 1):
            print(f"\n   🚨 PROBLÈME #{i} - {issue['type']}")
            print(f"      Description: {issue['description']}")
            print(f"      Fichier: {issue['fichier']}")
            print(f"      Impact: {issue['impact']}")
        
        # 4. Solutions recommandées
        print(f"\n4. SOLUTIONS RECOMMANDÉES:")
        print(f"\n   🔧 SOLUTION CRITIQUE #1:")
        print(f"      Modifier la route /formations dans app/routes/platform/investor.py")
        print(f"      Remplacer les données statiques par:")
        print(f"      formations = Apprentissage.query.filter_by(actif=True).order_by(Apprentissage.ordre).all()")
        
        print(f"\n   🔧 SOLUTION RECOMMANDÉE #2:")
        print(f"      Ajouter une route pour visualiser les PDFs côté utilisateur")
        print(f"      Exemple: /plateforme/formation/<int:id>/pdf")
        
        print(f"\n   🔧 SOLUTION MINEUR #3:")
        print(f"      Mettre à jour les formations existantes pour avoir un nom original:")
        for f in formations_sans_nom_original:
            print(f"      UPDATE: Formation '{f.nom}' - définir fichier_pdf_original")

if __name__ == "__main__":
    analyze_formations_issue()