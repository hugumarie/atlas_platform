#!/usr/bin/env python3
"""
Script de backup automatique de la base de données PostgreSQL de production
vers DigitalOcean Spaces.
"""

import os
import subprocess
import datetime
import gzip
import tempfile
import logging
from pathlib import Path

def setup_logging():
    """Configure le logging pour le script de backup"""
    log_dir = Path('/var/log/atlas')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'backup.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def get_production_config():
    """Récupère la configuration de production"""
    config = {
        'db_host': os.getenv('DB_HOST', 'localhost'),
        'db_port': os.getenv('DB_PORT', '5432'),
        'db_name': os.getenv('DB_NAME', 'atlas_production'),
        'db_user': os.getenv('DB_USER', 'atlas_user'),
        'db_password': os.getenv('DB_PASSWORD'),
        'spaces_key': os.getenv('DIGITALOCEAN_SPACES_KEY'),
        'spaces_secret': os.getenv('DIGITALOCEAN_SPACES_SECRET'),
        'spaces_endpoint': os.getenv('DIGITALOCEAN_SPACES_ENDPOINT'),
        'spaces_bucket': os.getenv('DIGITALOCEAN_SPACES_BUCKET')
    }
    
    # Vérification des variables requises
    required_vars = ['db_password', 'spaces_key', 'spaces_secret', 'spaces_endpoint', 'spaces_bucket']
    missing_vars = [var for var in required_vars if not config.get(var)]
    
    if missing_vars:
        raise ValueError(f"Variables d'environnement manquantes: {', '.join(missing_vars)}")
    
    return config

def create_database_backup(config, logger):
    """Crée un backup de la base de données PostgreSQL"""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"atlas_backup_{timestamp}.sql"
    compressed_filename = f"atlas_backup_{timestamp}.sql.gz"
    
    logger.info(f"Début du backup de la base de données: {config['db_name']}")
    
    # Créer un fichier temporaire pour le backup
    with tempfile.TemporaryDirectory() as temp_dir:
        backup_path = Path(temp_dir) / backup_filename
        compressed_path = Path(temp_dir) / compressed_filename
        
        # Commande pg_dump
        env = os.environ.copy()
        env['PGPASSWORD'] = config['db_password']
        
        cmd = [
            'pg_dump',
            '-h', config['db_host'],
            '-p', config['db_port'],
            '-U', config['db_user'],
            '-d', config['db_name'],
            '--verbose',
            '--no-owner',
            '--no-privileges',
            '-f', str(backup_path)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True,
                timeout=3600  # Timeout de 1 heure
            )
            
            logger.info(f"Backup SQL créé: {backup_path}")
            
            # Compresser le fichier
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    f_out.writelines(f_in)
            
            logger.info(f"Backup compressé: {compressed_path}")
            
            # Vérifier la taille du fichier compressé
            file_size = compressed_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            logger.info(f"Taille du backup compressé: {file_size_mb:.2f} MB")
            
            return compressed_path, compressed_filename
            
        except subprocess.TimeoutExpired:
            logger.error("Timeout lors du backup de la base de données")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"Erreur lors du backup: {e}")
            logger.error(f"Sortie d'erreur: {e.stderr}")
            raise

