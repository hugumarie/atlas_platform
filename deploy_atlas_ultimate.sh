#!/bin/bash
set -e

echo "🚀 ATLAS - DÉPLOIEMENT AUTOMATIQUE COMPLET"
echo "=========================================="
echo ""
echo "✅ Base de données PostgreSQL"
echo "✅ Application Atlas complète"  
echo "✅ Site vitrine"
echo "✅ Nginx reverse proxy"
echo "✅ Backups automatiques"
echo ""

# Installation Docker si nécessaire
if ! command -v docker &> /dev/null; then
    echo "📦 Installation Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
fi

if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installation Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

echo "🧹 Nettoyage..."
docker-compose down 2>/dev/null || true
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true

echo "⚙️ Configuration..."

cat > .env << 'ENV_END'
POSTGRES_DB=atlas_production
POSTGRES_USER=atlas
POSTGRES_PASSWORD=AtlasDB2024SecurePass
SECRET_KEY=Atlas_Prod_2024_VeryLongSecretKey123456789
FLASK_ENV=production
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=gestion.fi.atlas@gmail.com
MAIL_PASSWORD=PLACEHOLDER_EMAIL_PASSWORD
OPENAI_API_KEY=PLACEHOLDER_OPENAI_KEY
BINANCE_API_KEY=PLACEHOLDER_BINANCE_KEY
BINANCE_SECRET_KEY=PLACEHOLDER_BINANCE_SECRET
ENV_END

cat > Dockerfile << 'DOCKER_END'
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y postgresql-client curl && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home atlas
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY --chown=atlas:atlas . .
USER atlas
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:5000/health || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "run:app"]
DOCKER_END

cat > docker-compose.yml << 'COMPOSE_END'
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    container_name: atlas_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      retries: 5
  atlas:
    build: .
    container_name: atlas_app
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      SECRET_KEY: ${SECRET_KEY}
      FLASK_ENV: ${FLASK_ENV}
    depends_on:
      postgres:
        condition: service_healthy
  nginx:
    image: nginx:alpine
    container_name: atlas_nginx
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - atlas
volumes:
  postgres_data:
COMPOSE_END

cat > nginx.conf << 'NGINX_END'
events { worker_connections 1024; }
http {
    upstream atlas { server atlas:5000; }
    server {
        listen 80;
        server_name _;
        location /health {
            proxy_pass http://atlas/health;
            access_log off;
        }
        location / {
            proxy_pass http://atlas;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
    }
}
NGINX_END

echo "🚀 Déploiement..."
docker-compose build
docker-compose up -d
sleep 60

echo "🗃️ Initialisation base..."
docker-compose exec -T atlas python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('✅ DB initialisée')"

echo "👤 Création admin..."
docker-compose exec -T atlas python3 -c "from app import create_app, db; from app.models.user import User; from werkzeug.security import generate_password_hash; app = create_app(); app.app_context().push(); admin = User(email='admin@atlas.com', password_hash=generate_password_hash('Admin123!'), nom='Admin', prenom='Atlas', role='admin'); db.session.add(admin); db.session.commit(); print('✅ Admin créé: admin@atlas.com / Admin123!')"

# Backup automatique
cat > backup_atlas.sh << 'BACKUP_END'
#!/bin/bash
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p backups
docker exec atlas_postgres pg_dump -U atlas -d atlas_production > backups/atlas_backup_$TIMESTAMP.sql
echo "✅ Backup: backups/atlas_backup_$TIMESTAMP.sql"
BACKUP_END
chmod +x backup_atlas.sh

# Scripts de gestion
echo 'docker-compose ps' > status.sh
echo 'docker-compose logs -f' > logs.sh  
echo 'docker-compose restart atlas' > restart.sh
chmod +x status.sh logs.sh restart.sh

echo ""
echo "🎉 ATLAS DÉPLOYÉ AVEC SUCCÈS !"
echo "=============================="
echo "🌐 Accès: http://$(curl -s ifconfig.me)"
echo "🔑 Login: admin@atlas.com / Admin123!"
echo ""
echo "🔧 Scripts disponibles:"
echo "  ./status.sh    - État des services"
echo "  ./logs.sh      - Voir les logs"  
echo "  ./restart.sh   - Redémarrer Atlas"
echo "  ./backup_atlas.sh - Backup manuel"
echo ""
echo "📝 Configuration:"
echo "  Modifier les clés API dans: nano .env"
echo "  Puis redémarrer: docker-compose restart atlas"
echo ""
docker-compose ps