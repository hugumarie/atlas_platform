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
                   from_email: str = "noreply@atlas-finance.fr",
                   from_name: str = "Atlas Finance") -> bool:
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