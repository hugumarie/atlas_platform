# 🚀 Guide de Déploiement Atlas sur Dokku

Guide complet pour déployer Atlas en production sur le serveur Dokku.

## 📋 Prérequis

- **Serveur** : Ubuntu 22.04 avec Dokku installé
- **IP** : 167.172.108.93
- **Application** : `atlas` (déjà créée)
- **Base** : PostgreSQL `atlas-db` (déjà configurée)

## 🔧 Configuration Initiale (Déjà Fait)

```bash
# Sur le serveur (une seule fois)
dokku apps:create atlas
dokku postgres:create atlas-db
dokku postgres:link atlas-db atlas
dokku config:set atlas FLASK_ENV=production
dokku config:set atlas SECRET_KEY="atlas-production-secret-key-2024-ultra-secure"
dokku config:set atlas DATABASE_URL="postgresql://postgres:1c60de5151db7a41a15fec496624940f@dokku-postgres-atlas-db:5432/atlas_db"
dokku domains:set atlas 167.172.108.93
dokku proxy:ports-set atlas http:80:5000
```

## 🚀 Processus de Déploiement

### ÉTAPE 1 : Préparation Locale (Mac)

```bash
cd "/Users/huguesmarie/Documents/Jepargne digital"

# 1. Vérifier que tous les fichiers nécessaires sont présents
ls -la Procfile release.sh requirements.txt

# 2. Vérifier les modifications Git
git status
git add .
git commit -m "Mise à jour Atlas - [description des changements]"
```

### ÉTAPE 2 : Déploiement

```bash
# Sur votre Mac
git push dokku main

# Attendre la fin du déploiement (2-5 minutes)
# Vérifier les logs si nécessaire
```

### ÉTAPE 3 : Vérification Post-Déploiement

```bash
# Sur le serveur (si besoin de vérifier)
ssh root@167.172.108.93
dokku logs atlas --tail
dokku ps:report atlas
```

## 🔄 Mise à Jour de la Base de Données

### Si vous avez ajouté de nouvelles données localement :

```bash
# 1. Export base locale (Mac)
pg_dump -h localhost -U huguesmarie -d atlas_db --no-owner --no-privileges > atlas_update_backup.sql

# 2. Transfert vers serveur (Mac)
scp atlas_update_backup.sql root@167.172.108.93:/tmp/atlas_update.sql

# 3. Import sur serveur
ssh root@167.172.108.93
dokku postgres:connect atlas-db < /tmp/atlas_update.sql
dokku ps:restart atlas
```

## 🛠️ Dépannage Commun

### Problème 1 : Erreur de dépendances Python

**Symptôme** : `ModuleNotFoundError`

**Solution** :
```bash
# Vérifier requirements.txt et ajouter la dépendance manquante
echo "nouvelle-dependance==1.0.0" >> requirements.txt
git add requirements.txt
git commit -m "Add missing dependency"
git push dokku main
```

### Problème 2 : Erreur de base de données

**Symptôme** : `sqlalchemy.exc.NoSuchModuleError`

**Solution** :
```bash
# Sur le serveur
dokku config:show atlas | grep DATABASE_URL
# Vérifier que l'URL commence par postgresql:// et non postgres://
dokku config:set atlas DATABASE_URL="postgresql://..."
```

### Problème 3 : Nginx affiche page par défaut

**Symptôme** : Page "Welcome to nginx!"

**Solution** :
```bash
# Sur le serveur
dokku domains:set atlas 167.172.108.93
dokku proxy:ports-set atlas http:80:5000
dokku ps:restart atlas
```

### Problème 4 : Application ne démarre pas

**Solution** :
```bash
# Sur le serveur - voir les logs détaillés
dokku logs atlas --tail

# Reconstruire si nécessaire
dokku ps:rebuild atlas
```

## 📊 Vérification de Fonctionnement

### Checklist Post-Déploiement

- [ ] **URL accessible** : http://167.172.108.93
- [ ] **Connexion admin** fonctionne
- [ ] **Dashboard** s'affiche correctement
- [ ] **Base de données** connectée (prix crypto visibles)
- [ ] **Pas d'erreurs** dans les logs

### Commandes de Vérification

```bash
# Statut application
dokku ps:report atlas

# Logs en direct
dokku logs atlas --tail

# Configuration
dokku config atlas

# Base de données
dokku postgres:info atlas-db
```

## 🔄 Workflow de Développement

### Pour un Update Standard

1. **Développement local** avec `./start_atlas.sh`
2. **Test** des modifications
3. **Commit** des changements
4. **Push** vers Dokku : `git push dokku main`
5. **Vérification** sur http://167.172.108.93

### Pour un Update avec Nouvelles Dépendances

1. **Ajouter** dans `requirements.txt`
2. **Tester** localement si possible
3. **Commit** et **push**
4. **Surveiller** les logs de déploiement

### Pour un Update avec Migrations DB

1. **Modifier** `release.sh` si nécessaire
2. **Ou** utiliser la méthode export/import décrite ci-dessus
3. **Tester** la connexion admin après migration

## 🎯 URLs et Accès

- **Application** : http://167.172.108.93
- **Connexion** : `/platform/login`
- **Dashboard** : `/platform/dashboard`

## 🆘 Contact et Support

En cas de problème :
1. **Logs** : `dokku logs atlas --tail`
2. **Rebuild** : `dokku ps:rebuild atlas`
3. **Restart** : `dokku ps:restart atlas`
4. **Configuration** : `dokku config atlas`

---

**✅ Atlas déployé avec succès sur Dokku !**

*Dernière mise à jour : 26 Décembre 2024*