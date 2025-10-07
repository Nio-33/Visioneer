"""
Firebase Authentication integration for Visioneer
"""

import os
import json
import requests
from typing import Optional, Dict, Any
from flask import session, request, current_app
from firebase_admin import auth, credentials, initialize_app
from firebase_admin.exceptions import FirebaseError
import logging

logger = logging.getLogger(__name__)

class FirebaseAuthService:
    """Firebase Authentication service"""
    
    def __init__(self):
        """Initialize Firebase Auth service"""
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            try:
                # Try to get existing app
                from firebase_admin import get_app
                get_app()
            except ValueError:
                # No app exists, initialize one
                if os.path.exists('firebase-service-account.json'):
                    cred = credentials.Certificate('firebase-service-account.json')
                    initialize_app(cred)
                else:
                    # Use default credentials (for production with proper IAM roles)
                    initialize_app()
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            # For development, we can continue without Firebase
            logger.warning("Continuing without Firebase initialization")
    
    def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """Verify Firebase ID token"""
        try:
            decoded_token = auth.verify_id_token(id_token)
            return {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email'),
                'name': decoded_token.get('name'),
                'picture': decoded_token.get('picture'),
                'email_verified': decoded_token.get('email_verified', False)
            }
        except FirebaseError as e:
            logger.error(f"Token verification failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {str(e)}")
            return None
    
    def get_user_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get user information by UID"""
        try:
            user = auth.get_user(uid)
            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'photo_url': user.photo_url,
                'email_verified': user.email_verified,
                'disabled': user.disabled,
                'created_at': user.user_metadata.creation_timestamp,
                'last_sign_in': user.user_metadata.last_sign_in_timestamp
            }
        except FirebaseError as e:
            logger.error(f"Failed to get user {uid}: {str(e)}")
            return None
    
    def create_custom_token(self, uid: str, additional_claims: Optional[Dict] = None) -> Optional[str]:
        """Create custom token for user"""
        try:
            return auth.create_custom_token(uid, additional_claims).decode('utf-8')
        except FirebaseError as e:
            logger.error(f"Failed to create custom token: {str(e)}")
            return None
    
    def set_custom_user_claims(self, uid: str, claims: Dict[str, Any]) -> bool:
        """Set custom claims for user"""
        try:
            auth.set_custom_user_claims(uid, claims)
            return True
        except FirebaseError as e:
            logger.error(f"Failed to set custom claims: {str(e)}")
            return False
    
    def delete_user(self, uid: str) -> bool:
        """Delete user account"""
        try:
            auth.delete_user(uid)
            return True
        except FirebaseError as e:
            logger.error(f"Failed to delete user: {str(e)}")
            return False

class AuthManager:
    """Authentication manager for Flask sessions"""
    
    def __init__(self):
        try:
            self.firebase_auth = FirebaseAuthService()
        except Exception as e:
            logger.warning(f"Firebase Auth not available: {str(e)}")
            self.firebase_auth = None
    
    def login_user(self, id_token: str) -> bool:
        """Login user with Firebase ID token"""
        if not self.firebase_auth:
            logger.error("Firebase authentication is not available")
            return False

        user_data = self.firebase_auth.verify_id_token(id_token)
        if user_data:
            session['user_id'] = user_data['uid']
            session['user_email'] = user_data['email']
            session['user_name'] = user_data['name']
            session['user_picture'] = user_data['picture']
            session['authenticated'] = True
            return True
        return False
    
    def logout_user(self):
        """Logout current user"""
        session.clear()
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        if not session.get('authenticated'):
            return None
        
        return {
            'uid': session.get('user_id'),
            'email': session.get('user_email'),
            'name': session.get('user_name'),
            'picture': session.get('user_picture')
        }
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return session.get('authenticated', False)
    
    def require_auth(self, f):
        """Decorator to require authentication"""
        from functools import wraps
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.is_authenticated():
                return {'error': 'Authentication required'}, 401
            return f(*args, **kwargs)
        return decorated_function

# Global auth manager instance
auth_manager = AuthManager()

def require_auth(f):
    """Decorator to require authentication"""
    return auth_manager.require_auth(f)

def get_current_user():
    """Get current authenticated user"""
    return auth_manager.get_current_user()

def is_authenticated():
    """Check if user is authenticated"""
    return auth_manager.is_authenticated()