def upload_to_spaces(backup_path, backup_filename, config, logger):
    """Upload le backup vers DigitalOcean Spaces"""
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        logger.info("Début de l'upload vers DigitalOcean Spaces")
        
        # Configuration du client S3 pour DigitalOcean Spaces
        session = boto3.session.Session()
        client = session.client(
            's3',
            region_name='fra1',  # ou votre région
            endpoint_url=config['spaces_endpoint'],
            aws_access_key_id=config['spaces_key'],
            aws_secret_access_key=config['spaces_secret']
        )
        
        # Chemin de destination dans Spaces
        date_folder = datetime.datetime.now().strftime('%Y/%m/%d')
        spaces_key = f"backups/database/{date_folder}/{backup_filename}"
        
        # Upload du fichier
        with open(backup_path, 'rb') as file_data:
            client.upload_fileobj(
                file_data,
                config['spaces_bucket'],
                spaces_key,
                ExtraArgs={
                    'ContentType': 'application/gzip',
                    'Metadata': {
                        'backup-date': datetime.datetime.now().isoformat(),
                        'database': config['db_name'],
                        'type': 'postgresql-dump'
                    }
                }
            )
        
        # Construire l'URL publique
        spaces_url = f"{config['spaces_endpoint']}/{config['spaces_bucket']}/{spaces_key}"
        
        logger.info(f"Backup uploadé avec succès: {spaces_url}")
        return spaces_key, spaces_url
        
    except ImportError:
        logger.error("Module boto3 non disponible. Installez-le avec: pip install boto3")
        raise
    except ClientError as e:
        logger.error(f"Erreur lors de l'upload vers Spaces: {e}")
        raise

def cleanup_old_backups(config, logger, retention_days=30):
    """Supprime les anciens backups (garde les backups des X derniers jours)"""
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        logger.info(f"Nettoyage des backups de plus de {retention_days} jours")
        
        session = boto3.session.Session()
        client = session.client(
            's3',
            region_name='fra1',
            endpoint_url=config['spaces_endpoint'],
            aws_access_key_id=config['spaces_key'],
            aws_secret_access_key=config['spaces_secret']
        )
        
        # Date limite pour la suppression
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)
        
        # Lister les objets dans le dossier backups/database/
        response = client.list_objects_v2(
            Bucket=config['spaces_bucket'],
            Prefix='backups/database/'
        )
        
        deleted_count = 0
        if 'Contents' in response:
            for obj in response['Contents']:
                # Vérifier la date de modification
                if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                    try:
                        client.delete_object(
                            Bucket=config['spaces_bucket'],
                            Key=obj['Key']
                        )
                        logger.info(f"Backup supprimé: {obj['Key']}")
                        deleted_count += 1
                    except ClientError as e:
                        logger.warning(f"Impossible de supprimer {obj['Key']}: {e}")
        
        logger.info(f"Nettoyage terminé: {deleted_count} anciens backups supprimés")
        
    except Exception as e:
        logger.warning(f"Erreur lors du nettoyage: {e}")

def send_notification(status, message, config, logger):
    """Envoie une notification (optionnel - pour intégration future avec email/Slack)"""
    # Pour l'instant, juste un log
    if status == 'success':
        logger.info(f"✅ BACKUP RÉUSSI: {message}")
    else:
        logger.error(f"❌ BACKUP ÉCHOUÉ: {message}")

def main():
    """Fonction principale du script de backup"""
    logger = setup_logging()
    
    try:
        logger.info("=" * 50)
        logger.info("DÉBUT DU BACKUP AUTOMATIQUE ATLAS PRODUCTION")
        logger.info("=" * 50)
        
        # Récupération de la configuration
        config = get_production_config()
        logger.info(f"Configuration chargée - Base: {config['db_name']}@{config['db_host']}")
        
        # Création du backup
        backup_path, backup_filename = create_database_backup(config, logger)
        
        # Upload vers DigitalOcean Spaces
        spaces_key, spaces_url = upload_to_spaces(backup_path, backup_filename, config, logger)
        
        # Nettoyage des anciens backups (garde 30 jours)
        cleanup_old_backups(config, logger, retention_days=30)
        
        success_message = f"Backup {backup_filename} créé et uploadé avec succès"
        send_notification('success', success_message, config, logger)
        
        logger.info("=" * 50)
        logger.info("BACKUP TERMINÉ AVEC SUCCÈS")
        logger.info("=" * 50)
        
    except Exception as e:
        error_message = f"Erreur lors du backup: {str(e)}"
        logger.error(error_message, exc_info=True)
        send_notification('error', error_message, config, logger)
        
        logger.info("=" * 50)
        logger.error("BACKUP ÉCHOUÉ")
        logger.info("=" * 50)
        
        # Sortir avec un code d'erreur
        exit(1)

if __name__ == "__main__":
    main()