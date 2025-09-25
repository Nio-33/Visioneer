"""
Configuration package for Visioneer application
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Firebase configuration
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
    FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET')
    FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN')
    FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')
    
    # Gemini AI configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Application settings
    MOODBOARDS_PER_PAGE = 12
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Security settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # Development-specific settings
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Production-specific settings
    FLASK_ENV = 'production'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Testing-specific settings
    WTF_CSRF_ENABLED = False
