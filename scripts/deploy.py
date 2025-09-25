#!/usr/bin/env python3
"""
Production deployment script for Visioneer
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command, check=True):
    """Run shell command"""
    logger.info(f"Running: {command}")
    result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
    if result.stdout:
        logger.info(result.stdout)
    if result.stderr:
        logger.error(result.stderr)
    return result

def check_environment():
    """Check deployment environment"""
    logger.info("Checking deployment environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 9):
        raise RuntimeError(f"Python 3.9+ required, got {python_version.major}.{python_version.minor}")
    
    # Check required tools
    required_tools = ['git', 'firebase', 'gunicorn']
    for tool in required_tools:
        try:
            run_command(f"which {tool}")
        except subprocess.CalledProcessError:
            raise RuntimeError(f"Required tool not found: {tool}")
    
    logger.info("Environment check passed")

def install_dependencies():
    """Install Python dependencies"""
    logger.info("Installing Python dependencies...")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists('venv'):
        run_command("python -m venv venv")
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
    else:  # Unix/Linux/macOS
        activate_cmd = "source venv/bin/activate"
    
    run_command(f"{activate_cmd} && pip install --upgrade pip")
    run_command(f"{activate_cmd} && pip install -r requirements.txt")
    
    logger.info("Dependencies installed successfully")

def run_tests():
    """Run test suite"""
    logger.info("Running test suite...")
    
    try:
        run_command("python -m pytest tests/ -v --cov=app --cov-report=html")
        logger.info("All tests passed")
    except subprocess.CalledProcessError:
        logger.error("Tests failed")
        sys.exit(1)

def validate_configuration():
    """Validate production configuration"""
    logger.info("Validating configuration...")
    
    # Check environment variables
    required_vars = [
        'SECRET_KEY',
        'FIREBASE_PROJECT_ID',
        'FIREBASE_STORAGE_BUCKET',
        'FIREBASE_AUTH_DOMAIN',
        'GEMINI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise RuntimeError(f"Missing required environment variables: {missing_vars}")
    
    logger.info("Configuration validation passed")

def build_application():
    """Build application for production"""
    logger.info("Building application...")
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Create uploads directory
    os.makedirs('uploads', exist_ok=True)
    
    # Set proper permissions
    if os.name != 'nt':  # Not Windows
        run_command("chmod +x run.py")
        run_command("chmod 755 logs uploads")
    
    logger.info("Application built successfully")

def deploy_firebase():
    """Deploy Firebase services"""
    logger.info("Deploying Firebase services...")
    
    # Deploy Firestore rules
    run_command("firebase deploy --only firestore:rules")
    
    # Deploy Storage rules
    run_command("firebase deploy --only storage:rules")
    
    # Deploy Cloud Functions
    run_command("firebase deploy --only functions")
    
    logger.info("Firebase services deployed successfully")

def start_application():
    """Start production application"""
    logger.info("Starting production application...")
    
    # Set production environment
    os.environ['FLASK_ENV'] = 'production'
    
    # Start with Gunicorn
    gunicorn_cmd = [
        "gunicorn",
        "--bind", "0.0.0.0:8000",
        "--workers", "4",
        "--worker-class", "sync",
        "--timeout", "120",
        "--keep-alive", "2",
        "--max-requests", "1000",
        "--max-requests-jitter", "100",
        "--preload",
        "--access-logfile", "logs/access.log",
        "--error-logfile", "logs/error.log",
        "--log-level", "info",
        "run:app"
    ]
    
    logger.info(f"Starting with: {' '.join(gunicorn_cmd)}")
    subprocess.run(gunicorn_cmd)

def create_systemd_service():
    """Create systemd service file"""
    service_content = f"""[Unit]
Description=Visioneer Web Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory={project_root}
Environment=FLASK_ENV=production
ExecStart={project_root}/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 4 run:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    with open('/etc/systemd/system/visioneer.service', 'w') as f:
        f.write(service_content)
    
    run_command("systemctl daemon-reload")
    run_command("systemctl enable visioneer")
    
    logger.info("Systemd service created")

def setup_nginx():
    """Setup Nginx configuration"""
    nginx_config = """
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /path/to/visioneer/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
"""
    
    with open('/etc/nginx/sites-available/visioneer', 'w') as f:
        f.write(nginx_config)
    
    run_command("ln -sf /etc/nginx/sites-available/visioneer /etc/nginx/sites-enabled/")
    run_command("nginx -t")
    run_command("systemctl reload nginx")
    
    logger.info("Nginx configuration created")

def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description='Deploy Visioneer application')
    parser.add_argument('--skip-tests', action='store_true', help='Skip running tests')
    parser.add_argument('--skip-firebase', action='store_true', help='Skip Firebase deployment')
    parser.add_argument('--setup-systemd', action='store_true', help='Setup systemd service')
    parser.add_argument('--setup-nginx', action='store_true', help='Setup Nginx configuration')
    
    args = parser.parse_args()
    
    try:
        logger.info("Starting Visioneer deployment...")
        
        # Check environment
        check_environment()
        
        # Install dependencies
        install_dependencies()
        
        # Run tests (unless skipped)
        if not args.skip_tests:
            run_tests()
        
        # Validate configuration
        validate_configuration()
        
        # Build application
        build_application()
        
        # Deploy Firebase (unless skipped)
        if not args.skip_firebase:
            deploy_firebase()
        
        # Setup systemd service (if requested)
        if args.setup_systemd:
            create_systemd_service()
        
        # Setup Nginx (if requested)
        if args.setup_nginx:
            setup_nginx()
        
        logger.info("Deployment completed successfully!")
        
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
