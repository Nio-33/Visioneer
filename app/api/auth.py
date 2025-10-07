"""
Authentication API endpoints
"""

from flask import request, session, jsonify
from app.api import bp
from app.auth.firebase_auth import auth_manager, require_auth
from app.utils.validators import InputValidator
import logging

logger = logging.getLogger(__name__)

@bp.route('/login', methods=['POST'])
def api_login():
    """API endpoint for user login"""
    try:
        data = request.get_json()

        if not data or 'id_token' not in data:
            return jsonify({'error': 'ID token is required'}), 400

        # Verify Firebase ID token and login user
        if auth_manager.login_user(data['id_token']):
            user = auth_manager.get_current_user()
            return jsonify({
                'success': True,
                'status': 'success',
                'message': 'Login successful',
                'user': user
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'success': False, 'error': 'Login failed'}), 500

@bp.route('/register', methods=['POST'])
def api_register():
    """API endpoint for user registration"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'Registration data is required'}), 400

        # Validate email
        if 'email' not in data or not InputValidator.validate_email(data['email']):
            return jsonify({'success': False, 'error': 'Valid email is required'}), 400

        # Validate password
        if 'password' not in data:
            return jsonify({'success': False, 'error': 'Password is required'}), 400

        password_validation = InputValidator.validate_password(data['password'])
        if not password_validation['valid']:
            return jsonify({
                'success': False,
                'error': 'Password validation failed',
                'details': password_validation['errors']
            }), 400

        # Registration is handled by Firebase on the client side
        # This endpoint mainly validates the data
        return jsonify({
            'success': True,
            'status': 'success',
            'message': 'Registration successful. Please verify your email.'
        })

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'success': False, 'error': 'Registration failed'}), 500

@bp.route('/logout', methods=['POST'])
@require_auth
def api_logout():
    """API endpoint for user logout"""
    try:
        auth_manager.logout_user()
        return jsonify({
            'success': True,
            'status': 'success',
            'message': 'Logout successful'
        })
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'success': False, 'error': 'Logout failed'}), 500

@bp.route('/user', methods=['GET'])
@require_auth
def get_user():
    """Get current user information"""
    try:
        user = auth_manager.get_current_user()
        if user:
            return jsonify({
                'success': True,
                'status': 'success',
                'user': user
            })
        else:
            return jsonify({'success': False, 'error': 'User not found'}), 404
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get user'}), 500

@bp.route('/forgot-password', methods=['POST'])
def api_forgot_password():
    """API endpoint for password reset"""
    try:
        data = request.get_json()

        if not data or 'email' not in data:
            return jsonify({'success': False, 'error': 'Email is required'}), 400

        if not InputValidator.validate_email(data['email']):
            return jsonify({'success': False, 'error': 'Valid email is required'}), 400

        # Password reset is handled by Firebase on the client side
        # This endpoint mainly validates the email
        return jsonify({
            'success': True,
            'status': 'success',
            'message': 'Password reset email sent'
        })

    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to send reset email'}), 500
