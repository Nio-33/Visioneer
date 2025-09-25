"""
Test configuration and fixtures for Visioneer
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from app import create_app
from app.config import TestingConfig

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'FIREBASE_PROJECT_ID': 'test-project',
        'FIREBASE_STORAGE_BUCKET': 'test-bucket',
        'FIREBASE_AUTH_DOMAIN': 'test-domain',
        'FIREBASE_API_KEY': 'test-api-key',
        'FIREBASE_APP_ID': 'test-app-id',
        'GEMINI_API_KEY': 'test-gemini-key',
        'OPENAI_API_KEY': 'test-openai-key'
    })
    
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def mock_firebase_auth():
    """Mock Firebase authentication"""
    with patch('app.auth.firebase_auth.auth') as mock_auth:
        mock_auth.verify_id_token.return_value = {
            'uid': 'test-user-id',
            'email': 'test@example.com',
            'name': 'Test User',
            'picture': 'https://example.com/avatar.jpg',
            'email_verified': True
        }
        yield mock_auth

@pytest.fixture
def mock_firebase_service():
    """Mock Firebase service"""
    with patch('app.services.firebase_service.FirebaseService') as mock_service:
        mock_instance = Mock()
        mock_instance.create_moodboard.return_value = 'test-moodboard-id'
        mock_instance.create_project.return_value = 'test-project-id'
        mock_instance.get_moodboard.return_value = {
            'id': 'test-moodboard-id',
            'user_id': 'test-user-id',
            'story': 'Test story',
            'style': 'cinematic',
            'images': []
        }
        mock_instance.get_project.return_value = {
            'id': 'test-project-id',
            'user_id': 'test-user-id',
            'title': 'Test Project',
            'description': 'Test description'
        }
        mock_instance.get_user_moodboards.return_value = []
        mock_instance.get_user_projects.return_value = []
        mock_service.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_ai_service():
    """Mock AI service"""
    with patch('app.services.ai_service.AIService') as mock_service:
        mock_instance = Mock()
        mock_instance.generate_moodboard_concept.return_value = {
            'status': 'success',
            'concept': 'Test moodboard concept'
        }
        mock_instance.generate_image_prompts.return_value = [
            'Test prompt 1',
            'Test prompt 2',
            'Test prompt 3'
        ]
        mock_service.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_image_service():
    """Mock image generation service"""
    with patch('app.services.image_generation_service.ImageGenerationService') as mock_service:
        mock_instance = Mock()
        mock_instance.generate_images.return_value = [
            {
                'url': 'https://example.com/image1.jpg',
                'prompt': 'Test prompt 1',
                'index': 0,
                'provider': 'openai'
            },
            {
                'url': 'https://example.com/image2.jpg',
                'prompt': 'Test prompt 2',
                'index': 1,
                'provider': 'openai'
            }
        ]
        mock_service.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def authenticated_session(client):
    """Create authenticated session"""
    with client.session_transaction() as sess:
        sess['authenticated'] = True
        sess['user_id'] = 'test-user-id'
        sess['user_email'] = 'test@example.com'
        sess['user_name'] = 'Test User'
        sess['user_picture'] = 'https://example.com/avatar.jpg'
    return sess
