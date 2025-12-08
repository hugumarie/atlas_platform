"""
Service centralisé pour le refresh global des prix crypto.
Appelé UNIQUEMENT à la connexion utilisateur.
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models.crypto_price import CryptoPrice


class GlobalCryptoService:
    """
    Service centralisé pour gérer les prix crypto de toute la plateforme.
    Refresh global à la connexion, lecture DB partout ailleurs.
    """
    
    BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
    EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest/USD"
    
    # Symboles pertinents pour la plateforme (seulement ceux utilisés)
    PLATFORM_SYMBOLS = {
        'BTCUSDT': 'bitcoin',
        'ETHUSDT': 'ethereum', 
        'BNBUSDT': 'binancecoin',
        'SOLUSDT': 'solana',
        'ADAUSDT': 'cardano',
        'DOTUSDT': 'polkadot',
        'LINKUSDT': 'chainlink',
        'AVAXUSDT': 'avalanche-2',
        'ATOMUSDT': 'cosmos',
        'XLMUSDT': 'stellar'
    }
    
    @classmethod
    def needs_global_refresh(cls, max_age_minutes: int = 10) -> bool:
        """
        Vérifie si un refresh global est nécessaire.
        
        Args:
            max_age_minutes: Âge max des prix en minutes
            
        Returns:
            True si refresh nécessaire
        """
        try:
            # Trouver la date du dernier refresh global
            last_update = db.session.query(func.max(CryptoPrice.updated_at)).scalar()
            
            if not last_update:
                return True  # Aucun prix en base
                
            age = datetime.utcnow() - last_update
            needs_refresh = age > timedelta(minutes=max_age_minutes)
            
            if needs_refresh:
                print(f"🔄 Refresh nécessaire (âge: {age})")
            
            return needs_refresh
            
        except Exception as e:
            print(f"❌ Erreur check refresh: {e}")
            return True
    
    @classmethod
    def get_usd_to_eur_rate(cls) -> float:
        """Récupère le taux USD->EUR."""
        try:
            response = requests.get(cls.EXCHANGE_RATE_API, timeout=3)
            response.raise_for_status()
            return response.json()['rates']['EUR']
        except:
            return 0.92  # Fallback
    
    @classmethod
    def refresh_global_prices(cls) -> bool:
        """
        Refresh global de TOUS les prix de la plateforme.
        Appelé UNIQUEMENT à la connexion.
        
        Returns:
            True si succès
        """
        try:
            print("🌐 Refresh global des prix crypto...")
            
            # 1. Récupérer TOUS les prix depuis Binance (un seul appel)
            response = requests.get(cls.BINANCE_API_URL, timeout=10)
            response.raise_for_status()
            binance_data = response.json()
            
            # 2. Convertir en dict pour accès rapide
            binance_prices = {item['symbol']: float(item['price']) for item in binance_data}
            
            # 3. Récupérer taux de change
            eur_rate = cls.get_usd_to_eur_rate()
            
            # 4. Mettre à jour SEULEMENT les symboles de la plateforme
            now = datetime.utcnow()
            updated_count = 0
            
            for binance_symbol, our_symbol in cls.PLATFORM_SYMBOLS.items():
                if binance_symbol in binance_prices:
                    price_usd = binance_prices[binance_symbol]
                    price_eur = price_usd * eur_rate
                    
                    # Upsert en base
                    crypto_price = CryptoPrice.query.filter_by(symbol=our_symbol).first()
                    if crypto_price:
                        crypto_price.price_usd = price_usd
                        crypto_price.price_eur = price_eur
                        crypto_price.updated_at = now
                    else:
                        crypto_price = CryptoPrice(
                            symbol=our_symbol,
                            price_usd=price_usd,
                            price_eur=price_eur,
                            updated_at=now
                        )
                        db.session.add(crypto_price)
                    
                    updated_count += 1
            
            db.session.commit()
            print(f"✅ {updated_count} prix mis à jour globalement")
            return True
            
        except Exception as e:
            print(f"❌ Erreur refresh global: {e}")
            db.session.rollback()
            return False
    
    @classmethod
    def get_price_from_db(cls, symbol: str) -> Optional[float]:
        """
        Récupère le prix depuis la DB (pas d'API).
        
        Args:
            symbol: Symbole crypto (ex: 'bitcoin')
            
        Returns:
            Prix EUR ou None
        """
        try:
            crypto_price = CryptoPrice.query.filter_by(symbol=symbol).first()
            return crypto_price.price_eur if crypto_price else None
        except:
            return None
    
    @classmethod
    def recalculate_user_portfolio(cls, user_profile):
        """
        Recalcule le portefeuille crypto d'un utilisateur avec les prix en DB.
        Appelé à la connexion après refresh global.
        
        Args:
            user_profile: Profil investisseur de l'utilisateur
        """
        if not user_profile.cryptomonnaies_data:
            return
            
        total_value = 0
        now = datetime.utcnow()
        
        for crypto in user_profile.cryptomonnaies_data:
            symbol = crypto.get('symbol', '').lower()
            quantity = crypto.get('quantity', 0)
            
            if symbol and quantity > 0:
                # Récupérer le prix depuis la DB (pas d'API)
                price_eur = cls.get_price_from_db(symbol)
                
                if price_eur:
                    current_value = quantity * price_eur
                    total_value += current_value
                    
                    # Mettre à jour les données crypto
                    crypto['current_price'] = price_eur
                    crypto['calculated_value'] = round(current_value, 2)
                    crypto['last_updated'] = now.isoformat()
        
        # Sauvegarder les données enrichies
        try:
            user_profile.set_cryptomonnaies_data(user_profile.cryptomonnaies_data)
            user_profile.calculated_total_cryptomonnaies = round(total_value, 2)
            user_profile.last_calculation_date = now
            db.session.commit()
        except Exception as e:
            print(f"❌ Erreur sauvegarde portefeuille: {e}")
            db.session.rollback()
    
    @classmethod
    def refresh_at_login(cls, user):
        """
        Point d'entrée principal : appelé à la connexion utilisateur.
        
        Args:
            user: Utilisateur qui se connecte
        """
        try:
            # 1. Vérifier si refresh global nécessaire
            if cls.needs_global_refresh(max_age_minutes=10):
                cls.refresh_global_prices()
            
            # 2. Recalculer le portefeuille de cet utilisateur
            if user.investor_profile:
                cls.recalculate_user_portfolio(user.investor_profile)
                
        except Exception as e:
            print(f"❌ Erreur refresh login: {e}")