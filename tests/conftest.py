"""
Test configuration for Visioneer
"""

import pytest
import os
import tempfile
from app import create_app
from app.services.firebase_service import firebase_service
from app.services.ai_service import ai_service

@pytest.fixture
def app():
    """Create application for testing"""
    # Create temporary directory for test database
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'GEMINI_API_KEY': 'test-gemini-key',
        'FIREBASE_PROJECT_ID': 'test-project',
        'FIREBASE_STORAGE_BUCKET': 'test-bucket',
        'FIREBASE_AUTH_DOMAIN': 'test-domain',
    })
    
    with app.app_context():
        yield app
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers():
    """Mock authentication headers for testing"""
    return {
        'Authorization': 'Bearer test-token',
        'Content-Type': 'application/json'
    }

@pytest.fixture
def sample_story():
    """Sample story for testing"""
    return """
    A cyberpunk thriller set in Neo-Tokyo 2087. Neon-lit streets, 
    rain-soaked pavement, towering holographic advertisements. 
    The protagonist is a tech-savvy detective investigating 
    corporate espionage in the digital underground. The city 
    never sleeps, and neither does the conspiracy that threatens 
    to tear apart the fragile peace between humans and AI.
    """

@pytest.fixture
def sample_moodboard_data():
    """Sample moodboard data for testing"""
    return {
        'user_id': 'test-user-123',
        'title': 'Cyberpunk Neo-Tokyo',
        'story': 'A cyberpunk thriller...',
        'style': 'cinematic',
        'image_count': 6,
        'aspect_ratio': '16:9',
        'status': 'prompts_generated',
        'analysis': {
            'setting': ['Neo-Tokyo', 'cyberpunk city'],
            'time_period': '2087',
            'mood': ['dark', 'futuristic', 'mysterious'],
            'colors': ['neon', 'dark', 'blue', 'purple'],
            'lighting': 'neon lighting',
            'characters': ['tech detective'],
            'visual_elements': ['holograms', 'rain', 'neon signs'],
            'genre': 'cyberpunk thriller'
        },
        'image_prompts': [
            'Wide shot of Neo-Tokyo skyline with neon lights',
            'Close-up of rain-soaked street with neon reflections',
            'Detective in dark alley with holographic advertisements',
            'Cyberpunk cityscape with towering buildings',
            'Neon-lit interior of digital underground',
            'Futuristic detective silhouette against city lights'
        ]
    }
