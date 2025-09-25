"""
Security middleware for Visioneer application
"""

import time
import logging
from flask import request, jsonify, current_app
from app.utils.security import (
    sanitize_input, secure_headers, log_security_event,
    detect_suspicious_activity, check_origin_allowed
)

logger = logging.getLogger(__name__)

def security_middleware(app):
    """Apply security middleware to Flask app"""
    
    @app.before_request
    def security_checks():
        """Perform security checks before each request"""
        
        # Check for suspicious activity
        if request.method in ['POST', 'PUT', 'PATCH']:
            if detect_suspicious_activity(request.get_json() or {}):
                return jsonify({
                    'error': 'Suspicious Activity Detected',
                    'message': 'Request blocked due to suspicious content'
                }), 400
        
        # Sanitize input data
        if request.is_json:
            try:
                data = request.get_json()
                if data:
                    sanitized_data = sanitize_input(data)
                    # Note: In a real implementation, you would replace the request data
                    # This is a simplified version for demonstration
            except Exception as e:
                logger.warning(f"Failed to sanitize input: {str(e)}")
        
        # Log security events
        if request.endpoint in ['auth.api_login', 'auth.api_register']:
            log_security_event(
                'authentication_attempt',
                f'Authentication attempt from {request.remote_addr}',
                ip_address=request.remote_addr
            )
    
    @app.after_request
    def security_headers(response):
        """Add security headers to response"""
        return secure_headers(response)
    
    @app.before_request
    def cors_checks():
        """Check CORS origin"""
        origin = request.headers.get('Origin')
        if origin and not check_origin_allowed(origin):
            return jsonify({
                'error': 'CORS Error',
                'message': 'Origin not allowed'
            }), 403
    
    @app.before_request
    def content_length_check():
        """Check content length to prevent DoS"""
        max_content_length = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
        
        if request.content_length and request.content_length > max_content_length:
            return jsonify({
                'error': 'Request Too Large',
                'message': f'Request size exceeds maximum allowed size of {max_content_length} bytes'
            }), 413
    
    @app.before_request
    def method_validation():
        """Validate HTTP methods for endpoints"""
        allowed_methods = {
            'GET': ['/', '/dashboard', '/projects', '/settings'],
            'POST': ['/auth/login', '/auth/register', '/api/generate-moodboard', '/api/projects'],
            'PUT': ['/api/moodboard', '/api/projects'],
            'DELETE': ['/api/moodboard', '/api/projects']
        }
        
        if request.endpoint:
            endpoint_methods = allowed_methods.get(request.method, [])
            if request.endpoint not in endpoint_methods and not request.endpoint.startswith('static'):
                return jsonify({
                    'error': 'Method Not Allowed',
                    'message': f'{request.method} not allowed for this endpoint'
                }), 405

def rate_limit_middleware(app):
    """Apply rate limiting middleware"""
    
    @app.before_request
    def rate_limit_check():
        """Check rate limits before processing request"""
        from app.utils.security import rate_limiter
        
        # Different rate limits for different endpoints
        rate_limits = {
            'auth.api_login': (5, 300),  # 5 requests per 5 minutes
            'auth.api_register': (3, 300),  # 3 requests per 5 minutes
            'api.generate_moodboard': (10, 3600),  # 10 requests per hour
            'api.create_project': (20, 3600),  # 20 requests per hour
        }
        
        if request.endpoint in rate_limits:
            limit, window = rate_limits[request.endpoint]
            key = request.remote_addr
            
            if not rate_limiter.is_allowed(key, limit, window):
                logger.warning(f"Rate limit exceeded for {key} on {request.endpoint}")
                return jsonify({
                    'error': 'Rate Limit Exceeded',
                    'message': f'Too many requests. Limit: {limit} per {window} seconds'
                }), 429

def logging_middleware(app):
    """Apply logging middleware"""
    
    @app.before_request
    def log_request():
        """Log incoming requests"""
        logger.info(f"Request: {request.method} {request.url} from {request.remote_addr}")
    
    @app.after_request
    def log_response(response):
        """Log outgoing responses"""
        logger.info(f"Response: {response.status_code} for {request.method} {request.url}")
        return response

def error_handling_middleware(app):
    """Apply error handling middleware"""
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle bad requests"""
        log_security_event('bad_request', str(error), ip_address=request.remote_addr)
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request could not be understood by the server'
        }), 400
    
    @app.errorhandler(413)
    def handle_request_entity_too_large(error):
        """Handle request entity too large"""
        log_security_event('large_request', str(error), ip_address=request.remote_addr)
        return jsonify({
            'error': 'Request Entity Too Large',
            'message': 'The request size exceeds the maximum allowed size'
        }), 413
    
    @app.errorhandler(429)
    def handle_rate_limit_exceeded(error):
        """Handle rate limit exceeded"""
        log_security_event('rate_limit_exceeded', str(error), ip_address=request.remote_addr)
        return jsonify({
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429
