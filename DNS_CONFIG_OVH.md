# 🌐 Configuration DNS OVH pour atlas-invest.fr

## 📋 Records DNS à Ajouter dans OVH

### **1. Records Principaux (Domaine → Serveur)**

```dns
# Record A - Domaine principal
Type: A
Sous-domaine: @
Destination: 167.172.108.93
TTL: 3600

# Record A - Sous-domaine www
Type: A  
Sous-domaine: www
Destination: 167.172.108.93
TTL: 3600

# Record CNAME - App (optionnel)
Type: CNAME
Sous-domaine: app
Destination: atlas-invest.fr
TTL: 3600
```

### **2. Records Email (MailerSend)**

```dns
# SPF Record
Type: TXT
Sous-domaine: @
Valeur: v=spf1 include:spf.mailersend.net ~all

# DMARC Record  
Type: TXT
Sous-domaine: _dmarc
Valeur: v=DMARC1; p=quarantine; rua=mailto:dmarc@atlas-invest.fr; ruf=mailto:dmarc@atlas-invest.fr; sp=quarantine; adkim=r; aspf=r;

# DKIM Records (à configurer après validation MailerSend)
# Ces records seront fournis par MailerSend après ajout du domaine
```

## 🔧 **Configuration dans OVH Manager**

### **Étapes :**
1. **Se connecter** à OVH Manager
2. **Aller dans** "Web Cloud" → "Noms de domaine" → "atlas-invest.fr"
3. **Cliquer** sur "Zone DNS"
4. **Ajouter** les records ci-dessus un par un
5. **Attendre** 24-48h pour propagation complète

### **Vérification Propagation**
```bash
# Test propagation DNS
nslookup atlas-invest.fr
dig atlas-invest.fr A
```

---

**⏱️ Temps de propagation : 24-48h maximum**
**🎯 Résultat attendu : atlas-invest.fr → 167.172.108.93**