#!/bin/bash

# =================================
# ATLAS - Déploiement Production
# =================================

set -e

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Banner
clear
echo -e "${GREEN}"
cat << 'EOF'
  ___  _____ _      ___  _____ 
 / _ \|_   _| |    / _ \|  ___|
/ /_\ \ | | | |   / /_\ \ `--.
|  _  | | | | |   |  _  |`--. \
| | | | | | | |___| | | /\__/ /
\_| |_/ \_/ \_____\_| |_\____/ 

Production Deployment Script
EOF
echo -e "${NC}"

log "🚀 Démarrage du déploiement Atlas en production"

# =================================
# VÉRIFICATIONS PRÉALABLES
# =================================
log "🔍 Vérifications préalables..."

# Vérifier qu'on est root
if [[ $EUID -ne 0 ]]; then
    error "Ce script doit être exécuté en tant que root"
    exit 1
fi

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    error "Docker n'est pas installé"
    echo "Installez Docker avec: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# Vérifier Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    error "Docker Compose n'est pas installé"
    exit 1
fi

# Définir la commande Docker Compose
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

log "✅ Docker et Docker Compose sont installés"

# Vérifier qu'on est dans le bon répertoire
if [[ ! -f "run.py" ]] || [[ ! -d "app" ]]; then
    error "Ce script doit être exécuté depuis le répertoire racine d'Atlas"
    echo "Répertoire actuel: $(pwd)"
    exit 1
fi

log "✅ Répertoire Atlas détecté"

# =================================
# CONFIGURATION
# =================================
log "⚙️ Configuration de l'environnement..."

# Créer le fichier .env s'il n'existe pas
if [[ ! -f ".env" ]]; then
    log "📝 Création du fichier .env..."
    cp .env.production.template .env
    
    warning "⚠️ IMPORTANT: Modifiez le fichier .env avec vos vraies valeurs !"
    echo ""
    echo "Valeurs à modifier obligatoirement:"
    echo "  - POSTGRES_PASSWORD (mot de passe base de données)"
    echo "  - SECRET_KEY (clé secrète Flask)"
    echo ""
    echo "Valeurs optionnelles:"
    echo "  - MAIL_USERNAME et MAIL_PASSWORD (pour les emails)"
    echo "  - OPENAI_API_KEY (pour les fonctionnalités IA)"
    echo "  - BINANCE_API_KEY (pour les prix crypto)"
    echo ""
    read -p "Appuyez sur Entrée après avoir modifié le fichier .env..."
else
    log "✅ Fichier .env existant trouvé"
fi

# Vérifier que les valeurs critiques sont renseignées
source .env

if [[ -z "$POSTGRES_PASSWORD" ]] || [[ "$POSTGRES_PASSWORD" == "CHANGEZ_MOT_DE_PASSE_FORT_ICI" ]]; then
    error "POSTGRES_PASSWORD n'est pas configuré dans .env"
    exit 1
fi

if [[ -z "$SECRET_KEY" ]] || [[ "$SECRET_KEY" == "GENEREZ_UNE_CLE_SECRETE_UNIQUE_ICI" ]]; then
    error "SECRET_KEY n'est pas configuré dans .env"
    exit 1
fi

log "✅ Configuration .env validée"

# =================================
# PRÉPARATION DES FICHIERS
# =================================
log "📁 Préparation des fichiers de configuration..."

# Copier les fichiers de production
cp Dockerfile.production Dockerfile
cp docker-compose.production.yml docker-compose.yml

# Créer la structure Nginx
mkdir -p nginx/conf.d
cp nginx_main.conf nginx/nginx.conf
cp nginx_atlas.conf nginx/conf.d/atlas.conf

# Créer les répertoires nécessaires
mkdir -p backups
mkdir -p logs

log "✅ Fichiers de configuration préparés"

# =================================
# ARRÊT DES SERVICES EXISTANTS
# =================================
log "🛑 Arrêt des services existants..."
$DOCKER_COMPOSE down 2>/dev/null || true
docker system prune -f >/dev/null 2>&1 || true

# =================================
# CONSTRUCTION ET DÉMARRAGE
# =================================
log "🔨 Construction de l'image Atlas..."
$DOCKER_COMPOSE build --no-cache

log "🚀 Démarrage des services..."
$DOCKER_COMPOSE up -d

# =================================
# ATTENTE ET VÉRIFICATIONS
# =================================
log "⏳ Attente du démarrage des services..."

# Attendre PostgreSQL
for i in {1..30}; do
    if docker exec atlas_postgres pg_isready -U atlas >/dev/null 2>&1; then
        log "✅ PostgreSQL prêt"
        break
    fi
    
    if [[ $i -eq 30 ]]; then
        error "❌ PostgreSQL ne démarre pas"
        exit 1
    fi
    
    sleep 2
