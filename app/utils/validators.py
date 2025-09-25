"""
Validation utilities for Visioneer application
"""

import re
from typing import Dict, List, Optional, Any
from app.config import Config

class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_story_input(story: str) -> Dict[str, Any]:
        """Validate story input for moodboard generation"""
        errors = []
        
        if not story or not story.strip():
            errors.append("Story description is required")
        elif len(story.strip()) < 50:
            errors.append("Story description must be at least 50 characters long")
        elif len(story) > 2000:
            errors.append("Story description must be less than 2000 characters")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_style(style: str) -> bool:
        """Validate visual style selection"""
        valid_styles = [
            'cinematic', 'artistic', 'realistic', 'dark_moody', 
            'vintage', 'modern', 'noir', 'fantasy', 'sci_fi'
        ]
        return style.lower() in valid_styles
    
    @staticmethod
    def validate_image_count(count: int) -> bool:
        """Validate image count for moodboard"""
        return 4 <= count <= 12
    
    @staticmethod
    def validate_aspect_ratio(ratio: str) -> bool:
        """Validate aspect ratio selection"""
        valid_ratios = ['16:9', '2.35:1', '4:3', '1:1', '9:16']
        return ratio in valid_ratios

class ConfigValidator:
    """Configuration validation utilities"""
    
    @staticmethod
    def validate_environment() -> List[str]:
        """Validate environment configuration"""
        errors = Config.validate_config()
        
        # Additional validation
        if Config.FLASK_ENV == 'production':
            if Config.SECRET_KEY == 'dev-secret-key-change-in-production':
                errors.append("SECRET_KEY must be changed in production")
            
            if Config.JWT_SECRET_KEY == 'jwt-secret-key-change-in-production':
                errors.append("JWT_SECRET_KEY must be changed in production")
        
        return errors
    
    @staticmethod
    def validate_firebase_config() -> List[str]:
        """Validate Firebase configuration"""
        errors = []
        
        if not Config.FIREBASE_PROJECT_ID:
            errors.append("FIREBASE_PROJECT_ID is required")
        
        if not Config.FIREBASE_STORAGE_BUCKET:
            errors.append("FIREBASE_STORAGE_BUCKET is required")
        
        if not Config.FIREBASE_AUTH_DOMAIN:
            errors.append("FIREBASE_AUTH_DOMAIN is required")
        
        return errors

class APIValidator:
    """API request validation utilities"""
    
    @staticmethod
    def validate_moodboard_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate moodboard generation request"""
        errors = []
        
        # Required fields
        required_fields = ['story', 'style', 'image_count', 'aspect_ratio']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return {'valid': False, 'errors': errors}
        
        # Validate individual fields
        story_validation = InputValidator.validate_story_input(data['story'])
        if not story_validation['valid']:
            errors.extend(story_validation['errors'])
        
        if not InputValidator.validate_style(data['style']):
            errors.append("Invalid style selection")
        
        if not InputValidator.validate_image_count(data['image_count']):
            errors.append("Image count must be between 4 and 12")
        
        if not InputValidator.validate_aspect_ratio(data['aspect_ratio']):
            errors.append("Invalid aspect ratio selection")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_project_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate project creation request"""
        errors = []
        
        if 'title' not in data or not data['title'].strip():
            errors.append("Project title is required")
        elif len(data['title']) > 100:
            errors.append("Project title must be less than 100 characters")
        
        if 'description' in data and len(data['description']) > 500:
            errors.append("Project description must be less than 500 characters")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
