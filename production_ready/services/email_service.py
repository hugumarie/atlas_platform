"""
Service d'envoi d'emails utilisant MailerSend API
Atlas - Plateforme de Gestion de Patrimoine
"""

import requests
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MailerSendService:
    """Service d'envoi d'emails avec MailerSend"""
    
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.mailersend.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def send_email(self, to_email, to_name, subject, html_content, text_content=None):
        """
        Envoie un email via MailerSend
        
        Args:
            to_email (str): Email du destinataire
            to_name (str): Nom du destinataire
            subject (str): Sujet de l'email
            html_content (str): Contenu HTML de l'email
            text_content (str): Contenu texte (optionnel)
            
        Returns:
            dict: Réponse de l'API MailerSend
        """
        url = f"{self.base_url}/email"
        
        # Construction du payload
        payload = {
            "from": {
                "email": "atlas@test-xkjn41mx7dp4z781.mlsender.net",
                "name": "Atlas - Gestion de Patrimoine"
            },
            "to": [
                {
                    "email": to_email,
                    "name": to_name
                }
            ],
            "subject": subject,
            "html": html_content
        }
        
        # Ajout du contenu texte si fourni
        if text_content:
            payload["text"] = text_content
        
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(payload))
            
            if response.status_code == 202:
                logger.info(f"Email envoyé avec succès à {to_email}")
                return {
                    "success": True,
                    "message": "Email envoyé avec succès",
                    "response": response.json() if response.content else {}
                }
            else:
                logger.error(f"Erreur lors de l'envoi d'email: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "message": f"Erreur {response.status_code}: {response.text}",
                    "response": response.json() if response.content else {}
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur de connexion à MailerSend: {str(e)}")
            return {
                "success": False,
                "message": f"Erreur de connexion: {str(e)}",
                "response": {}
            }
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'envoi d'email: {str(e)}")
            return {
                "success": False,
                "message": f"Erreur inattendue: {str(e)}",
                "response": {}
            }
    
    def send_prospect_invitation(self, prospect_email, prospect_name, signup_url, token):
        """
        Envoie une invitation de création de compte à un prospect
        
        Args:
            prospect_email (str): Email du prospect
            prospect_name (str): Nom complet du prospect
            signup_url (str): URL de création de compte
            token (str): Token d'invitation
            
        Returns:
            dict: Réponse de l'envoi d'email
        """
        subject = f"🎯 Bienvenue chez Atlas, {prospect_name.split()[0]} !"
        
        # Contenu HTML de l'email
        html_content = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Bienvenue chez Atlas</title>
            <style>
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                    line-height: 1.6;
                    color: #344D59;
                    margin: 0;
                    padding: 0;
                    background: #f8f9fa;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 16px;
                    overflow: hidden;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #137C8B 0%, #709CA7 100%);
                    padding: 40px 32px;
                    text-align: center;
                    color: white;
                    position: relative;
                }}
                .header::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>') repeat;
                    opacity: 0.3;
                }}
                .logo {{
                    position: relative;
                    z-index: 2;
                    display: inline-flex;
                    align-items: center;
                    gap: 12px;
                    margin-bottom: 20px;
                }}
                .logo-icon {{
                    width: 48px;
                    height: 48px;
                    background: rgba(255, 255, 255, 0.2);
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 24px;
                    font-weight: 700;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                }}
                .logo-text {{
                    font-size: 28px;
                    font-weight: 700;
                    letter-spacing: -0.025em;
                }}
                .title {{
                    position: relative;
                    z-index: 2;
                    font-size: 32px;
                    font-weight: 800;
                    margin: 0 0 8px 0;
                    letter-spacing: -0.025em;
                }}
                .subtitle {{
                    position: relative;
                    z-index: 2;
                    font-size: 16px;
                    opacity: 0.9;
                    margin: 0;
                }}
                .content {{
                    padding: 40px 32px;
                }}
                .greeting {{
                    font-size: 18px;
                    font-weight: 600;
                    color: #137C8B;
                    margin-bottom: 24px;
                }}
                .message {{
                    font-size: 16px;
                    margin-bottom: 32px;
                    line-height: 1.7;
                }}
                .cta-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #137C8B 0%, #709CA7 100%);
                    color: white;
                    text-decoration: none;
                    padding: 16px 32px;
                    border-radius: 12px;
                    font-weight: 600;
                    font-size: 16px;
                    text-align: center;
                    margin: 24px 0;
                    box-shadow: 0 6px 20px rgba(19, 124, 139, 0.3);
                    transition: all 0.3s ease;
                }}
                .cta-button:hover {{
                    background: linear-gradient(135deg, #0f6b75 0%, #5d8a94 100%);
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(19, 124, 139, 0.4);
                }}
                .features {{
                    background: #f8f9fa;
                    border-radius: 12px;
                    padding: 24px;
                    margin: 32px 0;
                }}
                .features h3 {{
                    color: #137C8B;
                    font-size: 18px;
                    margin: 0 0 16px 0;
                }}
                .feature-list {{
                    list-style: none;
                    padding: 0;
                    margin: 0;
                }}
                .feature-list li {{
                    padding: 8px 0;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }}
                .feature-list li::before {{
                    content: '✓';
                    background: #137C8B;
                    color: white;
                    width: 20px;
                    height: 20px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .footer {{
                    background: #344D59;
                    color: white;
                    padding: 32px;
                    text-align: center;
                    font-size: 14px;
                }}
                .footer a {{
                    color: #B8CBD0;
                    text-decoration: none;
                }}
                @media (max-width: 600px) {{
                    .container {{
                        margin: 16px;
                        border-radius: 12px;
                    }}
                    .content {{
                        padding: 24px 20px;
                    }}
                    .header {{
                        padding: 32px 20px;
                    }}
                    .title {{
                        font-size: 28px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">
                        <div class="logo-icon">A</div>
                        <span class="logo-text">Atlas</span>
                    </div>
                    <h1 class="title">Bienvenue chez Atlas</h1>
                    <p class="subtitle">Votre partenaire en gestion de patrimoine</p>
                </div>
                
                <div class="content">
                    <div class="greeting">Bonjour {prospect_name} 👋</div>
                    
                    <div class="message">
                        <p>Nous sommes ravis de vous accueillir dans la communauté <strong>Atlas</strong> ! 🎉</p>
                        
                        <p>Après notre échange, nous avons le plaisir de vous inviter à créer votre compte personnel sur notre plateforme de gestion de patrimoine. Atlas vous permettra de :</p>
                    </div>
                    
                    <div class="features">
                        <h3>🎯 Vos avantages Atlas</h3>
                        <ul class="feature-list">
                            <li>Visualiser votre patrimoine global en temps réel</li>
                            <li>Accéder à des plans d'investissement personnalisés</li>
                            <li>Suivre l'évolution de vos actifs automatiquement</li>
                            <li>Bénéficier de conseils d'experts en gestion patrimoniale</li>
                            <li>Optimiser votre stratégie d'investissement</li>
                        </ul>
                    </div>
                    
                    <p style="text-align: center; margin: 32px 0;">
                        <a href="{signup_url}?token={token}" class="cta-button">
                            🚀 Créer mon compte Atlas
                        </a>
                    </p>
                    
                    <div class="message">
                        <p><strong>Cette invitation est personnalisée</strong> et vous donne accès direct à la création de votre compte. Votre adresse email est déjà pré-remplie pour simplifier le processus.</p>
                        
                        <p>Si vous avez des questions ou besoin d'assistance, n'hésitez pas à nous contacter. Notre équipe est là pour vous accompagner dans cette nouvelle étape ! 💪</p>
                        
                        <p style="margin-top: 32px; font-style: italic; color: #7A90A4;">
                            À très bientôt sur Atlas,<br>
                            L'équipe Atlas 🌟
                        </p>
                    </div>
                </div>
                
                <div class="footer">
                    <p>© 2024 Atlas - Plateforme de Gestion de Patrimoine</p>
                    <p>
                        <a href="#">Conditions d'utilisation</a> • 
                        <a href="#">Politique de confidentialité</a> • 
                        <a href="#">Nous contacter</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Contenu texte alternatif
        text_content = f"""
        Bienvenue chez Atlas !
        
        Bonjour {prospect_name},
        
        Nous sommes ravis de vous accueillir dans la communauté Atlas !
        
        Après notre échange, nous avons le plaisir de vous inviter à créer votre compte personnel sur notre plateforme de gestion de patrimoine.
        
        Atlas vous permettra de :
        ✓ Visualiser votre patrimoine global en temps réel
        ✓ Accéder à des plans d'investissement personnalisés
        ✓ Suivre l'évolution de vos actifs automatiquement
        ✓ Bénéficier de conseils d'experts en gestion patrimoniale
        ✓ Optimiser votre stratégie d'investissement
        
        Créez votre compte Atlas : {signup_url}?token={token}
        
        Cette invitation est personnalisée et vous donne accès direct à la création de votre compte.
        
        Si vous avez des questions, n'hésitez pas à nous contacter.
        
        À très bientôt sur Atlas,
        L'équipe Atlas
        
        © 2024 Atlas - Plateforme de Gestion de Patrimoine
        """
        
        return self.send_email(
            to_email=prospect_email,
            to_name=prospect_name,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )


# Instance du service avec le token de test
mailer_send_service = MailerSendService("mlsn.c07089a1533a350ffe3c5430eda53efd48be1cfa29ec0da10839456535c46d94")