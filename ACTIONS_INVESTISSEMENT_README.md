# 📈 Module Actions d'Investissement - Guide de Test

## 🎯 Vue d'ensemble

Le module "Actions d'Investissement" permet aux utilisateurs de suivre et valider leurs investissements mensuels basés sur leur plan d'investissement personnalisé. Il génère automatiquement des actions à réaliser chaque mois et permet un suivi précis de la progression.

## 🚀 Comment tester en local

### Prérequis
1. Flask démarré : `python run.py`
2. Base de données PostgreSQL connectée
3. Migration des actions exécutée (déjà fait)

### Étapes de test

#### 1. **Mode Test Activé Automatiquement**
Le module est configuré pour fonctionner automatiquement avec certains utilisateurs de test :
- `admin@gmail.com`
- `hugues.marie925@gmail.com`

Ou activez le mode global avec : `export ACTIONS_TEST_MODE=1`

#### 2. **Se connecter sur la plateforme**
```bash
# URL: http://127.0.0.1:5001/plateforme/connexion
# Utilisateur de test : admin@gmail.com
# Ou créer un nouveau compte avec l'un des emails de test
```

#### 3. **Avoir un plan d'investissement**
- Assurez-vous que l'utilisateur a un plan d'investissement configuré
- Si pas de plan : aller dans `/plateforme/plan-investissement`
- Créer des lignes (ex: PEA 500€/mois, Assurance Vie 300€/mois)

#### 4. **Accéder au Dashboard**
```bash
# URL: http://127.0.0.1:5001/plateforme/dashboard
```
**Résultat attendu :**
- Section "Actions à réaliser" avec les investissements du mois
- KPI de progression mensuelle et annuelle
- Boutons d'interaction (Fait/Ajuster/Reporter)

#### 5. **Tester les interactions**

**Marquer comme "Fait" :**
- Cliquer sur ✅ → Action passe en statut "done"
- Montant réalisé = montant attendu

**Ajuster le montant :**
- Cliquer sur ✏️ → Modal de saisie
- Saisir un montant différent → Statut "adjusted"

**Reporter l'action :**
- Cliquer sur 🕒 → Statut "skipped"
- Montant réalisé = 0€

#### 6. **Page de test dédiée**
```bash
# URL: http://127.0.0.1:5001/plateforme/actions/test
```
Interface de debug avec :
- Toutes les actions du mois
- Statistiques détaillées
- Tableau complet des statuts

## 🔧 API Endpoints disponibles

### Génération d'actions
```bash
POST /plateforme/actions/api/generate
Content-Type: application/json

{
  "year_month": "2024-12",  // optionnel
  "force_current": true     // optionnel
}
```

### Mise à jour d'action
```bash
POST /plateforme/actions/api/update/{action_id}
Content-Type: application/json

{
  "status": "done",        // done|adjusted|skipped
  "realized_amount": 500   // requis si status=adjusted
}
```

### Données dashboard
```bash
GET /plateforme/actions/api/dashboard-data?year_month=2024-12
```

## 📊 Données de test

Le système génère automatiquement des actions basées sur le plan d'investissement de l'utilisateur.

**Exemple de données générées :**
```json
{
  "year_month": "2024-12",
  "actions": [
    {
      "id": 1,
      "support_type": "PEA",
      "label": "Investissement PEA",
      "expected_amount": 500.0,
      "status": "pending"
    },
    {
      "id": 2,
      "support_type": "Assurance Vie",
      "label": "Investissement Assurance Vie",
      "expected_amount": 300.0,
      "status": "pending"
    }
  ]
}
```

## 🎨 Interface utilisateur

### Dashboard principal
- **Section "Actions à réaliser"** : Affiche les actions en attente
- **KPI mensuel** : Progression vs objectif du mois
- **KPI annuel** : Progression vs objectif de l'année

### Interactions
- **Boutons colorés** : Vert (fait), Orange (ajuster), Gris (reporter)
- **Modal d'ajustement** : Saisie de montant avec validation
- **Feedback temps réel** : Rechargement automatique après action

### Page de test
- **Vue détaillée** : Toutes les actions avec statuts
- **Statistiques** : Progression, taux de réalisation, montants
- **Debug** : Mode test, email utilisateur, génération automatique

## ⚙️ Configuration technique

### Variables d'environnement
```bash
# Mode test global (optionnel)
export ACTIONS_TEST_MODE=1

# Base de données (déjà configuré)
export DATABASE_URL=postgresql://huguesmarie:@localhost:5432/atlas_db
```

### Base de données
**Table principale :** `investment_actions`
- Index unique : `(user_id, plan_line_id, year_month)`
- Idempotence garantie : pas de doublons

### Règles business
- **Mode normal** : Actions créées pour le mois suivant l'inscription
- **Mode test** : Actions créées pour le mois courant
- **Idempotence** : Générations multiples sans doublons
- **Calculs temps réel** : KPI recalculés à chaque action

## 🐛 Dépannage

### Aucune action générée
1. Vérifier que l'utilisateur a un plan d'investissement
2. Vérifier les lignes du plan (montants > 0)
3. Vérifier les logs Flask pour les erreurs

### Actions non visibles
1. Vérifier le mode test activé
2. Redémarrer Flask après changement de configuration
3. Vérifier la base de données : `SELECT * FROM investment_actions WHERE user_id = X`

### Erreurs API
1. Ouvrir les outils de développement (F12)
2. Vérifier l'onglet Console pour les erreurs JavaScript
3. Vérifier l'onglet Réseau pour les erreurs API

## 🔄 Workflow complet de test

1. **Démarrer Flask** → `python run.py`
2. **Se connecter** → Utilisateur test (admin@gmail.com)
3. **Configurer plan** → Ajouter quelques lignes d'investissement
4. **Aller au dashboard** → Actions générées automatiquement
5. **Tester interactions** → Fait/Ajuster/Reporter
6. **Vérifier KPI** → Progression mise à jour
7. **Page test** → `/plateforme/actions/test` pour vue détaillée

## 🎉 Résultat attendu

✅ **Module fonctionnel** avec :
- Génération automatique d'actions mensuelles
- Interface utilisateur intuitive
- KPI de suivi précis
- Interactions en temps réel
- API robuste et sécurisée

Le module est maintenant prêt pour la production et peut être étendu avec des fonctionnalités supplémentaires (notifications, export PDF, analytics avancés, etc.).