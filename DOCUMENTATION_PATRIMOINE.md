# 📊 DOCUMENTATION SYSTÈME PATRIMONIAL

**Date de mise à jour :** 09 décembre 2024  
**Version :** 2.0 - Refonte complète avec calculs d'amortissement précis

---

## 🎯 RÉSUMÉ DES CHANGEMENTS MAJEURS

### ❌ **AVANT (Problèmes identifiés)**
- Calculs patrimoniaux incorrects (valeurs hardcodées : 37,118€)
- JavaScript écrasait les valeurs backend
- Pas de calcul d'amortissement précis pour l'immobilier
- Prix crypto non intégrés correctement
- Logs de debug polluant l'interface

### ✅ **APRÈS (Solution implémentée)**
- **Nouveau service centralisé** : `PatrimonyCalculationEngine`
- **Calculs d'amortissement précis** avec `CreditCalculationService`
- **Valeurs correctes** : 36,380.59€ (calcul réel vs estimation)
- **Prix crypto automatisés** via API Binance
- **Interface propre** sans debug
- **Système extensible** pour nouvelles cryptomonnaies

---

## 🏗️ ARCHITECTURE SYSTÈME PATRIMONIAL

### **1. Service Central : `PatrimonyCalculationEngine`**

**Fichier :** `/app/services/patrimony_calculation_engine.py`

**Responsabilités :**
- Calcul de TOUS les totaux patrimoniaux
- Sauvegarde automatique en base de données
- Intégration avec les services externes (crypto, crédit)
- Gestion de la cohérence des données

**Formules principales :**
```
TOTAL ÉPARGNE & PATRIMOINE = Liquidités + Placements Financiers + Immobilier Net + Cryptos + Autres Biens

PATRIMOINE TOTAL NET = TOTAL ÉPARGNE & PATRIMOINE - Crédits à rembourser
```

### **2. Calculs de Crédit : `CreditCalculationService`**

**Fichier :** `/app/services/credit_calculation.py`

**Formules d'amortissement :**
```python
# Mensualité
M = P * [r(1+r)^n] / [(1+r)^n - 1]

# Capital restant dû (formule précise)
CRD = P * [(1+r)^n - (1+r)^m] / [(1+r)^n - 1]

Où :
- P = Capital initial
- r = Taux mensuel (taux_annuel / 100 / 12)
- n = Durée totale en mois
- m = Mois écoulés
```

### **3. Prix Crypto : `BinancePriceService`**

**Fichier :** `/app/services/binance_price_service.py`

**Fonctionnalités :**
- Récupération temps réel via API Binance
- Conversion automatique USD → EUR
- Support de 28+ cryptomonnaies
- Cache intelligent (5 minutes)

---

## 📊 STRUCTURE BASE DE DONNÉES

### **Modèle : `InvestorProfile`**

**Fichier :** `/app/models/investor_profile.py`

#### **Colonnes de calcul (nouvelles) :**
```python
# Totaux calculés et sauvegardés
calculated_total_liquidites = db.Column(db.Float)           # Total liquidités
calculated_total_placements = db.Column(db.Float)          # Total placements
calculated_total_immobilier_net = db.Column(db.Float)      # Immobilier net (CORRIGÉ)
calculated_total_cryptomonnaies = db.Column(db.Float)      # Total crypto
calculated_total_autres_biens = db.Column(db.Float)        # Autres biens
calculated_total_credits_consommation = db.Column(db.Float) # Crédits
calculated_total_actifs = db.Column(db.Float)              # TOTAL ÉPARGNE & PATRIMOINE
calculated_patrimoine_total_net = db.Column(db.Float)      # PATRIMOINE NET
last_calculation_date = db.Column(db.DateTime)             # Horodatage
```

#### **Données JSON (existantes) :**
```python
# Données détaillées
immobilier_data_json = db.Column(JSONB)        # Biens immobiliers détaillés
cryptomonnaies_data_json = db.Column(JSONB)    # Cryptos avec prix
autres_biens_data_json = db.Column(JSONB)      # Autres biens
credits_data_json = db.Column(JSONB)           # Crédits détaillés
```

---

## 🧮 DÉTAIL DES CALCULS

### **1. LIQUIDITÉS**
```python
def _calculate_liquidites(cls, profile):
    total = Decimal('0')
    total += Decimal(str(profile.livret_a_value or 0))
    total += Decimal(str(profile.ldds_value or 0))
    total += Decimal(str(profile.pel_cel_value or 0))
    total += Decimal(str(profile.current_savings or 0))
    
    # Liquidités personnalisées (JSONB)
    if profile.liquidites_personnalisees_data:
        for liquidite in profile.liquidites_personnalisees_data:
            total += Decimal(str(liquidite.get('amount', 0)))
    
    return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
```

