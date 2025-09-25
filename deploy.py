#!/usr/bin/env python3
"""
Production deployment script for Visioneer
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking deployment requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found. Please create one with your configuration.")
        sys.exit(1)
    
    # Check required environment variables
    required_vars = [
        'GEMINI_API_KEY',
        'FIREBASE_PROJECT_ID',
        'FIREBASE_STORAGE_BUCKET',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    print("✅ All requirements met")

def install_dependencies():
    """Install production dependencies"""
    print("📦 Installing production dependencies...")
    
    # Upgrade pip
    run_command("pip install --upgrade pip", "Upgrading pip")
    
    # Install requirements
    run_command("pip install -r requirements.txt", "Installing Python dependencies")
    
    # Install additional production packages
    production_packages = [
        "gunicorn",
        "waitress",
        "flask-compress",
        "flask-caching",
        "redis"
    ]
    
    for package in production_packages:
        run_command(f"pip install {package}", f"Installing {package}")

def setup_production_config():
    """Setup production configuration"""
    print("⚙️ Setting up production configuration...")
    
    # Create production environment file
    prod_env_content = """# Production Environment Configuration
FLASK_ENV=production
DEBUG=False
TESTING=False

# Security
SECRET_KEY=your-production-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database
DATABASE_URL=your-database-url-here

# Redis
REDIS_URL=redis://localhost:6379

# Monitoring
SENTRY_DSN=your-sentry-dsn-here

# Email
MAIL_SERVER=your-mail-server
MAIL_USERNAME=your-mail-username
MAIL_PASSWORD=your-mail-password

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
"""
    
    with open('.env.production', 'w') as f:
        f.write(prod_env_content)
    
    print("✅ Production configuration created")

def create_systemd_service():
    """Create systemd service file"""
    print("🔧 Creating systemd service...")
    
    service_content = f"""[Unit]
Description=Visioneer AI Moodboard Creator
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory={os.getcwd()}
Environment=PATH={os.getcwd()}/venv/bin
Environment=FLASK_ENV=production
ExecStart={os.getcwd()}/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 run:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    with open('visioneer.service', 'w') as f:
        f.write(service_content)
    
    print("✅ Systemd service file created")

def create_nginx_config():
    """Create nginx configuration"""
    print("🌐 Creating nginx configuration...")
    
    nginx_config = """server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    
    # API endpoints
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Auth endpoints
    location /auth/ {
        limit_req zone=login burst=10 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        alias /path/to/your/static/files/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
"""
    
    with open('nginx.conf', 'w') as f:
        f.write(nginx_config)
    
    print("✅ Nginx configuration created")

def create_docker_config():
    """Create Docker configuration"""
    print("🐳 Creating Docker configuration...")
    
    dockerfile_content = """FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libffi-dev \\
    libssl-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 visioneer && chown -R visioneer:visioneer /app
USER visioneer

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "run:app"]
"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    # Create docker-compose.yml
    docker_compose_content = """version: '3.8'

services:
  visioneer:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - visioneer
    restart: unless-stopped

volumes:
  redis_data:
"""
    
    with open('docker-compose.yml', 'w') as f:
        f.write(docker_compose_content)
    
    print("✅ Docker configuration created")

def create_monitoring_config():
    """Create monitoring configuration"""
    print("📊 Creating monitoring configuration...")
    
    # Prometheus configuration
    prometheus_config = """global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'visioneer'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
"""
    
    with open('prometheus.yml', 'w') as f:
        f.write(prometheus_config)
    
    print("✅ Monitoring configuration created")

def main():
    """Main deployment function"""
    print("🚀 Starting Visioneer production deployment...")
    
    # Check requirements
    check_requirements()
    
    # Install dependencies
    install_dependencies()
    
    # Setup configuration
    setup_production_config()
    
    # Create service files
    create_systemd_service()
    create_nginx_config()
    create_docker_config()
    create_monitoring_config()
    
    print("\n🎉 Deployment preparation completed!")
    print("\n📋 Next steps:")
    print("1. Update the configuration files with your actual values")
    print("2. Set up SSL certificates for HTTPS")
    print("3. Configure your domain DNS")
    print("4. Start the services:")
    print("   - sudo systemctl enable visioneer.service")
    print("   - sudo systemctl start visioneer.service")
    print("   - sudo systemctl reload nginx")
    print("\n🐳 Or use Docker:")
    print("   - docker-compose up -d")
    print("\n📊 Monitor your application:")
    print("   - Check logs: sudo journalctl -u visioneer.service -f")
    print("   - Monitor metrics: http://localhost:8000/metrics")

if __name__ == "__main__":
    main()
