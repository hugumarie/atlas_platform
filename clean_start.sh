#!/bin/bash

echo "🧹 Nettoyage complet d'Atlas..."

# Arrêter tous les processus Python/Flask
pkill -f python3 2>/dev/null
pkill -f flask 2>/dev/null
sleep 2

# Supprimer tous les caches Python
echo "🗑️ Suppression des caches Python..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# Vérifier que la route existe dans pages.py
echo "🔍 Vérification de la route solutions..."
if grep -q "@site_pages_bp.route('/solutions')" app/routes/site/pages.py; then
    echo "✅ Route /solutions trouvée dans pages.py"
else
    echo "❌ Route /solutions manquante dans pages.py"
    exit 1
fi

# Vérifier que le template existe
if [ -f "app/templates/site/solutions_simple.html" ]; then
    echo "✅ Template solutions_simple.html trouvé"
else
    echo "❌ Template solutions_simple.html manquant"
    exit 1
fi

echo ""
echo "🚀 Démarrage propre de Flask..."
export FLASK_ENV=development
export FLASK_DEBUG=1
python3 run.py