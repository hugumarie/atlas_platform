#!/bin/bash

echo "🚀 Configuration du serveur Ubuntu pour Atlas"
echo "=============================================="

# Mise à jour du système
echo "📦 Mise à jour du système..."
apt update && apt upgrade -y

# Installation des dépendances système
echo "🔧 Installation des dépendances..."
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx supervisor git curl

# Configuration PostgreSQL
echo "💾 Configuration de PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE atlas_production_db;"
sudo -u postgres psql -c "CREATE USER atlas WITH ENCRYPTED PASSWORD 'atlas_secure_pass_2024';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE atlas_production_db TO atlas;"
sudo -u postgres psql -c "ALTER USER atlas CREATEDB;"

# Configuration du répertoire de l'application
echo "📁 Préparation du répertoire application..."
mkdir -p /var/www/atlas
cd /var/www/atlas

# Extraction du package Atlas
echo "📦 Extraction du package Atlas..."
if [ -f "/root/atlas_production_20251223_023409.tar.gz" ]; then
    tar -xzf /root/atlas_production_20251223_023409.tar.gz
    mv production_ready/* .
    rmdir production_ready
    echo "✅ Package Atlas extrait"
else
    echo "❌ Package Atlas non trouvé dans /root/"
    exit 1
fi

# Création de l'environnement virtuel Python
echo "🐍 Configuration de l'environnement Python..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "✅ Serveur configuré avec succès !"
echo ""
echo "📋 Prochaines étapes:"
echo "1. Configurer .env.production"
echo "2. Importer la base de données"
echo "3. Configurer nginx"
echo "4. Démarrer l'application"