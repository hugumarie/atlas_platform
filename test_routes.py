#!/usr/bin/env python3
"""
Script de test pour vérifier les routes Atlas
"""

from app import create_app

def test_routes():
    print("🔍 Test des routes Atlas...")
    print("="*50)
    
    try:
        app = create_app()
        print("✅ Application créée avec succès")
        
        with app.app_context():
            print("\n📋 Routes disponibles:")
            for rule in app.url_map.iter_rules():
                print(f"  {rule.rule} -> {rule.endpoint}")
        
        print(f"\n🌐 Serveur de test sur http://127.0.0.1:5001")
        app.run(debug=True, host='127.0.0.1', port=5001)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_routes()