"""
Service crypto INTELLIGENT - Ne récupère QUE les prix nécessaires
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app import db
from app.models.crypto_price import CryptoPrice


class SmartCryptoService:
    """
    Service crypto intelligent qui ne récupère QUE les prix nécessaires.
    """
    
    BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
    EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest/USD"
    
    # Mapping symboles vers paires Binance
    SYMBOL_TO_BINANCE = {
        'bitcoin': 'BTCUSDT',
        'ethereum': 'ETHUSDT',
        'binancecoin': 'BNBUSDT',
        'solana': 'SOLUSDT',
        'cardano': 'ADAUSDT',
        'polkadot': 'DOTUSDT',
        'chainlink': 'LINKUSDT',
        'avalanche-2': 'AVAXUSDT',
        'cosmos': 'ATOMUSDT',
        'stellar': 'XLMUSDT'
    }
    
    @classmethod
    def get_usd_to_eur_rate(cls) -> float:
        """Récupère le taux USD->EUR en temps réel."""
        try:
            response = requests.get(cls.EXCHANGE_RATE_API, timeout=3)
            response.raise_for_status()
            return response.json()['rates']['EUR']
        except:
            return 0.92  # Fallback
    
    @classmethod
    def get_price_for_symbol(cls, symbol: str) -> Optional[float]:
        """
        Récupère le prix EUR pour UN SEUL symbole via Binance.
        
        Args:
            symbol: Le symbole crypto (ex: 'bitcoin', 'ethereum')
            
        Returns:
            Prix en EUR ou None si erreur
        """
        if symbol not in cls.SYMBOL_TO_BINANCE:
            print(f"❌ Symbole {symbol} non supporté")
            return None
            
        binance_symbol = cls.SYMBOL_TO_BINANCE[symbol]
        
        try:
            # Appel API pour UN SEUL symbole
            url = f"{cls.BINANCE_API_URL}?symbol={binance_symbol}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            price_usd = float(data['price'])
            
            # Conversion EUR
            eur_rate = cls.get_usd_to_eur_rate()
            price_eur = price_usd * eur_rate
            
            print(f"💰 {symbol}: ${price_usd:.2f} → €{price_eur:.2f}")
            return price_eur
            
        except Exception as e:
            print(f"❌ Erreur récupération prix {symbol}: {e}")
            return None
    
    @classmethod
    def get_cached_price(cls, symbol: str, max_age_minutes: int = 10) -> Optional[float]:
        """
        Récupère le prix en cache depuis la DB.
        
        Args:
            symbol: Le symbole crypto
            max_age_minutes: Âge max du prix en minutes
            
        Returns:
            Prix EUR ou None si pas trouvé/trop ancien
        """
        try:
            crypto_price = CryptoPrice.query.filter_by(symbol=symbol).first()
            
            if not crypto_price:
                return None
                
            # Vérifier l'âge
            age = datetime.utcnow() - crypto_price.updated_at
            if age > timedelta(minutes=max_age_minutes):
                print(f"⏰ Prix {symbol} trop ancien: {age}")
                return None
                
            return crypto_price.price_eur
            
        except Exception as e:
            print(f"❌ Erreur lecture cache {symbol}: {e}")
            return None
    
    @classmethod
    def get_fresh_price(cls, symbol: str) -> Optional[float]:
        """
        Récupère un prix frais : cache d'abord, sinon API.
        
        Args:
            symbol: Le symbole crypto
            
        Returns:
            Prix EUR
        """
        # 1. Essayer le cache d'abord
        cached_price = cls.get_cached_price(symbol, max_age_minutes=10)
        if cached_price is not None:
            print(f"📊 {symbol}: prix en cache €{cached_price:.2f}")
            return cached_price
        
        # 2. Sinon, appel API pour CE symbole uniquement
        print(f"🔄 {symbol}: récupération prix live...")
        live_price = cls.get_price_for_symbol(symbol)
        
        if live_price is not None:
            # Sauvegarder en cache
            cls.save_price_to_cache(symbol, live_price)
            
        return live_price
    
    @classmethod
    def save_price_to_cache(cls, symbol: str, price_eur: float):
        """Sauvegarde le prix en cache."""
        try:
            crypto_price = CryptoPrice.query.filter_by(symbol=symbol).first()
            
            if crypto_price:
                crypto_price.price_eur = price_eur
                crypto_price.price_usd = price_eur / cls.get_usd_to_eur_rate()
                crypto_price.updated_at = datetime.utcnow()
            else:
                crypto_price = CryptoPrice(
                    symbol=symbol,
                    price_eur=price_eur,
                    price_usd=price_eur / cls.get_usd_to_eur_rate(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(crypto_price)
            
            db.session.commit()
            print(f"💾 Prix {symbol} sauvé en cache")
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde cache {symbol}: {e}")
            db.session.rollback()
    
    @classmethod
    def get_portfolio_prices(cls, user_crypto_symbols: List[str]) -> Dict[str, float]:
        """
        Récupère les prix SEULEMENT pour les cryptos du portefeuille utilisateur.
        
        Args:
            user_crypto_symbols: Liste des symboles que possède l'utilisateur
            
        Returns:
            Dict {symbol: price_eur}
        """
        print(f"🎯 Récupération prix pour {len(user_crypto_symbols)} cryptos seulement")
        
        prices = {}
        
        for symbol in user_crypto_symbols:
            price = cls.get_fresh_price(symbol)
            if price is not None:
                prices[symbol] = price
            else:
                print(f"⚠️ Impossible de récupérer le prix pour {symbol}")
                prices[symbol] = 0.0  # Fallback
        
        print(f"✅ {len(prices)} prix récupérés")
        return prices