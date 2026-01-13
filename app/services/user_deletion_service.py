"""
Service de suppression complète d'un utilisateur.
Gère la suppression Stripe et toutes les données en cascade.
"""

import os
from app import db
from app.models.user import User


class UserDeletionService:
    """Service pour supprimer complètement un utilisateur et toutes ses données."""

    @staticmethod
    def delete_user_completely(user_id: int):
        """
        Supprime complètement un utilisateur et toutes ses données.
        
        Args:
            user_id (int): ID de l'utilisateur à supprimer
            
        Returns:
            dict: Résultat de la suppression avec succès/erreur et détails
        """
        user = User.query.get(user_id)
        if not user:
            return {
                'success': False,
                'message': f'Utilisateur avec ID {user_id} non trouvé'
            }
        
        user_name = f"{user.first_name} {user.last_name}"
        user_email = user.email
        stripe_errors = []
        
        print(f"🗑️ Début suppression utilisateur: {user_name} ({user_email})")
        
        try:
            # 1. Annulation Stripe en premier
            stripe_errors = UserDeletionService._cancel_stripe_subscription(user)
            
            # 2. Suppression préparatoire des contraintes FK problématiques 
            UserDeletionService._delete_investment_plans(user_id)
            
            # 3. Utiliser la méthode simple qui marche (comme les scripts)
            db.session.delete(user)
            db.session.commit()
            
            print(f"✅ Suppression complète réussie: {user_name} ({user_email})")
            
            # Message de succès
            success_message = f"Utilisateur {user_name} ({user_email}) supprimé avec succès"
            if stripe_errors:
                success_message += f"\n⚠️ Avertissements Stripe: {', '.join(stripe_errors)}"
            else:
                success_message += "\n✅ Abonnement Stripe annulé"
            
            return {
                'success': True,
                'message': success_message,
                'stripe_warnings': stripe_errors if stripe_errors else None
            }
            
        except Exception as e:
            try:
                db.session.rollback()
            except:
                pass
            
            error_msg = f"Erreur lors de la suppression: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                'success': False,
                'message': error_msg
            }
    
    @staticmethod
    def _cancel_stripe_subscription(user):
        """Annule l'abonnement Stripe de l'utilisateur."""
        stripe_errors = []
        
        if not user.subscription:
            return stripe_errors
        
        try:
            import stripe
            
            # Configurer Stripe
            stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
            
            if not stripe.api_key:
                stripe_errors.append("Clé API Stripe non configurée")
                return stripe_errors
            
            # Récupérer les IDs Stripe via SQL direct pour éviter problèmes ORM
            stripe_result = db.session.execute(
                db.text("SELECT stripe_subscription_id, stripe_customer_id FROM subscriptions WHERE user_id = :user_id"),
                {"user_id": user.id}
            )
            stripe_row = stripe_result.fetchone()
            
            if not stripe_row:
                return stripe_errors
                
            stripe_subscription_id = stripe_row[0]
            stripe_customer_id = stripe_row[1]
            
            # Annuler l'abonnement Stripe
            if stripe_subscription_id:
                try:
                    subscription = stripe.Subscription.retrieve(stripe_subscription_id)
                    if subscription.status in ['active', 'trialing', 'past_due']:
                        stripe.Subscription.delete(stripe_subscription_id)
                        print(f"✅ Abonnement Stripe {stripe_subscription_id} annulé")
                except stripe.error.InvalidRequestError as e:
                    if "No such subscription" in str(e):
                        print(f"⚠️ Abonnement Stripe déjà supprimé: {stripe_subscription_id}")
                    else:
                        stripe_errors.append(f"Erreur Stripe subscription: {str(e)}")
            
            # Supprimer le customer Stripe
            if stripe_customer_id:
                try:
                    stripe.Customer.delete(stripe_customer_id)
                    print(f"✅ Customer Stripe {stripe_customer_id} supprimé")
                except stripe.error.InvalidRequestError as e:
                    if "No such customer" in str(e):
                        print(f"⚠️ Customer Stripe déjà supprimé: {stripe_customer_id}")
                    else:
                        stripe_errors.append(f"Erreur Stripe customer: {str(e)}")
            
        except Exception as e:
            stripe_errors.append(f"Erreur générale Stripe: {str(e)}")
        
        return stripe_errors
    
    @staticmethod
    def _delete_investment_plans(user_id: int):
        """Supprime TOUTES les données liées à l'utilisateur avant suppression."""
        try:
            deleted_counts = {}

            # 1. Supprimer les comptes rendus (NOUVELLE TABLE - Janvier 2026)
            result = db.session.execute(
                db.text("DELETE FROM comptes_rendus WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            deleted_counts['comptes_rendus'] = result.rowcount

            # 2. Supprimer les investment_actions
            result = db.session.execute(
                db.text("DELETE FROM investment_actions WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            deleted_counts['investment_actions'] = result.rowcount

            # 3. Supprimer les lignes de plans d'investissement
            result = db.session.execute(
                db.text("DELETE FROM investment_plan_lines WHERE plan_id IN (SELECT id FROM investment_plans WHERE user_id = :user_id)"),
                {"user_id": user_id}
            )
            deleted_counts['investment_plan_lines'] = result.rowcount

            # 4. Supprimer les plans d'investissement
            result = db.session.execute(
                db.text("DELETE FROM investment_plans WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            deleted_counts['investment_plans'] = result.rowcount

            # 5. Supprimer les password_reset_tokens
            result = db.session.execute(
                db.text("DELETE FROM password_reset_tokens WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            deleted_counts['password_reset_tokens'] = result.rowcount

            # 6. Supprimer les invitation_tokens (utilisent prospect_id)
            result = db.session.execute(
                db.text("DELETE FROM invitation_tokens WHERE prospect_id = :user_id"),
                {"user_id": user_id}
            )
            deleted_counts['invitation_tokens'] = result.rowcount

            # 7. Supprimer les user_plans
            result = db.session.execute(
                db.text("DELETE FROM user_plans WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            deleted_counts['user_plans'] = result.rowcount

            # 8. Supprimer les payment_methods
            result = db.session.execute(
                db.text("DELETE FROM payment_methods WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            deleted_counts['payment_methods'] = result.rowcount

            # 9. Supprimer les portfolios
            result = db.session.execute(
                db.text("DELETE FROM portfolios WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            deleted_counts['portfolios'] = result.rowcount

            # 10. Supprimer les subscriptions
            result = db.session.execute(
                db.text("DELETE FROM subscriptions WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            deleted_counts['subscriptions'] = result.rowcount

            # 11. Supprimer les investor_profiles
            result = db.session.execute(
                db.text("DELETE FROM investor_profiles WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            deleted_counts['investor_profiles'] = result.rowcount

            # Commit toutes ces suppressions
            db.session.commit()

            # Afficher le résumé
            total = sum(deleted_counts.values())
            if total > 0:
                details = ", ".join([f"{count} {table}" for table, count in deleted_counts.items() if count > 0])
                print(f"✅ Données supprimées: {details}")

        except Exception as e:
            print(f"⚠️ Erreur suppression données liées: {e}")
            db.session.rollback()
    
    @staticmethod
    def _delete_related_data_sql(user_id: int):
        """Supprime toutes les données liées avec du SQL direct."""
        
        # Tables essentielles qui doivent être supprimées (contraintes FK)
        essential_tables = [
            "DELETE FROM investment_plan_lines WHERE plan_id IN (SELECT id FROM investment_plans WHERE user_id = :user_id)",
            "DELETE FROM investment_plans WHERE user_id = :user_id",
            "DELETE FROM investor_profiles WHERE user_id = :user_id",
            "DELETE FROM subscriptions WHERE user_id = :user_id",
            "DELETE FROM portfolios WHERE user_id = :user_id",
            "DELETE FROM payment_methods WHERE user_id = :user_id",
            "DELETE FROM invitation_tokens WHERE prospect_id = :user_id"
        ]
        
        # Tables optionnelles (peuvent ne pas exister)
        optional_tables = [
            "DELETE FROM user_plans WHERE user_id = :user_id",
            "DELETE FROM user_apprentissage_progress WHERE user_id = :user_id",
            "DELETE FROM user_subscription_history WHERE user_id = :user_id",
            "DELETE FROM user_sessions WHERE user_id = :user_id",
            "DELETE FROM user_activity_log WHERE user_id = :user_id",
            "DELETE FROM user_notifications WHERE user_id = :user_id",
            "DELETE FROM user_documents WHERE user_id = :user_id",
            "DELETE FROM user_logs WHERE user_id = :user_id",
            "DELETE FROM user_preferences WHERE user_id = :user_id",
            "DELETE FROM user_settings WHERE user_id = :user_id"
        ]
        
        total_deleted = 0
        
        # 1. Supprimer les tables essentielles
        print("🔥 Suppression des tables essentielles...")
        for query in essential_tables:
            try:
                result = db.session.execute(db.text(query), {"user_id": user_id})
                deleted_count = result.rowcount
                if deleted_count > 0:
                    table_name = query.split("FROM ")[1].split(" ")[0]
                    print(f"✅ {table_name}: {deleted_count} lignes supprimées")
                    total_deleted += deleted_count
            except Exception as e:
                if "does not exist" not in str(e):
                    # Erreur grave sur table essentielle
                    print(f"❌ ERREUR CRITIQUE sur table essentielle: {e}")
                    raise e
                else:
                    table_name = query.split("FROM ")[1].split(" ")[0]
                    print(f"⚠️ Table {table_name} non existante (ignorée)")
        
        # 2. Supprimer les tables optionnelles (en mode best effort)
        print("🧹 Nettoyage des tables optionnelles...")
        for query in optional_tables:
            try:
                result = db.session.execute(db.text(query), {"user_id": user_id})
                deleted_count = result.rowcount
                if deleted_count > 0:
                    table_name = query.split("FROM ")[1].split(" ")[0]
                    print(f"✅ {table_name}: {deleted_count} lignes supprimées")
                    total_deleted += deleted_count
            except Exception as e:
                table_name = query.split("FROM ")[1].split(" ")[0]
                if "does not exist" in str(e):
                    print(f"⚠️ Table {table_name} non existante (ignorée)")
                else:
                    print(f"⚠️ Table {table_name} erreur ignorée: {e}")
                    # Ne pas rollback pour les tables optionnelles
        
        print(f"📊 Total suppressions: {total_deleted} lignes")