#!/usr/bin/env python3
"""
Script pour charger les variables d'environnement depuis .env
Usage: from load_env import load_env; load_env()
"""

import os
from pathlib import Path

def load_env(env_file=".env"):
    """Charge les variables d'environnement depuis un fichier .env"""
    env_path = Path(__file__).parent / env_file
    
    if not env_path.exists():
        print(f"⚠️ Fichier {env_file} non trouvé. Utilisez .env.example comme template.")
        return False
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    
    return True

def get_env(key, default=None):
    """Récupère une variable d'environnement avec valeur par défaut"""
    return os.environ.get(key, default)

def require_env(key):
    """Récupère une variable d'environnement obligatoire"""
    value = os.environ.get(key)
    if not value:
        raise ValueError(f"Variable d'environnement {key} manquante !")
    return value

if __name__ == "__main__":
    # Test du chargement
    if load_env():
        print("✅ Variables d'environnement chargées")
        print(f"🔧 FLASK_ENV: {get_env('FLASK_ENV', 'non défini')}")
        print(f"🌐 SERVER_IP: {get_env('SERVER_IP', 'non défini')}")
        print(f"📱 APP_NAME: {get_env('APP_NAME', 'non défini')}")
    else:
        print("❌ Erreur chargement variables d'environnement")