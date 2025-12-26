#!/bin/bash

# 🚀 ATLAS - RÉPARATION RAPIDE
# ============================

SERVER="139.59.158.149"

echo "🚀 ATLAS - RÉPARATION RAPIDE"
echo "============================"
echo ""
echo "Atlas sera réparé sur: $SERVER"
echo ""
read -p "Appuyez sur Entrée pour continuer ou Ctrl+C pour annuler..."

echo ""
echo "[INFO] 📤 Transfert de la configuration corrigée..."
scp atlas_config.env root@$SERVER:/root/atlas_config.env

echo "[INFO] 🎬 Exécution de la réparation sur le serveur..."
ssh root@$SERVER << 'REMOTE_SCRIPT'

echo "🔧 RÉPARATION ATLAS SUR SERVEUR"
echo "==============================="

cd /var/www/atlas

# Stopper Atlas
echo "[INFO] 🛑 Arrêt d'Atlas..."
systemctl stop atlas 2>/dev/null || true

# Appliquer la configuration corrigée
echo "[INFO] 📝 Application de la nouvelle configuration..."
cp /root/atlas_config.env /var/www/atlas/.env
chown www-data:www-data /var/www/atlas/.env

# Ajouter les variables Flask nécessaires
echo "
FLASK_ENV=production
SQLALCHEMY_DATABASE_URI=postgresql://atlas:AtlasDB2024_SecurePass!@localhost/atlas_production
SECRET_KEY=Atlas_Prod_2024_9x8w7v6u5t4r3e2w1q0p9o8i7u6y5t4r3e2w1q" >> /var/www/atlas/.env

# Configurer PostgreSQL
echo "[INFO] 🔧 Configuration PostgreSQL..."
sudo -u postgres psql << 'PSQL'
ALTER USER atlas WITH PASSWORD 'AtlasDB2024_SecurePass!';
\q
PSQL

# Configuration authentification PostgreSQL
echo "[INFO] 🔐 Configuration authentification..."
sed -i.bak 's/local   all             atlas                                   peer/local   all             atlas                                   md5/' /etc/postgresql/*/main/pg_hba.conf
systemctl restart postgresql

# Attendre PostgreSQL
sleep 3

# Test connexion DB
echo "[INFO] 🧪 Test de connexion base de données..."
export PGPASSWORD='AtlasDB2024_SecurePass!'
if psql -U atlas -d atlas_production -h localhost -c "SELECT 1;" >/dev/null 2>&1; then
    echo "✅ Connexion DB réussie"
else
    echo "❌ Échec connexion DB"
fi

# Créer les tables
echo "[INFO] 🗃️ Création des tables..."
cd /var/www/atlas
source venv/bin/activate
export SQLALCHEMY_DATABASE_URI='postgresql://atlas:AtlasDB2024_SecurePass!@localhost/atlas_production'

python3 << 'PYTHON'
try:
    from app import create_app
    from app.extensions import db
    app = create_app()
    with app.app_context():
        db.create_all()
    print("✅ Tables OK")
except Exception as e:
    print(f"❌ Erreur tables: {e}")
PYTHON

# Redémarrer Atlas
echo "[INFO] 🚀 Redémarrage d'Atlas..."
systemctl start atlas
sleep 5

# Vérifier le statut
echo ""
echo "=== STATUT SERVICES ==="
systemctl status atlas --no-pager -l | head -10

echo ""
echo "=== TEST HTTP ==="
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000)
echo "Code HTTP local: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Atlas fonctionne !"
else
    echo "⚠️ Problème détecté"
    echo ""
    echo "=== LOGS ATLAS (5 dernières lignes) ==="
    journalctl -u atlas -n 5 --no-pager
fi

REMOTE_SCRIPT

echo ""
echo "🧪 TEST FINAL EXTERNE"
echo "===================="
HTTP_FINAL=$(curl -s -o /dev/null -w "%{http_code}" http://$SERVER)
echo "🌐 URL: http://$SERVER"
echo "📊 Code HTTP: $HTTP_FINAL"

if [ "$HTTP_FINAL" = "200" ]; then
    echo "✅ Atlas est opérationnel !"
    echo ""
    echo "🔑 Comptes disponibles:"
    echo "   - Admin: admin@gmail.com"
    echo "   - Client: test.client@gmail.com"
else
    echo "⚠️ Problème détecté (code: $HTTP_FINAL)"
    echo "🔧 Connectez-vous au serveur: ssh root@$SERVER"
    echo "🔍 Vérifiez les logs: journalctl -fu atlas"
fi

echo ""
echo "🎯 Réparation terminée !"