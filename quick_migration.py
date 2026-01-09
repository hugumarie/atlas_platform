from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("MIGRATION PRODUCTION ATLAS")
    print("=" * 40)
    
    # Migration 1
    try:
        db.session.execute(text("ALTER TABLE investor_profiles ADD COLUMN IF NOT EXISTS calculated_risk_profile VARCHAR(20);"))
        db.session.commit()
        print("OK investor_profiles.calculated_risk_profile")
    except Exception as e:
        print(f"SKIP investor_profiles.calculated_risk_profile: {e}")
        db.session.rollback()
    
    # Migration 2
    try:
        db.session.execute(text("ALTER TABLE apprentissages ADD COLUMN IF NOT EXISTS categorie VARCHAR(100);"))
        db.session.commit()
        print("OK apprentissages.categorie")
    except Exception as e:
        print(f"SKIP apprentissages.categorie: {e}")
        db.session.rollback()
    
    # Migration 3
    try:
        db.session.execute(text("ALTER TABLE apprentissages ADD COLUMN IF NOT EXISTS storage_type VARCHAR(20) DEFAULT 'local';"))
        db.session.commit()
        print("OK apprentissages.storage_type")
    except Exception as e:
        print(f"SKIP apprentissages.storage_type: {e}")
        db.session.rollback()
    
    # Migration 4
    try:
        db.session.execute(text("ALTER TABLE apprentissages ADD COLUMN IF NOT EXISTS fichier_pdf_url VARCHAR(500);"))
        db.session.commit()
        print("OK apprentissages.fichier_pdf_url")
    except Exception as e:
        print(f"SKIP apprentissages.fichier_pdf_url: {e}")
        db.session.rollback()
    
    # Migration 5
    try:
        db.session.execute(text("ALTER TABLE apprentissages ADD COLUMN IF NOT EXISTS image_url VARCHAR(500);"))
        db.session.commit()
        print("OK apprentissages.image_url")
    except Exception as e:
        print(f"SKIP apprentissages.image_url: {e}")
        db.session.rollback()
    
    print("MIGRATION COMPLETE")