### **2. PLACEMENTS FINANCIERS**
```python
def _calculate_placements_financiers(cls, profile):
    total = Decimal('0')
    total += Decimal(str(profile.pea_value or 0))
    total += Decimal(str(profile.per_value or 0))
    total += Decimal(str(profile.life_insurance_value or 0))
    total += Decimal(str(profile.cto_value or 0))
    total += Decimal(str(profile.pee_value or 0))
    
    # Placements personnalisés (JSONB)
    if profile.placements_personnalises_data:
        for placement in profile.placements_personnalises_data:
            total += Decimal(str(placement.get('amount', 0)))
    
    return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
```

### **3. PATRIMOINE IMMOBILIER NET (CORRIGÉ)**
```python
def _calculate_patrimoine_immobilier_net_correct(cls, profile):
    valeur_totale = Decimal('0')
    capital_restant_total = Decimal('0')
    
    if profile.immobilier_data:
        for bien in profile.immobilier_data:
            # Valeur du bien
            valeur_bien = Decimal(str(bien.get('valeur', 0)))
            valeur_totale += valeur_bien
            
            # Si crédit associé
            if bien.get('has_credit', False):
                montant_initial = float(bien.get('credit_montant', 0))
                taux_interet = float(bien.get('credit_taeg', 0))  # TAEG en %
                duree_annees = int(bien.get('credit_duree', 0))   # En années
                duree_mois = duree_annees * 12
                
                # Parse date début
                date_debut_str = bien.get('credit_date', '')  # Format: "2025-10"
                date_debut = parse_credit_date(date_debut_str)
                
                # CALCUL PRÉCIS avec CreditCalculationService
                if montant_initial > 0 and duree_mois > 0:
                    capital_restant_reel = CreditCalculationService.calculate_remaining_capital(
                        principal=montant_initial,
                        annual_rate=taux_interet,
                        duration_months=duree_mois,
                        start_date=date_debut,
                        current_date=date.today()
                    )
                    capital_restant_total += Decimal(str(capital_restant_reel))
    
    # Patrimoine Net = Valeur totale - Capital restant RÉEL
    patrimoine_net = valeur_totale - capital_restant_total
    return patrimoine_net.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
```

**🔑 DIFFÉRENCE CLÉ :**
- **AVANT :** `valeur_nette = 250000 - 215000 = 35000€` (montant initial)
- **APRÈS :** `valeur_nette = 250000 - 213619.41 = 36380.59€` (capital restant après 3 mois de paiements)

### **4. CRYPTOMONNAIES**
```python
def _calculate_total_cryptomonnaies(cls, profile):
    total = Decimal('0')
    
    if profile.cryptomonnaies_data:
        # Récupérer prix depuis base de données (mis à jour via Binance)
        prix_cryptos = cls._get_crypto_prices_from_db()
        
        cryptos_updated = []
        for crypto in profile.cryptomonnaies_data:
            symbol = crypto.get('symbol', '').lower()
            quantity = Decimal(str(crypto.get('quantity', 0)))
            
            if quantity > 0 and symbol in prix_cryptos:
                price_eur = Decimal(str(prix_cryptos[symbol]))
                valeur_calculee = quantity * price_eur
                
                # Mettre à jour les données crypto avec prix actuel
                crypto_copy = dict(crypto)
                crypto_copy['current_price'] = float(price_eur)
                crypto_copy['calculated_value'] = float(valeur_calculee)
                crypto_copy['last_updated'] = datetime.utcnow().isoformat()
                
                total += valeur_calculee
                cryptos_updated.append(crypto_copy)
        
        # Sauvegarder immédiatement les cryptos mises à jour
        profile.set_cryptomonnaies_data(cryptos_updated)
    
    return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
```

### **5. AUTRES BIENS**
```python
def _calculate_total_autres_biens(cls, profile):
    total = Decimal('0')
    
    if profile.autres_biens_data:
        for bien in profile.autres_biens_data:
            valeur = bien.get('valeur', 0)
            total += Decimal(str(valeur))
    
    return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
```

### **6. CRÉDITS À REMBOURSER**
```python
def _calculate_total_credits(cls, profile):
    total = Decimal('0')
    
    if profile.credits_data:
        for credit in profile.credits_data:
            # Utiliser montant_restant si disponible, sinon montant_initial
            montant_restant = credit.get('montant_restant', credit.get('montant_initial', 0))
            total += Decimal(str(montant_restant))
    
    return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
```

---

## 🔄 PROCESSUS DE CALCUL

