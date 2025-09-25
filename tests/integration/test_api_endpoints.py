"""
Integration tests for API endpoints
"""

import pytest
import json
from unittest.mock import patch, Mock

class TestMoodboardAPI:
    """Test cases for moodboard API endpoints"""
    
    def test_generate_moodboard_success(self, client, authenticated_session, 
                                       mock_ai_service, mock_image_service, 
                                       mock_firebase_service):
        """Test successful moodboard generation"""
        data = {
            'story': 'A cyberpunk thriller set in Neo-Tokyo 2087',
            'style': 'cinematic',
            'image_count': 6,
            'aspect_ratio': '16:9'
        }
        
        response = client.post('/api/generate-moodboard', 
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'success'
        assert 'moodboard_id' in response_data
        assert 'images' in response_data
    
    def test_generate_moodboard_validation_error(self, client, authenticated_session):
        """Test moodboard generation with validation error"""
        data = {
            'story': 'Short',  # Too short
            'style': 'invalid_style',
            'image_count': 2,  # Too few
            'aspect_ratio': 'invalid_ratio'
        }
        
        response = client.post('/api/generate-moodboard',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'Validation failed' in response_data['error']
    
    def test_generate_moodboard_unauthorized(self, client):
        """Test moodboard generation without authentication"""
        data = {
            'story': 'A cyberpunk thriller set in Neo-Tokyo 2087',
            'style': 'cinematic',
            'image_count': 6,
            'aspect_ratio': '16:9'
        }
        
        response = client.post('/api/generate-moodboard',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 401
    
    def test_get_moodboard_success(self, client, authenticated_session, mock_firebase_service):
        """Test successful moodboard retrieval"""
        response = client.get('/api/moodboard/test-moodboard-id')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'success'
        assert 'moodboard' in response_data
    
    def test_get_moodboard_not_found(self, client, authenticated_session, mock_firebase_service):
        """Test moodboard retrieval when not found"""
        mock_firebase_service.get_moodboard.return_value = None
        
        response = client.get('/api/moodboard/non-existent-id')
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'Moodboard not found' in response_data['error']
    
    def test_get_user_moodboards_success(self, client, authenticated_session, mock_firebase_service):
        """Test successful user moodboards retrieval"""
        response = client.get('/api/moodboards')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'success'
        assert 'moodboards' in response_data
    
    def test_update_moodboard_success(self, client, authenticated_session, mock_firebase_service):
        """Test successful moodboard update"""
        data = {'title': 'Updated Moodboard'}
        
        response = client.put('/api/moodboard/test-moodboard-id',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'success'
    
    def test_delete_moodboard_success(self, client, authenticated_session, mock_firebase_service):
        """Test successful moodboard deletion"""
        response = client.delete('/api/moodboard/test-moodboard-id')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'success'

class TestProjectsAPI:
    """Test cases for projects API endpoints"""
    
    def test_create_project_success(self, client, authenticated_session, mock_firebase_service):
        """Test successful project creation"""
        data = {
            'title': 'Test Project',
            'description': 'A test project for moodboard creation'
        }
        
        response = client.post('/api/projects',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'success'
        assert 'project_id' in response_data
    
    def test_create_project_validation_error(self, client, authenticated_session):
        """Test project creation with validation error"""
        data = {
            'title': '',  # Empty title
            'description': 'A' * 600  # Too long description
        }
        
        response = client.post('/api/projects',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'Validation failed' in response_data['error']
    
    def test_get_projects_success(self, client, authenticated_session, mock_firebase_service):
        """Test successful projects retrieval"""
        response = client.get('/api/projects')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'success'
        assert 'projects' in response_data
    
    def test_get_project_success(self, client, authenticated_session, mock_firebase_service):
        """Test successful project retrieval"""
        response = client.get('/api/projects/test-project-id')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'success'
        assert 'project' in response_data
    
    def test_update_project_success(self, client, authenticated_session, mock_firebase_service):
        """Test successful project update"""
        data = {'title': 'Updated Project Title'}
        
        response = client.put('/api/projects/test-project-id',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'success'
    
    def test_delete_project_success(self, client, authenticated_session, mock_firebase_service):
        """Test successful project deletion"""
        response = client.delete('/api/projects/test-project-id')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'success'

class TestAuthenticationAPI:
    """Test cases for authentication API endpoints"""
    
    def test_login_success(self, client, mock_firebase_auth):
        """Test successful user login"""
        data = {'id_token': 'valid-firebase-token'}
        
        response = client.post('/auth/api/login',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'success'
        assert 'user' in response_data
    
    def test_login_invalid_token(self, client, mock_firebase_auth):
        """Test login with invalid token"""
        mock_firebase_auth.verify_id_token.return_value = None
        
        data = {'id_token': 'invalid-token'}
        
        response = client.post('/auth/api/login',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_register_success(self, client):
        """Test successful user registration"""
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        }
        
        response = client.post('/auth/api/register',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'success'
    
    def test_register_validation_error(self, client):
        """Test registration with validation error"""
        data = {
            'email': 'invalid-email',
            'password': 'weak'
        }
        
        response = client.post('/auth/api/register',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
    
    def test_logout_success(self, client, authenticated_session):
        """Test successful user logout"""
        response = client.post('/auth/api/logout')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'success'
    
    def test_get_user_success(self, client, authenticated_session):
        """Test successful user information retrieval"""
        response = client.get('/auth/api/user')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'success'
        assert 'user' in response_data
    
    def test_get_user_unauthorized(self, client):
        """Test user information retrieval without authentication"""
        response = client.get('/auth/api/user')
        
        assert response.status_code == 401
