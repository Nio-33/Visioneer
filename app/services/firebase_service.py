"""
Firebase Service for data management
"""

import os
from typing import Dict, List, Optional
from google.cloud import firestore
from google.cloud import storage
from google.cloud.exceptions import NotFound

class FirebaseService:
    """Service for Firebase operations"""
    
    def __init__(self):
        """Initialize Firebase services"""
        self.db = firestore.Client()
        self.storage_client = storage.Client()
        self.bucket_name = os.environ.get('FIREBASE_STORAGE_BUCKET')
    
    # User operations
    def create_user(self, user_data: Dict) -> str:
        """Create a new user document"""
        try:
            doc_ref = self.db.collection('users').add(user_data)
            return doc_ref[1].id
        except Exception as e:
            raise Exception(f"Error creating user: {str(e)}")
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc = doc_ref.get()
            if doc.exists:
                user_data = doc.to_dict()
                user_data['id'] = doc.id
                return user_data
            return None
        except Exception as e:
            raise Exception(f"Error getting user: {str(e)}")
    
    def update_user(self, user_id: str, update_data: Dict) -> bool:
        """Update user document"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc_ref.update(update_data)
            return True
        except Exception as e:
            raise Exception(f"Error updating user: {str(e)}")
    
    # Project operations
    def create_project(self, project_data: Dict) -> str:
        """Create a new project"""
        try:
            doc_ref = self.db.collection('projects').add(project_data)
            return doc_ref[1].id
        except Exception as e:
            raise Exception(f"Error creating project: {str(e)}")
    
    def get_user_projects(self, user_id: str) -> List[Dict]:
        """Get all projects for a user"""
        try:
            projects_ref = self.db.collection('projects').where('user_id', '==', user_id)
            projects = projects_ref.stream()
            
            project_list = []
            for project in projects:
                project_data = project.to_dict()
                project_data['id'] = project.id
                project_list.append(project_data)
            
            return project_list
        except Exception as e:
            raise Exception(f"Error getting projects: {str(e)}")
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project by ID"""
        try:
            doc_ref = self.db.collection('projects').document(project_id)
            doc = doc_ref.get()
            if doc.exists:
                project_data = doc.to_dict()
                project_data['id'] = doc.id
                return project_data
            return None
        except Exception as e:
            raise Exception(f"Error getting project: {str(e)}")
    
    def update_project(self, project_id: str, update_data: Dict) -> bool:
        """Update project"""
        try:
            doc_ref = self.db.collection('projects').document(project_id)
            doc_ref.update(update_data)
            return True
        except Exception as e:
            raise Exception(f"Error updating project: {str(e)}")
    
    def delete_project(self, project_id: str) -> bool:
        """Delete project"""
        try:
            doc_ref = self.db.collection('projects').document(project_id)
            doc_ref.delete()
            return True
        except Exception as e:
            raise Exception(f"Error deleting project: {str(e)}")
    
    # Moodboard operations
    def create_moodboard(self, moodboard_data: Dict) -> str:
        """Create a new moodboard"""
        try:
            doc_ref = self.db.collection('moodboards').add(moodboard_data)
            return doc_ref[1].id
        except Exception as e:
            raise Exception(f"Error creating moodboard: {str(e)}")
    
    def get_user_moodboards(self, user_id: str) -> List[Dict]:
        """Get all moodboards for a user"""
        try:
            moodboards_ref = self.db.collection('moodboards').where('user_id', '==', user_id)
            moodboards = moodboards_ref.stream()
            
            moodboard_list = []
            for moodboard in moodboards:
                moodboard_data = moodboard.to_dict()
                moodboard_data['id'] = moodboard.id
                moodboard_list.append(moodboard_data)
            
            return moodboard_list
        except Exception as e:
            raise Exception(f"Error getting moodboards: {str(e)}")
    
    def get_moodboard(self, moodboard_id: str) -> Optional[Dict]:
        """Get moodboard by ID"""
        try:
            doc_ref = self.db.collection('moodboards').document(moodboard_id)
            doc = doc_ref.get()
            if doc.exists:
                moodboard_data = doc.to_dict()
                moodboard_data['id'] = doc.id
                return moodboard_data
            return None
        except Exception as e:
            raise Exception(f"Error getting moodboard: {str(e)}")
    
    def update_moodboard(self, moodboard_id: str, update_data: Dict) -> bool:
        """Update moodboard"""
        try:
            doc_ref = self.db.collection('moodboards').document(moodboard_id)
            doc_ref.update(update_data)
            return True
        except Exception as e:
            raise Exception(f"Error updating moodboard: {str(e)}")
    
    def delete_moodboard(self, moodboard_id: str) -> bool:
        """Delete moodboard"""
        try:
            doc_ref = self.db.collection('moodboards').document(moodboard_id)
            doc_ref.delete()
            return True
        except Exception as e:
            raise Exception(f"Error deleting moodboard: {str(e)}")
    
    # Storage operations
    def upload_file(self, file_path: str, destination_path: str) -> str:
        """Upload file to Firebase Storage"""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(destination_path)
            blob.upload_from_filename(file_path)
            
            # Make the file publicly accessible
            blob.make_public()
            
            return blob.public_url
        except Exception as e:
            raise Exception(f"Error uploading file: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from Firebase Storage"""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(file_path)
            blob.delete()
            return True
        except NotFound:
            return True  # File doesn't exist, consider it deleted
        except Exception as e:
            raise Exception(f"Error deleting file: {str(e)}")
    
    def get_file_url(self, file_path: str) -> str:
        """Get public URL for a file"""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(file_path)
            return blob.public_url
        except Exception as e:
            raise Exception(f"Error getting file URL: {str(e)}")
