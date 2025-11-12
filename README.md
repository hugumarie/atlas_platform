# 🏛️ Atlas Platform - Plateforme de Gestion de Patrimoine

> **Une plateforme web moderne et complète pour démocratiser l'accès au conseil en gestion de patrimoine**

Atlas Platform permet aux particuliers d'optimiser leur épargne et d'apprendre à investir grâce à une interface intuitive, des outils d'analyse avancés et un accompagnement personnalisé.

## 🎯 Vision du Projet

**Démocratiser l'accès au conseil financier** en combinant :
- 🤖 **Intelligence artificielle** pour des conseils instantanés
- 📊 **Outils d'analyse** sophistiqués mais accessibles
- 🎓 **Formation continue** avec contenus éducatifs
- 👥 **Accompagnement humain** personnalisé
- ⚡ **Technologie moderne** pour une expérience fluide

## 📋 Fonctionnalités

### Interface Investisseur
- ✅ **Inscription et authentification** sécurisées
- ✅ **Questionnaire de profil** complet (revenus, épargne, objectifs, tolérance au risque)
- ✅ **Dashboard personnalisé** avec visualisation des investissements
- ✅ **Section formation** avec vidéos et modules d'apprentissage
- ✅ **Assistant IA** pour conseils financiers instantanés
- ✅ **Gestion de profil** utilisateur

### Interface Administrateur
- ✅ **Dashboard admin** avec statistiques en temps réel
- ✅ **Gestion des clients** avec recherche, filtres et export
- ✅ **Gestion des prospects** avec suivi de conversion
- ✅ **Vue détaillée** de chaque utilisateur avec profil complet
- ✅ **Édition avancée** des données patrimoniales
- ✅ **Suivi des abonnements** et métriques financières
- ✅ **Système d'invitations** pour prospects

### Fonctionnalités Techniques
- ✅ **Base de données** SQLite/PostgreSQL
- ✅ **Authentication** Flask-Login
- ✅ **Interface responsive** Bootstrap 5
- ✅ **Graphiques interactifs** Chart.js
- ✅ **API REST** pour l'assistant IA

## 🛠 Installation et Démarrage

### Prérequis
- Python 3.8+
- pip (gestionnaire de packages Python)

### Installation automatique
```bash
# Naviguez vers le dossier du projet
cd "Jepargne digital"

# Lancez le script de démarrage automatique
python3 start_app.py
```

### Installation manuelle
```bash
# Installation des dépendances
pip3 install -r requirements.txt

# Lancement de l'application
python3 run.py
```

L'application sera accessible sur : **http://127.0.0.1:5000**

## 👥 Comptes de Test

### Compte Administrateur
- **Email** : `admin@gmail.com`
- **Mot de passe** : `admin`

### Compte Utilisateur
Créez un nouveau compte via l'interface d'inscription pour tester l'expérience investisseur complète.

## 🗂 Structure du Projet

```
Jepargne digital/
├── app/                          # Application Flask
│   ├── __init__.py              # Factory de l'application
│   ├── models/                  # Modèles de données
│   │   ├── user.py             # Modèle utilisateur
│   │   ├── investor_profile.py # Profil investisseur
│   │   ├── subscription.py     # Gestion abonnements
│   │   └── portfolio.py        # Portefeuille
│   ├── routes/                  # Routes et contrôleurs
│   │   ├── auth.py             # Authentification
│   │   ├── investor.py         # Interface investisseur
│   │   ├── admin.py            # Interface admin
│   │   └── main.py             # Pages principales
│   ├── templates/               # Templates HTML
│   │   ├── base.html           # Template de base
│   │   ├── main/               # Pages publiques
│   │   ├── auth/               # Authentification
│   │   ├── investor/           # Interface investisseur
│   │   └── admin/              # Interface admin
│   └── static/                  # Fichiers statiques
│       ├── css/                # Styles CSS
│       ├── js/                 # JavaScript
│       └── img/                # Images
├── requirements.txt             # Dépendances Python
├── run.py                      # Point d'entrée
├── start_app.py               # Script de démarrage
├── statut_projet.md           # Documentation projet
├── todo_list.md               # Liste des tâches
└── README.md                  # Ce fichier
```

