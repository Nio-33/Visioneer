"""
Authentication routes for Visioneer
"""

from flask import render_template, request, redirect, url_for, flash, session, current_app
from app.auth import auth_bp
from app.services.firebase_service import firebase_service
from functools import wraps
import uuid

def login_required(f):
    """Decorator to require user authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            # Development mode - simple mock authentication
            if current_app.config.get('DEBUG', False) and not firebase_service.auth_client:
                # Mock authentication for development
                if email and password:
                    session['user'] = {
                        'uid': str(uuid.uuid4()),
                        'email': email,
                        'display_name': email.split('@')[0],
                        'id_token': 'mock-token'
                    }
                    flash('Successfully logged in! (Development mode)', 'success')
                    return redirect(url_for('main.dashboard'))
                else:
                    flash('Please enter both email and password.', 'error')
                    return render_template('auth/login.html')
            else:
                # Production Firebase authentication
                import firebase_admin.auth as auth
                user = auth.sign_in_with_email_and_password(email, password)
                
                # Store user info in session
                session['user'] = {
                    'uid': user['localId'],
                    'email': user['email'],
                    'display_name': user.get('displayName', ''),
                    'id_token': user['idToken']
                }
                
                # Get or create user in Firestore
                user_data = firebase_service.get_user(user['localId'])
                if not user_data:
                    # Create new user
                    firebase_service.create_user({
                        'uid': user['localId'],
                        'email': user['email'],
                        'display_name': user.get('displayName', ''),
                        'created_at': firestore.SERVER_TIMESTAMP,
                        'subscription_tier': 'free'
                    })
                
                flash('Successfully logged in!', 'success')
                return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        display_name = request.form.get('display_name')
        
        try:
            # Create user with Firebase Auth
            user = auth.create_user_with_email_and_password(email, password)
            
            # Update display name
            auth.update_profile(user['idToken'], display_name=display_name)
            
            # Store user info in session
            session['user'] = {
                'uid': user['localId'],
                'email': user['email'],
                'display_name': display_name,
                'id_token': user['idToken']
            }
            
            # Create user in Firestore
            firebase_service.create_user({
                'uid': user['localId'],
                'email': user['email'],
                'display_name': display_name,
                'created_at': firestore.SERVER_TIMESTAMP,
                'subscription_tier': 'free'
            })
            
            flash('Account created successfully!', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            current_app.logger.error(f"Registration error: {str(e)}")
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/google-auth')
def google_auth():
    """Initiate Google OAuth flow"""
    # This would typically redirect to Google OAuth
    # For now, we'll implement a simple version
    flash('Google authentication not yet implemented.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Password reset request"""
    if request.method == 'POST':
        email = request.form.get('email')
        
        try:
            auth.send_password_reset_email(email)
            flash('Password reset email sent!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            current_app.logger.error(f"Password reset error: {str(e)}")
            flash('Error sending password reset email.', 'error')
    
    return render_template('auth/forgot_password.html')
