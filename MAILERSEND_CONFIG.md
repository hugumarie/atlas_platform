# 📧 Configuration MailerSend pour Atlas

## 🎯 **À Configurer Côté Domaine**

### **1. Domaine à Utiliser**
- **Domaine :** `atlas-invest.fr`
- **Email expéditeur :** `noreply@atlas-invest.fr`
- **Email contact :** `contact@atlas-invest.fr`

### **2. Configuration DNS Required**
Pour que MailerSend fonctionne avec votre domaine :

#### **SPF Record**
```
Type: TXT
Name: @
Value: v=spf1 include:spf.mailersend.net ~all
```

#### **DKIM Record** 
```
Type: TXT
Name: [fourni par MailerSend]
Value: [fourni par MailerSend]
```

#### **DMARC Record**
```
Type: TXT
Name: _dmarc
Value: v=DMARC1; p=none; rua=mailto:dmarc@atlas-invest.fr
```

## 🔧 **Configuration Code**

### **Variables d'Environnement**
```bash
# Dans .env
MAILERSEND_API_TOKEN=your-mailersend-token
ATLAS_FROM_EMAIL=noreply@atlas-finance.fr
ATLAS_FROM_NAME="Atlas Finance"
```

### **Modifications à Faire**
1. **Dans admin.py ligne 1083 :** Remplacer le token MailerSend
2. **Dans admin.py ligne 1091 :** Remplacer `noreply@votre-domaine.com` par `noreply@atlas-finance.fr`

## 📋 **Étapes de Configuration**

### **1. Côté MailerSend Dashboard**
1. Ajouter le domaine `atlas-finance.fr`
2. Copier les valeurs DNS (SPF, DKIM)
3. Générer un nouveau API token

### **2. Côté Hébergeur/Domaine**
1. Ajouter les records DNS fournis par MailerSend
2. Attendre propagation (24-48h)
3. Vérifier dans MailerSend que le domaine est validé

### **3. Côté Code**
1. Remplacer le token API dans `admin.py`
2. Remplacer l'email expéditeur
3. Tester l'envoi

## 🧪 **Test de Validation**

Une fois configuré, tester avec :
```python
# Test simple
mailer = MailerSendService("votre-nouveau-token")
result = mailer.send_email(
    to_email="test@gmail.com",
    to_name="Test",
    subject="Test Atlas",
    html_content="<p>Test</p>",
    text_content="Test",
    from_email="noreply@atlas-finance.fr",
    from_name="Atlas Finance"
)
```

## 🎯 **Avantages MailerSend vs Mailjet**
- ✅ **Plus fiable** pour la délivrabilité
- ✅ **Interface plus claire**
- ✅ **Logs détaillés** des envois
- ✅ **Templates visuels** disponibles
- ✅ **Webhooks** pour le tracking

---

**Une fois votre domaine configuré, le système d'invitation fonctionnera parfaitement !**