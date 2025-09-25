"""
API endpoints for conversational image editing using Gemini 2.5 Flash Image
"""

from flask import Blueprint, request, jsonify, current_app
from app.services.ai_service import AIService
from PIL import Image
import base64
import io
import logging

bp = Blueprint('conversational_editing', __name__, url_prefix='/api/conversational-editing')
logger = logging.getLogger(__name__)

# Store active chat sessions (in production, use Redis or database)
active_sessions = {}

@bp.route('/start-session', methods=['POST'])
def start_editing_session():
    """Start a new conversational editing session"""
    try:
        ai_service = AIService()
        session_result = ai_service.create_conversational_edit_session()
        
        if session_result['success']:
            session_id = session_result['session_id']
            active_sessions[session_id] = {
                'chat_session': session_result['chat_session'],
                'created_at': current_app.logger.info(f"Session {session_id} created")
            }
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'message': 'Conversational editing session started'
            })
        else:
            return jsonify({
                'success': False,
                'error': session_result.get('error', 'Failed to create session')
            }), 500
            
    except Exception as e:
        logger.error(f"Error starting editing session: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@bp.route('/send-message', methods=['POST'])
def send_edit_message():
    """Send a message to the conversational editing session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        message = data.get('message', '')
        image_data = data.get('image')  # Base64 encoded image
        
        if not session_id or session_id not in active_sessions:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired session'
            }), 400
        
        ai_service = AIService()
        chat_session = active_sessions[session_id]['chat_session']
        
        # Process image if provided
        image = None
        if image_data:
            try:
                # Decode base64 image
                image_bytes = base64.b64decode(image_data.split(',')[1])
                image = Image.open(io.BytesIO(image_bytes))
            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': 'Invalid image data'
                }), 400
        
        # Send message to chat session
        result = ai_service.send_conversational_edit(chat_session, message, image)
        
        if result['success']:
            # Convert generated images to base64 for response
            generated_images_b64 = []
            for img in result['generated_images']:
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                img_b64 = base64.b64encode(buffer.getvalue()).decode()
                generated_images_b64.append(f"data:image/png;base64,{img_b64}")
            
            return jsonify({
                'success': True,
                'response_text': result['response_text'],
                'generated_images': generated_images_b64,
                'model_used': result['model_used']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to process message')
            }), 500
            
    except Exception as e:
        logger.error(f"Error sending edit message: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@bp.route('/end-session/<session_id>', methods=['DELETE'])
def end_editing_session(session_id):
    """End a conversational editing session"""
    try:
        if session_id in active_sessions:
            del active_sessions[session_id]
            return jsonify({
                'success': True,
                'message': 'Session ended successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@bp.route('/restore-image', methods=['POST'])
def restore_image():
    """Restore and colorize an old or damaged image"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        context = data.get('context', '')
        
        if not image_data:
            return jsonify({
                'success': False,
                'error': 'No image provided'
            }), 400
        
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data.split(',')[1])
            image = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Invalid image data'
            }), 400
        
        ai_service = AIService()
        result = ai_service.restore_and_colorize_image(image, context)
        
        if result['success']:
            # Convert restored images to base64 for response
            restored_images_b64 = []
            for img in result['restored_images']:
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                img_b64 = base64.b64encode(buffer.getvalue()).decode()
                restored_images_b64.append(f"data:image/png;base64,{img_b64}")
            
            return jsonify({
                'success': True,
                'restored_images': restored_images_b64,
                'model_used': result['model_used'],
                'restoration_context': result['restoration_context']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to restore image')
            }), 500
            
    except Exception as e:
        logger.error(f"Error restoring image: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@bp.route('/edit-image', methods=['POST'])
def edit_image():
    """Edit an existing image with specific instructions"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        edit_prompt = data.get('edit_prompt', '')
        
        if not image_data or not edit_prompt:
            return jsonify({
                'success': False,
                'error': 'Image and edit prompt are required'
            }), 400
        
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data.split(',')[1])
            image = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Invalid image data'
            }), 400
        
        ai_service = AIService()
        result = ai_service.edit_image_with_nano_banana(image, edit_prompt)
        
        if result['success']:
            # Convert edited images to base64 for response
            edited_images_b64 = []
            for img in result['edited_images']:
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                img_b64 = base64.b64encode(buffer.getvalue()).decode()
                edited_images_b64.append(f"data:image/png;base64,{img_b64}")
            
            return jsonify({
                'success': True,
                'edited_images': edited_images_b64,
                'model_used': result['model_used'],
                'edit_prompt': result['edit_prompt']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to edit image')
            }), 500
            
    except Exception as e:
        logger.error(f"Error editing image: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
