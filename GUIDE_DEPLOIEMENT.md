# 🚀 Guide de Déploiement Atlas

## 🎯 Workflow Recommandé

### 1. **Premier Déploiement** (Une seule fois)
```bash
# Installer Atlas avec vos utilisateurs de test
./deploy_initial.sh
```

### 2. **Mises à Jour Normales** (Usage courant)
```bash
# Déployer code seulement (PRÉSERVE la DB prod)
./deploy.sh
```

## 📋 Scripts Disponibles

### `deploy_initial.sh` - Premier Déploiement ⚠️
**À utiliser UNIQUEMENT pour la première installation**

```bash
./deploy_initial.sh
```

**Ce script :**
- ✅ Déploie votre code Atlas
- ✅ Installe vos utilisateurs de test en production
- ⚠️ REMPLACE toute DB existante
- 🔒 Demande confirmation explicite ("OUI" en majuscules)

---

### `deploy.sh` - Déploiements Normaux ✅
**Script principal pour toutes les mises à jour**

```bash
# Déploiement normal (code seulement - RECOMMANDÉ)
./deploy.sh

# Si vraiment besoin de remplacer la DB (RARE)
./deploy.sh --sync-db

# Forcer remplacement DB sans confirmation (DANGEREUX)
./deploy.sh --force-db
```

**Comportement par défaut :**
- ✅ Déploie votre code
- ✅ PRÉSERVE la base de données de production
- ✅ Garde tous les utilisateurs et données créés en prod
- 🛡️ Mode sécurisé par défaut

---

## 🛡️ Sécurités Intégrées

### Protection Base de Données
- **Par défaut** : Base de production PRÉSERVÉE
- **Confirmations** : Multiples confirmations avant écrasement DB
- **Backups automatiques** : Sauvegarde prod avant tout remplacement
- **Vérifications** : Contrôle taille/validité des backups

### Vérifications Pré-Déploiement
- ✅ Git commit status
- ✅ Connexion serveur
- ✅ Base de données locale (si sync demandée)
- ✅ Applications Dokku existantes

---

## 📊 Workflow Réel de Production

### Première Installation
```bash
# 1. Préparer code et DB locale avec utilisateurs de test
git add .
git commit -m "Version initiale avec utilisateurs de test"

# 2. Premier déploiement
./deploy_initial.sh
```

### Mises à Jour Quotidiennes
```bash
# 1. Développer nouvelles fonctionnalités
git add .
git commit -m "Ajout fonctionnalité X"

# 2. Déployer SANS toucher à la DB
./deploy.sh
```

### Cas Exceptionnels (Migration DB)
```bash
# Si vraiment besoin de changer le schéma DB
# ⚠️ TRÈS RARE - prévoir migration script plutôt !
./deploy.sh --sync-db
```

---

## 🗂️ Gestion des Backups

### Backups Automatiques
Tous les backups sont dans `./backups/` avec horodatage :
- `initial_deploy_YYYYMMDD_HHMMSS.sql` - Déploiement initial
- `production_backup_YYYYMMDD_HHMMSS.sql` - Sauvegarde prod avant sync
- `local_backup_YYYYMMDD_HHMMSS.sql` - Sauvegarde locale

### Restauration d'Urgence
```bash
# En cas de problème grave
ssh dokku@167.172.108.93 postgres:import atlas-postgres < ./backups/production_backup_XXX.sql
```

---

## ⚡ Exemples d'Usage

### Scénario 1: Nouveau bug fix
```bash
# Fix le bug en local
git add .
git commit -m "Fix bug login"

# Déployer juste le code
./deploy.sh
# → La DB prod est préservée ✅
```

### Scénario 2: Nouvelle fonctionnalité
```bash
# Développer la fonctionnalité
git add .
git commit -m "Ajout dashboard analytics"

# Déployer
./deploy.sh
# → Seul le code est mis à jour ✅
```

### Scénario 3: Modification structure DB
```bash
# Cas TRÈS RARE - à éviter si possible
# Préférer les migrations SQL automatiques

# Si vraiment nécessaire :
./deploy.sh --sync-db
# → Backup auto de la prod + remplacement
```

---

## 🚨 Règles de Sécurité

### ✅ À FAIRE
- Utiliser `./deploy.sh` pour toutes les mises à jour normales
- Committer avant de déployer
- Tester en local avant déploiement
- Vérifier que l'app fonctionne après déploiement

### ❌ À ÉVITER
- Utiliser `--sync-db` sauf cas exceptionnel
- Déployer sans backup
- Ignorer les confirmations de sécurité
- Utiliser `--force-db` en production

### 🛑 JAMAIS
- Utiliser `deploy_initial.sh` sur une prod avec vraies données
- Bypasser les confirmations sans réfléchir
- Déployer sans comprendre ce qui va être écrasé

---

## 🔍 Résolution de Problèmes

### "Impossible de se connecter à la DB locale"
```bash
brew services start postgresql
psql -U postgres -h localhost -d atlas_db -c "SELECT 1;"
```

### "Erreur git push dokku"
```bash
# Vérifier remote dokku
git remote -v

# Re-ajouter si nécessaire
git remote add dokku dokku@167.172.108.93:atlas
```

### "Application pas accessible après déploiement"
```bash
# Voir les logs
ssh dokku@167.172.108.93 logs atlas -t

# Redémarrer si nécessaire
ssh dokku@167.172.108.93 apps:restart atlas
```

---

## 📈 Bonnes Pratiques

1. **Toujours** utiliser `./deploy.sh` par défaut
2. **Tester** en local avant chaque déploiement
3. **Committer** avant de déployer
4. **Vérifier** l'app après déploiement
5. **Documenter** les changements importants
6. **Garder** les backups automatiques
7. **Planifier** les migrations DB complexes

---

**🎯 Résumé Simple :**
- **Premier déploiement** : `./deploy_initial.sh`
- **Tous les autres déploiements** : `./deploy.sh`
- **La DB prod est protégée par défaut** ✅