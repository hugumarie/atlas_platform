#!/bin/bash

# 🗃️ TEST ET VALIDATION BASE DE DONNÉES UNIQUEMENT
# ================================================

SERVER="139.59.158.149"

echo "🗃️ VALIDATION BASE DE DONNÉES ATLAS"
echo "=================================="
echo ""
echo "Test sur serveur: $SERVER"
echo ""

ssh root@$SERVER << 'REMOTE_SCRIPT'

echo "🔍 DIAGNOSTIC POSTGRESQL COMPLET"
echo "==============================="

# 1. Vérifier que PostgreSQL est actif
echo ""
echo "[1] 📊 Statut PostgreSQL"
echo "------------------------"
systemctl status postgresql --no-pager -l | head -5

# 2. Vérifier les bases existantes
echo ""
echo "[2] 📋 Bases de données existantes"
echo "---------------------------------"
sudo -u postgres psql -l

# 3. Vérifier l'utilisateur atlas
echo ""
echo "[3] 👤 Utilisateur atlas"
echo "----------------------"
sudo -u postgres psql -c "\du atlas"

# 4. Tenter de créer/recréer la base et l'utilisateur
echo ""
echo "[4] 🔧 Recréation base et utilisateur"
echo "-----------------------------------"

sudo -u postgres psql << 'PSQL_SETUP'
-- Supprimer la base si elle existe (avec connexions forcées)
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'atlas_production' AND pid <> pg_backend_pid();

DROP DATABASE IF EXISTS atlas_production;

-- Supprimer et recréer l'utilisateur
DROP USER IF EXISTS atlas;
CREATE USER atlas WITH PASSWORD 'AtlasDB2024_SecurePass!';

-- Créer la base avec le bon owner
CREATE DATABASE atlas_production OWNER atlas;

-- Donner tous les privilèges
GRANT ALL PRIVILEGES ON DATABASE atlas_production TO atlas;

-- Se connecter à la nouvelle base et donner les permissions sur les schémas
\c atlas_production;
GRANT ALL ON SCHEMA public TO atlas;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO atlas;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO atlas;

\q
PSQL_SETUP

echo "✅ Base recréée"

# 5. Configurer pg_hba.conf pour md5
echo ""
echo "[5] 🔐 Configuration authentification"
echo "-----------------------------------"

# Backup du fichier actuel
PG_VERSION=$(ls /etc/postgresql/)
PG_HBA_FILE="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"

echo "Fichier pg_hba.conf: $PG_HBA_FILE"
cp "$PG_HBA_FILE" "$PG_HBA_FILE.backup.$(date +%Y%m%d_%H%M%S)"

# Modifier la ligne pour atlas spécifiquement
sed -i '/^local.*atlas.*peer/d' "$PG_HBA_FILE"
echo "local   atlas_production   atlas                           md5" >> "$PG_HBA_FILE"
echo "host    atlas_production   atlas   127.0.0.1/32            md5" >> "$PG_HBA_FILE"

echo "Configuration pg_hba.conf mise à jour"

# 6. Redémarrer PostgreSQL
echo ""
echo "[6] 🔄 Redémarrage PostgreSQL"
echo "----------------------------"
systemctl restart postgresql
sleep 3

# 7. Test de connexion avec différentes méthodes
echo ""
echo "[7] 🧪 TESTS DE CONNEXION"
echo "========================"

echo ""
echo "Test 1: Connexion locale avec mot de passe"
echo "-------------------------------------------"
export PGPASSWORD='AtlasDB2024_SecurePass!'
if psql -U atlas -d atlas_production -h localhost -c "SELECT 'Connexion OK' as status;" 2>/dev/null; then
    echo "✅ Connexion localhost RÉUSSIE"
else
    echo "❌ Connexion localhost ÉCHOUÉE"
    echo "Détails de l'erreur:"
    psql -U atlas -d atlas_production -h localhost -c "SELECT 1;" 2>&1 | head -3
fi

echo ""
echo "Test 2: Connexion Unix socket"
echo "-----------------------------"
if PGPASSWORD='AtlasDB2024_SecurePass!' psql -U atlas -d atlas_production -c "SELECT 'Socket OK' as status;" 2>/dev/null; then
    echo "✅ Connexion socket RÉUSSIE"
else
    echo "❌ Connexion socket ÉCHOUÉE"
fi

echo ""
echo "Test 3: URL de connexion SQLAlchemy"
echo "----------------------------------"
export PGPASSWORD='AtlasDB2024_SecurePass!'
python3 << 'PYTHON_TEST'
import psycopg2
import sys

try:
    # Test de connexion direct avec psycopg2
    conn = psycopg2.connect(
        host="localhost",
        database="atlas_production",
        user="atlas",
        password="AtlasDB2024_SecurePass!"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print("✅ psycopg2 connexion RÉUSSIE")
    print(f"Version PostgreSQL: {version[0][:50]}...")
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ psycopg2 connexion ÉCHOUÉE: {e}")
    sys.exit(1)

try:
    # Test avec SQLAlchemy
    from sqlalchemy import create_engine, text
    
    url = "postgresql://atlas:AtlasDB2024_SecurePass!@localhost/atlas_production"
    engine = create_engine(url)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 'SQLAlchemy OK' as status"))
        row = result.fetchone()
        print(f"✅ SQLAlchemy connexion RÉUSSIE: {row[0]}")
        
except Exception as e:
    print(f"❌ SQLAlchemy connexion ÉCHOUÉE: {e}")
PYTHON_TEST

# 8. Informations de debug
echo ""
echo "[8] 🔍 INFORMATIONS DE DEBUG"
echo "==========================="

echo ""
echo "Ports PostgreSQL:"
netstat -tlnp | grep postgres

echo ""
echo "Processus PostgreSQL:"
ps aux | grep postgres | head -3

echo ""
echo "Variables d'environnement pour test:"
echo "PGPASSWORD='AtlasDB2024_SecurePass!'"
echo "URL: postgresql://atlas:AtlasDB2024_SecurePass!@localhost/atlas_production"

echo ""
echo "Configuration pg_hba.conf (lignes Atlas):"
grep -n atlas /etc/postgresql/*/main/pg_hba.conf || echo "Aucune ligne atlas trouvée"

REMOTE_SCRIPT

echo ""
echo "🎯 DIAGNOSTIC BASE DE DONNÉES TERMINÉ"
echo "===================================="