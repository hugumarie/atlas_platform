#!/bin/bash

# =================================
# ATLAS - Script de Restauration
# =================================

set -e

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction de log
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERREUR:${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ATTENTION:${NC} $1"
}

# Vérifier les paramètres
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 [TIMESTAMP]"
    echo ""
    echo "Exemple: $0 20231223_143022"
    echo ""
    echo "Backups disponibles:"
    find /root/atlas_backups -name "atlas_db_*.sql" -exec basename {} \; | sed 's/atlas_db_//' | sed 's/.sql//' | sort -r | head -10
    exit 1
fi

TIMESTAMP="$1"
BACKUP_DIR="/root/atlas_backups"
DB_BACKUP_FILE="$BACKUP_DIR/atlas_db_$TIMESTAMP.sql"
CUSTOM_BACKUP_FILE="$BACKUP_DIR/atlas_db_$TIMESTAMP.custom"
UPLOADS_BACKUP_FILE="$BACKUP_DIR/atlas_uploads_$TIMESTAMP.tar.gz"

# Vérifier que le backup existe
if [[ ! -f "$DB_BACKUP_FILE" && ! -f "$CUSTOM_BACKUP_FILE" ]]; then
    error "Aucun backup trouvé pour le timestamp: $TIMESTAMP"
    echo ""
    echo "Backups disponibles:"
    find "$BACKUP_DIR" -name "atlas_db_*.sql" -exec basename {} \; | sed 's/atlas_db_//' | sed 's/.sql//' | sort -r
    exit 1
fi

log "🔄 Démarrage de la restauration Atlas..."
log "📅 Timestamp: $TIMESTAMP"

# =================================
# CONFIRMATION
# =================================
warning "⚠️  ATTENTION: Cette opération va REMPLACER toutes les données actuelles !"
echo ""
read -p "Êtes-vous sûr de vouloir continuer ? (tapez 'oui' pour confiruer): " confirm

if [[ "$confirm" != "oui" ]]; then
    log "❌ Restauration annulée"
    exit 0
fi

# =================================
# 1. ARRÊTER L'APPLICATION
# =================================
log "🛑 Arrêt de l'application Atlas..."
docker-compose -f docker-compose.production.yml stop atlas nginx || true

# =================================
# 2. BACKUP DE SÉCURITÉ AVANT RESTAURATION
# =================================
log "💾 Création d'un backup de sécurité avant restauration..."
SAFETY_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
docker exec atlas_postgres pg_dump -U atlas -d atlas_production > "$BACKUP_DIR/safety_backup_$SAFETY_TIMESTAMP.sql" 2>/dev/null || true

# =================================
# 3. RESTAURATION BASE DE DONNÉES
# =================================
log "🗃️ Restauration de la base de données..."

# Supprimer et recréer la base
docker exec atlas_postgres psql -U atlas -c "DROP DATABASE IF EXISTS atlas_production;"
docker exec atlas_postgres psql -U atlas -c "CREATE DATABASE atlas_production;"

# Restaurer depuis le backup
if [[ -f "$CUSTOM_BACKUP_FILE" ]]; then
    log "📥 Restauration depuis le format custom..."
    if docker exec -i atlas_postgres pg_restore -U atlas -d atlas_production < "$CUSTOM_BACKUP_FILE"; then
        log "✅ Base de données restaurée (custom)"
    else
        error "❌ Échec de la restauration custom"
        exit 1
    fi
elif [[ -f "$DB_BACKUP_FILE" ]]; then
    log "📥 Restauration depuis le format SQL..."
    if docker exec -i atlas_postgres psql -U atlas -d atlas_production < "$DB_BACKUP_FILE"; then
        log "✅ Base de données restaurée (SQL)"
    else
        error "❌ Échec de la restauration SQL"
        exit 1
    fi
fi

# =================================
# 4. RESTAURATION UPLOADS
# =================================
if [[ -f "$UPLOADS_BACKUP_FILE" ]]; then
    log "📁 Restauration des fichiers uploads..."
    
    # Supprimer l'ancien volume et en créer un nouveau
    docker volume rm atlas_uploads 2>/dev/null || true
    docker volume create atlas_uploads
    
    # Restaurer les uploads
    if docker run --rm -v atlas_uploads:/target -v "$BACKUP_DIR":/backup alpine tar xzf "/backup/atlas_uploads_$TIMESTAMP.tar.gz" -C /target; then
        log "✅ Uploads restaurés"
    else
        warning "⚠️ Échec de la restauration des uploads"
    fi
else
    warning "⚠️ Pas de backup d'uploads trouvé pour $TIMESTAMP"
fi

# =================================
# 5. REDÉMARRAGE DES SERVICES
# =================================
log "🚀 Redémarrage des services..."
docker-compose -f docker-compose.production.yml up -d

# Attendre que les services soient prêts
log "⏳ Attente du démarrage complet..."
sleep 30

# =================================
# 6. VÉRIFICATION
# =================================
log "🔍 Vérification de la restauration..."

# Vérifier que PostgreSQL répond
if docker exec atlas_postgres pg_isready -U atlas -d atlas_production >/dev/null 2>&1; then
    log "✅ PostgreSQL opérationnel"
else
    error "❌ PostgreSQL ne répond pas"
    exit 1
fi

# Vérifier que l'application répond
sleep 10
if curl -f http://localhost/health >/dev/null 2>&1; then
    log "✅ Application Atlas opérationnelle"
else
    warning "⚠️ L'application Atlas ne répond pas encore (normal si démarrage en cours)"
fi

# Afficher le statut des containers
log "📊 Statut des containers:"
docker-compose -f docker-compose.production.yml ps

# =================================
# 7. RÉSUMÉ
# =================================
log "🎉 Restauration Atlas terminée !"

echo ""
echo "📊 RÉSUMÉ:"
echo "   📅 Backup restauré: $TIMESTAMP"
echo "   🗃️ Base de données: ✅ Restaurée"
echo "   📁 Uploads: $(if [[ -f "$UPLOADS_BACKUP_FILE" ]]; then echo "✅ Restaurés"; else echo "⚠️ Non disponibles"; fi)"
echo "   💾 Backup de sécurité: safety_backup_$SAFETY_TIMESTAMP.sql"

echo ""
echo "🌐 ACCÈS:"
echo "   URL: http://$(curl -s ifconfig.me 2>/dev/null || echo 'votre_ip')"
echo "   Health: http://$(curl -s ifconfig.me 2>/dev/null || echo 'votre_ip')/health"

echo ""
log "💡 Si l'application ne répond pas, attendez quelques minutes le temps du démarrage complet."

exit 0