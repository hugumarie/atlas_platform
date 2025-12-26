#!/bin/bash
clear
echo "🚀 ATLAS AUTO-DEPLOY"
echo "==================="

# Nettoyage
docker-compose down 2>/dev/null || true

# Configuration .env
cat > .env << 'ENVEOF'
DATABASE_PASSWORD=AtlasDB2024_SecurePass!
SECRET_KEY=Atlas_Prod_2024_9x8w7v6u5t4r3e2w1q0p9o8i7u6y5t4r3e2w1q
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=gestion.fi.atlas@gmail.com
MAIL_PASSWORD=placeholder
OPENAI_API_KEY=placeholder
BINANCE_API_KEY=
BINANCE_SECRET_KEY=
ENVEOF

# Docker Compose
cat > docker-compose.yml << 'DOCKEREOF'
version: '3.8'
services:
  postgres:
    image: postgres:15
    container_name: atlas_postgres
    environment:
      POSTGRES_DB: atlas_production
      POSTGRES_USER: atlas
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U atlas -d atlas_production"]
      interval: 30s
      timeout: 10s
      retries: 3

  atlas:
    build: .
    container_name: atlas_app
    environment:
      DATABASE_URL: postgresql://atlas:${DATABASE_PASSWORD}@postgres:5432/atlas_production
      SECRET_KEY: ${SECRET_KEY}
      FLASK_ENV: production
    depends_on:
      postgres:
        condition: service_healthy

  nginx:
    image: nginx:alpine
    container_name: atlas_nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
    depends_on:
      - atlas

volumes:
  postgres_data:
DOCKEREOF

# Configuration Nginx
mkdir -p nginx/conf.d
cat > nginx/conf.d/atlas.conf << 'NGINXEOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://atlas:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://atlas:5000/health;
        access_log off;
    }
}
NGINXEOF

echo "🔨 Building Atlas..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for startup (30s)..."
sleep 30

echo "🗃️ Initializing database..."
docker-compose exec -T atlas python3 -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Database initialized')
"

echo "👤 Creating admin user..."
docker-compose exec -T atlas python3 -c "
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    admin = User.query.filter_by(email='admin@atlas.com').first()
    if not admin:
        admin = User(
            email='admin@atlas.com',
            password_hash=generate_password_hash('admin123'),
            nom='Admin',
            prenom='Atlas',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin created: admin@atlas.com / admin123')
    else:
        print('✅ Admin already exists')
"

echo ""
echo "🎉 ATLAS DEPLOYED SUCCESSFULLY!"
echo "==============================="
echo ""
echo "🌐 Access: http://$(curl -s ifconfig.me)"
echo "🔑 Login: admin@atlas.com / admin123"
echo ""
echo "📊 Services status:"
docker-compose ps