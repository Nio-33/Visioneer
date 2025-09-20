"""
Authentication blueprint for Visioneer
"""

from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from app.auth import routes
