#!/bin/bash

# Script d'application des migrations pour Atlas
# Usage: ./apply_migrations.sh [production|local]

set -e

ENVIRONMENT=${1:-local}

if [ "$ENVIRONMENT" = "production" ]; then
    echo "🚀 Application des migrations en PRODUCTION"
    echo "⚠️  ATTENTION: Vous allez modifier la base de données de production!"
    read -p "Continuer? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "❌ Annulé par l'utilisateur"
        exit 1
    fi
    
    # Variables production (à définir via environment)
    DB_HOST=${DB_HOST:-"localhost"}
    DB_PORT=${DB_PORT:-"5432"}  
    DB_NAME=${DB_NAME:-"atlas_db"}
    DB_USER=${DB_USER:-"atlas_user"}
    
    if [ -z "$DB_PASSWORD" ]; then
        echo "❌ Variable DB_PASSWORD manquante"
        exit 1
    fi
    
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\dt"
    
else
    echo "🔧 Application des migrations en LOCAL"
    DB_HOST="localhost"
    DB_PORT="5432"
    DB_NAME="atlas_db"
    DB_USER="huguesmarie"
    
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\dt"
fi

echo "📊 Base de données connectée avec succès"

# Application des migrations dans l'ordre
echo "📁 Application des migrations..."

for migration in migrations/*.sql; do
    if [ -f "$migration" ]; then
        echo "  ▶️  Applying: $(basename $migration)"
        
        if [ "$ENVIRONMENT" = "production" ]; then
            PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f "$migration"
        else
            psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f "$migration"
        fi
        
        echo "  ✅ Applied: $(basename $migration)"
    fi
done

echo ""
echo "✅ Toutes les migrations ont été appliquées avec succès!"
echo ""

# Vérification des nouvelles tables
echo "📋 Vérification des tables créées..."

if [ "$ENVIRONMENT" = "production" ]; then
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\dt password_reset_tokens; \dt comptes_rendus;"
else
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\dt password_reset_tokens; \dt comptes_rendus;"
fi

echo ""
echo "🎉 Migration terminée!"