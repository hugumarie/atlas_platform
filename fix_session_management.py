#!/usr/bin/env python3
"""
Script pour améliorer la gestion des sessions utilisateur
- Forcer déconnexion après paiement Stripe
- Éviter les boucles de redirection
- Nettoyer les sessions persistantes
"""

from app import create_app, db
from app.models.user import User
from app.models.subscription import Subscription

def cleanup_test_users():
    """Nettoie les utilisateurs de test pour éviter les sessions persistantes"""
    app = create_app()
    with app.app_context():
        # Supprimer les utilisateurs de test
        test_emails = [
            'tim@yopmail.com',
            'test@yopmail.com',
            'demo@yopmail.com'
        ]
        
        for email in test_emails:
            user = User.query.filter_by(email=email).first()
            if user:
                # Supprimer les abonnements associés
                subscriptions = Subscription.query.filter_by(user_id=user.id).all()
                for sub in subscriptions:
                    db.session.delete(sub)
                
                # Supprimer l'utilisateur
                db.session.delete(user)
                print(f"✅ Utilisateur de test supprimé: {email}")
            else:
                print(f"ℹ️ Utilisateur non trouvé: {email}")
        
        db.session.commit()
        print("✅ Nettoyage des utilisateurs de test terminé")

def check_subscription_status():
    """Vérifie le statut des abonnements"""
    app = create_app()
    with app.app_context():
        users = User.query.filter_by(is_admin=False).all()
        
        print(f"📊 {len(users)} utilisateurs trouvés:")
        
        for user in users:
            subscription = Subscription.query.filter_by(user_id=user.id).first()
            if subscription:
                print(f"  - {user.email}: {subscription.status}")
            else:
                print(f"  - {user.email}: AUCUN ABONNEMENT")

if __name__ == '__main__':
    print("🔧 AMÉLIORATION GESTION DES SESSIONS")
    print("===================================")
    
    print("\n1️⃣ Nettoyage des utilisateurs de test...")
    cleanup_test_users()
    
    print("\n2️⃣ Vérification des abonnements...")
    check_subscription_status()
    
    print("\n✅ Script terminé")
    print("\n💡 PROCHAINES ÉTAPES:")
    print("1. Redémarrer Flask: flask run")
    print("2. Aller sur /plateforme/deconnexion pour forcer la déconnexion")
    print("3. Créer un nouveau compte de test")
    print("4. Tester le flow complet")