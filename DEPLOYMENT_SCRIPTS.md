# 🚀 Scripts de Déploiement Atlas

Ce dossier contient plusieurs scripts pour automatiser le déploiement d'Atlas avec synchronisation de base de données.

## 📋 Scripts Disponibles

### 1. `deploy_complete.sh` - Déploiement Complet
**Script principal recommandé** qui fait tout en une fois.

```bash
# Déploiement normal (code + DB avec confirmation)
./deploy_complete.sh

# Déploiement code seulement (sans toucher à la DB)
./deploy_complete.sh --no-db

# Déploiement avec DB forcée (sans confirmation)
./deploy_complete.sh --force-db
```

**Fonctionnalités :**
- ✅ Vérifications pré-déploiement (git, connexion serveur, DB locale)
- ✅ Sauvegarde automatique de la production AVANT sync
- ✅ Déploiement du code via git push
- ✅ Synchronisation optionnelle de la base de données
- ✅ Confirmations de sécurité
- ✅ Vérifications post-déploiement

---

### 2. `sync_database.sh` - Synchronisation DB Seule
Pour synchroniser uniquement la base de données (sans deployer le code).

```bash
# Synchronisation avec confirmation
./sync_database.sh

# Synchronisation forcée
./sync_database.sh --force
```

**Fonctionnalités :**
- 🛡️ Sauvegarde de sécurité de la production
- 📦 Sauvegarde de la base locale
- 🔄 Remplacement complet de la DB production
- ✅ Confirmations de sécurité

---

### 3. `deploy_with_database.sh` - Version Simple
Version basique qui fait code + DB sans confirmations avancées.

```bash
./deploy_with_database.sh
```

## 🔧 Configuration Requise

### Prérequis
- **PostgreSQL** installé localement
- **SSH** configuré pour `dokku@167.172.108.93`
- **Git** configuré avec remote `dokku`
- Accès en écriture au dossier `./backups/`

### Variables à modifier si nécessaire
Dans chaque script, ajustez ces variables :
```bash
SERVER_IP="167.172.108.93"        # IP du serveur Dokku
APP_NAME="atlas"                   # Nom de l'app Dokku
LOCAL_DB_NAME="atlas_db"           # Nom DB locale
LOCAL_DB_USER="postgres"           # Utilisateur DB local
```

## 🛡️ Sécurité et Sauvegardes

### Sauvegardes Automatiques
Tous les scripts créent des sauvegardes horodatées dans `./backups/` :
- `production_backup_YYYYMMDD_HHMMSS.sql` - Sauvegarde de la production
- `local_backup_YYYYMMDD_HHMMSS.sql` - Sauvegarde locale
- `atlas_sync_YYYYMMDD_HHMMSS.sql` - Sauvegarde pour sync

### Restauration d'Urgence
En cas de problème, restaurez la production :
```bash
# Récupérer le fichier de backup
scp dokku@167.172.108.93:/chemin/vers/backup.sql ./

# Restaurer sur le serveur
ssh dokku@167.172.108.93 postgres:import atlas-postgres < backup.sql
```

### Vérifications de Sécurité
- ✅ Vérification de la taille du backup avant sync
- ✅ Confirmation obligatoire avant remplacement DB
- ✅ Sauvegarde automatique de la production
- ✅ Mode `--force` pour bypasser les confirmations

## 📊 Workflow Recommandé

### Déploiement Normal
```bash
# 1. Vérifier le statut git
git status

# 2. Committer les changements
git add .
git commit -m "Description des changements"

# 3. Déployer avec sync DB
./deploy_complete.sh
```

### Déploiement Code Seulement
```bash
# Si vous voulez juste déployer le code sans toucher à la DB
./deploy_complete.sh --no-db
```

### Synchronisation DB Seule
```bash
# Si vous voulez juste synchroniser la DB
./sync_database.sh
```

## 🆘 Dépannage

### Erreur "Impossible de se connecter à la DB locale"
```bash
# Vérifier que PostgreSQL est démarré
brew services start postgresql

# Vérifier la connexion
psql -U postgres -h localhost -d atlas_db -c "SELECT 1;"
```

### Erreur "Connexion SSH refusée"
```bash
# Vérifier la clé SSH
ssh dokku@167.172.108.93 apps:list

# Ajouter la clé si nécessaire
ssh-copy-id dokku@167.172.108.93
```

### Erreur "App non trouvée"
```bash
# Lister les apps sur le serveur
ssh dokku@167.172.108.93 apps:list

# Vérifier le nom de l'app dans le script
```

## 📝 Logs et Debug

### Voir les logs de l'application
```bash
ssh dokku@167.172.108.93 logs atlas -t
```

### Vérifier l'état de l'app
```bash
ssh dokku@167.172.108.93 apps:report atlas
```

### Vérifier la base de données
```bash
ssh dokku@167.172.108.93 postgres:info atlas-postgres
```

---

## 🔄 Exemples d'Usage

### Cas 1: Première mise en production
```bash
# Déployer tout avec la DB locale
./deploy_complete.sh
```

### Cas 2: Mise à jour code seulement
```bash
# Juste le code, garder les données production
./deploy_complete.sh --no-db
```

### Cas 3: Synchroniser de nouvelles données
```bash
# Juste la DB, garder le code actuel
./sync_database.sh
```

### Cas 4: Déploiement d'urgence
```bash
# Tout déployer sans confirmation
./deploy_complete.sh --force-db
```

---

**⚠️ Important :** Ces scripts remplacent COMPLÈTEMENT la base de données de production. Utilisez-les avec précaution et assurez-vous d'avoir des sauvegardes !