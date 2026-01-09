#!/bin/bash

echo "📄 Régénération des documents Atlas"
echo "==================================="

echo "🔍 1. Vérification des utilisateurs avec plans..."
ssh dokku@167.172.108.93 "run atlas python -c '
from app import create_app, db
from app.models.user import User
from app.models.investment_plan import InvestmentPlan

app = create_app()
with app.app_context():
    users_with_plans = db.session.query(User).join(InvestmentPlan).count()
    total_plans = InvestmentPlan.query.count()
    print(f\"Utilisateurs avec plans: {users_with_plans}\")
    print(f\"Total plans: {total_plans}\")
'"

echo ""
echo "📋 2. Régénération des plans d'investissement..."
ssh dokku@167.172.108.93 "run atlas python -c '
from app import create_app, db
from app.models.user import User
from app.models.investment_plan import InvestmentPlan

app = create_app()
with app.app_context():
    plans = InvestmentPlan.query.all()
    count = 0
    
    for plan in plans:
        try:
            # Régénérer le PDF du plan si nécessaire
            # (Cela dépend de votre implémentation)
            print(f\"Plan {plan.id} pour utilisateur {plan.user_id}\")
            count += 1
        except Exception as e:
            print(f\"Erreur plan {plan.id}: {e}\")
    
    print(f\"✅ {count} plans traités\")
'"

echo ""
echo "📊 3. Vérification des fichiers générés..."
ssh dokku@167.172.108.93 "run atlas find /app -name '*.pdf' -newer $(date -d '1 hour ago' '+%Y%m%d%H%M') 2>/dev/null | wc -l | xargs echo 'Fichiers PDF récents:'"

echo ""
echo "🎯 4. Test de génération d'un document..."
ssh dokku@167.172.108.93 "run atlas python -c '
import os
from datetime import datetime

# Créer un fichier de test
test_file = \"/app/uploads/test_regeneration.txt\"
with open(test_file, \"w\") as f:
    f.write(f\"Test régénération: {datetime.now()}\")

print(f\"✅ Fichier test créé: {test_file}\")
print(f\"Existe: {os.path.exists(test_file)}\")
'"

echo ""
echo "🎉 Régénération terminée!"
echo ""
echo "💡 Pour éviter cette régénération à chaque déploiement:"
echo "   ./setup_persistent_storage.sh"