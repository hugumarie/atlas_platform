#!/bin/bash

# Configuration automatique des backups DigitalOcean Spaces pour Atlas
# Usage: ./setup_backup_digitalocean.sh

echo "🗄️ Configuration des backups automatiques DigitalOcean Spaces"
echo ""

# Variables DigitalOcean Spaces
echo "📝 Configuration DigitalOcean Spaces..."
echo ""
echo "Tu auras besoin de tes clés DigitalOcean Spaces:"
echo "1. Va sur: https://cloud.digitalocean.com/settings/api/tokens"
echo "2. Génère un 'Spaces access key'"
echo "3. Note la région de ton Space (ex: fra1, ams3, nyc3)"
echo ""

read -p "🔑 Access Key ID: " DO_ACCESS_KEY
read -p "🔐 Secret Access Key: " DO_SECRET_KEY
read -p "🌍 Région (ex: fra1): " DO_REGION
read -p "🪣 Nom du bucket/space (ex: atlas-backups): " DO_BUCKET

echo ""
echo "⚙️ Configuration du serveur..."

# Installer s3cmd sur le serveur Dokku
ssh root@167.172.108.93 << EOF
echo "📦 Installation de s3cmd..."
apt update
apt install -y s3cmd

echo "🔧 Configuration s3cmd pour DigitalOcean Spaces..."
cat > /root/.s3cfg << EOL
[default]
access_key = $DO_ACCESS_KEY
secret_key = $DO_SECRET_KEY
host_base = ${DO_REGION}.digitaloceanspaces.com
host_bucket = %(bucket)s.${DO_REGION}.digitaloceanspaces.com
bucket_location = $DO_REGION
use_https = True
signature_v2 = False
EOL

echo "✅ s3cmd configuré pour DigitalOcean Spaces"

echo "🧪 Test de connexion..."
s3cmd ls s3://$DO_BUCKET/ || {
    echo "📦 Création du bucket $DO_BUCKET..."
    s3cmd mb s3://$DO_BUCKET/
}

echo "✅ Bucket $DO_BUCKET accessible"
EOF

echo "✅ Serveur configuré pour DigitalOcean Spaces"
echo ""

# Installer le plugin Dokku postgres backup avec S3
echo "📦 Installation du plugin Dokku backup..."
ssh root@167.172.108.93 << EOF
# Créer script de backup personnalisé
cat > /usr/local/bin/atlas-backup.sh << 'EOL'
#!/bin/bash

# Script de backup Atlas vers DigitalOcean Spaces
TIMESTAMP=\$(date +%Y%m%d_%H%M%S)
DB_NAME="atlas-db"
BUCKET_NAME="$DO_BUCKET"
BACKUP_FILE="atlas_backup_\${TIMESTAMP}.sql"
TEMP_FILE="/tmp/\${BACKUP_FILE}"

echo "🗄️ Backup Atlas vers DigitalOcean Spaces - \$TIMESTAMP"

# Créer backup PostgreSQL
echo "   Export base de données..."
dokku postgres:export \$DB_NAME > \$TEMP_FILE

