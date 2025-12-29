# ⚡ Configuration Dokku pour atlas-invest.fr

## 🖥️ **Commandes à Exécuter sur le Serveur**

### **1. Se Connecter au Serveur**
```bash
ssh root@167.172.108.93
```

### **2. Configuration Domaine Dokku**
```bash
# Ajouter le domaine principal
dokku domains:add atlas atlas-invest.fr

# Ajouter le sous-domaine www
dokku domains:add atlas www.atlas-invest.fr

# Vérifier les domaines configurés
dokku domains:report atlas

# Supprimer l'ancien domaine IP (optionnel)
dokku domains:remove atlas 167.172.108.93
```

### **3. Configuration SSL/HTTPS Automatique**
```bash
# Installer le plugin Let's Encrypt si pas déjà fait
dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git

# Configurer l'email pour Let's Encrypt
dokku letsencrypt:set atlas email hugues.marie925@gmail.com

# Activer SSL automatique
dokku letsencrypt:enable atlas

# Activer le renouvellement automatique
dokku letsencrypt:cron-job --add
```

### **4. Variables d'Environnement Production**
```bash
# Configuration domaine
dokku config:set atlas FLASK_ENV=production
dokku config:set atlas SECRET_KEY="$(openssl rand -hex 32)"

# URL du site (pour les emails)
dokku config:set atlas SITE_URL="https://atlas-invest.fr"

# Email configuration
dokku config:set atlas ATLAS_FROM_EMAIL="noreply@atlas-invest.fr"
dokku config:set atlas ATLAS_FROM_NAME="Atlas Invest"

# MailerSend (à configurer après avoir le token)
dokku config:set atlas MAILERSEND_API_TOKEN="votre-token-mailersend"

# Base de données (vérifier qu'elle existe)
dokku postgres:info atlas-db
```

### **5. Vérification Configuration**
```bash
# Voir toutes les variables
dokku config atlas

# Voir les domaines
dokku domains:report atlas

# Voir les certificats SSL
dokku letsencrypt:list
```

## 🌟 **Résultat Attendu**

Après ces commandes :
- ✅ **atlas-invest.fr** → App Atlas
- ✅ **www.atlas-invest.fr** → App Atlas  
- ✅ **HTTPS automatique** avec certificat valide
- ✅ **Redirection HTTP → HTTPS**
- ✅ **Variables d'env** configurées pour production

## 🚨 **Points Importants**

1. **Attendre propagation DNS** avant de lancer Let's Encrypt
2. **Vérifier que le domaine pointe bien** vers le serveur
3. **Sauvegarder** les certificats générés
4. **Tester HTTPS** après configuration

---

**⚡ Serveur configuré pour atlas-invest.fr en production !**