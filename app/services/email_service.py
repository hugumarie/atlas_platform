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
                   from_name: str = "Atlas") -> bool:
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
    
    # Contenu HTML de l'email de bienvenue avec nouveau design Atlas
    html_content = f"""
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <meta name="x-apple-disable-message-reformatting" />
  <title>Atlas</title>
</head>

<body style="margin:0;padding:0;background:#f2f4f5;">
  <div style="display:none;max-height:0;overflow:hidden;opacity:0;color:transparent;">
    Bienvenue chez Atlas – complétez votre profil investisseur.
  </div>

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f2f4f5;">
    <tr>
      <td align="center" style="padding:28px 16px;">
        <table role="presentation" width="640" cellpadding="0" cellspacing="0" style="max-width:640px;background:#ffffff;border-radius:18px;overflow:hidden;">

          <!-- Header -->
          <tr>
            <td align="center" style="background:#137C8B;padding:18px;">
              <div style="font-family:Arial,sans-serif;font-size:22px;font-weight:700;color:#ffffff;">
                Atlas
              </div>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:34px;">
              <div style="font-family:Arial,sans-serif;font-size:18px;line-height:28px;color:#3a3a3a;">

                <div style="font-weight:700;margin-bottom:16px;">
                  Bonjour {user.first_name},
                </div>

                <div style="margin-bottom:6px;font-size:20px;font-weight:700;">
                  Bienvenue chez <strong>Atlas</strong> 👋
                </div>

                <div style="margin-bottom:22px;">
                  Merci pour ta confiance, nous sommes <strong>ravis de t'accompagner</strong>.
                </div>

                <div style="margin-bottom:14px;font-weight:700;">
                  Avec ton abonnement, tu bénéficies :
                </div>

                <ul style="margin:0 0 26px 18px;padding:0;font-size:18px;line-height:28px;">
                  <li>d'un <strong>accompagnement pas à pas</strong> pour te lancer dans l'investissement</li>
                  <li>d'une <strong>stratégie adaptée à ta situation personnelle</strong></li>
                  <li>de <strong>contenus pédagogiques exclusifs</strong> pour mieux comprendre la finance et l'investissement</li>
                  <li>d'un <strong>tableau de bord clair</strong> pour suivre tes avancées et garder le cap</li>
                  <li>d'un <strong>conseiller de confiance</strong>, pédagogique et indépendant, pour t'orienter</li>
                </ul>

                <div style="margin-bottom:18px;">
                  Pour que nous puissions te proposer des recommandations réellement adaptées, il y a <strong>une seule étape à faire maintenant 👇</strong>
                </div>

                <!-- Button -->
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:22px 0 28px 0;">
                  <tr>
                    <td align="center">
                      <!--[if mso]>
                      <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" href="{profile_url}" style="height:54px;v-text-anchor:middle;width:360px;" arcsize="50%" stroke="f" fillcolor="#137C8B">
                        <w:anchorlock/>
                        <center style="color:#ffffff;font-family:Arial,sans-serif;font-size:18px;font-weight:bold;">
                          👉 Compléter ton profil investisseur
                        </center>
                      </v:roundrect>
                      <![endif]-->
                      <!--[if !mso]><!-- -->
                      <a href="{profile_url}"
                        style="display:inline-block;background:#137C8B;color:#ffffff;text-decoration:none;font-family:Arial,sans-serif;font-size:18px;font-weight:700;padding:16px 28px;border-radius:999px;">
                        👉 Compléter ton profil investisseur
                      </a>
                      <!--<![endif]-->
                    </td>
                  </tr>
                </table>

                <div style="margin-bottom:22px;">
                  Cela nous permet de comprendre ta situation, ton horizon d'investissement et ton <strong>profil de risque</strong>.  
                  Cela prend seulement quelques minutes ⏱️
                </div>

                <div>À tout de suite dans ton espace client,</div>
                <div style="font-weight:700;margin-bottom:20px;">L'équipe Atlas</div>

              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:0 34px 30px 34px;">
              <a href="https://atlas-invest.fr" style="font-family:Arial,sans-serif;color:#137C8B;text-decoration:underline;">
                https://atlas-invest.fr
              </a>

              <div style="margin-top:12px;">
                <img src="https://atlas-invest.fr/static/img/logo-atlas.png" alt="Atlas" style="height:32px;width:auto;vertical-align:middle;margin-right:12px;">
                <span style="display:inline-block;background:#137C8B;color:#ffffff;font-family:Arial,sans-serif;font-size:14px;font-weight:700;padding:10px 14px;border-radius:10px;vertical-align:middle;">
                  Atlas – le conseil financier clair et indépendant
                </span>
              </div>

              <div style="margin-top:20px;font-family:Arial,sans-serif;font-size:12px;color:#8a8a8a;">
                Cet email a été envoyé automatiquement, merci de ne pas y répondre.
              </div>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
    """
    
    # Version texte
    text_content = f"""
    Bonjour {user.first_name},
    
    Bienvenue chez Atlas 👋
    
    Merci pour ta confiance, nous sommes ravis de t'accompagner.
    
    Avec ton abonnement, tu bénéficies :
    - d'un accompagnement pas à pas pour te lancer dans l'investissement
    - d'une stratégie adaptée à ta situation personnelle
    - de contenus pédagogiques exclusifs pour mieux comprendre la finance et l'investissement
    - d'un tableau de bord clair pour suivre tes avancées et garder le cap
    - d'un conseiller de confiance, pédagogique et indépendant, pour t'orienter
    
    Pour que nous puissions te proposer des recommandations réellement adaptées, il y a une seule étape à faire maintenant :
    
    Compléter ton profil investisseur : {profile_url}
    
    Cela nous permet de comprendre ta situation, ton horizon d'investissement et ton profil de risque. Cela prend seulement quelques minutes.
    
    À tout de suite dans ton espace client,
    L'équipe Atlas
    """
    
    try:
        success = mailer.send_email(
            to_email=user.email,
            to_name=user.get_full_name(),
            subject="🚀 Bienvenue chez Atlas !",
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

def send_password_reset_email(user, reset_token):
    """
    Envoie un email de réinitialisation de mot de passe
    
    Args:
        user: Instance User
        reset_token: Token de réinitialisation
    """
    import os
    from flask import url_for, current_app
    
    # Récupérer l'API token depuis les variables d'environnement
    api_token = os.getenv('MAILERSEND_API_TOKEN')
    if not api_token:
        print("⚠️ MAILERSEND_API_TOKEN non configuré")
        return False
    
    mailer = MailerSendService(api_token)
    
    # Construire l'URL de réinitialisation
    with current_app.app_context():
        reset_url = url_for('platform_auth.reset_password', token=reset_token, _external=True)
    
    # Contenu HTML de l'email de réinitialisation avec design Atlas
    html_content = f"""
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <meta name="x-apple-disable-message-reformatting" />
  <title>Atlas</title>
</head>

<body style="margin:0;padding:0;background:#f2f4f5;">
  <div style="display:none;max-height:0;overflow:hidden;opacity:0;color:transparent;">
    Réinitialisez votre mot de passe Atlas en toute sécurité.
  </div>

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f2f4f5;">
    <tr>
      <td align="center" style="padding:28px 16px;">
        <table role="presentation" width="640" cellpadding="0" cellspacing="0" style="max-width:640px;background:#ffffff;border-radius:18px;overflow:hidden;">

          <!-- Header -->
          <tr>
            <td align="center" style="background:#137C8B;padding:18px;">
              <div style="font-family:Arial,sans-serif;font-size:22px;font-weight:700;color:#ffffff;">
                Atlas
              </div>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:34px;">
              <div style="font-family:Arial,sans-serif;font-size:18px;line-height:28px;color:#3a3a3a;">

                <div style="font-weight:700;margin-bottom:16px;">
                  Bonjour {user.first_name},
                </div>

                <div style="margin-bottom:6px;font-size:20px;font-weight:700;">
                  Réinitialisation de votre mot de passe 🔐
                </div>

                <div style="margin-bottom:22px;">
                  Nous avons reçu une demande de réinitialisation de mot de passe pour votre compte Atlas.
                </div>

                <div style="margin-bottom:18px;">
                  <strong>Cliquez sur le bouton ci-dessous pour créer un nouveau mot de passe :</strong>
                </div>

                <!-- Button -->
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:22px 0 28px 0;">
                  <tr>
                    <td align="center">
                      <!--[if mso]>
                      <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" href="{reset_url}" style="height:54px;v-text-anchor:middle;width:360px;" arcsize="50%" stroke="f" fillcolor="#137C8B">
                        <w:anchorlock/>
                        <center style="color:#ffffff;font-family:Arial,sans-serif;font-size:18px;font-weight:bold;">
                          🔑 Réinitialiser mon mot de passe
                        </center>
                      </v:roundrect>
                      <![endif]-->
                      <!--[if !mso]><!-- -->
                      <a href="{reset_url}"
                        style="display:inline-block;background:#137C8B;color:#ffffff;text-decoration:none;font-family:Arial,sans-serif;font-size:18px;font-weight:700;padding:16px 28px;border-radius:999px;">
                        🔑 Réinitialiser mon mot de passe
                      </a>
                      <!--<![endif]-->
                    </td>
                  </tr>
                </table>

                <div style="background:rgba(220,38,38,0.1);border:1px solid rgba(220,38,38,0.3);border-radius:12px;padding:16px;margin-bottom:22px;">
                  <div style="color:#991b1b;font-weight:600;margin-bottom:8px;">
                    ⚠️ Important - Sécurité
                  </div>
                  <div style="color:#991b1b;font-size:14px;line-height:1.6;">
                    • Ce lien expire dans <strong>24 heures</strong><br>
                    • Si vous n'avez pas demandé cette réinitialisation, ignorez cet email<br>
                    • Ne partagez jamais ce lien avec qui que ce soit
                  </div>
                </div>

                <div style="margin-bottom:14px;">
                  Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur :
                </div>
                
                <div style="word-break:break-all;font-family:monospace;background:#f3f4f6;padding:12px;border-radius:8px;font-size:14px;margin-bottom:22px;">
                  {reset_url}
                </div>

                <div>Cordialement,</div>
                <div style="font-weight:700;margin-bottom:20px;">L'équipe Atlas</div>

              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:0 34px 30px 34px;">
              <a href="https://atlas-invest.fr" style="font-family:Arial,sans-serif;color:#137C8B;text-decoration:underline;">
                https://atlas-invest.fr
              </a>

              <div style="margin-top:12px;">
                <img src="https://atlas-invest.fr/static/img/logo-atlas.png" alt="Atlas" style="height:32px;width:auto;vertical-align:middle;margin-right:12px;">
                <span style="display:inline-block;background:#137C8B;color:#ffffff;font-family:Arial,sans-serif;font-size:14px;font-weight:700;padding:10px 14px;border-radius:10px;vertical-align:middle;">
                  Atlas – le conseil financier clair et indépendant
                </span>
              </div>

              <div style="margin-top:20px;font-family:Arial,sans-serif;font-size:12px;color:#8a8a8a;">
                Cet email a été envoyé automatiquement, merci de ne pas y répondre.
              </div>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
    """
    
    # Version texte
    text_content = f"""
    Bonjour {user.first_name},
    
    Réinitialisation de votre mot de passe
    
    Nous avons reçu une demande de réinitialisation de mot de passe pour votre compte Atlas.
    
    Cliquez sur ce lien pour créer un nouveau mot de passe :
    {reset_url}
    
    IMPORTANT - Sécurité :
    - Ce lien expire dans 24 heures
    - Si vous n'avez pas demandé cette réinitialisation, ignorez cet email
    - Ne partagez jamais ce lien avec qui que ce soit
    
    Cordialement,
    L'équipe Atlas
    """
    
    try:
        success = mailer.send_email(
            to_email=user.email,
            to_name=user.get_full_name(),
            subject="🔐 Réinitialisation de votre mot de passe Atlas",
            html_content=html_content,
            text_content=text_content
        )
        
        if success:
            print(f"✅ Email de réinitialisation envoyé à {user.email}")
        else:
            print(f"❌ Échec envoi email de réinitialisation à {user.email}")
            
        return success
        
    except Exception as e:
        print(f"❌ Erreur envoi email de réinitialisation: {e}")
        return False