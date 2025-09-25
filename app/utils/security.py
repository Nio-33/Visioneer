"""
Security utilities for Visioneer application
"""

import os
import hashlib
import secrets
import time
from functools import wraps
from flask import request, jsonify, current_app
from werkzeug.exceptions import TooManyRequests
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = {}
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    def is_allowed(self, key, limit, window):
        """Check if request is allowed based on rate limit"""
        current_time = time.time()
        
        # Cleanup old entries periodically
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries(current_time, window)
            self.last_cleanup = current_time
        
        # Get or create request history for this key
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the window
        cutoff_time = current_time - window
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > cutoff_time]
        
        # Check if limit is exceeded
        if len(self.requests[key]) >= limit:
            return False
        
        # Add current request
        self.requests[key].append(current_time)
        return True
    
    def _cleanup_old_entries(self, current_time, window):
        """Clean up old entries from memory"""
        cutoff_time = current_time - window
        keys_to_remove = []
        
        for key, requests in self.requests.items():
            self.requests[key] = [req_time for req_time in requests if req_time > cutoff_time]
            if not self.requests[key]:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.requests[key]

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(limit, window, per='ip'):
    """
    Rate limiting decorator
    
    Args:
        limit: Maximum number of requests
        window: Time window in seconds
        per: Rate limit per 'ip' or 'user'
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Determine the key for rate limiting
            if per == 'ip':
                key = request.remote_addr
            elif per == 'user':
                # Use user ID if authenticated, otherwise IP
                from app.auth.firebase_auth import get_current_user
                user = get_current_user()
                key = user['uid'] if user else request.remote_addr
            else:
                key = request.remote_addr
            
            # Check rate limit
            if not rate_limiter.is_allowed(key, limit, window):
                logger.warning(f"Rate limit exceeded for {key}")
                return jsonify({
                    'error': 'Rate Limit Exceeded',
                    'message': f'Too many requests. Limit: {limit} per {window} seconds'
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_https(f):
    """Require HTTPS in production"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_app.config.get('FLASK_ENV') == 'production':
            if not request.is_secure:
                return jsonify({
                    'error': 'HTTPS Required',
                    'message': 'This endpoint requires HTTPS'
                }), 400
        return f(*args, **kwargs)
    return decorated_function

def validate_csrf_token(f):
    """Validate CSRF token for state-changing operations"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            csrf_token = request.headers.get('X-CSRF-Token')
            if not csrf_token:
                return jsonify({
                    'error': 'CSRF Token Required',
                    'message': 'CSRF token is required for this operation'
                }), 400
            
            # In a real implementation, you would validate the CSRF token
            # For now, we'll just check if it exists
            if not csrf_token or len(csrf_token) < 32:
                return jsonify({
                    'error': 'Invalid CSRF Token',
                    'message': 'Invalid or missing CSRF token'
                }), 400
        
        return f(*args, **kwargs)
    return decorated_function

def sanitize_input(data):
    """Sanitize input data to prevent XSS and injection attacks"""
    if isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    elif isinstance(data, str):
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`', '$']
        for char in dangerous_chars:
            data = data.replace(char, '')
        return data.strip()
    else:
        return data

def validate_file_upload(file, allowed_extensions=None, max_size=None):
    """Validate file upload"""
    if not file:
        return False, "No file provided"
    
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    if max_size is None:
        max_size = 16 * 1024 * 1024  # 16MB
    
    # Check file extension
    if '.' not in file.filename:
        return False, "File must have an extension"
    
    extension = file.filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        return False, f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > max_size:
        return False, f"File too large. Maximum size: {max_size} bytes"
    
    return True, "Valid file"

def generate_secure_token(length=32):
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)

def hash_password(password, salt=None):
    """Hash password with salt"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Use PBKDF2 for password hashing
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # iterations
    )
    
    return password_hash.hex(), salt

def verify_password(password, password_hash, salt):
    """Verify password against hash"""
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == password_hash

def secure_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    return response

def log_security_event(event_type, details, user_id=None, ip_address=None):
    """Log security events"""
    security_logger = logging.getLogger('security')
    
    log_data = {
        'event_type': event_type,
        'details': details,
        'timestamp': time.time(),
        'user_id': user_id,
        'ip_address': ip_address or request.remote_addr,
        'user_agent': request.headers.get('User-Agent')
    }
    
    security_logger.warning(f"Security Event: {log_data}")

def detect_suspicious_activity(request_data, user_id=None):
    """Detect suspicious activity patterns"""
    suspicious_patterns = [
        'script', 'javascript', 'vbscript', 'onload', 'onerror',
        'eval', 'expression', 'url(', 'import', 'include'
    ]
    
    request_str = str(request_data).lower()
    
    for pattern in suspicious_patterns:
        if pattern in request_str:
            log_security_event(
                'suspicious_activity',
                f'Detected suspicious pattern: {pattern}',
                user_id
            )
            return True
    
    return False

def validate_api_key(api_key):
    """Validate API key format"""
    if not api_key:
        return False
    
    # API key should be at least 32 characters and contain only alphanumeric characters
    if len(api_key) < 32:
        return False
    
    if not api_key.replace('-', '').replace('_', '').isalnum():
        return False
    
    return True

def check_origin_allowed(origin):
    """Check if origin is allowed for CORS"""
    allowed_origins = current_app.config.get('CORS_ORIGINS', [])
    
    if not allowed_origins:
        return True  # Allow all if not configured
    
    return origin in allowed_origins
