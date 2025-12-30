#!/usr/bin/env python3
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    admin = User.query.filter_by(email="admin@atlas.fr").first()
    
    if not admin:
        admin = User(
            email="admin@atlas.fr",
            first_name="Admin",
            last_name="Atlas",
            password_hash=generate_password_hash("Atlas2024!"),
            is_admin=True,
            user_type="admin",
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Compte admin créé: admin@atlas.fr / Atlas2024!")
    else:
        print("✅ Compte admin existe déjà")