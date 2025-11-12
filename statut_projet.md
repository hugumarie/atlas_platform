# Plateforme de Conseil en Gestion de Patrimoine

## Objectif du Projet

Développer une plateforme web simple et intuitive pour démocratiser le conseil en gestion de patrimoine. La plateforme vise à accompagner les particuliers souhaitant apprendre à investir et optimiser leur épargne.

## Modèle Économique

- **Abonnement mensuel** : 20€/mois
- **Services inclus** :
  - Accès à la plateforme de suivi financier
  - Outils d'analyse et de recommandations
  - Appel mensuel personnalisé avec un conseiller

## Fonctionnalités Principales

### Interface Investisseur
1. **Inscription et Onboarding**
   - Création de compte
   - Souscription d'abonnement (simulation avant intégration Stripe)
   - Questionnaire de profil investisseur

2. **Espace Personnel**
   - Dashboard financier avec visualisations (camembert, graphiques)
   - Suivi des investissements par enveloppe (Livret A, PEA, Immobilier, Assurance vie)
   - Objectifs d'épargne et capacité mensuelle

3. **Formation et Apprentissage**
   - Vidéos éducatives
   - Modules de formation
   - Ressources pédagogiques

4. **Assistant Financier IA**
   - Chat personnalisé avec GPT financier
   - Conseils adaptés au profil utilisateur

### Interface Administrateur
1. **Gestion des Clients**
   - Liste complète des utilisateurs
   - Recherche et filtres
   - Détails des profils clients
   - Suivi des abonnements

## Technologies Utilisées

- **Backend** : Python (Flask/Django)
- **Frontend** : HTML, CSS, JavaScript
- **Base de données** : SQLite/PostgreSQL
- **Authentification** : Sessions sécurisées
- **Graphiques** : Chart.js/Plotly

## Architecture

```
├── app/
│   ├── models/          # Modèles de données
│   ├── routes/          # Routes et contrôleurs
│   ├── templates/       # Templates HTML
│   ├── static/          # CSS, JS, images
│   └── utils/           # Fonctions utilitaires
├── database/            # Scripts et migrations DB
├── documentation/       # Documentation technique
└── tests/              # Tests unitaires
```

## Phases de Développement

### Phase 1 - MVP (Minimum Viable Product)
- Authentification et gestion des comptes
- Questionnaire de profil investisseur
- Dashboard basique
- Interface admin simple

### Phase 2 - Enrichissement
- Assistant IA financier
- Modules de formation
- Graphiques avancés
- Optimisations UX/UI

### Phase 3 - Monétisation
- Intégration Stripe
- Système de paiement récurrent
- Notifications et rappels
- Analytics avancées

## Sécurité et Conformité

- Chiffrement des données sensibles
- Conformité RGPD
- Authentification sécurisée
- Protection des données financières

## État Actuel du Développement

### ✅ Fonctionnalités Implémentées

#### Backend & Infrastructure
- [x] Architecture Flask avec structure modulaire
- [x] Base de données SQLite avec modèles complets (User, InvestorProfile, Subscription, Portfolio)
- [x] Système d'authentification sécurisé (Flask-Login, bcrypt)
- [x] API REST pour l'assistant IA
- [x] Gestion des sessions et sécurité CSRF

#### Interface Utilisateur
- [x] Page d'accueil attractive avec présentation des services
- [x] Système d'inscription/connexion complet
- [x] Questionnaire de profil investisseur détaillé (15+ questions)
- [x] Interface responsive avec Bootstrap 5
- [x] Navigation intuitive et design moderne

#### Interface Administrateur
- [x] Dashboard admin avec statistiques en temps réel
- [x] Gestion complète des clients avec recherche et pagination
- [x] Vue détaillée de chaque client
- [x] Authentification admin sécurisée

#### Fonctionnalités Métier
- [x] Gestion des abonnements avec période d'essai de 7 jours
- [x] Calcul automatique des profils de risque
- [x] Simulation de l'assistant IA financier
- [x] Modélisation complète des portefeuilles

### 🚧 En Développement
- [ ] Dashboard investisseur avec graphiques interactifs
- [ ] Section formation avec vidéos
- [ ] Interface de chat pour l'assistant IA
- [ ] Gestion des profils utilisateurs

### 📈 Prochaines Étapes
1. **Dashboard Investisseur** - Graphiques Chart.js pour visualisation des données
2. **Assistant IA** - Intégration réelle OpenAI GPT
3. **Formations** - Système de vidéos et progression
4. **Intégration Stripe** - Paiements réels
5. **Notifications** - Système d'alertes par email

---

**Dernière mise à jour** : 11 octobre 2024
**Status** : MVP Fonctionnel - Prêt pour démonstration