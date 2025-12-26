#!/bin/bash

# 🔧 Fix PostgreSQL pour Atlas
# Répare les problèmes courants de PostgreSQL

echo "🔧 RÉPARATION POSTGRESQL POUR ATLAS"
echo "===================================="
echo ""

DB_NAME="atlas_db"
DB_USER="atlas_user"  
DB_PASSWORD="atlas_password_2024_secure"

echo "📊 1. DIAGNOSTIC POSTGRESQL"
echo "---------------------------"

# Vérifier si PostgreSQL est installé
if ! command -v psql >/dev/null 2>&1; then
    echo "❌ PostgreSQL non installé"
    echo "🔧 Installation de PostgreSQL..."
    export DEBIAN_FRONTEND=noninteractive
    apt update -y
    apt install -y postgresql postgresql-contrib
    echo "✅ PostgreSQL installé"
fi

# Vérifier le statut du service
echo "Statut PostgreSQL:"
systemctl status postgresql --no-pager || echo "Service non actif"

# Vérifier les processus
echo "Processus PostgreSQL:"
ps aux | grep postgres | grep -v grep || echo "Aucun processus PostgreSQL"

# Vérifier les ports
echo "Ports d'écoute PostgreSQL:"
ss -ln | grep 5432 || echo "Port 5432 non ouvert"

echo ""
echo "🔄 2. REDÉMARRAGE ET RÉINITIALISATION"
echo "------------------------------------"

# Arrêter proprement
echo "Arrêt de PostgreSQL..."
systemctl stop postgresql 2>/dev/null || true
pkill -f postgres 2>/dev/null || true
sleep 3

# Vérifier les verrous et fichiers temporaires
echo "Nettoyage des fichiers temporaires..."
rm -f /var/lib/postgresql/*/main/postmaster.pid 2>/dev/null || true
rm -f /tmp/.s.PGSQL.* 2>/dev/null || true

# Vérifier les permissions
echo "Vérification des permissions..."
chown -R postgres:postgres /var/lib/postgresql/ 2>/dev/null || true
chmod -R 700 /var/lib/postgresql/*/main/ 2>/dev/null || true

# Redémarrer
echo "Redémarrage de PostgreSQL..."
systemctl enable postgresql
systemctl start postgresql
sleep 5

# Vérifier le démarrage
if systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL démarré avec succès"
else
    echo "❌ Échec du démarrage de PostgreSQL"
    echo "Logs d'erreur PostgreSQL:"
    journalctl -u postgresql --no-pager -n 20
    
    echo ""
    echo "🆘 TENTATIVE DE RÉINITIALISATION COMPLÈTE"
    echo "----------------------------------------"
    
    # Sauvegarde et réinitialisation si nécessaire
    systemctl stop postgresql
    mv /var/lib/postgresql /var/lib/postgresql.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
    
    # Réinstallation propre
    apt purge -y postgresql postgresql-* 2>/dev/null || true
    apt autoremove -y
    apt install -y postgresql postgresql-contrib
    
    systemctl enable postgresql
    systemctl start postgresql
    sleep 10
    
    if systemctl is-active --quiet postgresql; then
        echo "✅ PostgreSQL réinitialisé et démarré"
    else
        echo "❌ ÉCHEC CRITIQUE: Impossible de démarrer PostgreSQL"
        journalctl -u postgresql --no-pager -n 50
        exit 1
    fi
fi

echo ""
echo "🗄️ 3. CONFIGURATION DE LA BASE DE DONNÉES"
echo "-------------------------------------------"

# Attendre que PostgreSQL soit prêt
echo "Attente que PostgreSQL soit prêt..."
for i in {1..30}; do
    if sudo -u postgres psql -c "SELECT 1;" >/dev/null 2>&1; then
        echo "✅ PostgreSQL prêt après $i secondes"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ PostgreSQL n'est pas prêt après 30 secondes"
        exit 1
    fi
    sleep 1
done

# Créer/recréer la base de données et l'utilisateur
echo "Configuration de la base de données Atlas..."
sudo -u postgres psql << EOF
-- Supprimer l'ancienne configuration si elle existe
DROP DATABASE IF EXISTS $DB_NAME;
DROP USER IF EXISTS $DB_USER;

-- Créer l'utilisateur
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Créer la base de données
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Accorder tous les privilèges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER USER $DB_USER CREATEDB;

-- Vérifications
\l
\du

\q
EOF

if [ $? -eq 0 ]; then
    echo "✅ Base de données configurée avec succès"
else
    echo "❌ Erreur lors de la configuration de la base"
    exit 1
fi

echo ""
echo "🧪 4. TESTS DE CONNEXION"
echo "------------------------"

# Test de connexion avec l'utilisateur atlas_user
echo "Test de connexion avec atlas_user..."
export PGPASSWORD="$DB_PASSWORD"
if psql -h localhost -U $DB_USER -d $DB_NAME -c "SELECT version();" >/dev/null 2>&1; then
    echo "✅ Connexion atlas_user OK"
else
    echo "❌ Erreur de connexion atlas_user"
    echo "Détails:"
    psql -h localhost -U $DB_USER -d $DB_NAME -c "SELECT version();" 2>&1 || true
fi

# Test avec Python psycopg2
echo "Test de connexion Python..."
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        database='$DB_NAME',
        user='$DB_USER',
        password='$DB_PASSWORD'
    )
    print('✅ Connexion Python psycopg2 OK')
    conn.close()
except Exception as e:
    print(f'❌ Erreur Python: {e}')
" 2>/dev/null || echo "⚠️ psycopg2 non installé ou erreur Python"

echo ""
echo "📋 5. INFORMATIONS DE CONNEXION"
echo "-------------------------------"
echo "Host: localhost"
echo "Port: 5432"
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Password: $DB_PASSWORD"
echo ""
echo "URL de connexion:"
echo "postgresql://$DB_USER:$DB_PASSWORD@localhost/$DB_NAME"

echo ""
echo "✅ RÉPARATION POSTGRESQL TERMINÉE"
echo "=================================="
echo ""
echo "🔧 Commandes de diagnostic utiles:"
echo "  - systemctl status postgresql"
echo "  - sudo -u postgres psql"
echo "  - journalctl -u postgresql -f"
echo "  - ps aux | grep postgres"
echo ""