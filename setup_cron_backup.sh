#!/bin/bash

# =================================
# ATLAS - Configuration Cron Backup
# =================================

set -e

# Configuration
ATLAS_DIR="/root/atlas_platform"
BACKUP_SCRIPT="$ATLAS_DIR/backup_atlas.sh"

# Couleurs pour les logs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ATTENTION:${NC} $1"
}

log "📅 Configuration du backup automatique Atlas..."

# Vérifier que le script de backup existe
if [[ ! -f "$BACKUP_SCRIPT" ]]; then
    echo "Erreur: Script de backup non trouvé à $BACKUP_SCRIPT"
    exit 1
fi

# Rendre le script exécutable
chmod +x "$BACKUP_SCRIPT"

# Créer le répertoire de logs pour cron
mkdir -p /var/log/atlas

# Configuration cron
CRON_JOB="0 2 * * * cd $ATLAS_DIR && $BACKUP_SCRIPT >> /var/log/atlas/backup.log 2>&1"

# Vérifier si le job cron existe déjà
if crontab -l 2>/dev/null | grep -q "backup_atlas.sh"; then
    warning "⚠️ Un job de backup existe déjà dans la crontab"
    echo ""
    echo "Crontab actuelle:"
    crontab -l 2>/dev/null | grep backup_atlas.sh || echo "Aucun job trouvé"
    echo ""
    read -p "Voulez-vous remplacer la configuration existante ? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "❌ Configuration annulée"
        exit 0
    fi
    
    # Supprimer l'ancien job
    crontab -l 2>/dev/null | grep -v "backup_atlas.sh" | crontab - || true
fi

# Ajouter le nouveau job cron
(crontab -l 2>/dev/null || echo "") | grep -v "backup_atlas.sh" | { cat; echo "$CRON_JOB"; } | crontab -

log "✅ Job cron configuré"

# Créer un script de rotation des logs
cat > /etc/logrotate.d/atlas << 'EOF'
/var/log/atlas/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    copytruncate
    create 644 root root
}
EOF

log "✅ Rotation des logs configurée"

# Test du backup (optionnel)
read -p "Voulez-vous tester le backup maintenant ? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "🧪 Test du backup..."
    cd "$ATLAS_DIR"
    if ./backup_atlas.sh; then
        log "✅ Test de backup réussi"
    else
        warning "❌ Échec du test de backup"
    fi
fi

# Résumé
echo ""
log "🎉 Configuration terminée !"
echo ""
echo "📊 RÉSUMÉ:"
echo "   ⏰ Planification: Tous les jours à 2h00"
echo "   📁 Logs: /var/log/atlas/backup.log"
echo "   💾 Backups: /root/atlas_backups/"
echo "   🔄 Rétention: 14 jours"
echo ""
echo "📋 COMMANDES UTILES:"
echo "   Voir la crontab: crontab -l"
echo "   Voir les logs: tail -f /var/log/atlas/backup.log"
echo "   Backup manuel: cd $ATLAS_DIR && ./backup_atlas.sh"
echo "   Lister backups: ls -la /root/atlas_backups/"
echo ""

# Afficher le prochain backup
NEXT_BACKUP=$(date -d "tomorrow 02:00" '+%Y-%m-%d %H:%M:%S')
echo "🕐 Prochain backup automatique: $NEXT_BACKUP"

exit 0