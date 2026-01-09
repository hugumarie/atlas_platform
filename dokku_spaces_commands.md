# 🚀 Configuration DigitalOcean Spaces avec Dokku - Atlas Production

## 📋 Guide Rapide

### 🔧 Configuration Automatique (Recommandé)

```bash
# 1. Copier le script sur le serveur
scp configure_spaces_production.sh root@atlas-invest.fr:/root/

# 2. Se connecter au serveur
ssh root@atlas-invest.fr

# 3. Exécuter le script de configuration
cd /root
chmod +x configure_spaces_production.sh
./configure_spaces_production.sh
```

### 🖥️ Configuration Manuelle (Alternative)

```bash
# Se connecter au serveur
ssh root@atlas-invest.fr

# Configurer les variables DigitalOcean Spaces
dokku config:set atlas \
    DIGITALOCEAN_SPACES_KEY="your_access_key" \
    DIGITALOCEAN_SPACES_SECRET="your_secret_key" \
    DIGITALOCEAN_SPACES_ENDPOINT="https://fra1.digitaloceanspaces.com" \
    DIGITALOCEAN_SPACES_BUCKET="atlas-storage"

# Optionnel: Variables pour les backups
dokku config:set atlas \
    DB_HOST="localhost" \
    DB_PORT="5432" \
    DB_NAME="atlas_production" \
    DB_USER="atlas_user" \
    DB_PASSWORD="your_db_password"

# Redémarrer l'application
dokku ps:restart atlas
```

## 🔍 Vérification

### Voir la Configuration Actuelle
```bash
# Voir toutes les variables (masquées pour sécurité)
dokku config atlas

# Voir spécifiquement les variables Spaces
dokku config:get atlas DIGITALOCEAN_SPACES_KEY
dokku config:get atlas DIGITALOCEAN_SPACES_BUCKET
```

### Tester la Configuration
```bash
# Se connecter au container de l'app
dokku enter atlas web

# Tester Python depuis le container
python3 -c "
import os
print('Spaces Key:', os.getenv('DIGITALOCEAN_SPACES_KEY', 'NOT_SET'))
print('Spaces Bucket:', os.getenv('DIGITALOCEAN_SPACES_BUCKET', 'NOT_SET'))
print('Spaces Endpoint:', os.getenv('DIGITALOCEAN_SPACES_ENDPOINT', 'NOT_SET'))
"

# Sortir du container
exit
```

## 🔄 Gestion des Variables

### Ajouter une Variable
```bash
dokku config:set atlas NOUVELLE_VARIABLE="valeur"
```

### Supprimer une Variable
```bash
dokku config:unset atlas VARIABLE_A_SUPPRIMER
```

### Modifier une Variable
```bash
dokku config:set atlas VARIABLE_EXISTANTE="nouvelle_valeur"
```

## 📊 État de l'Application

### Vérifier l'État
```bash
# État général
dokku ps:report atlas

# Processus en cours
dokku ps atlas

# Logs en temps réel
dokku logs atlas --tail
```

### Redéploiement
```bash
# Redémarrer (prend en compte nouvelles variables)
dokku ps:restart atlas

# Redéployer complètement
dokku deploy atlas
```

## 🎯 Variables DigitalOcean Spaces Requises

| Variable | Description | Exemple |
|----------|-------------|---------|
| `DIGITALOCEAN_SPACES_KEY` | Access Key ID | `DO00XXXXXXXXXX` |
| `DIGITALOCEAN_SPACES_SECRET` | Secret Access Key | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `DIGITALOCEAN_SPACES_ENDPOINT` | URL de l'endpoint | `https://fra1.digitaloceanspaces.com` |
| `DIGITALOCEAN_SPACES_BUCKET` | Nom du bucket | `atlas-storage` |

## 🔒 Variables Backup (Optionnelles)

| Variable | Description | Exemple |
|----------|-------------|---------|
| `DB_HOST` | Host PostgreSQL | `localhost` ou IP |
| `DB_PORT` | Port PostgreSQL | `5432` |
| `DB_NAME` | Nom de la base | `atlas_production` |
| `DB_USER` | Utilisateur DB | `atlas_user` |
| `DB_PASSWORD` | Mot de passe DB | `secure_password` |

## 🚨 Sécurité

### Permissions des Variables
```bash
# Les variables sont automatiquement sécurisées par Dokku
# Elles ne sont visibles que par l'application

# Vérifier les permissions
dokku config atlas | head -5
```

### Backup de Configuration
```bash
# Sauvegarder la configuration actuelle
dokku config atlas > /root/atlas_config_backup.txt

# Attention: contient des informations sensibles !
chmod 600 /root/atlas_config_backup.txt
```

## 🔍 Dépannage

### Variables Non Reconnues
```bash
# Redémarrer après changement de config
dokku ps:restart atlas

# Vérifier les logs d'erreur
dokku logs atlas --tail -n 100
```

### Test de Connexion Spaces
```bash
# Depuis le serveur, installer AWS CLI pour test
apt-get install awscli

# Configurer temporairement
aws configure set aws_access_key_id YOUR_SPACES_KEY
aws configure set aws_secret_access_key YOUR_SPACES_SECRET

# Tester la connexion
aws s3 ls --endpoint-url=https://fra1.digitaloceanspaces.com

# Nettoyer après test
rm -rf ~/.aws/
```

---

## 📝 Notes Importantes

1. **Redémarrage Requis** : L'application doit être redémarrée après changement de variables
2. **Variables Sensibles** : Dokku masque automatiquement les valeurs dans les logs
3. **Persistence** : Les variables sont persistantes entre les redéploiements
4. **Rollback** : En cas de problème, utilisez le backup de configuration

---

**⚠️ Rappel** : Ne jamais commiter les clés d'accès dans Git ! Utilisez uniquement les variables d'environnement Dokku.