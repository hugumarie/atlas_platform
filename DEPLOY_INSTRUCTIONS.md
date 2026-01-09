# 🚀 Instructions de Déploiement Production

## Commandes à Exécuter sur atlas-invest.fr

```bash
# Se connecter au serveur
ssh root@atlas-invest.fr

# 1. Aller dans le répertoire de l'app
cd /opt/atlas

# 2. Pull les derniers changements depuis GitHub
git pull origin main

# 3. Déployer avec Dokku
dokku git:sync atlas /opt/atlas
dokku ps:rebuild atlas

# 4. Vérifier le déploiement
dokku logs atlas --tail

# 5. Si besoin de redémarrer
dokku ps:restart atlas
```

## 🎯 Changements de Cette Version

✅ **Fix contrainte Foreign Key (investment_actions)** - CRITIQUE pour production  
✅ **Système de backup DigitalOcean automatique** - Sauvegarde horaire  
✅ **4e catégorie formations + stockage cloud** - Nouvel upload système  
✅ **Modal mobile optimisé + menu universel** - UX améliorée  
✅ **Templates nettoyés et pages légales MAJ** - Contact email mis à jour  

## ⚠️ Notes Importantes

- ✅ **Aucune migration manuelle requise**
- ✅ **Compatible base de données existante** 
- ✅ **Variables d'environnement préservées**
- ✅ **Aucun fichier sensible committé**

## 🔍 Vérifications Post-Déploiement

1. **Test édition plan investissement** (bug critique fixé)
2. **Test upload formation** (nouveau système DigitalOcean)  
3. **Test modal RDV mobile** (responsive amélioré)
4. **Vérifier logs** : aucune erreur FK

## 📞 En Cas de Problème

Si erreur au déploiement :
```bash
# Voir les logs détaillés
dokku logs atlas --tail --num 100

# Revenir à la version précédente
dokku git:from-archive atlas https://github.com/hugumarie/atlas_platform/archive/refs/heads/main.zip

# Redémarrer
dokku ps:restart atlas
```

---
**Commit:** be9a45b - Fix critique contrainte FK + Système backup DigitalOcean + Améliorations  
**Date:** 9 Janvier 2026  
**Status:** 🟢 READY FOR PRODUCTION