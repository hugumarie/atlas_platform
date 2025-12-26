#!/bin/bash

echo "🚀 Atlas - Déploiement Production"
echo "================================"

# Vérifier l'environnement de production
if [ ! -f ".env.production" ]; then
    echo "❌ Fichier .env.production manquant"
    exit 1
fi

# Charger les variables d'environnement
export $(grep -v '^#' .env.production | xargs)

echo "✅ Variables d'environnement chargées"

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# Créer la base de données si elle n'existe pas
echo "💾 Configuration de la base de données..."
python -c "
from app import create_app
from app.models import db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Tables créées')
"

# Importer les données
if [ -f "atlas_data_import.sql" ]; then
    echo "📥 Import des données..."
    psql $SQLALCHEMY_DATABASE_URI -f atlas_data_import.sql
    echo "✅ Données importées"
fi

echo ""
echo "🎯 Déploiement terminé !"
echo "========================"
echo "🌐 L'application peut être lancée avec:"
echo "   python run.py"
echo ""
echo "🔧 Configuration requise:"
echo "   - Configurez un serveur web (nginx, apache)"
echo "   - Utilisez un serveur WSGI (gunicorn, uwsgi)"
echo "   - Configurez SSL/TLS"
echo "   - Configurez les sauvegardes automatiques"