done

# Attendre Atlas
sleep 20

for i in {1..30}; do
    if curl -f http://localhost/health >/dev/null 2>&1; then
        log "✅ Application Atlas prête"
        break
    fi
    
    if [[ $i -eq 30 ]]; then
        warning "⚠️ L'application Atlas ne répond pas encore"
        break
    fi
    
    sleep 2
done

# =================================
# INITIALISATION BASE DE DONNÉES
# =================================
log "🗃️ Initialisation de la base de données..."

# Créer les tables
if docker exec atlas_app python3 -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('Tables créées avec succès')
" >/dev/null 2>&1; then
    log "✅ Base de données initialisée"
else
    error "❌ Échec de l'initialisation de la base"
    exit 1
fi

# Créer un utilisateur admin si demandé
read -p "Voulez-vous créer un utilisateur administrateur ? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Email admin: " admin_email
    read -s -p "Mot de passe admin: " admin_password
    echo
    
    if docker exec atlas_app python3 -c "
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Vérifier si l'admin existe déjà
    admin = User.query.filter_by(email='$admin_email').first()
    if not admin:
        admin = User(
            email='$admin_email',
            password_hash=generate_password_hash('$admin_password'),
            nom='Admin',
            prenom='Atlas',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('Administrateur créé')
    else:
        print('Administrateur existe déjà')
"; then
        log "✅ Utilisateur administrateur configuré"
    else
        warning "⚠️ Échec de la création de l'administrateur"
    fi
fi

# =================================
# CONFIGURATION DES BACKUPS
# =================================
log "💾 Configuration des backups automatiques..."

# Rendre les scripts exécutables
chmod +x backup_atlas.sh restore_atlas.sh setup_cron_backup.sh

# Configurer les backups automatiques
read -p "Voulez-vous configurer les backups automatiques quotidiens ? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    ./setup_cron_backup.sh
fi

# =================================
# TESTS FINAUX
# =================================
log "🧪 Tests de fonctionnement..."

# Test des services
SERVICES_OK=true

if ! $DOCKER_COMPOSE ps | grep -q "atlas_postgres.*Up"; then
    error "❌ PostgreSQL n'est pas en cours d'exécution"
    SERVICES_OK=false
fi

if ! $DOCKER_COMPOSE ps | grep -q "atlas_app.*Up"; then
    error "❌ Atlas App n'est pas en cours d'exécution"
    SERVICES_OK=false
fi

if ! $DOCKER_COMPOSE ps | grep -q "atlas_nginx.*Up"; then
    error "❌ Nginx n'est pas en cours d'exécution"
    SERVICES_OK=false
fi

if [[ "$SERVICES_OK" == "true" ]]; then
    log "✅ Tous les services sont opérationnels"
else
    error "❌ Certains services ne fonctionnent pas correctement"
    echo ""
    echo "État des services:"
    $DOCKER_COMPOSE ps
    exit 1
fi

# =================================
# FINALISATION
# =================================
log "🎉 Déploiement Atlas terminé avec succès !"

# Obtenir l'IP publique
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "votre_ip")

echo ""
echo -e "${GREEN}📊 RÉSUMÉ DU DÉPLOIEMENT${NC}"
echo "=================================="
echo ""
echo -e "${BLUE}🌐 ACCÈS WEB:${NC}"
echo "   Principal: http://$PUBLIC_IP"
echo "   Health check: http://$PUBLIC_IP/health"
echo "   Login: http://$PUBLIC_IP/plateforme/login"
echo ""

if [[ -n "$admin_email" ]]; then
    echo -e "${BLUE}🔑 COMPTE ADMINISTRATEUR:${NC}"
    echo "   Email: $admin_email"
    echo "   Interface admin: http://$PUBLIC_IP/plateforme/admin/dashboard"
    echo ""
fi

echo -e "${BLUE}📊 SERVICES:${NC}"
$DOCKER_COMPOSE ps

echo ""
echo -e "${BLUE}📋 COMMANDES UTILES:${NC}"
echo "   Voir les logs: $DOCKER_COMPOSE logs -f"
echo "   Redémarrer: $DOCKER_COMPOSE restart"
echo "   Arrêter: $DOCKER_COMPOSE down"
echo "   Backup: ./backup_atlas.sh"
echo "   Monitoring: docker stats"
echo ""

echo -e "${BLUE}📁 FICHIERS IMPORTANTS:${NC}"
echo "   Configuration: .env"
echo "   Logs: /var/log/atlas/"
echo "   Backups: /root/atlas_backups/"
echo ""

log "🚀 Atlas est maintenant en production et accessible !"

exit 0