## 🎮 Guide d'Utilisation

### 1. Structure de l'Application
L'application est divisée en deux parties :
- **Site vitrine** : `/site/` - Présentation du produit et marketing
- **Plateforme** : `/plateforme/` - Application fonctionnelle pour les utilisateurs

### 2. Inscription Investisseur
1. Depuis le site vitrine, cliquez sur "Commencer" (ouvre un nouvel onglet)
2. Remplissez le formulaire d'inscription complet
3. **Ajoutez vos informations de paiement** (20€/mois, simulation)
4. Paiement immédiat requis - pas d'essai gratuit

### 3. Questionnaire de Profil
1. Complétez le questionnaire détaillé :
   - Revenus et capacité d'épargne
   - Situation familiale et professionnelle
   - Objectifs d'investissement
   - Tolérance au risque
   - Investissements existants

### 4. Dashboard Investisseur
- Visualisez vos investissements en graphiques
- Consultez vos statistiques financières
- Accédez aux différentes sections

### 5. Formation et Apprentissage
- Parcourez les formations vidéo
- Suivez votre progression
- Approfondissez vos connaissances

### 6. Assistant IA
- Posez vos questions financières
- Recevez des conseils personnalisés
- Disponible 24h/24

### 7. Administration
- Connectez-vous avec le compte admin
- Consultez les statistiques générales
- Gérez la liste des clients
- Suivez les conversions

## 💡 Fonctionnalités à Venir

### Phase 2 - Enrichissement
- [ ] Intégration réelle de l'IA (OpenAI GPT)
- [ ] Graphiques avancés et tableaux de bord
- [ ] Système de notifications
- [ ] Module de formation interactif

### Phase 3 - Monétisation
- [ ] Intégration Stripe pour les paiements
- [ ] Système de facturation automatique
- [ ] Gestion des remboursements
- [ ] Analytics avancées

### Phase 4 - Évolutions
- [ ] Application mobile
- [ ] API publique
- [ ] Intégrations bancaires
- [ ] Rapports PDF automatisés

## 🔧 Configuration

### Variables d'Environnement
```bash
# Base de données
DATABASE_URL=sqlite:///patrimoine.db

# Clé secrète Flask
SECRET_KEY=votre-cle-secrete-très-longue

# Configuration OpenAI (pour l'assistant IA)
OPENAI_API_KEY=your-api-key-here
```

### Base de Données
La base de données SQLite est créée automatiquement au premier lancement.
Pour utiliser PostgreSQL en production, modifiez `SQLALCHEMY_DATABASE_URI` dans `app/__init__.py`.

## 🛡 Sécurité

- Hachage des mots de passe avec bcrypt
- Protection CSRF avec Flask-WTF
- Sessions sécurisées
- Validation des données d'entrée
- Autorisation basée sur les rôles

## 📊 Modèle Économique

- **Abonnement mensuel** : 20€/mois
- **Période d'essai** : 7 jours gratuits
- **Services inclus** :
  - Accès complet à la plateforme
  - Assistant IA illimité
  - Formations vidéo
  - Appel mensuel avec conseiller

## 🤝 Contribution

Ce projet est en développement actif. Les contributions sont les bienvenues !

1. Fork du projet
2. Créez votre branche (`git checkout -b feature/NouvelleFonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/NouvelleFonctionnalite`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou assistance :
- Email : contact@patrimoine-pro.fr
- Documentation : Consultez les fichiers `statut_projet.md` et `todo_list.md`

---

**Développé avec ❤️ pour démocratiser l'accès au conseil financier**
