"""
Visioneer Web Application Factory
"""

import os
import logging
from flask import Flask
from dotenv import load_dotenv
from app.config import config
from app.utils.error_handlers import register_error_handlers

# Load environment variables
load_dotenv()

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Set configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Configure logging
    configure_logging(app)
    
    # Validate configuration
    validate_configuration(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from app.api.conversational_editing import bp as conversational_bp
    app.register_blueprint(conversational_bp)
    
    # Add request logging middleware
    @app.before_request
    def log_request_info():
        from flask import request
        if app.config.get('LOG_REQUESTS', True):
            logging.info(f"Request: {request.method} {request.url}")
    
    @app.after_request
    def log_response_info(response):
        if app.config.get('LOG_REQUESTS', True):
            logging.info(f"Response: {response.status_code}")
        return response
    
    return app

def configure_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        # Production logging configuration
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/visioneer.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Visioneer startup')

def validate_configuration(app):
    """Validate application configuration"""
    # Basic configuration validation
    required_config = [
        'SECRET_KEY',
        'FIREBASE_PROJECT_ID',
        'FIREBASE_STORAGE_BUCKET',
        'FIREBASE_AUTH_DOMAIN',
        'GEMINI_API_KEY'
    ]
    
    missing_config = []
    for config_key in required_config:
        if not app.config.get(config_key):
            missing_config.append(config_key)
    
    if missing_config:
        app.logger.warning(f"Missing configuration: {missing_config}")
        if app.config.get('FLASK_ENV') == 'production':
            raise ValueError(f"Missing required configuration: {missing_config}")
