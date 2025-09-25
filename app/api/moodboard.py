"""
Moodboard API endpoints
"""

from flask import request, jsonify, session
from app.api import bp
from app.auth.firebase_auth import require_auth, get_current_user
from app.services.ai_service import AIService
from app.services.image_generation_service import ImageGenerationService
from app.services.firebase_service import FirebaseService
from app.utils.validators import APIValidator
import logging

logger = logging.getLogger(__name__)

@bp.route('/generate-moodboard', methods=['POST'])
@require_auth
def generate_moodboard():
    """Generate a new moodboard"""
    try:
        data = request.get_json()
        
        # Validate request data
        validation = APIValidator.validate_moodboard_request(data)
        if not validation['valid']:
            return jsonify({
                'error': 'Validation failed',
                'details': validation['errors']
            }), 400
        
        # Get current user
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        # Initialize services
        ai_service = AIService()
        image_service = ImageGenerationService()
        firebase_service = FirebaseService()
        
        # Generate moodboard concept using AI
        logger.info(f"Generating moodboard concept for user {user['uid']}")
        concept_result = ai_service.generate_moodboard_concept(
            data['story'],
            data['style'],
            data['image_count'],
            data['aspect_ratio']
        )
        
        if concept_result['status'] != 'success':
            return jsonify({
                'error': 'Failed to generate concept',
                'details': concept_result.get('error', 'Unknown error')
            }), 500
        
        # Generate image prompts
        prompts = ai_service.generate_image_prompts(
            concept_result['concept'],
            data['image_count']
        )
        
        if not prompts:
            return jsonify({
                'error': 'Failed to generate image prompts'
            }), 500
        
        # Generate images
        logger.info(f"Generating {len(prompts)} images")
        images = image_service.generate_images(
            prompts,
            data['style'],
            provider='openai'  # Default to OpenAI, could be made configurable
        )
        
        if not images:
            return jsonify({
                'error': 'Failed to generate images'
            }), 500
        
        # Save moodboard to database
        moodboard_data = {
            'user_id': user['uid'],
            'story': data['story'],
            'style': data['style'],
            'image_count': data['image_count'],
            'aspect_ratio': data['aspect_ratio'],
            'concept': concept_result['concept'],
            'images': images,
            'status': 'completed',
            'created_at': firebase_service.db.SERVER_TIMESTAMP,
            'updated_at': firebase_service.db.SERVER_TIMESTAMP
        }
        
        moodboard_id = firebase_service.create_moodboard(moodboard_data)
        
        logger.info(f"Successfully created moodboard {moodboard_id}")
        
        return jsonify({
            'status': 'success',
            'moodboard_id': moodboard_id,
            'message': 'Moodboard generated successfully',
            'images': images,
            'concept': concept_result['concept']
        })
        
    except Exception as e:
        logger.error(f"Moodboard generation failed: {str(e)}")
        return jsonify({
            'error': 'Moodboard generation failed',
            'details': str(e)
        }), 500

@bp.route('/moodboard/<moodboard_id>', methods=['GET'])
@require_auth
def get_moodboard(moodboard_id):
    """Get moodboard by ID"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        firebase_service = FirebaseService()
        moodboard = firebase_service.get_moodboard(moodboard_id)
        
        if not moodboard:
            return jsonify({'error': 'Moodboard not found'}), 404
        
        # Check if user owns this moodboard
        if moodboard['user_id'] != user['uid']:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'status': 'success',
            'moodboard': moodboard
        })
        
    except Exception as e:
        logger.error(f"Failed to get moodboard {moodboard_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve moodboard',
            'details': str(e)
        }), 500

@bp.route('/moodboard/<moodboard_id>', methods=['PUT'])
@require_auth
def update_moodboard(moodboard_id):
    """Update moodboard"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Update data is required'}), 400
        
        firebase_service = FirebaseService()
        
        # Check if moodboard exists and user owns it
        moodboard = firebase_service.get_moodboard(moodboard_id)
        if not moodboard:
            return jsonify({'error': 'Moodboard not found'}), 404
        
        if moodboard['user_id'] != user['uid']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Update moodboard
        update_data = {
            **data,
            'updated_at': firebase_service.db.SERVER_TIMESTAMP
        }
        
        success = firebase_service.update_moodboard(moodboard_id, update_data)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Moodboard updated successfully'
            })
        else:
            return jsonify({
                'error': 'Failed to update moodboard'
            }), 500
        
    except Exception as e:
        logger.error(f"Failed to update moodboard {moodboard_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to update moodboard',
            'details': str(e)
        }), 500

@bp.route('/moodboard/<moodboard_id>', methods=['DELETE'])
@require_auth
def delete_moodboard(moodboard_id):
    """Delete moodboard"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        firebase_service = FirebaseService()
        
        # Check if moodboard exists and user owns it
        moodboard = firebase_service.get_moodboard(moodboard_id)
        if not moodboard:
            return jsonify({'error': 'Moodboard not found'}), 404
        
        if moodboard['user_id'] != user['uid']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Delete moodboard
        success = firebase_service.delete_moodboard(moodboard_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Moodboard deleted successfully'
            })
        else:
            return jsonify({
                'error': 'Failed to delete moodboard'
            }), 500
        
    except Exception as e:
        logger.error(f"Failed to delete moodboard {moodboard_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to delete moodboard',
            'details': str(e)
        }), 500

@bp.route('/moodboards', methods=['GET'])
@require_auth
def get_user_moodboards():
    """Get all moodboards for current user"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not authenticated'}), 401
        
        firebase_service = FirebaseService()
        moodboards = firebase_service.get_user_moodboards(user['uid'])
        
        return jsonify({
            'status': 'success',
            'moodboards': moodboards
        })
        
    except Exception as e:
        logger.error(f"Failed to get user moodboards: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve moodboards',
            'details': str(e)
        }), 500
