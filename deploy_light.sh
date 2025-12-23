#!/bin/bash
set -e
echo "🚀 ATLAS - VERSION ULTRA-LÉGÈRE"
echo "=============================="

# Arrêter le container problématique
docker stop atlas_app 2>/dev/null || true
docker rm atlas_app 2>/dev/null || true

# Créer un container plus léger
docker run -d --name atlas_app \
  --network atlas_platform_default \
  -p 5000:5000 \
  -v $(pwd):/app \
  -w /app \
  -e DATABASE_URL=postgresql://atlas:atlas123@atlas_postgres:5432/atlas \
  -e FLASK_ENV=production \
  python:3.11-alpine \
  sh -c "
    apk add --no-cache postgresql-client &&
    pip install --no-cache-dir flask flask-sqlalchemy psycopg2-binary gunicorn werkzeug &&
    python -c 'from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print(\"DB OK\")' &&
    python -c 'from app import create_app, db; from app.models.user import User; from werkzeug.security import generate_password_hash; app = create_app(); app.app_context().push(); admin = User(email=\"admin@atlas.com\", password_hash=generate_password_hash(\"Admin123!\"), nom=\"Admin\", prenom=\"Atlas\", role=\"admin\"); db.session.add(admin); db.session.commit(); print(\"Admin créé\")' &&
    gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 120 run:app
  "

echo "⏳ Attente démarrage (30s)..."
sleep 30

echo ""
echo "🎉 ATLAS LÉGER DÉPLOYÉ !"
echo "======================="
echo "🌐 URL: http://$(curl -s ifconfig.me):5000"
echo "🔑 Login: admin@atlas.com / Admin123!"
echo ""
echo "📊 État:"
docker ps | grep atlas