# 🚀 Déploiement Atlas sur Dokku

Guide complet pour déployer l'application Flask Atlas sur Dokku (mini-Heroku).

## 📋 Prérequis

### Sur le serveur Ubuntu
```bash
# Installation Dokku
wget https://raw.githubusercontent.com/dokku/dokku/v0.34.6/bootstrap.sh
sudo DOKKU_TAG=v0.34.6 bash bootstrap.sh

# Configuration initiale via interface web
# Rendez-vous sur http://VOTRE_IP pour configurer Dokku
```

### Plugins nécessaires
```bash
# Plugin PostgreSQL
sudo dokku plugin:install https://github.com/dokku/dokku-postgres.git

# Plugin Let's Encrypt (SSL)
sudo dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
```

## 🗄️ Préparation Base de Données

```bash
# Créer service PostgreSQL
dokku postgres:create atlas-db

# Lier à l'application (crée automatiquement DATABASE_URL)
dokku postgres:link atlas-db atlas
```

## 📦 Préparation du Projet

Votre projet est déjà configuré avec :
- ✅ `Procfile` - Configuration Dokku
- ✅ `requirements.txt` - Dépendances production
- ✅ `release.sh` - Script de migration
- ✅ Configuration environnement dans `app/__init__.py`

## 🚀 Déploiement

### 1. Créer l'application Dokku
```bash
# Sur le serveur
dokku apps:create atlas
```

### 2. Configuration des variables d'environnement
```bash
# Variable SECRET_KEY (générer une clé secrète forte)
dokku config:set atlas SECRET_KEY="votre-cle-secrete-ultra-longue-et-complexe-ici"

# Configuration Flask pour production
dokku config:set atlas FLASK_ENV=production

# Configuration port (Dokku gère automatiquement)
dokku config:set atlas PORT=5000
```

### 3. Déploiement depuis votre machine locale
```bash
# Ajouter remote Dokku
git remote add dokku dokku@VOTRE_IP:atlas

# Déployer
git push dokku main
```

### 4. Configuration domaine (optionnel)
```bash
# Configurer domaine personnalisé
dokku domains:set atlas votre-domaine.com

# SSL automatique avec Let's Encrypt
dokku letsencrypt:enable atlas
```

## 🎯 URLs d'accès

Après déploiement :
- **Application** : `http://VOTRE_IP` ou `https://votre-domaine.com`
- **Connexion admin** : `/platform/login`
- **Dashboard** : `/platform/dashboard`

## 🔑 Comptes de Test

L'application crée automatiquement :
- **Email** : `admin@atlas.com`
- **Mot de passe** : `Admin123!`

## 📊 Gestion de l'Application

### Logs en temps réel
```bash
dokku logs atlas --tail
```

### Redémarrage
```bash
dokku ps:restart atlas
```

### Variables d'environnement
```bash
# Lister
dokku config atlas

# Ajouter
dokku config:set atlas NOUVELLE_VAR=valeur

# Supprimer
dokku config:unset atlas ANCIENNE_VAR
```

### Base de données
```bash
# Backup
dokku postgres:backup atlas-db backup-$(date +%Y%m%d)

# Restore
dokku postgres:import atlas-db < backup.sql

# Connexion directe
dokku postgres:connect atlas-db
```

## 🔄 Mise à Jour

```bash
# Déployer nouvelles modifications
git push dokku main

# Le script release.sh s'exécute automatiquement :
# - Création/mise à jour tables
# - Création utilisateur admin si nécessaire
# - Mise à jour prix crypto
```

## 📈 Surveillance

### Métriques
```bash
# Utilisation ressources
dokku ps:report atlas

# Statistiques PostgreSQL
dokku postgres:info atlas-db
```

### Monitoring
```bash
# Processus actifs
dokku ps atlas

# État des services
dokku postgres:list
```

## 🔧 Dépannage

### Application ne démarre pas
```bash
# Vérifier logs
dokku logs atlas --tail

# Vérifier configuration
dokku config atlas

# Redéployer
git push dokku main --force
```

### Problèmes de base de données
```bash
# Vérifier connexion PostgreSQL
dokku postgres:connect atlas-db

# Recréer la liaison
dokku postgres:unlink atlas-db atlas
dokku postgres:link atlas-db atlas
```

### Erreurs de dépendances
```bash
# Reconstruire avec cache vidé
dokku ps:rebuild atlas
```

## 🛡️ Sécurité

### SSL/TLS
```bash
# Forcer HTTPS
dokku letsencrypt:enable atlas

# Renouvellement automatique
dokku letsencrypt:cron-job --add
```

### Backup automatique
```bash
# Cron backup quotidien PostgreSQL
dokku postgres:backup-schedule atlas-db "0 2 * * *" backup-daily
```

## 📋 Checklist Déploiement

- [ ] Dokku installé et configuré
- [ ] Plugin PostgreSQL installé
- [ ] Application `atlas` créée
- [ ] Base de données `atlas-db` créée et liée
- [ ] Variables d'environnement configurées
- [ ] Code poussé vers `dokku` remote
- [ ] SSL configuré (optionnel)
- [ ] Test connexion admin
- [ ] Backup automatique configuré

## 🆘 Support

En cas de problème :
1. Consulter les logs : `dokku logs atlas --tail`
2. Vérifier la configuration : `dokku config atlas`
3. Tester la base de données : `dokku postgres:connect atlas-db`
4. Redéployer : `git push dokku main --force`

---

**Atlas déployé avec succès sur Dokku ! 🎉**