#!/bin/bash

# Script de déploiement automatique pour Atlas sur Dokku
# Exécuté automatiquement lors du déploiement via le Procfile

echo "🚀 Début du script de release Atlas..."

# Attendre que PostgreSQL soit prêt
echo "⏳ Vérification de la disponibilité de PostgreSQL..."
while ! python3 -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    conn.close()
    print('✅ PostgreSQL accessible')
    exit(0)
except:
    exit(1)
" 2>/dev/null; do
    echo "   Attente de PostgreSQL..."
    sleep 2
done

# Exécuter les migrations de base de données
echo "📊 Application des migrations de base de données..."

# Migration 1: Tables de base (auto-créées par SQLAlchemy)
python3 << EOF
from app import create_app, db
from app.models import User, InvestorProfile, Subscription, InvestmentPlan, InvestmentPlanLine, InvestmentAction

app = create_app()
with app.app_context():
    print("   Création des tables de base...")
    db.create_all()
    print("   ✅ Tables de base créées")
EOF

# Migration 2: Colonnes calculées sur investor_profiles
echo "   Application de la migration: colonnes calculées..."
python3 << EOF
import psycopg2
import os

try:
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    cur = conn.cursor()
    
    # Vérifier si les colonnes existent déjà
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name='investor_profiles' AND column_name='calculated_patrimoine_total_net'
    """)
    
    if not cur.fetchone():
        print("   Ajout des colonnes de totaux calculés...")
        
        # Ajouter les colonnes calculées
        migrations = [
            "ALTER TABLE investor_profiles ADD COLUMN calculated_total_liquidites FLOAT DEFAULT 0.0",
            "ALTER TABLE investor_profiles ADD COLUMN calculated_total_placements FLOAT DEFAULT 0.0", 
            "ALTER TABLE investor_profiles ADD COLUMN calculated_total_immobilier_net FLOAT DEFAULT 0.0",
            "ALTER TABLE investor_profiles ADD COLUMN calculated_total_cryptomonnaies FLOAT DEFAULT 0.0",
            "ALTER TABLE investor_profiles ADD COLUMN calculated_total_autres_biens FLOAT DEFAULT 0.0",
            "ALTER TABLE investor_profiles ADD COLUMN calculated_total_credits_consommation FLOAT DEFAULT 0.0",
            "ALTER TABLE investor_profiles ADD COLUMN calculated_total_actifs FLOAT DEFAULT 0.0",
            "ALTER TABLE investor_profiles ADD COLUMN calculated_patrimoine_total_net FLOAT DEFAULT 0.0",
            "ALTER TABLE investor_profiles ADD COLUMN last_calculation_date TIMESTAMP"
        ]
        
        for migration in migrations:
            try:
                cur.execute(migration)
                conn.commit()
            except psycopg2.Error as e:
                if "already exists" not in str(e):
                    print(f"   Erreur migration: {e}")
                    conn.rollback()
                else:
                    conn.commit()
        
        print("   ✅ Colonnes calculées ajoutées")
    else:
        print("   ✅ Colonnes calculées déjà présentes")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"   Erreur lors de la migration des colonnes: {e}")
EOF

# Migration 3: Tables investment_plans et investment_plan_lines
echo "   Application de la migration: plans d'investissement..."
python3 << EOF
import psycopg2
import os

try:
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    cur = conn.cursor()
    
    # Vérifier si la table investment_plans existe
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema='public' AND table_name='investment_plans'
    """)
    
    if not cur.fetchone():
        print("   Création des tables de plans d'investissement...")
        
        # Créer les tables investment_plans
        cur.execute("""
            CREATE TABLE investment_plans (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(100) NOT NULL DEFAULT 'Plan principal',
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Créer les tables investment_plan_lines
        cur.execute("""
            CREATE TABLE investment_plan_lines (
                id SERIAL PRIMARY KEY,
                plan_id INTEGER NOT NULL REFERENCES investment_plans(id) ON DELETE CASCADE,
                support_envelope VARCHAR(100) NOT NULL,
                description VARCHAR(200) NOT NULL,
                reference VARCHAR(50),
                percentage FLOAT NOT NULL DEFAULT 0.0,
                order_index INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Index
        cur.execute("CREATE INDEX idx_investment_plans_user_active ON investment_plans(user_id, is_active)")
        cur.execute("CREATE INDEX idx_plan_lines_plan_order ON investment_plan_lines(plan_id, order_index)")
        
        # Contraintes
        cur.execute("ALTER TABLE investment_plan_lines ADD CONSTRAINT chk_percentage_positive CHECK (percentage >= 0)")
        cur.execute("ALTER TABLE investment_plan_lines ADD CONSTRAINT chk_percentage_max CHECK (percentage <= 100)")
        
        conn.commit()
        print("   ✅ Tables de plans d'investissement créées")
    else:
        print("   ✅ Tables de plans d'investissement déjà présentes")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"   Erreur lors de la migration des plans: {e}")
EOF

# Migration 4: Table investment_actions
echo "   Application de la migration: actions d'investissement..."
python3 << EOF
import psycopg2
import os

try:
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    cur = conn.cursor()
    
    # Vérifier si la table investment_actions existe
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema='public' AND table_name='investment_actions'
    """)
    
    if not cur.fetchone():
        print("   Création de la table investment_actions...")
        
        cur.execute("""
            CREATE TABLE investment_actions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                plan_line_id INTEGER NOT NULL REFERENCES investment_plan_lines(id),
                year_month VARCHAR(7) NOT NULL,
                support_type VARCHAR(50) NOT NULL,
                label VARCHAR(200),
                expected_amount FLOAT NOT NULL DEFAULT 0.0,
                realized_amount FLOAT DEFAULT 0.0,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                answered_at TIMESTAMP
            )
        """)
        
        # Index
        cur.execute("CREATE UNIQUE INDEX idx_unique_action ON investment_actions(user_id, plan_line_id, year_month)")
        cur.execute("CREATE INDEX idx_user_year_month ON investment_actions(user_id, year_month)")
        cur.execute("CREATE INDEX idx_status_year_month ON investment_actions(status, year_month)")
        
        conn.commit()
        print("   ✅ Table investment_actions créée")
    else:
        print("   ✅ Table investment_actions déjà présente")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"   Erreur lors de la migration investment_actions: {e}")
EOF

# Créer l'utilisateur admin par défaut
echo "👤 Création de l'utilisateur administrateur..."
python3 << EOF
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Vérifier si l'admin existe
    admin = User.query.filter_by(email='admin@atlas.fr').first()
    
    if not admin:
        print("   Création du compte administrateur...")
        admin = User(
            email='admin@atlas.fr',
            first_name='Admin',
            last_name='Atlas',
            password_hash=generate_password_hash('Atlas2024!'),
            is_admin=True,
            user_type='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("   ✅ Compte admin créé: admin@atlas.fr / Atlas2024!")
    else:
        print("   ✅ Compte administrateur déjà présent")
EOF

# Mise à jour des prix crypto (si les clés API sont configurées)
echo "₿ Mise à jour des prix des cryptomonnaies..."
python3 << EOF
from app import create_app
from app.services.binance_price_service import BinancePriceService
import os

app = create_app()
with app.app_context():
    try:
        binance_key = os.environ.get('BINANCE_API_KEY')
        if binance_key and binance_key != 'YOUR_BINANCE_API_KEY_HERE':
            service = BinancePriceService()
            updated = service.update_crypto_prices_in_db()
            print(f"   ✅ {updated} prix crypto mis à jour")
        else:
            print("   ⚠️ Clés Binance non configurées, prix crypto non mis à jour")
    except Exception as e:
        print(f"   ⚠️ Erreur mise à jour crypto: {e}")
EOF

echo "✅ Script de release Atlas terminé avec succès!"