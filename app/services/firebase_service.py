"""
Firebase service integration for Visioneer
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
from google.cloud import firestore as gcp_firestore
from flask import current_app
import json

class FirebaseService:
    """Firebase service wrapper"""
    
    def __init__(self):
        self.db = None
        self.bucket = None
        self.auth_client = None
    
    def initialize(self, app):
        """Initialize Firebase services"""
        try:
            # Initialize Firebase Admin SDK
            if not firebase_admin._apps:
                # Try to use service account key file first
                service_account_path = os.path.join(app.root_path, '..', 'firebase-service-account.json')
                
                if os.path.exists(service_account_path):
                    cred = credentials.Certificate(service_account_path)
                    firebase_admin.initialize_app(cred, {
                        'storageBucket': app.config['FIREBASE_STORAGE_BUCKET']
                    })
                else:
                    # Use default credentials (for production with proper IAM)
                    firebase_admin.initialize_app(options={
                        'storageBucket': app.config['FIREBASE_STORAGE_BUCKET']
                    })
            
            # Initialize services
            self.db = firestore.client()
            self.bucket = storage.bucket()
            self.auth_client = auth
            
            current_app.logger.info("Firebase services initialized successfully")
            
        except Exception as e:
            # Log error but don't raise in development mode
            if app.config.get('DEBUG', False):
                print(f"Warning: Firebase initialization failed: {str(e)}")
                print("App will run in development mode without Firebase")
                # Initialize with None values for development
                self.db = None
                self.bucket = None
                self.auth_client = None
            else:
                raise
    
    def get_db(self):
        """Get Firestore database instance"""
        return self.db
    
    def get_storage(self):
        """Get Cloud Storage bucket"""
        return self.bucket
    
    def get_auth(self):
        """Get Firebase Auth client"""
        return self.auth_client
    
    def create_user(self, user_data):
        """Create a new user in Firestore"""
        try:
            user_ref = self.db.collection('users').document(user_data['uid'])
            user_ref.set(user_data)
            return user_ref
        except Exception as e:
            current_app.logger.error(f"Error creating user: {str(e)}")
            raise
    
    def get_user(self, user_id):
        """Get user data from Firestore"""
        try:
            user_doc = self.db.collection('users').document(user_id).get()
            if user_doc.exists:
                return user_doc.to_dict()
            return None
        except Exception as e:
            current_app.logger.error(f"Error getting user: {str(e)}")
            raise
    
    def update_user(self, user_id, update_data):
        """Update user data in Firestore"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update(update_data)
            return user_ref
        except Exception as e:
            current_app.logger.error(f"Error updating user: {str(e)}")
            raise
    
    def save_moodboard(self, moodboard_data):
        """Save moodboard to Firestore"""
        try:
            moodboard_ref = self.db.collection('moodboards').document()
            moodboard_data['id'] = moodboard_ref.id
            moodboard_ref.set(moodboard_data)
            return moodboard_ref
        except Exception as e:
            current_app.logger.error(f"Error saving moodboard: {str(e)}")
            raise
    
    def get_user_moodboards(self, user_id, limit=20):
        """Get user's moodboards"""
        try:
            moodboards = self.db.collection('moodboards')\
                .where('user_id', '==', user_id)\
                .order_by('created_at', direction=firestore.Query.DESCENDING)\
                .limit(limit)\
                .stream()
            
            return [doc.to_dict() for doc in moodboards]
        except Exception as e:
            current_app.logger.error(f"Error getting user moodboards: {str(e)}")
            raise

# Global Firebase service instance
firebase_service = FirebaseService()

def initialize_firebase(app):
    """Initialize Firebase with Flask app"""
    firebase_service.initialize(app)
    return firebase_service
