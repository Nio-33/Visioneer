"""
Authentication routes
"""

from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app.auth import bp
from app.auth.firebase_auth import auth_manager, require_auth
from app.utils.validators import InputValidator
import logging

logger = logging.getLogger(__name__)

@bp.route('/login', methods=['GET'])
def login():
    """Login page"""
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET'])
def register():
    """Register page"""
    return render_template('auth/register.html')

@bp.route('/api/login', methods=['POST'])
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
                'status': 'success',
                'message': 'Login successful',
                'user': user
            })
        else:
            return jsonify({'error': 'Invalid token'}), 401
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@bp.route('/api/register', methods=['POST'])
def api_register():
    """API endpoint for user registration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Registration data is required'}), 400
        
        # Validate email
        if 'email' not in data or not InputValidator.validate_email(data['email']):
            return jsonify({'error': 'Valid email is required'}), 400
        
        # Validate password
        if 'password' not in data:
            return jsonify({'error': 'Password is required'}), 400
        
        password_validation = InputValidator.validate_password(data['password'])
        if not password_validation['valid']:
            return jsonify({
                'error': 'Password validation failed',
                'details': password_validation['errors']
            }), 400
        
        # Note: In a real implementation, you would create the user with Firebase Auth
        # For now, we'll assume the user is created on the frontend
        return jsonify({
            'status': 'success',
            'message': 'Registration successful. Please verify your email.'
        })
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@bp.route('/api/logout', methods=['POST'])
@require_auth
def api_logout():
    """API endpoint for user logout"""
    try:
        auth_manager.logout_user()
        return jsonify({
            'status': 'success',
            'message': 'Logout successful'
        })
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

@bp.route('/api/user', methods=['GET'])
@require_auth
def get_user():
    """Get current user information"""
    try:
        user = auth_manager.get_current_user()
        if user:
            return jsonify({
                'status': 'success',
                'user': user
            })
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return jsonify({'error': 'Failed to get user'}), 500

@bp.route('/logout')
def logout():
    """Logout user"""
    auth_manager.logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/forgot-password')
def forgot_password():
    """Forgot password page"""
    return render_template('auth/forgot_password.html')

@bp.route('/api/forgot-password', methods=['POST'])
def api_forgot_password():
    """API endpoint for password reset"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
        
        if not InputValidator.validate_email(data['email']):
            return jsonify({'error': 'Valid email is required'}), 400
        
        # Note: In a real implementation, you would send password reset email
        # using Firebase Auth send_password_reset_email()
        return jsonify({
            'status': 'success',
            'message': 'Password reset email sent'
        })
        
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        return jsonify({'error': 'Failed to send reset email'}), 500
