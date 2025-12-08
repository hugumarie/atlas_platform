"""
Service pour récupérer les prix crypto depuis l'API Binance UNIQUEMENT.
Pas de CoinGecko, que du Binance pur.
"""

import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from app import db
from app.models.crypto_price import CryptoPrice


class BinancePriceService:
    """
    Service centralisé pour la gestion des prix crypto via Binance UNIQUEMENT.
    """
    
    BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/price"
    EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest/USD"
    
    # Mapping des symboles crypto vers Binance
    SYMBOL_TO_BINANCE = {
        'bitcoin': 'BTCUSDT',
        'btc': 'BTCUSDT',
        'ethereum': 'ETHUSDT', 
        'eth': 'ETHUSDT',
        'binancecoin': 'BNBUSDT',
        'bnb': 'BNBUSDT',
        'solana': 'SOLUSDT',
        'sol': 'SOLUSDT',
        'cardano': 'ADAUSDT',
        'ada': 'ADAUSDT',
        'polkadot': 'DOTUSDT',
        'dot': 'DOTUSDT',
        'matic-network': 'MATICUSDT',
        'matic': 'MATICUSDT',
        'chainlink': 'LINKUSDT',
        'link': 'LINKUSDT',
        'avalanche-2': 'AVAXUSDT',
        'avax': 'AVAXUSDT',
        'cosmos': 'ATOMUSDT',
        'atom': 'ATOMUSDT',
        'stellar': 'XLMUSDT',
        'xlm': 'XLMUSDT',
        'vechain': 'VETUSDT',
        'vet': 'VETUSDT',
        'algorand': 'ALGOUSDT',
        'algo': 'ALGOUSDT',
        'hedera-hashgraph': 'HBARUSDT',
        'hbar': 'HBARUSDT'
    }
    
    @classmethod 
    def get_usd_to_eur_rate(cls) -> float:
        """Récupère le taux de change USD vers EUR en temps réel."""
        try:
            response = requests.get(cls.EXCHANGE_RATE_API, timeout=5)
            response.raise_for_status()
            data = response.json()
            return data['rates']['EUR']
        except Exception as e:
            print(f"⚠️ Erreur taux change: {e}, utilisation taux fixe")
            return 0.92  # Fallback
    
    @classmethod
    def fetch_all_prices(cls) -> Dict[str, float]:
        """
        Récupère tous les prix depuis Binance et convertit en EUR.
        
        Returns:
            Dict: {"bitcoin": 78525.0, "ethereum": 3600.0, ...}
        """
        try:
            print(f"🔄 Récupération des prix Binance...")
            
            # 1. Récupérer le taux USD/EUR
            usd_to_eur = cls.get_usd_to_eur_rate()
            print(f"💱 Taux USD->EUR: {usd_to_eur:.4f}")
            
            # 2. Récupérer tous les prix Binance
            response = requests.get(cls.BINANCE_API_URL, timeout=10)
            response.raise_for_status()
            binance_data = response.json()
            
            # 3. Convertir en dict {pair: price_usd}
            binance_prices = {}
            for item in binance_data:
                binance_prices[item['symbol']] = float(item['price'])
            
            # 4. Convertir vers nos symboles avec prix EUR
            prices = {}
            for crypto_symbol, binance_pair in cls.SYMBOL_TO_BINANCE.items():
                if binance_pair in binance_prices:
                    price_usd = binance_prices[binance_pair]
                    price_eur = price_usd * usd_to_eur
                    prices[crypto_symbol] = price_eur
            
            print(f"✅ {len(prices)} prix récupérés depuis Binance")
            for symbol, price in prices.items():
                print(f"💰 {symbol}: €{price:.2f}")
            
            return prices
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur API Binance: {e}")
            return {}
        except Exception as e:
            print(f"❌ Erreur parsing Binance: {e}")
            return {}
    
    @classmethod
    def update_crypto_prices_in_db(cls) -> bool:
        """
        Met à jour tous les prix crypto en base depuis Binance.
        
        Returns:
            bool: True si succès, False sinon
        """
        try:
            # Récupérer les prix depuis Binance
            binance_prices = cls.fetch_all_prices()
            
            if not binance_prices:
                print("⚠️ Aucun prix récupéré de Binance")
                return False
            
            # Mettre à jour chaque crypto supportée
            updated_count = 0
            now = datetime.utcnow()
            
            for crypto_symbol in cls.SYMBOL_TO_BINANCE.keys():
                if crypto_symbol in binance_prices:
                    price_eur = binance_prices[crypto_symbol]
                    price_usd = price_eur / cls.get_usd_to_eur_rate()  # Conversion EUR->USD
                    
                    # Créer ou mettre à jour l'enregistrement
                    crypto_price = CryptoPrice.query.filter_by(symbol=crypto_symbol).first()
                    
                    if crypto_price:
                        crypto_price.price_usd = price_usd
                        crypto_price.price_eur = price_eur
                        crypto_price.updated_at = now
                    else:
                        crypto_price = CryptoPrice(
                            symbol=crypto_symbol,
                            price_usd=price_usd,
                            price_eur=price_eur,
                            updated_at=now
                        )
                        db.session.add(crypto_price)
                    
                    updated_count += 1
                    print(f"💰 {crypto_symbol}: €{price_eur:.2f}")
            
            db.session.commit()
            print(f"✅ {updated_count} prix crypto mis à jour en base")
            return True
            
        except Exception as e:
            print(f"❌ Erreur mise à jour DB crypto: {e}")
            db.session.rollback()
            return False
    
    @classmethod
    def get_crypto_price_from_db(cls, symbol: str, max_age_minutes: int = 5) -> Optional[float]:
        """
        Récupère le prix d'une crypto depuis la base de données.
        
        Args:
            symbol: Symbole de la crypto (ex: 'bitcoin', 'ethereum')
            max_age_minutes: Age maximum des données en minutes
            
        Returns:
            float: Prix en EUR ou None si pas trouvé/trop ancien
        """
        try:
            # Normaliser le symbole
            symbol = symbol.lower()
            
            crypto_price = CryptoPrice.query.filter_by(symbol=symbol).first()
            
            if not crypto_price:
                print(f"⚠️ Prix non trouvé en DB pour {symbol}")
                return None
            
            # Vérifier l'âge des données
            max_age = timedelta(minutes=max_age_minutes)
            age = datetime.utcnow() - crypto_price.updated_at
            
            if age > max_age:
                print(f"⚠️ Prix trop ancien pour {symbol}: {age}")
                return None
            
            return crypto_price.price_eur
            
        except Exception as e:
            print(f"❌ Erreur lecture DB crypto {symbol}: {e}")
            return None
    
    @classmethod
    def get_crypto_prices_for_symbols(cls, symbols: List[str], force_update: bool = False) -> Dict[str, float]:
        """
        Récupère les prix pour une liste de symboles crypto.
        
        Args:
            symbols: Liste des symboles crypto
            force_update: Force la mise à jour depuis l'API
            
        Returns:
            Dict: {symbol: price_eur}
        """
        result = {}
        
        # Si force_update, mettre à jour tous les prix
        if force_update:
            cls.update_crypto_prices_in_db()
        
        # Récupérer les prix pour chaque symbole
        for symbol in symbols:
            price = cls.get_crypto_price_from_db(symbol, max_age_minutes=5)
            
            if price is None and not force_update:
                # Prix pas trouvé/trop ancien, essayer une mise à jour
                print(f"🔄 Mise à jour nécessaire pour {symbol}")
                cls.update_crypto_prices_in_db()
                price = cls.get_crypto_price_from_db(symbol, max_age_minutes=1)
            
            if price is not None:
                result[symbol] = price
                print(f"💰 {symbol}: €{price:.2f}")
            else:
                print(f"❌ Prix indisponible pour {symbol}")
        
        return result
    
    @classmethod
    def get_supported_symbols(cls) -> List[str]:
        """
        Retourne la liste des symboles crypto supportés.
        
        Returns:
            List[str]: Liste des symboles
        """
        return list(cls.SYMBOL_TO_BINANCE.keys())