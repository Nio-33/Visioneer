"""
Configuration management for Visioneer application
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID')
    FIREBASE_STORAGE_BUCKET = os.environ.get('FIREBASE_STORAGE_BUCKET')
    FIREBASE_AUTH_DOMAIN = os.environ.get('FIREBASE_AUTH_DOMAIN')
    FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY')
    FIREBASE_APP_ID = os.environ.get('FIREBASE_APP_ID')
    
    # AI Services
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Database
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Security
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5000,http://127.0.0.1:5000').split(',')
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "100 per hour"
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    @staticmethod
    def validate_config() -> list:
        """Validate required configuration variables"""
        errors = []
        
        required_vars = [
            'FIREBASE_PROJECT_ID',
            'FIREBASE_STORAGE_BUCKET', 
            'FIREBASE_AUTH_DOMAIN',
            'FIREBASE_API_KEY',
            'FIREBASE_APP_ID',
            'GEMINI_API_KEY'
        ]
        
        for var in required_vars:
            if not getattr(Config, var):
                errors.append(f"Missing required environment variable: {var}")
        
        return errors

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with production values
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    # Only validate in production environment
    if os.environ.get('FLASK_ENV') == 'production':
        if not SECRET_KEY or SECRET_KEY == 'your_secret_key_here_change_in_production':
            raise ValueError("SECRET_KEY must be set in production")
        
        if not JWT_SECRET_KEY or JWT_SECRET_KEY == 'jwt-secret-key-change-in-production':
            raise ValueError("JWT_SECRET_KEY must be set in production")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
