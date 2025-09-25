"""
Projects API endpoints
"""

from flask import request, jsonify
from app.api import bp
from app.auth.firebase_auth import require_auth, get_current_user
from app.services.firebase_service import FirebaseService
from app.utils.validators import APIValidator
import logging

logger = logging.getLogger(__name__)

@bp.route('/projects', methods=['GET'])
@require_auth
def get_projects():
    """Get user projects"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        firebase_service = FirebaseService()
        projects = firebase_service.get_user_projects(user['uid'])
        
        return jsonify({
            'status': 'success',
            'projects': projects
        })
        
    except Exception as e:
        logger.error(f"Failed to get projects: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve projects',
            'details': str(e)
        }), 500

@bp.route('/projects', methods=['POST'])
@require_auth
def create_project():
    """Create new project"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Project data is required'}), 400
        
        # Validate project data
        validation = APIValidator.validate_project_request(data)
        if not validation['valid']:
            return jsonify({
                'error': 'Validation failed',
                'details': validation['errors']
            }), 400
        
        # Create project data
        project_data = {
            'user_id': user['uid'],
            'title': data['title'],
            'description': data.get('description', ''),
            'status': 'active',
            'created_at': FirebaseService().db.SERVER_TIMESTAMP,
            'updated_at': FirebaseService().db.SERVER_TIMESTAMP
        }
        
        firebase_service = FirebaseService()
        project_id = firebase_service.create_project(project_data)
        
        logger.info(f"Created project {project_id} for user {user['uid']}")
        
        return jsonify({
            'status': 'success',
            'project_id': project_id,
            'message': 'Project created successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to create project: {str(e)}")
        return jsonify({
            'error': 'Failed to create project',
            'details': str(e)
        }), 500

@bp.route('/projects/<project_id>', methods=['GET'])
@require_auth
def get_project(project_id):
    """Get project by ID"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        firebase_service = FirebaseService()
        project = firebase_service.get_project(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check if user owns this project
        if project['user_id'] != user['uid']:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'status': 'success',
            'project': project
        })
        
    except Exception as e:
        logger.error(f"Failed to get project {project_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve project',
            'details': str(e)
        }), 500

@bp.route('/projects/<project_id>', methods=['PUT'])
@require_auth
def update_project(project_id):
    """Update project"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Update data is required'}), 400
        
        firebase_service = FirebaseService()
        
        # Check if project exists and user owns it
        project = firebase_service.get_project(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        if project['user_id'] != user['uid']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Update project
        update_data = {
            **data,
            'updated_at': firebase_service.db.SERVER_TIMESTAMP
        }
        
        success = firebase_service.update_project(project_id, update_data)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Project updated successfully'
            })
        else:
            return jsonify({
                'error': 'Failed to update project'
            }), 500
        
    except Exception as e:
        logger.error(f"Failed to update project {project_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to update project',
            'details': str(e)
        }), 500

@bp.route('/projects/<project_id>', methods=['DELETE'])
@require_auth
def delete_project(project_id):
    """Delete project"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        firebase_service = FirebaseService()
        
        # Check if project exists and user owns it
        project = firebase_service.get_project(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        if project['user_id'] != user['uid']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Delete project
        success = firebase_service.delete_project(project_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Project deleted successfully'
            })
        else:
            return jsonify({
                'error': 'Failed to delete project'
            }), 500
        
    except Exception as e:
        logger.error(f"Failed to delete project {project_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to delete project',
            'details': str(e)
        }), 500
