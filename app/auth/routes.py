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
