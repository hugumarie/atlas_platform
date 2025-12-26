#!/bin/bash
set -e

echo "🚀 Atlas - Phase de release Dokku"

# Créer les tables de base de données
echo "📊 Création des tables..."
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Tables créées')
"

# Créer utilisateur admin par défaut si inexistant
echo "👤 Vérification utilisateur admin..."
python -c "
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    admin = User.query.filter_by(email='admin@atlas.com').first()
    if not admin:
        admin = User(
            email='admin@atlas.com',
            password_hash=generate_password_hash('Admin123!'),
            nom='Admin',
            prenom='Atlas', 
            role='admin',
            email_verified=True
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ Utilisateur admin créé')
    else:
        print('✅ Utilisateur admin existe déjà')
"

# Mise à jour des prix crypto si possible
echo "💰 Tentative mise à jour prix crypto..."
python -c "
try:
    from app.services.binance_price_service import BinancePriceService
    success = BinancePriceService.update_crypto_prices_in_db()
    if success:
        print('✅ Prix crypto mis à jour')
    else:
        print('⚠️ Échec mise à jour crypto')
except Exception as e:
    print(f'⚠️ Erreur crypto: {e}')
" || echo "⚠️ Service crypto non disponible"

echo "🎉 Release terminée avec succès"