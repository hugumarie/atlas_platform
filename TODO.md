# ATLAS - TODO LIST

## État actuel du projet (Octobre 2025)

### ✅ TERMINÉ

#### Site Vitrine
- [x] **Réplication exacte du design Qlower** avec couleurs Atlas
- [x] **Page d'accueil** avec hero utilisant l'image du dashboard 
- [x] **Menu organisé** : Nos Offres, Ressources, À propos
- [x] **Animation shimmer** sur l'image du dashboard dans le hero
- [x] **Pages complètes** : À propos, Tarifs, Contact, Blog, FAQ, CGU
- [x] **Design responsive** avec breakpoints exacts de Qlower

#### Plateforme Client & Admin  
- [x] **Design system Atlas** unifié pour client et admin
- [x] **Sidebar primary color** (#137C8B) avec texte blanc pour les deux interfaces
- [x] **Dashboard investisseur** avec :
  - [x] 3 cartes statistiques (Patrimoine, Objectif mensuel, Revenu)
  - [x] Barre de progression épargne annuelle animée (75% pour simulation)
  - [x] Graphique camembert répartition actifs avec Chart.js
- [x] **Page Apprentissage** : grille 3x3 formations avec cartes uniformes
- [x] **Page Formations** : layout étendu une par ligne avec durée et bouton

#### Base de données & Authentification
- [x] **Models SQLAlchemy** : User, InvestorProfile, Subscription avec tier
- [x] **Authentification complète** avec rôles client/admin
- [x] **Gestion abonnements** avec plans INITIA/OPTIMA/ULTIMA
- [x] **Données utilisateur** : hugu@gmail.com avec Plan ULTIMA et simulation épargne
- [x] **Suppression popup déconnexion** agaçant

#### Fonctionnalités avancées
- [x] **Onboarding flow** complet en 5 étapes
- [x] **Animations CSS** et transitions fluides
- [x] **Responsive design** mobile/desktop
- [x] **Navigation cohérente** entre toutes les sections

#### Interface Admin Utilisateur (Nouvelle session - Novembre 2025)
- [x] **Section IMMOBILIER** complète avec calculs automatiques
- [x] **Section CRYPTOMONNAIES** avec API CoinGecko temps réel
- [x] **Section AUTRES BIENS** (art, collectibles, voitures...)
- [x] **Section CRÉDITS** avec calcul capital restant dû automatique
- [x] **Section OBJECTIFS D'INVESTISSEMENT** avec 10 objectifs à cocher
- [x] **Section PROFIL DE RISQUE** avec 5 questions et calcul automatique
- [x] **Total capital restant dû** pour crédits immobiliers
- [x] **Réorganisation formulaire** identité (situation familiale après prénom)
- [x] **Design Atlas cohérent** avec badges verts et animations

---

### 🔄 EN COURS / À AMÉLIORER

#### Contenu et données
- [ ] **Remplacer données mockées** par vraies données utilisateur
- [ ] **Système de formation** avec contenu vidéo réel
- [ ] **Intégration API** pour données financières en temps réel

#### Fonctionnalités manquantes
- [ ] **Page individuelle de formation** avec vidéo/contenu
- [ ] **Système de progression** des formations
- [ ] **Notifications** utilisateur
- [ ] **Export données** (PDF, Excel)

#### Optimisations techniques
- [ ] **Performance** : lazy loading, optimisation images
- [ ] **SEO** : meta tags, sitemap, robots.txt
- [ ] **Tests** : tests unitaires et d'intégration
- [ ] **Sécurité** : audit sécurité complet

---

### 🎯 PROCHAINES PRIORITÉS

1. **Contenu des formations** - Ajouter vidéos et contenu pédagogique
2. **Page formation individuelle** - Template pour visionner une formation
3. **Système de progression** - Tracking completion formations
4. **Dashboard admin** - Interface gestion utilisateurs/formations
5. **API REST** - Endpoints pour mobile app future

---

### 🔧 CONFIGURATION TECHNIQUE

#### Environnement de développement
- **Framework** : Flask (Python)
- **Base de données** : SQLite (dev) 
- **Frontend** : HTML/CSS/JS avec design Atlas
- **Charts** : Chart.js
- **Icons** : Font Awesome 6.4.0
- **Fonts** : Inter + Encode Sans Condensed

#### Structure des routes
- `/` - Site vitrine
- `/plateforme/connexion` - Login
- `/plateforme/dashboard` - Dashboard investisseur  
- `/plateforme/apprentissage` - Grille formations 3x3
- `/plateforme/formations` - Liste formations détaillée
- `/admin/dashboard` - Interface admin

#### Utilisateur de test
- **Email** : hugu@gmail.com
- **Plan** : ULTIMA
- **Simulation** : 900€/1200€ épargne annuelle (75%)

---

*Dernière mise à jour : Octobre 2025*
*Développement en cours avec Claude Code*