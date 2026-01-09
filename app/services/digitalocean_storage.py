"""
Service pour la gestion des fichiers sur DigitalOcean Spaces
"""

import boto3
from botocore.client import Config
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import logging

logger = logging.getLogger(__name__)

class DigitalOceanSpacesService:
    def __init__(self, access_key, secret_key, region='fra1', space_name='atlas-database'):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.space_name = space_name
        self.endpoint_url = f'https://{region}.digitaloceanspaces.com'
        self.public_url = f'https://{space_name}.{region}.digitaloceanspaces.com'
        
        # Configuration du client S3 compatible
        self.session = boto3.session.Session()
        self.client = self.session.client(
            's3',
            region_name=region,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4')
        )
        
        logger.info(f"✅ DigitalOcean Spaces configuré - Space: {space_name}, Région: {region}")

    def upload_file(self, file, folder_path, custom_filename=None, make_public=True):
        """
        Upload un fichier vers DigitalOcean Spaces
        
        Args:
            file: Fichier werkzeug FileStorage
            folder_path: Chemin du dossier dans le Space (ex: 'apprentissages/pdfs')
            custom_filename: Nom personnalisé pour le fichier (optionnel)
            make_public: Rendre le fichier public (défaut: True)
            
        Returns:
            dict: {'success': bool, 'url': str, 'key': str, 'error': str}
        """
        try:
            if not file or not file.filename:
                return {
                    'success': False,
                    'error': 'Aucun fichier fourni',
                    'url': None,
                    'key': None
                }
            
            # Générer un nom de fichier unique si pas fourni
            if custom_filename:
                filename = custom_filename
            else:
                # Nom sécurisé avec timestamp et UUID
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                original_name = secure_filename(file.filename)
                name_without_ext = os.path.splitext(original_name)[0]
                extension = os.path.splitext(original_name)[1]
                filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{name_without_ext}{extension}"
            
            # Construire le chemin complet dans le Space
            key = f"{folder_path.strip('/')}/{filename}"
            
            # Déterminer le type MIME
            content_type = file.content_type or 'application/octet-stream'
            
            # Configuration pour l'upload
            extra_args = {
                'ContentType': content_type,
            }
            
            if make_public:
                extra_args['ACL'] = 'public-read'
            
            # Upload du fichier
            logger.info(f"📤 Upload vers DigitalOcean Spaces: {key}")
            self.client.upload_fileobj(
                file,
                self.space_name,
                key,
                ExtraArgs=extra_args
            )
            
            # URL publique du fichier
            public_url = f"{self.public_url}/{key}"
            
            logger.info(f"✅ Fichier uploadé avec succès: {public_url}")
            
            return {
                'success': True,
                'url': public_url,
                'key': key,
                'error': None
            }
            
        except Exception as e:
            error_msg = f"Erreur lors de l'upload: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'url': None,
                'key': None
            }

    def delete_file(self, key):
        """
        Supprime un fichier de DigitalOcean Spaces
        
        Args:
            key: Clé du fichier dans le Space
            
        Returns:
            dict: {'success': bool, 'error': str}
        """
        try:
            logger.info(f"🗑️ Suppression du fichier: {key}")
            self.client.delete_object(Bucket=self.space_name, Key=key)
            logger.info(f"✅ Fichier supprimé avec succès: {key}")
            
            return {
                'success': True,
                'error': None
            }
            
        except Exception as e:
            error_msg = f"Erreur lors de la suppression: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

    def file_exists(self, key):
        """
        Vérifie si un fichier existe dans le Space
        
        Args:
            key: Clé du fichier dans le Space
            
        Returns:
            bool: True si le fichier existe
        """
        try:
            self.client.head_object(Bucket=self.space_name, Key=key)
            return True
        except:
            return False

    def get_file_url(self, key):
        """
        Retourne l'URL publique d'un fichier
        
        Args:
            key: Clé du fichier dans le Space
            
        Returns:
            str: URL publique du fichier
        """
        return f"{self.public_url}/{key}"

    def list_files(self, folder_path="", max_keys=1000):
        """
        Liste les fichiers dans un dossier
        
        Args:
            folder_path: Chemin du dossier (optionnel)
            max_keys: Nombre maximum de fichiers à retourner
            
        Returns:
            list: Liste des fichiers avec leurs métadonnées
        """
        try:
            prefix = folder_path.strip('/') + '/' if folder_path else ''
            
            response = self.client.list_objects_v2(
                Bucket=self.space_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'url': self.get_file_url(obj['Key'])
                    })
            
            return files
            
        except Exception as e:
            logger.error(f"Erreur lors de la liste des fichiers: {str(e)}")
            return []


# Instance globale du service (sera configurée depuis les variables d'environnement)
spaces_service = None

def init_spaces_service(access_key, secret_key):
    """
    Initialise le service DigitalOcean Spaces
    """
    global spaces_service
    spaces_service = DigitalOceanSpacesService(
        access_key=access_key,
        secret_key=secret_key
    )
    return spaces_service

def get_spaces_service():
    """
    Retourne l'instance du service DigitalOcean Spaces
    Initialise le service si pas encore fait
    """
    global spaces_service
    if spaces_service is None:
        # Tentative d'initialisation à la demande
        from flask import current_app
        try:
            if current_app.config.get('DO_SPACES_ACCESS_KEY') and current_app.config.get('DO_SPACES_SECRET_KEY'):
                spaces_service = DigitalOceanSpacesService(
                    access_key=current_app.config['DO_SPACES_ACCESS_KEY'],
                    secret_key=current_app.config['DO_SPACES_SECRET_KEY']
                )
                print(f"✅ Service DigitalOcean initialisé à la demande")
        except Exception as e:
            print(f"❌ Erreur initialisation DigitalOcean à la demande: {e}")
    
    return spaces_service