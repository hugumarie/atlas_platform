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
    
    # Mapping des symboles crypto vers Binance (liste complète)
    SYMBOL_TO_BINANCE = {
        # Top cryptos
        'bitcoin': 'BTCUSDT',
        'btc': 'BTCUSDT',
        'ethereum': 'ETHUSDT', 
        'eth': 'ETHUSDT',
        'binancecoin': 'BNBUSDT',
        'bnb': 'BNBUSDT',
        'ripple': 'XRPUSDT',
        'xrp': 'XRPUSDT',
        'solana': 'SOLUSDT',
        'sol': 'SOLUSDT',
        'cardano': 'ADAUSDT',
        'ada': 'ADAUSDT',
        'avalanche-2': 'AVAXUSDT',
        'avax': 'AVAXUSDT',
        'dogecoin': 'DOGEUSDT',
        'doge': 'DOGEUSDT',
        'tron': 'TRXUSDT',
        'trx': 'TRXUSDT',
        'polkadot': 'DOTUSDT',
        'dot': 'DOTUSDT',
        
        # DeFi & Infrastructure
        'chainlink': 'LINKUSDT',
        'link': 'LINKUSDT',
        'uniswap': 'UNIUSDT',
        'uni': 'UNIUSDT',
        'aave': 'AAVEUSDT',
        'compound-governance-token': 'COMPUSDT',
        'comp': 'COMPUSDT',
        'maker': 'MKRUSDT',
        'mkr': 'MKRUSDT',
        'sushiswap': 'SUSHIUSDT',
        'sushi': 'SUSHIUSDT',
        'curve-dao-token': 'CRVUSDT',
        'crv': 'CRVUSDT',
        '1inch': '1INCHUSDT',
        
        # Stablecoins
        'tether': 'USDCUSDT',  # Note: USDT pair contre USDC
        'usdt': 'USDCUSDT',
        'usd-coin': 'USDCUSDT',
        'usdc': 'USDCUSDT',
        'binance-usd': 'BUSDUSDT',
        'busd': 'BUSDUSDT',
        'dai': 'DAIUSDT',
        'terrausd': 'USTUSDT',
        'ust': 'USTUSDT',
        
        # Gaming & NFT
        'axie-infinity': 'AXSUSDT',
        'axs': 'AXSUSDT',
        'the-sandbox': 'SANDUSDT',
        'sand': 'SANDUSDT',
        'decentraland': 'MANAUSDT',
        'mana': 'MANAUSDT',
        'enjincoin': 'ENJUSDT',
        'enj': 'ENJUSDT',
        'gala': 'GALAUSDT',
        'flow': 'FLOWUSDT',
        
        # Altcoins Populaires
        'litecoin': 'LTCUSDT',
        'ltc': 'LTCUSDT',
        'bitcoin-cash': 'BCHUSDT',
        'bch': 'BCHUSDT',
        'ethereum-classic': 'ETCUSDT',
        'etc': 'ETCUSDT',
        'monero': 'XMRUSDT',
        'xmr': 'XMRUSDT',
        'zcash': 'ZECUSDT',
        'zec': 'ZECUSDT',
        'dash': 'DASHUSDT',
        'neo': 'NEOUSDT',
        'iota': 'IOTAUSDT',
        'miota': 'IOTAUSDT',
        
        # Autres projets
        'polygon': 'MATICUSDT',
        'matic': 'MATICUSDT',
        'fantom': 'FTMUSDT',
        'ftm': 'FTMUSDT',
        'cosmos': 'ATOMUSDT',
        'atom': 'ATOMUSDT',
        'algorand': 'ALGOUSDT',
        'algo': 'ALGOUSDT',
        'vechain': 'VETUSDT',
        'vet': 'VETUSDT',
        'theta-token': 'THETAUSDT',
        'theta': 'THETAUSDT',
        'filecoin': 'FILUSDT',
        'fil': 'FILUSDT',
        'internet-computer': 'ICPUSDT',
        'icp': 'ICPUSDT',
        'hedera-hashgraph': 'HBARUSDT',
        'hbar': 'HBARUSDT',
        'elrond-egd-2': 'EGLDUSDT',
        'egld': 'EGLDUSDT',
        
        # Autres cryptos supportées
        'stellar': 'XLMUSDT',
        'xlm': 'XLMUSDT',
        
        # Top 50 cryptos supplémentaires (seulement les pairs existantes sur Binance)
        'wrapped-bitcoin': 'WBTCUSDT',
        'shiba-inu': 'SHIBUSDT',
        'near': 'NEARUSDT',
        'aptos': 'APTUSDT',
        'arbitrum': 'ARBUSDT',
        'first-digital-usd': 'FDUSDUSDT',
        'optimism': 'OPUSDT',
        'immutable-x': 'IMXUSDT',
        'render-token': 'RNDRUSDT',
        'the-graph': 'GRTUSDT',
        'injective-protocol': 'INJUSDT',
        'sei-network': 'SEIUSDT',
        'bittensor': 'TAOUSDT',
        'rune': 'RUNEUSDT',
        'stacks': 'STXUSDT'
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
            # 1. Récupérer le taux USD/EUR
            usd_to_eur = cls.get_usd_to_eur_rate()
            
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
            missing_pairs = []
            
            for crypto_symbol, binance_pair in cls.SYMBOL_TO_BINANCE.items():
                if binance_pair in binance_prices:
                    price_usd = binance_prices[binance_pair]
                    price_eur = price_usd * usd_to_eur
                    prices[crypto_symbol] = price_eur
                else:
                    missing_pairs.append(f"{crypto_symbol} -> {binance_pair}")
            
            
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
            
            db.session.commit()
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
            
            # Protection contre les erreurs de session DB en cours
            from sqlalchemy.exc import InvalidRequestError, PendingRollbackError
            try:
                crypto_price = CryptoPrice.query.filter_by(symbol=symbol).first()
            except (InvalidRequestError, PendingRollbackError):
                # Session DB corrompue, ne pas essayer de lire
                return None
            
            if not crypto_price:
                return None
            
            # Vérifier l'âge des données
            max_age = timedelta(minutes=max_age_minutes)
            age = datetime.utcnow() - crypto_price.updated_at
            
            if age > max_age:
                # Prix trop ancien (silencieux pendant les erreurs DB)
                return None
            
            return crypto_price.price_eur
            
        except Exception as e:
            # Suppression du log pour éviter le spam pendant les erreurs DB
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
                # Prix pas trouvé/trop ancien, utiliser valeur de cache étendue (24h) SILENCIEUSEMENT
                price = cls.get_crypto_price_from_db(symbol, max_age_minutes=1440)  # 24h cache
            
            if price is not None:
                result[symbol] = price
            # Suppression des logs pour éviter le spam pendant les erreurs DB
        
        return result
    
    @classmethod
    def get_supported_symbols(cls) -> List[str]:
        """
        Retourne la liste des symboles crypto supportés.
        
        Returns:
            List[str]: Liste des symboles
        """
        return list(cls.SYMBOL_TO_BINANCE.keys())