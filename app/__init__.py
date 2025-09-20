"""
Visioneer Flask Application Factory
"""

import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

# Import configurations
from config import DevelopmentConfig, ProductionConfig, TestingConfig

def create_app(config_name=None):
    """Application factory pattern"""
    
    # Load environment variables
    load_dotenv()
    
    # Create Flask app
    app = Flask(__name__)
    
    # Determine configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    app.config.from_object(config_map.get(config_name, DevelopmentConfig))
    
    # Initialize CSRF protection
    csrf = CSRFProtect()
    csrf.init_app(app)
    
    # Initialize Firebase (optional in development)
    try:
        from app.services.firebase_service import initialize_firebase
        initialize_firebase(app)
    except Exception as e:
        if app.config.get('DEBUG', False):
            print(f"Firebase initialization skipped: {e}")
        else:
            raise
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

def register_blueprints(app):
    """Register application blueprints"""
    from app.auth import auth_bp
    from app.main import main_bp
    from app.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

def register_error_handlers(app):
    """Register error handlers"""
    from flask import render_template
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
