"""
Service d'envoi d'emails via MailerSend
"""

import requests
import json
from typing import Optional

class MailerSendService:
    """Service d'envoi d'emails via l'API MailerSend"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.mailersend.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def send_email(self, to_email: str, to_name: str, subject: str, 
                   html_content: str, text_content: str, 
                   from_email: str = "noreply@atlas-invest.fr",
                   from_name: str = "Atlas Invest") -> bool:
        """
        Envoie un email via MailerSend
        
        Args:
            to_email: Email du destinataire
            to_name: Nom du destinataire
            subject: Sujet de l'email
            html_content: Contenu HTML
            text_content: Contenu texte
            from_email: Email expéditeur
            from_name: Nom expéditeur
            
        Returns:
            bool: True si envoyé avec succès, False sinon
        """
        
        payload = {
            "from": {
                "email": from_email,
                "name": from_name
            },
            "to": [
                {
                    "email": to_email,
                    "name": to_name
                }
            ],
            "subject": subject,
            "text": text_content,
            "html": html_content
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/email",
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 202:
                print(f"Email envoyé avec succès à {to_email}")
                return True
            else:
                print(f"Erreur envoi email: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Erreur lors de l'envoi d'email: {e}")
            return False

def send_welcome_email(user):
    """
    Envoie un email de bienvenue après activation de l'abonnement
    
    Args:
        user: Instance User avec abonnement actif
    """
    import os
    from flask import url_for, current_app
    
    # Récupérer l'API token depuis les variables d'environnement
    api_token = os.getenv('MAILERSEND_API_TOKEN')
    if not api_token:
        print("⚠️ MAILERSEND_API_TOKEN non configuré")
        return False
    
    mailer = MailerSendService(api_token)
    
    # Construire l'URL pour compléter le profil (questionnaire)
    with current_app.app_context():
        profile_url = url_for('platform_investor.investor_data', edit='true', _external=True)
    
    # Contenu HTML de l'email
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #1a365d; margin-bottom: 10px;">Bienvenue chez Atlas 👋</h1>
        </div>
        
        <p>Bonjour {user.first_name},</p>
        
        <p>Bienvenue chez Atlas 👋</p>
        
        <p>Avec ton abonnement, tu bénéficies :</p>
        <ul style="line-height: 1.6;">
            <li>D'un accompagnement pas à pas pour te lancer dans l'investissement</li>
            <li>D'une stratégie adaptée à ta situation personnelle</li>
            <li>De contenus pédagogiques exclusifs pour mieux comprendre la finance et l'investissement</li>
            <li>D'un tableau de bord clair pour suivre tes avancées et garder le cap</li>
            <li>D'un conseiller de confiance, pédagogique et indépendant, pour t'orienter</li>
        </ul>
        
        <p>Pour que nous puissions te recommander des solutions réellement adaptées, il y a une seule étape à faire maintenant 👇</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{profile_url}" style="background-color: #3182ce; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                👉 Compléter mon profil investisseur
            </a>
        </div>
        
        <p>Cela nous permet de comprendre ta situation, ton horizon d'investissement et ton profil de risque. ⏱ Cela prend seulement quelques minutes.</p>
        
        <p>À tout de suite dans ton espace client,</p>
        <p><strong>L'équipe Atlas</strong></p>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #e2e8f0;">
        <p style="font-size: 12px; color: #718096; text-align: center;">
            Atlas Invest - Votre partenaire pour l'investissement
        </p>
    </div>
    """
    
    # Version texte
    text_content = f"""
    Bonjour {user.first_name},
    
    Bienvenue chez Atlas !
    
    Avec ton abonnement, tu bénéficies :
    - D'un accompagnement pas à pas pour te lancer dans l'investissement
    - D'une stratégie adaptée à ta situation personnelle
    - De contenus pédagogiques exclusifs pour mieux comprendre la finance et l'investissement
    - D'un tableau de bord clair pour suivre tes avancées et garder le cap
    - D'un conseiller de confiance, pédagogique et indépendant, pour t'orienter
    
    Pour que nous puissions te recommander des solutions réellement adaptées, il y a une seule étape à faire maintenant :
    
    Compléter ton profil investisseur : {profile_url}
    
    Cela nous permet de comprendre ta situation, ton horizon d'investissement et ton profil de risque. Cela prend seulement quelques minutes.
    
    À tout de suite dans ton espace client,
    L'équipe Atlas
    """
    
    try:
        success = mailer.send_email(
            to_email=user.email,
            to_name=user.get_full_name(),
            subject="Bienvenue chez Atlas ! 🚀",
            html_content=html_content,
            text_content=text_content
        )
        
        if success:
            print(f"✅ Email de bienvenue envoyé à {user.email}")
        else:
            print(f"❌ Échec envoi email de bienvenue à {user.email}")
            
        return success
        
    except Exception as e:
        print(f"❌ Erreur envoi email de bienvenue: {e}")
        return False