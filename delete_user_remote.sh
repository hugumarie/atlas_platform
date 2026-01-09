#!/bin/bash

echo "🗑️  SUPPRESSION D'UTILISATEUR EN PRODUCTION"
echo "=========================================="

# Demander l'email
read -p "📧 Entrez l'email de l'utilisateur à supprimer: " EMAIL

if [ -z "$EMAIL" ]; then
    echo "❌ Email requis!"
    exit 1
fi

echo ""
echo "⚠️  Connexion à la production pour supprimer: $EMAIL"
echo "⚠️  Cette action est IRRÉVERSIBLE!"
echo ""

# Exécuter le script Python sur le serveur de production
ssh dokku@167.172.108.93 "run atlas python -c '
import sys
sys.path.append(\".\")

from app import create_app, db
from app.models.user import User

def delete_user():
    app = create_app()
    with app.app_context():
        email = \"$EMAIL\".strip().lower()
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f\"❌ Aucun utilisateur trouvé avec l'\''email: {email}\")
            return
        
        # Afficher les informations
        print(f\"👤 UTILISATEUR TROUVÉ:\")
        print(f\"   Nom: {user.first_name} {user.last_name}\")
        print(f\"   Email: {user.email}\")
        print(f\"   Type: {'\"'\"'Admin'\"'\"' if user.is_admin else '\"'\"'Prospect'\"'\"' if user.is_prospect else '\"'\"'Client'\"'\"'}\")
        
        confirmation = input(f\"❓ Confirmez la suppression de {user.email} ? (tapez SUPPRIMER): \").strip()
        
        if confirmation != \"SUPPRIMER\":
            print(\"❌ Suppression annulée.\")
            return
        
        # Supprimer
        try:
            username = f\"{user.first_name} {user.last_name}\"
            db.session.delete(user)
            db.session.commit()
            
            print(f\"✅ SUPPRESSION RÉUSSIE!\")
            print(f\"✅ L'\''utilisateur {username} ({email}) a été supprimé.\")
            
        except Exception as e:
            db.session.rollback()
            print(f\"❌ ERREUR: {e}\")

delete_user()
'"