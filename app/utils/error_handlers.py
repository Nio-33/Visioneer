"""
Error handling utilities for Visioneer application
"""

import logging
import traceback
from flask import jsonify, request, current_app
from werkzeug.exceptions import HTTPException
from app.config import Config

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom API error class"""
    
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        return rv

def register_error_handlers(app):
    """Register error handlers with Flask app"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle custom API errors"""
        logger.error(f"API Error: {error.message}")
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle 400 Bad Request errors"""
        logger.warning(f"Bad Request: {request.url}")
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request could not be understood by the server'
        }), 400
    
    @app.errorhandler(401)
    def handle_unauthorized(error):
        """Handle 401 Unauthorized errors"""
        logger.warning(f"Unauthorized access attempt: {request.url}")
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication is required'
        }), 401
    
    @app.errorhandler(403)
    def handle_forbidden(error):
        """Handle 403 Forbidden errors"""
        logger.warning(f"Forbidden access attempt: {request.url}")
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 Not Found errors"""
        logger.warning(f"Not Found: {request.url}")
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(422)
    def handle_unprocessable_entity(error):
        """Handle 422 Unprocessable Entity errors"""
        logger.warning(f"Unprocessable Entity: {request.url}")
        return jsonify({
            'error': 'Unprocessable Entity',
            'message': 'The request was well-formed but contains semantic errors'
        }), 422
    
    @app.errorhandler(429)
    def handle_rate_limit_exceeded(error):
        """Handle 429 Rate Limit Exceeded errors"""
        logger.warning(f"Rate limit exceeded: {request.url}")
        return jsonify({
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429
    
    @app.errorhandler(500)
    def handle_internal_server_error(error):
        """Handle 500 Internal Server Error"""
        logger.error(f"Internal Server Error: {str(error)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        if Config.DEBUG:
            return jsonify({
                'error': 'Internal Server Error',
                'message': str(error),
                'traceback': traceback.format_exc()
            }), 500
        else:
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred'
            }), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle unexpected errors"""
        logger.error(f"Unexpected error: {str(error)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        if Config.DEBUG:
            return jsonify({
                'error': 'Unexpected Error',
                'message': str(error),
                'traceback': traceback.format_exc()
            }), 500
        else:
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred'
            }), 500

def log_api_request(request, response=None, error=None):
    """Log API request details"""
    log_data = {
        'method': request.method,
        'url': request.url,
        'remote_addr': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'content_type': request.content_type
    }
    
    if response:
        log_data.update({
            'status_code': response.status_code,
            'response_size': len(response.get_data()) if hasattr(response, 'get_data') else 0
        })
    
    if error:
        log_data.update({
            'error': str(error),
            'error_type': type(error).__name__
        })
        logger.error(f"API Request Error: {log_data}")
    else:
        logger.info(f"API Request: {log_data}")

def handle_validation_error(errors):
    """Handle validation errors"""
    return jsonify({
        'error': 'Validation Error',
        'message': 'The request data is invalid',
        'details': errors
    }), 400

def handle_authentication_error():
    """Handle authentication errors"""
    return jsonify({
        'error': 'Authentication Error',
        'message': 'Invalid or missing authentication credentials'
    }), 401

def handle_authorization_error():
    """Handle authorization errors"""
    return jsonify({
        'error': 'Authorization Error',
        'message': 'You do not have permission to perform this action'
    }), 403

def handle_not_found_error(resource_type="Resource"):
    """Handle not found errors"""
    return jsonify({
        'error': 'Not Found',
        'message': f'{resource_type} not found'
    }), 404

def handle_rate_limit_error():
    """Handle rate limit errors"""
    return jsonify({
        'error': 'Rate Limit Exceeded',
        'message': 'Too many requests. Please try again later.'
    }), 429

def handle_external_service_error(service_name, error_message):
    """Handle external service errors"""
    logger.error(f"External service error ({service_name}): {error_message}")
    return jsonify({
        'error': 'Service Unavailable',
        'message': f'External service ({service_name}) is currently unavailable'
    }), 503