### **Point d'entrée principal :**
```python
from app.services.patrimony_calculation_engine import PatrimonyCalculationEngine

# Calcul complet et sauvegarde
results = PatrimonyCalculationEngine.calculate_and_save_all(
    investor_profile,
    force_recalculate=True,
    save_to_db=True
)
```

### **Intégration dans les routes :**

#### **Route Admin (`/app/routes/platform/admin.py`) :**
```python
@platform_admin_bp.route('/utilisateur/<int:user_id>')
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    
    # CALCUL AUTOMATIQUE à chaque affichage
    if user.investor_profile:
        totaux = PatrimonyCalculationEngine.calculate_and_save_all(
            user.investor_profile,
            force_recalculate=True,
            save_to_db=True
        )
    
    return render_template('platform/admin/user_detail.html', user=user, totaux=totaux)
```

#### **Route Édition :**
```python
@platform_admin_bp.route('/update-user-data/<int:user_id>', methods=['POST'])
def update_user_data(user_id):
    # Mise à jour des données utilisateur
    # ...
    
    # RECALCUL AUTOMATIQUE après modification
    totaux = PatrimonyCalculationEngine.calculate_and_save_all(
        user.investor_profile,
        force_recalculate=True,
        save_to_db=True
    )
    
    return redirect(url_for('platform_admin.user_detail', user_id=user.id))
```

---

## 💰 SYSTÈME CRYPTO

### **Service de prix :** `BinancePriceService`

#### **Cryptomonnaies supportées (28+) :**
```python
SYMBOL_TO_BINANCE = {
    'bitcoin': 'BTCUSDT',      'btc': 'BTCUSDT',
    'ethereum': 'ETHUSDT',     'eth': 'ETHUSDT', 
    'binancecoin': 'BNBUSDT',  'bnb': 'BNBUSDT',
    'solana': 'SOLUSDT',       'sol': 'SOLUSDT',
    'cardano': 'ADAUSDT',      'ada': 'ADAUSDT',
    'polkadot': 'DOTUSDT',     'dot': 'DOTUSDT',
    'matic-network': 'MATICUSDT', 'matic': 'MATICUSDT',
    'chainlink': 'LINKUSDT',   'link': 'LINKUSDT',
    'avalanche-2': 'AVAXUSDT', 'avax': 'AVAXUSDT',
    'cosmos': 'ATOMUSDT',      'atom': 'ATOMUSDT',
    'stellar': 'XLMUSDT',      'xlm': 'XLMUSDT',
    'vechain': 'VETUSDT',      'vet': 'VETUSDT',
    'algorand': 'ALGOUSDT',    'algo': 'ALGOUSDT',
    'hedera-hashgraph': 'HBARUSDT', 'hbar': 'HBARUSDT'
    # ... + autres cryptos
}
```

#### **Mise à jour automatique :**
```bash
# Script de mise à jour
python refresh_crypto_prices.py

# Intégré dans le démarrage Atlas
./start_atlas.sh  # Inclut automatiquement la mise à jour crypto
```

### **Cache intelligent :**
- Prix mis à jour automatiquement si > 5 minutes d'ancienneté
- Fallback sur prix en cache si API indisponible
- Taux USD→EUR récupéré en temps réel

---

## 🔧 CORRECTIONS FRONTEND

### **Problèmes JavaScript résolus :**

#### **1. updateImmobilierViewValues() - DÉSACTIVÉ**
```javascript
// AVANT : Calcul JavaScript incorrect
const valeurNette = valeur - capitalRestant;
valeurNetteDisplay.textContent = valeurNette + '€';  // 37,118€

// APRÈS : Utilise valeur backend
// const valeurNetteDisplay = viewItem.querySelector('.immobilier-valeur-nette-display');
// DÉSACTIVÉ pour éviter l'écrasement
```

#### **2. calculateTotalImmobilier() - DÉSACTIVÉ**
```javascript
// AVANT : Calcul total JavaScript
totalDisplay.textContent = total + '€';  // 37,118€

// APRÈS : Template utilise valeur backend
// const totalDisplay = document.getElementById('totalImmobilier');
// DÉSACTIVÉ
```

#### **3. calculateValeurNette() - CORRIGÉ**
```javascript
// AVANT : Calcul local
const valeurNette = valeurBien - capitalRestant;

// APRÈS : Utilise data-backend-value
const backendValue = parseFloat(valeurNetteValue.getAttribute('data-backend-value') || 0);
valeurNetteValue.textContent = backendValue.toFixed(0) + '€';  // 36,381€
```

