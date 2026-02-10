"""Script one-shot: mise à jour mot de passe admin"""
from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(email='admin@gmail.com').first()
    if user:
        user.set_password('Admin_strong2026#')
        db.session.commit()
        print('OK mot de passe mis a jour: ' + user.email + ' | is_admin: ' + str(user.is_admin))
    else:
        print('ERREUR: admin@gmail.com introuvable')
