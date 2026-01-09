from app import create_app, db
from app.models.apprentissage import Apprentissage

app = create_app()

with app.app_context():
    print("SUPPRESSION DE TOUTES LES FORMATIONS")
    print("=" * 40)
    
    # Lister toutes les formations
    formations = Apprentissage.query.all()
    
    print(f"Formations trouvees: {len(formations)}")
    print()
    
    for formation in formations:
        print(f"- ID {formation.id}: {formation.nom}")
        print(f"  Categorie: {formation.categorie or 'Non definie'}")
        print(f"  PDF: {'Oui' if formation.fichier_pdf else 'Non'}")
        print()
    
    if formations:
        print("SUPPRESSION EN COURS...")
        
        # Supprimer toutes les formations une par une
        deleted_count = 0
        for formation in formations:
            try:
                formation_name = formation.nom
                db.session.delete(formation)
                db.session.commit()
                print(f"OK: {formation_name}")
                deleted_count += 1
            except Exception as e:
                print(f"ERREUR: {formation.nom} - {e}")
                db.session.rollback()
        
        print()
        print(f"SUPPRESSION TERMINEE: {deleted_count}/{len(formations)} formations supprimees")
    else:
        print("Aucune formation a supprimer")