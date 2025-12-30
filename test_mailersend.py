#!/usr/bin/env python3
"""
Script de test pour vérifier l'envoi d'emails MailerSend
"""

import os
import sys
sys.path.append('.')

from app.services.email_service import MailerSendService

def test_email():
    """Teste l'envoi d'un email via MailerSend"""
    
    # Token depuis .env
    api_token = "mlsn.9e9b282d3af43d5d17dcf35d4a27c3a485b2716ebf698ff66aca8c73a55f0a2c"
    
    print("🧪 TEST MAILERSEND")
    print("==================")
    print(f"Token: {api_token[:20]}...")
    print()
    
    try:
        # Créer le service
        mailer = MailerSendService(api_token)
        
        # Envoi de test
        success = mailer.send_email(
            to_email="hugues.marie925@gmail.com",
            to_name="Hugues Marie",
            subject="🧪 Test Atlas - MailerSend",
            html_content="""
            <h2>Test Atlas MailerSend ✅</h2>
            <p>Salut Hugues,</p>
            <p>Ce test confirme que MailerSend fonctionne correctement avec Atlas !</p>
            <ul>
                <li>✅ Token API valide</li>
                <li>✅ Domaine atlas-invest.fr vérifié</li>
                <li>✅ Service email opérationnel</li>
            </ul>
            <p>Ton équipe de dev 🤖</p>
            """,
            text_content="Test Atlas - MailerSend fonctionne ! Token valide, domaine vérifié, service opérationnel.",
            from_email="noreply@atlas-invest.fr",
            from_name="Atlas Test"
        )
        
        if success:
            print("✅ EMAIL ENVOYÉ AVEC SUCCÈS !")
            print("📧 Vérifie ta boîte mail: hugues.marie925@gmail.com")
        else:
            print("❌ ÉCHEC ENVOI EMAIL")
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")

if __name__ == '__main__':
    test_email()