"""
API blueprint
"""

from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import moodboard, projects, health, auth
