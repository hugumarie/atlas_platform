#!/bin/bash
set -e
echo "🚀 ATLAS - DÉPLOIEMENT SIMPLIFIÉ"
echo "==============================="

# Arrêter tout
docker-compose down 2>/dev/null || true
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true

# Configuration simple
cat > docker-compose.yml << 'COMPOSE'
version: '3.8'
services:
  postgres:
    image: postgres:15
    container_name: atlas_postgres
    environment:
      POSTGRES_DB: atlas
      POSTGRES_USER: atlas
      POSTGRES_PASSWORD: atlas123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U atlas"]
      interval: 10s
      retries: 5

  atlas:
    image: python:3.11-slim
    container_name: atlas_app
    working_dir: /app
    volumes:
      - .:/app
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://atlas:atlas123@postgres:5432/atlas
      FLASK_ENV: production
    command: >
      bash -c "
        apt-get update && 
        apt-get install -y postgresql-client curl &&
        pip install flask flask-sqlalchemy psycopg2-binary gunicorn werkzeug &&
        python -c 'from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print(\"DB initialisée\")' &&
        python -c 'from app import create_app, db; from app.models.user import User; from werkzeug.security import generate_password_hash; app = create_app(); app.app_context().push(); admin = User(email=\"admin@atlas.com\", password_hash=generate_password_hash(\"Admin123!\"), nom=\"Admin\", prenom=\"Atlas\", role=\"admin\"); db.session.add(admin); db.session.commit(); print(\"Admin créé\")' &&
        gunicorn --bind 0.0.0.0:5000 --workers 1 run:app
      "
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:
COMPOSE

echo "DATABASE_URL=postgresql://atlas:atlas123@postgres:5432/atlas" > .env

echo "🚀 Démarrage..."
docker-compose up -d

echo "⏳ Attente (45s)..."
sleep 45

echo ""
echo "🎉 ATLAS DÉPLOYÉ !"
echo "=================="
echo "🌐 URL: http://$(curl -s ifconfig.me):5000"
echo "🔑 Login: admin@atlas.com / Admin123!"
echo ""
echo "📊 État:"
docker-compose ps