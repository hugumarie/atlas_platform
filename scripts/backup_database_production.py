#!/usr/bin/env python3
"""
Script de sauvegarde automatique de la base de données PostgreSQL vers DigitalOcean Spaces.

Ce script :
1. Effectue un dump de la base de données PostgreSQL
2. Compresse le fichier avec gzip
3. Upload vers DigitalOcean Spaces dans backups/database/YYYY/MM/DD/
4. Supprime les backups de plus de 30 jours

Conçu pour être exécuté via cron toutes les heures.
"""

import os
import sys
import subprocess
import gzip
import boto3
from datetime import datetime, timedelta
from pathlib import Path

# Ajouter le répertoire parent au path pour importer app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_database_url():
    """Récupère l'URL de la base de données depuis les variables d'environnement."""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ Erreur: DATABASE_URL non défini")
        sys.exit(1)
    return db_url

def get_spaces_config():
    """Récupère la configuration DigitalOcean Spaces."""
    config = {
        'key': os.environ.get('DIGITALOCEAN_SPACES_KEY'),
        'secret': os.environ.get('DIGITALOCEAN_SPACES_SECRET'),
        'endpoint': os.environ.get('DIGITALOCEAN_SPACES_ENDPOINT', 'https://fra1.digitaloceanspaces.com'),
        'bucket': os.environ.get('DIGITALOCEAN_SPACES_BUCKET', 'atlas-storage')
    }

    if not config['key'] or not config['secret']:
        print("❌ Erreur: Clés DigitalOcean Spaces non définies")
        sys.exit(1)

    return config

def create_database_backup():
    """Crée un backup de la base de données avec pg_dump."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"atlas_backup_{timestamp}.sql"
    backup_path = f"/tmp/{backup_filename}"

    print(f"📦 Création du backup: {backup_filename}")

    # Extraire les infos de connexion depuis DATABASE_URL
    db_url = get_database_url()

    try:
        # pg_dump avec connexion depuis DATABASE_URL
        result = subprocess.run(
            ['pg_dump', db_url, '-f', backup_path],
            capture_output=True,
            text=True,
            timeout=3600  # 1 heure max
        )

        if result.returncode != 0:
            print(f"❌ Erreur pg_dump: {result.stderr}")
            return None

        print(f"✅ Backup SQL créé: {os.path.getsize(backup_path) / (1024*1024):.2f} MB")
        return backup_path

    except subprocess.TimeoutExpired:
        print("❌ Timeout lors du backup (> 1h)")
        return None
    except Exception as e:
        print(f"❌ Erreur lors du backup: {e}")
        return None

def compress_backup(backup_path):
    """Compresse le backup avec gzip."""
    compressed_path = f"{backup_path}.gz"

    print(f"🗜️  Compression du backup...")

    try:
        with open(backup_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb', compresslevel=9) as f_out:
                f_out.writelines(f_in)

        # Supprimer le fichier non compressé
        os.remove(backup_path)

        compressed_size = os.path.getsize(compressed_path) / (1024*1024)
        print(f"✅ Backup compressé: {compressed_size:.2f} MB")

        return compressed_path

    except Exception as e:
        print(f"❌ Erreur lors de la compression: {e}")
        return None

def upload_to_spaces(file_path):
    """Upload le backup vers DigitalOcean Spaces."""
    config = get_spaces_config()

    # Créer le chemin dans Spaces: backups/database/YYYY/MM/DD/filename
    now = datetime.now()
    spaces_key = f"backups/database/{now.year}/{now.month:02d}/{now.day:02d}/{os.path.basename(file_path)}"

    print(f"☁️  Upload vers Spaces: {spaces_key}")

    try:
        # Initialiser le client S3 (compatible avec Spaces)
        s3_client = boto3.client(
            's3',
            endpoint_url=config['endpoint'],
            aws_access_key_id=config['key'],
            aws_secret_access_key=config['secret']
        )

        # Upload avec metadata
        s3_client.upload_file(
            file_path,
            config['bucket'],
            spaces_key,
            ExtraArgs={
                'ACL': 'private',
                'Metadata': {
                    'backup-date': now.isoformat(),
                    'database': 'atlas_production',
                    'type': 'postgresql_dump'
                }
            }
        )

        # Supprimer le fichier local
        os.remove(file_path)

        print(f"✅ Backup uploadé avec succès")
        return spaces_key

    except Exception as e:
        print(f"❌ Erreur lors de l'upload: {e}")
        return None

def cleanup_old_backups():
    """Supprime les backups de plus de 30 jours."""
    config = get_spaces_config()
    retention_days = 30
    cutoff_date = datetime.now() - timedelta(days=retention_days)

    print(f"🧹 Nettoyage des backups > {retention_days} jours...")

    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=config['endpoint'],
            aws_access_key_id=config['key'],
            aws_secret_access_key=config['secret']
        )

        # Lister tous les backups
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=config['bucket'], Prefix='backups/database/')

        deleted_count = 0
        for page in pages:
            if 'Contents' not in page:
                continue

            for obj in page['Contents']:
                # Vérifier la date de modification
                if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                    s3_client.delete_object(Bucket=config['bucket'], Key=obj['Key'])
                    deleted_count += 1
                    print(f"  🗑️  Supprimé: {obj['Key']}")

        if deleted_count > 0:
            print(f"✅ {deleted_count} ancien(s) backup(s) supprimé(s)")
        else:
            print(f"✅ Aucun backup à supprimer")

    except Exception as e:
        print(f"⚠️  Erreur lors du nettoyage: {e}")

def main():
    """Fonction principale."""
    print("=" * 70)
    print("🚀 BACKUP AUTOMATIQUE BASE DE DONNÉES ATLAS")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()

    # 1. Créer le backup SQL
    backup_path = create_database_backup()
    if not backup_path:
        print("\n❌ Échec du backup")
        sys.exit(1)

    # 2. Compresser
    compressed_path = compress_backup(backup_path)
    if not compressed_path:
        print("\n❌ Échec de la compression")
        sys.exit(1)

    # 3. Upload vers Spaces
    spaces_key = upload_to_spaces(compressed_path)
    if not spaces_key:
        print("\n❌ Échec de l'upload")
        sys.exit(1)

    # 4. Nettoyer les vieux backups
    cleanup_old_backups()

    print()
    print("=" * 70)
    print("✅ BACKUP TERMINÉ AVEC SUCCÈS")
    print(f"📂 Fichier: {spaces_key}")
    print("=" * 70)

if __name__ == '__main__':
    main()