if [[ \$? -eq 0 && -s \$TEMP_FILE ]]; then
    # Compresser le backup
    echo "   Compression..."
    gzip \$TEMP_FILE
    TEMP_FILE="\${TEMP_FILE}.gz"
    BACKUP_FILE="\${BACKUP_FILE}.gz"
    
    # Upload vers DigitalOcean Spaces  
    echo "   Upload vers DigitalOcean Spaces..."
    s3cmd put \$TEMP_FILE s3://\$BUCKET_NAME/\$BACKUP_FILE
    
    if [[ \$? -eq 0 ]]; then
        echo "   ✅ Backup réussi: \$BACKUP_FILE"
        
        # Garder seulement les 30 derniers backups
        echo "   🧹 Nettoyage anciens backups..."
        s3cmd ls s3://\$BUCKET_NAME/ | grep "atlas_backup_" | sort | head -n -30 | awk '{print \$4}' | while read file; do
            s3cmd del "\$file" 2>/dev/null
        done
        
        # Afficher l'espace utilisé
        TOTAL_SIZE=\$(s3cmd ls s3://\$BUCKET_NAME/ --recursive | awk '{sum += \$3} END {print sum/1024/1024}')
        echo "   📊 Espace utilisé: \${TOTAL_SIZE} MB"
        
    else
        echo "   ❌ Erreur upload DigitalOcean Spaces"
        exit 1
    fi
    
    # Nettoyer fichier temporaire
    rm -f \$TEMP_FILE
else
    echo "   ❌ Erreur export base de données"
    exit 1
fi
EOL

chmod +x /usr/local/bin/atlas-backup.sh

echo "✅ Script de backup installé"
EOF

# Configurer le cron pour backups automatiques
echo "⏰ Configuration des backups automatiques..."
ssh root@167.172.108.93 << 'EOF'
# Ajouter tâche cron pour backup quotidien à 2h du matin
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/atlas-backup.sh >> /var/log/atlas-backup.log 2>&1") | crontab -

echo "✅ Backup automatique configuré (tous les jours à 2h)"

# Créer aussi un script de restauration
cat > /usr/local/bin/atlas-restore.sh << 'EOL'
#!/bin/bash

# Script de restauration Atlas depuis DigitalOcean Spaces
BUCKET_NAME="$DO_BUCKET"

if [[ -z "$1" ]]; then
    echo "Usage: $0 <nom_du_backup>"
    echo ""
    echo "Backups disponibles:"
    s3cmd ls s3://$BUCKET_NAME/ | grep "atlas_backup_" | awk '{print $4}' | sed 's|s3://'$BUCKET_NAME'/||'
    exit 1
fi

BACKUP_FILE="$1"
TEMP_FILE="/tmp/$BACKUP_FILE"

echo "🔄 Restauration Atlas depuis: $BACKUP_FILE"

# Télécharger le backup
echo "   Téléchargement..."
s3cmd get s3://$BUCKET_NAME/$BACKUP_FILE $TEMP_FILE

if [[ $? -eq 0 ]]; then
    # Décompresser si nécessaire
    if [[ $BACKUP_FILE == *.gz ]]; then
        echo "   Décompression..."
        gunzip $TEMP_FILE
        TEMP_FILE="${TEMP_FILE%.gz}"
    fi
    
    # Restaurer la base
    echo "   Restauration base de données..."
    echo "⚠️  ATTENTION: Ceci va REMPLACER la base de données actuelle !"
    read -p "   Continuer ? (y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        dokku postgres:import atlas-db < $TEMP_FILE
        echo "   ✅ Restauration terminée"
    else
        echo "   ❌ Restauration annulée"
    fi
    
    rm -f $TEMP_FILE
else
    echo "   ❌ Erreur téléchargement backup"
    exit 1
fi
EOL

chmod +x /usr/local/bin/atlas-restore.sh

echo "✅ Script de restauration installé"
EOF

echo ""
echo "🎉 Configuration terminée !"
echo ""
echo "📊 Commandes disponibles sur le serveur:"
echo "   • Backup manuel: ssh root@167.172.108.93 '/usr/local/bin/atlas-backup.sh'"
echo "   • Lister backups: ssh root@167.172.108.93 's3cmd ls s3://$DO_BUCKET/'"
echo "   • Restaurer: ssh root@167.172.108.93 '/usr/local/bin/atlas-restore.sh BACKUP_NAME'"
echo "   • Logs: ssh root@167.172.108.93 'tail -f /var/log/atlas-backup.log'"
echo ""
echo "⏰ Backups automatiques: Tous les jours à 2h du matin"
echo "🗄️ Rétention: 30 derniers backups gardés automatiquement"
echo ""
echo "🧪 Tester maintenant:"
echo "   ssh root@167.172.108.93 '/usr/local/bin/atlas-backup.sh'"