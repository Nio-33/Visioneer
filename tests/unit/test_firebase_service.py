"""
Unit tests for Firebase Service
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.firebase_service import FirebaseService

class TestFirebaseService:
    """Test cases for Firebase Service"""
    
    def test_init(self):
        """Test Firebase service initialization"""
        with patch('google.cloud.firestore.Client') as mock_firestore:
            with patch('google.cloud.storage.Client') as mock_storage:
                with patch.dict('os.environ', {'FIREBASE_STORAGE_BUCKET': 'test-bucket'}):
                    service = FirebaseService()
                    
                    mock_firestore.assert_called_once()
                    mock_storage.assert_called_once()
                    assert service.bucket_name == 'test-bucket'
    
    def test_create_user_success(self):
        """Test successful user creation"""
        with patch('google.cloud.firestore.Client') as mock_firestore:
            with patch('google.cloud.storage.Client'):
                mock_db = Mock()
                mock_firestore.return_value = mock_db
                mock_collection = Mock()
                mock_db.collection.return_value = mock_collection
                mock_add = Mock()
                mock_collection.add = mock_add
                mock_add.return_value = (None, Mock(id='test-user-id'))
                
                with patch.dict('os.environ', {'FIREBASE_STORAGE_BUCKET': 'test-bucket'}):
                    service = FirebaseService()
                    result = service.create_user({'name': 'Test User'})
                    
                    assert result == 'test-user-id'
                    mock_add.assert_called_once_with({'name': 'Test User'})
    
    def test_create_user_failure(self):
        """Test user creation failure"""
        with patch('google.cloud.firestore.Client') as mock_firestore:
            with patch('google.cloud.storage.Client'):
                mock_db = Mock()
                mock_firestore.return_value = mock_db
                mock_collection = Mock()
                mock_db.collection.return_value = mock_collection
                mock_collection.add.side_effect = Exception("Database error")
                
                with patch.dict('os.environ', {'FIREBASE_STORAGE_BUCKET': 'test-bucket'}):
                    service = FirebaseService()
                    
                    with pytest.raises(Exception, match="Error creating user"):
                        service.create_user({'name': 'Test User'})
    
    def test_get_user_success(self):
        """Test successful user retrieval"""
        with patch('google.cloud.firestore.Client') as mock_firestore:
            with patch('google.cloud.storage.Client'):
                mock_db = Mock()
                mock_firestore.return_value = mock_db
                mock_doc = Mock()
                mock_doc.exists = True
                mock_doc.to_dict.return_value = {'name': 'Test User'}
                mock_doc.id = 'test-user-id'
                mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
                
                with patch.dict('os.environ', {'FIREBASE_STORAGE_BUCKET': 'test-bucket'}):
                    service = FirebaseService()
                    result = service.get_user('test-user-id')
                    
                    assert result['name'] == 'Test User'
                    assert result['id'] == 'test-user-id'
    
    def test_get_user_not_found(self):
        """Test user not found"""
        with patch('google.cloud.firestore.Client') as mock_firestore:
            with patch('google.cloud.storage.Client'):
                mock_db = Mock()
                mock_firestore.return_value = mock_db
                mock_doc = Mock()
                mock_doc.exists = False
                mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
                
                with patch.dict('os.environ', {'FIREBASE_STORAGE_BUCKET': 'test-bucket'}):
                    service = FirebaseService()
                    result = service.get_user('non-existent-id')
                    
                    assert result is None
    
    def test_create_project_success(self):
        """Test successful project creation"""
        with patch('google.cloud.firestore.Client') as mock_firestore:
            with patch('google.cloud.storage.Client'):
                mock_db = Mock()
                mock_firestore.return_value = mock_db
                mock_collection = Mock()
                mock_db.collection.return_value = mock_collection
                mock_add = Mock()
                mock_collection.add = mock_add
                mock_add.return_value = (None, Mock(id='test-project-id'))
                
                with patch.dict('os.environ', {'FIREBASE_STORAGE_BUCKET': 'test-bucket'}):
                    service = FirebaseService()
                    result = service.create_project({'title': 'Test Project'})
                    
                    assert result == 'test-project-id'
    
    def test_get_user_projects(self):
        """Test getting user projects"""
        with patch('google.cloud.firestore.Client') as mock_firestore:
            with patch('google.cloud.storage.Client'):
                mock_db = Mock()
                mock_firestore.return_value = mock_db
                mock_collection = Mock()
                mock_db.collection.return_value = mock_collection
                mock_where = Mock()
                mock_collection.where.return_value = mock_where
                
                # Mock stream results
                mock_project1 = Mock()
                mock_project1.to_dict.return_value = {'title': 'Project 1'}
                mock_project1.id = 'project-1'
                
                mock_project2 = Mock()
                mock_project2.to_dict.return_value = {'title': 'Project 2'}
                mock_project2.id = 'project-2'
                
                mock_where.stream.return_value = [mock_project1, mock_project2]
                
                with patch.dict('os.environ', {'FIREBASE_STORAGE_BUCKET': 'test-bucket'}):
                    service = FirebaseService()
                    result = service.get_user_projects('test-user-id')
                    
                    assert len(result) == 2
                    assert result[0]['title'] == 'Project 1'
                    assert result[0]['id'] == 'project-1'
                    assert result[1]['title'] == 'Project 2'
                    assert result[1]['id'] == 'project-2'
    
    def test_upload_file_success(self):
        """Test successful file upload"""
        with patch('google.cloud.firestore.Client'):
            with patch('google.cloud.storage.Client') as mock_storage:
                mock_storage_client = Mock()
                mock_storage.return_value = mock_storage_client
                mock_bucket = Mock()
                mock_storage_client.bucket.return_value = mock_bucket
                mock_blob = Mock()
                mock_bucket.blob.return_value = mock_blob
                mock_blob.public_url = 'https://storage.googleapis.com/test-bucket/test-file.jpg'
                
                with patch.dict('os.environ', {'FIREBASE_STORAGE_BUCKET': 'test-bucket'}):
                    service = FirebaseService()
                    
                    # Create a temporary file for testing
                    import tempfile
                    with tempfile.NamedTemporaryFile() as temp_file:
                        temp_file.write(b'test content')
                        temp_file.flush()
                        
                        result = service.upload_file(temp_file.name, 'test-file.jpg')
                        
                        assert result == 'https://storage.googleapis.com/test-bucket/test-file.jpg'
                        mock_blob.upload_from_filename.assert_called_once_with(temp_file.name)
                        mock_blob.make_public.assert_called_once()
    
    def test_delete_file_success(self):
        """Test successful file deletion"""
        with patch('google.cloud.firestore.Client'):
            with patch('google.cloud.storage.Client') as mock_storage:
                mock_storage_client = Mock()
                mock_storage.return_value = mock_storage_client
                mock_bucket = Mock()
                mock_storage_client.bucket.return_value = mock_bucket
                mock_blob = Mock()
                mock_bucket.blob.return_value = mock_blob
                
                with patch.dict('os.environ', {'FIREBASE_STORAGE_BUCKET': 'test-bucket'}):
                    service = FirebaseService()
                    result = service.delete_file('test-file.jpg')
                    
                    assert result is True
                    mock_blob.delete.assert_called_once()
    
    def test_delete_file_not_found(self):
        """Test file deletion when file not found"""
        with patch('google.cloud.firestore.Client'):
            with patch('google.cloud.storage.Client') as mock_storage:
                from google.cloud.exceptions import NotFound
                
                mock_storage_client = Mock()
                mock_storage.return_value = mock_storage_client
                mock_bucket = Mock()
                mock_storage_client.bucket.return_value = mock_bucket
                mock_blob = Mock()
                mock_bucket.blob.return_value = mock_blob
                mock_blob.delete.side_effect = NotFound("File not found")
                
                with patch.dict('os.environ', {'FIREBASE_STORAGE_BUCKET': 'test-bucket'}):
                    service = FirebaseService()
                    result = service.delete_file('non-existent-file.jpg')
                    
                    assert result is True  # Should return True for NotFound exception