### **Template HTML corrigé :**
```html
<!-- Valeur nette individuelle -->
<span class="valeur-nette-value" data-backend-value="{{ user.investor_profile.calculated_total_immobilier_net }}">
    {{ "{:,.0f}".format(user.investor_profile.calculated_total_immobilier_net) }}€
</span>

<!-- Total patrimoine immobilier -->
<span id="totalImmobilier">
    {{ "{:,.0f}".format(user.investor_profile.calculated_total_immobilier_net) }}€
</span>

<!-- Section visualisation -->
<span id="totalImmobilierView">
    {{ "{:,.0f}".format(user.investor_profile.calculated_total_immobilier_net) }}€
</span>
```

---

## 📈 EXEMPLE CONCRET

### **Cas d'usage : Hugues Marie (user_id=2)**

#### **Données immobilier :**
```json
{
    "type": "investissement_locatif",
    "valeur": 250000.0,
    "surface": 43.0,
    "has_credit": true,
    "credit_montant": 215000.0,
    "credit_taeg": 3.35,
    "credit_duree": 25,
    "credit_date": "2025-10"
}
```

#### **Calcul précis :**
```python
# Paramètres
montant_initial = 215000.0
taux_taeg = 3.35  # % annuel
duree_mois = 25 * 12 = 300 mois
date_debut = datetime(2025, 10, 1)
date_actuelle = datetime(2024, 12, 9)
mois_ecoules = 3  # Octobre, Novembre, Décembre

# Mensualité
mensualite = CreditCalculationService.calculate_monthly_payment(215000, 3.35, 300)
# = 1059.12€

# Capital restant (formule d'amortissement)
capital_restant = CreditCalculationService.calculate_remaining_capital(
    215000, 3.35, 300, date(2025, 10, 1), date.today()
)
# = 213619.41€

# Valeur nette CORRECTE
valeur_nette = 250000 - 213619.41 = 36380.59€
```

#### **Résultat patrimoine complet :**
```
💧 LIQUIDITÉS                 : 4,700.00€
📈 PLACEMENTS FINANCIERS      : 25,700.00€
🏠 PATRIMOINE IMMOBILIER NET  : 36,380.59€  ← CORRIGÉ
💎 CRYPTOMONNAIES             : 11,924.19€
💍 AUTRES BIENS               : 8,000.00€
────────────────────────────────────────
= TOTAL ÉPARGNE & PATRIMOINE  : 86,704.78€

💳 CRÉDITS À REMBOURSER       : 1,759.50€
────────────────────────────────────────
👑 PATRIMOINE TOTAL NET       : 84,945.28€
```

---

## 🚀 DÉMARRAGE ET MAINTENANCE

### **Script de démarrage intégré :**
```bash
./start_atlas.sh
```

**Séquence automatique :**
1. ✅ Vérification PostgreSQL
2. ✅ Test connexion base
3. ✅ **Mise à jour prix crypto** (nouveau)
4. ✅ Démarrage Flask

### **Maintenance des prix crypto :**
```bash
# Mise à jour manuelle
python refresh_crypto_prices.py

# Ajout nouvelle crypto
python scripts/add_new_crypto.py XRPUSDT ripple
```

### **Vérification système :**
- **Admin :** http://127.0.0.1:5001/plateforme/admin/utilisateur/2
- **Toutes les valeurs** doivent afficher 36,381€ (plus de 37,118€)
- **Logs silencieux** (plus de debug)

---

## 📝 NOTES TECHNIQUES

### **Précision décimale :**
- Utilisation de `Decimal` pour éviter erreurs d'arrondi
- Arrondi à 2 décimales : `ROUND_HALF_UP`
- Conversion float ↔ Decimal sécurisée

### **Gestion d'erreurs :**
- Try/catch sur tous les calculs
- Rollback base de données en cas d'erreur
- Valeurs par défaut (0) si données manquantes

### **Performance :**
- Calculs en mémoire puis sauvegarde groupée
- Cache crypto (5 min)
- Requêtes optimisées

### **Extensibilité :**
- Structure modulaire
- Ajout facile nouvelles cryptos
- Interface standardisée

---

## ⚠️ POINTS CRITIQUES

1. **Ne jamais utiliser les anciens calculs** (`patrimoine_calculation.py` legacy)
2. **Toujours passer par `PatrimonyCalculationEngine`** pour cohérence
3. **Vérifier que JavaScript ne surcharge pas** les valeurs backend
4. **Mettre à jour les prix crypto** avant calculs patrimoniaux
5. **Sauvegarder en base** après chaque calcul important

---

**📞 Support :** Ce système a été développé le 09/12/2024 avec calculs d'amortissement précis et intégration crypto automatisée.