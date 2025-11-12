#!/bin/bash

echo "🔧 CORRECTION DU DÉPLOIEMENT - Réinitialisation des utilisateurs"
echo "📋 Vous allez devoir copier-coller quelques commandes..."
echo ""

echo "1️⃣  Connectez-vous au serveur avec cette commande :"
echo "ssh root@165.227.167.78"
echo "Mot de passe : (!=ZL@-nZu7eB?7a"
echo ""

echo "2️⃣  Une fois connecté, copiez-collez ces commandes UNE PAR UNE :"
echo ""

echo "# Aller dans le répertoire de l'app"
echo "cd /home/appuser/coach-patrimoine"
echo ""

echo "# Créer le script de réinitialisation"
cat << 'EOF'
cat > reset_demo.py << 'RESETEOF'
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.investor_profile import InvestorProfile
from app.models.subscription import Subscription
from datetime import datetime, timedelta

def reset_demo():
    app = create_app()
    with app.app_context():
        print("🗑️ Suppression des utilisateurs existants...")
        InvestorProfile.query.delete()
        Subscription.query.delete()
        User.query.delete()
        db.session.commit()
        print("✅ Base nettoyée")
        
        print("👑 Création admin...")
        admin = User(email='admin@azur.com', first_name='Admin', last_name='Azur', is_admin=True, phone='+33123456789')
        admin.set_password('Admin123!')
        db.session.add(admin)
        db.session.flush()
        
        admin_sub = Subscription(user_id=admin.id, start_date=datetime.now(), end_date=datetime.now() + timedelta(days=365), status='active')
        db.session.add(admin_sub)
        
        print("👥 Création Marie...")
        marie = User(email='marie@test.com', first_name='Marie', last_name='Dubois', is_admin=False, phone='+33123456780')
        marie.set_password('Test123!')
        db.session.add(marie)
        db.session.flush()
        
        marie_sub = Subscription(user_id=marie.id, start_date=datetime.now(), end_date=datetime.now() + timedelta(days=365), status='active')
        db.session.add(marie_sub)
        
        marie_profile = InvestorProfile(
            user_id=marie.id, monthly_net_income=3500, current_savings=25000, monthly_savings_capacity=400,
            risk_tolerance='conservateur', investment_experience='débutant', 
            investment_goals='Préparation retraite et sécurité financière', investment_horizon='long terme',
            family_situation='célibataire', professional_situation='employé',
            has_real_estate=False, real_estate_value=0, has_life_insurance=True, life_insurance_value=15000,
            has_pea=False, pea_value=0, has_livret_a=True, livret_a_value=10000,
            other_investments='Quelques actions Total en direct'
        )
        db.session.add(marie_profile)
        
        print("👥 Création Paul...")
        paul = User(email='paul@test.com', first_name='Paul', last_name='Martin', is_admin=False, phone='+33123456781')
        paul.set_password('Test123!')
        db.session.add(paul)
        db.session.flush()
        
        paul_sub = Subscription(user_id=paul.id, start_date=datetime.now(), end_date=datetime.now() + timedelta(days=365), status='active')
        db.session.add(paul_sub)
        
        paul_profile = InvestorProfile(
            user_id=paul.id, monthly_net_income=4500, current_savings=45000, monthly_savings_capacity=800,
            risk_tolerance='dynamique', investment_experience='intermédiaire',
            investment_goals='Maximisation du rendement et création de patrimoine', investment_horizon='long terme',
            family_situation='en couple', professional_situation='cadre',
            has_real_estate=True, real_estate_value=250000, has_life_insurance=True, life_insurance_value=30000,
            has_pea=True, pea_value=15000, has_livret_a=True, livret_a_value=22950,
            other_investments='ETF World, crypto (Bitcoin, Ethereum)'
        )
        db.session.add(paul_profile)
        
        print("👥 Création Sophie...")
        sophie = User(email='sophie@test.com', first_name='Sophie', last_name='Leroy', is_admin=False, phone='+33123456782')
        sophie.set_password('Test123!')
        db.session.add(sophie)
        db.session.flush()
        
        sophie_sub = Subscription(user_id=sophie.id, start_date=datetime.now(), end_date=datetime.now() + timedelta(days=365), status='active')
        db.session.add(sophie_sub)
        
        sophie_profile = InvestorProfile(
            user_id=sophie.id, monthly_net_income=3800, current_savings=32000, monthly_savings_capacity=600,
            risk_tolerance='modéré', investment_experience='débutant',
            investment_goals='Équilibre entre sécurité et rendement pour projet immobilier', investment_horizon='moyen terme',
            family_situation='en couple avec enfants', professional_situation='profession libérale',
            has_real_estate=False, real_estate_value=0, has_life_insurance=True, life_insurance_value=20000,
            has_pea=True, pea_value=12000, has_livret_a=True, livret_a_value=22950,
            other_investments='LDDS, quelques OPCVM'
        )
        db.session.add(sophie_profile)
        
        db.session.commit()
        print("✅ COMPTES CRÉÉS:")
        print("👑 admin@azur.com / Admin123!")
        print("👤 marie@test.com / Test123!")
        print("👤 paul@test.com / Test123!")
        print("👤 sophie@test.com / Test123!")

if __name__ == '__main__':
    reset_demo()
RESETEOF
EOF

echo ""
echo "3️⃣  Exécuter le script de réinitialisation :"
echo "su - appuser"
echo "cd /home/appuser/coach-patrimoine"
echo "source venv/bin/activate"
echo "python3 reset_demo.py"
echo ""

echo "4️⃣  Redémarrer l'application :"
echo "pkill -f gunicorn"
echo "gunicorn --bind 127.0.0.1:5000 --workers 2 --daemon wsgi:app"
echo "exit"
echo "exit"
echo ""

echo "5️⃣  Votre site sera prêt à :"
echo "🌐 http://165.227.167.78"
echo ""
echo "🔑 Comptes de test :"
echo "👑 admin@azur.com / Admin123!"
echo "👤 marie@test.com / Test123!"
echo "👤 paul@test.com / Test123!"
echo "👤 sophie@test.com / Test123!"