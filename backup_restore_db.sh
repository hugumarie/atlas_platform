#!/bin/bash

echo "💾 Sauvegarde et restauration base de données Atlas"
echo "=================================================="

case "$1" in
    "backup")
        echo "📤 Création backup de la base de données..."
        BACKUP_FILE="atlas_backup_$(date +%Y%m%d_%H%M%S).sql"
        
        # Backup depuis le serveur
        ssh dokku@167.172.108.93 "postgres:export atlas-db" > "$BACKUP_FILE" 2>/dev/null || \
        ssh dokku@167.172.108.93 "postgres:export atlas-postgres" > "$BACKUP_FILE" 2>/dev/null || \
        ssh dokku@167.172.108.93 "run atlas pg_dump \$DATABASE_URL" > "$BACKUP_FILE"
        
        if [ -s "$BACKUP_FILE" ]; then
            echo "✅ Backup créé: $BACKUP_FILE"
            echo "📊 Taille: $(du -h "$BACKUP_FILE" | cut -f1)"
        else
            echo "❌ Échec du backup"
            rm -f "$BACKUP_FILE"
        fi
        ;;
        
    "restore")
        if [ -z "$2" ]; then
            echo "Usage: $0 restore <fichier_backup.sql>"
            echo "Backups disponibles:"
            ls -la atlas_backup_*.sql 2>/dev/null || echo "Aucun backup trouvé"
            exit 1
        fi
        
        BACKUP_FILE="$2"
        if [ ! -f "$BACKUP_FILE" ]; then
            echo "❌ Fichier $BACKUP_FILE non trouvé"
            exit 1
        fi
        
        echo "📥 Restauration depuis $BACKUP_FILE..."
        echo "⚠️  ATTENTION: Cela va écraser toutes les données existantes!"
        read -p "Confirmer la restauration? (yes/no) " -r
        if [ "$REPLY" != "yes" ]; then
            echo "❌ Restauration annulée"
            exit 1
        fi
        
        # Restaurer sur le serveur
        cat "$BACKUP_FILE" | ssh dokku@167.172.108.93 "postgres:import atlas-db" 2>/dev/null || \
        cat "$BACKUP_FILE" | ssh dokku@167.172.108.93 "postgres:import atlas-postgres" 2>/dev/null || \
        cat "$BACKUP_FILE" | ssh dokku@167.172.108.93 "run atlas psql \$DATABASE_URL"
        
        echo "✅ Restauration terminée"
        echo "🔄 Redémarrage de l'application..."
        ssh dokku@167.172.108.93 "ps:restart atlas"
        ;;
        
    "init")
        echo "🏗️ Initialisation base de données avec données par défaut..."
        ssh dokku@167.172.108.93 "run atlas python -c '
from app import create_app, db
from app.models.apprentissage import Apprentissage

app = create_app()
with app.app_context():
    # Créer les tables si elles n existent pas
    db.create_all()
    
    # Vérifier si on a déjà des formations
    count = Apprentissage.query.count()
    print(f\"Formations existantes: {count}\")
    
    if count == 0:
        print(\"Ajout de formations par défaut...\")
        formations = [
            Apprentissage(
                title=\"Introduction aux ETF\",
                description=\"Comprendre les fonds indiciels cotés\",
                content=\"Contenu de formation sur les ETF...\",
                category=\"placements\",
                difficulty=\"debutant\",
                duration_minutes=15,
                order_index=1
            ),
            Apprentissage(
                title=\"Le PEA : Plan Épargne en Actions\",
                description=\"Tout savoir sur le Plan Épargne en Actions\",
                content=\"Guide complet du PEA...\",
                category=\"fiscalite\",
                difficulty=\"debutant\",
                duration_minutes=20,
                order_index=2
            ),
            Apprentissage(
                title=\"Diversification de portefeuille\",
                description=\"Principes de base de la diversification\",
                content=\"Comment bien diversifier ses investissements...\",
                category=\"strategie\",
                difficulty=\"intermediaire\",
                duration_minutes=25,
                order_index=3
            )
        ]
        
        for formation in formations:
            db.session.add(formation)
        
        db.session.commit()
        print(f\"✅ {len(formations)} formations ajoutées\")
    else:
        print(\"✅ Formations déjà présentes\")
'"
        ;;
        
    *)
        echo "Usage:"
        echo "  $0 backup              # Sauvegarder la base"
        echo "  $0 restore <file.sql>  # Restaurer depuis backup"  
        echo "  $0 init                # Initialiser avec données par défaut"
        echo ""
        echo "Exemples:"
        echo "  $0 backup"
        echo "  $0 restore atlas_backup_20241231_123456.sql"
        echo "  $0 init"
        ;;
esac