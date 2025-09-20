"""
Moodboard API endpoints
"""

from flask import request, jsonify, session, current_app
from app.api import api_bp
from app.auth.routes import login_required
from app.services.firebase_service import firebase_service
from app.services.ai_service import ai_service
from datetime import datetime

@api_bp.route('/moodboard/generate', methods=['POST'])
@login_required
def api_generate_moodboard():
    """API endpoint for moodboard generation"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['story', 'style', 'image_count', 'aspect_ratio']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Extract parameters
        story_text = data['story']
        style = data['style']
        image_count = int(data['image_count'])
        aspect_ratio = data['aspect_ratio']
        
        # Validate story length
        if len(story_text.strip()) < 50:
            return jsonify({
                'success': False,
                'error': 'Story description must be at least 50 characters long.'
            }), 400
        
        # Validate image count
        if image_count < 4 or image_count > 12:
            return jsonify({
                'success': False,
                'error': 'Image count must be between 4 and 12.'
            }), 400
        
        # Initialize AI service if needed
        if not ai_service.initialized:
            ai_service.initialize(current_app.config['GEMINI_API_KEY'])
        
        # Analyze story
        analysis_result = ai_service.analyze_story(story_text, style)
        
        if not analysis_result['success']:
            return jsonify({
                'success': False,
                'error': 'Failed to analyze story: ' + analysis_result.get('error', 'Unknown error')
            }), 500
        
        # Generate image prompts
        image_prompts = ai_service.generate_image_prompts(
            analysis_result['analysis'], 
            image_count
        )
        
        if not image_prompts:
            return jsonify({
                'success': False,
                'error': 'Failed to generate image prompts.'
            }), 500
        
        # Create moodboard data
        user_id = session['user']['uid']
        moodboard_data = {
            'user_id': user_id,
            'title': story_text[:100] + ('...' if len(story_text) > 100 else ''),
            'story': story_text,
            'style': style,
            'image_count': image_count,
            'aspect_ratio': aspect_ratio,
            'analysis': analysis_result['analysis'],
            'image_prompts': image_prompts,
            'status': 'prompts_generated',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Save to Firestore
        moodboard_ref = firebase_service.save_moodboard(moodboard_data)
        
        return jsonify({
            'success': True,
            'moodboard_id': moodboard_ref.id,
            'analysis': analysis_result['analysis'],
            'image_prompts': image_prompts,
            'status': 'prompts_generated'
        })
        
    except Exception as e:
        current_app.logger.error(f"API moodboard generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@api_bp.route('/moodboard/<moodboard_id>', methods=['GET'])
@login_required
def api_get_moodboard(moodboard_id):
    """Get moodboard by ID"""
    try:
        moodboard_doc = firebase_service.db.collection('moodboards').document(moodboard_id).get()
        
        if not moodboard_doc.exists:
            return jsonify({
                'success': False,
                'error': 'Moodboard not found'
            }), 404
        
        moodboard_data = moodboard_doc.to_dict()
        
        # Check ownership
        if moodboard_data['user_id'] != session['user']['uid']:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Convert datetime objects to strings for JSON serialization
        if 'created_at' in moodboard_data:
            moodboard_data['created_at'] = moodboard_data['created_at'].isoformat()
        if 'updated_at' in moodboard_data:
            moodboard_data['updated_at'] = moodboard_data['updated_at'].isoformat()
        
        return jsonify({
            'success': True,
            'moodboard': moodboard_data
        })
        
    except Exception as e:
        current_app.logger.error(f"API get moodboard error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@api_bp.route('/moodboard/<moodboard_id>', methods=['PUT'])
@login_required
def api_update_moodboard(moodboard_id):
    """Update moodboard"""
    try:
        data = request.get_json()
        
        # Get existing moodboard
        moodboard_ref = firebase_service.db.collection('moodboards').document(moodboard_id)
        moodboard_doc = moodboard_ref.get()
        
        if not moodboard_doc.exists:
            return jsonify({
                'success': False,
                'error': 'Moodboard not found'
            }), 404
        
        moodboard_data = moodboard_doc.to_dict()
        
        # Check ownership
        if moodboard_data['user_id'] != session['user']['uid']:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Update allowed fields
        allowed_fields = ['title', 'status', 'images']
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        update_data['updated_at'] = datetime.utcnow()
        
        # Update in Firestore
        moodboard_ref.update(update_data)
        
        return jsonify({
            'success': True,
            'message': 'Moodboard updated successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"API update moodboard error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@api_bp.route('/moodboard/<moodboard_id>', methods=['DELETE'])
@login_required
def api_delete_moodboard(moodboard_id):
    """Delete moodboard"""
    try:
        # Get moodboard
        moodboard_doc = firebase_service.db.collection('moodboards').document(moodboard_id).get()
        
        if not moodboard_doc.exists:
            return jsonify({
                'success': False,
                'error': 'Moodboard not found'
            }), 404
        
        moodboard_data = moodboard_doc.to_dict()
        
        # Check ownership
        if moodboard_data['user_id'] != session['user']['uid']:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Delete from Firestore
        firebase_service.db.collection('moodboards').document(moodboard_id).delete()
        
        return jsonify({
            'success': True,
            'message': 'Moodboard deleted successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"API delete moodboard error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
