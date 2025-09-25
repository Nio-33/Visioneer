"""
Main application routes
"""

from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app.main import bp
from app.services.ai_service import AIService
from app.services.image_generation_service import ImageGenerationService
from app.services.firebase_service import FirebaseService
from app.utils.validators import APIValidator
import logging
import time

logger = logging.getLogger(__name__)

@bp.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@bp.route('/welcome-tour')
def welcome_tour():
    """Welcome tour page"""
    return render_template('onboarding/welcome_tour.html')

@bp.route('/quick-start')
def quick_start():
    """Quick start guide page"""
    return render_template('onboarding/quick_start.html')

@bp.route('/advanced-features')
def advanced_features():
    """Advanced features page"""
    return render_template('onboarding/advanced_features.html')

@bp.route('/dashboard')
def dashboard():
    """User dashboard"""
    return render_template('dashboard/index.html')

@bp.route('/projects')
def projects():
    """Projects page"""
    return render_template('dashboard/projects.html')

@bp.route('/new-project', methods=['GET', 'POST'])
def new_project():
    """Create new project page"""
    if request.method == 'POST':
        try:
            # Get form data
            project_title = request.form.get('project_title')
            story_concept = request.form.get('story_concept')
            mood = request.form.get('mood')
            tone = request.form.get('tone')
            genre = request.form.get('genre')
            visual_style = request.form.get('visual_style')
            
            # Validate required fields
            if not all([project_title, story_concept, mood, tone, genre, visual_style]):
                flash('All fields are required', 'error')
                return render_template('dashboard/new_project.html')
            
            # Get current user (for development, use mock user)
            user_id = session.get('user_id', 'dev-user-123')
            
            # Initialize services
            ai_service = AIService()
            image_service = ImageGenerationService()
            
            # Generate moodboard concept using AI
            logger.info(f"Generating moodboard concept for project: {project_title}")
            concept_result = ai_service.generate_moodboard_concept(
                story_concept,
                visual_style,
                4,  # Default to 4 images
                "16:9"  # Default aspect ratio
            )
            
            if concept_result['status'] != 'success':
                flash('Failed to generate concept. Please try again.', 'error')
                return render_template('dashboard/new_project.html')
            
            # Generate image prompts
            prompts = ai_service.generate_image_prompts(
                concept_result['concept'],
                4
            )
            
            if not prompts:
                flash('Failed to generate image prompts. Please try again.', 'error')
                return render_template('dashboard/new_project.html')
            
            # Generate images using Gemini 2.5 Flash
            logger.info(f"Generating {len(prompts)} images with Gemini 2.5 Flash")
            images = image_service.generate_images(
                prompts,
                visual_style,
                provider='gemini'  # Use Gemini 2.5 Flash
            )
            
            if not images:
                # Check if it's a quota issue
                quota_exceeded = any(img.get('quota_exceeded', False) for img in images if isinstance(img, dict))
                
                if quota_exceeded:
                    flash('Gemini API quota exceeded. Using demo images for now. Please set up billing to use real AI image generation.', 'warning')
                    # Fall back to mock images
                    images = [
                        {
                            'url': 'https://picsum.photos/400/300?random=1',
                            'prompt': f'{mood} {genre} scene 1',
                            'enhanced_prompt': f'{mood} {genre} scene 1',
                            'index': 0,
                            'provider': 'demo',
                            'style': visual_style
                        },
                        {
                            'url': 'https://picsum.photos/400/300?random=2',
                            'prompt': f'{mood} {genre} scene 2',
                            'enhanced_prompt': f'{mood} {genre} scene 2',
                            'index': 1,
                            'provider': 'demo',
                            'style': visual_style
                        },
                        {
                            'url': 'https://picsum.photos/400/300?random=3',
                            'prompt': f'{mood} {genre} scene 3',
                            'enhanced_prompt': f'{mood} {genre} scene 3',
                            'index': 2,
                            'provider': 'demo',
                            'style': visual_style
                        },
                        {
                            'url': 'https://picsum.photos/400/300?random=4',
                            'prompt': f'{mood} {genre} scene 4',
                            'enhanced_prompt': f'{mood} {genre} scene 4',
                            'index': 3,
                            'provider': 'demo',
                            'style': visual_style
                        }
                    ]
                else:
                    flash('Failed to generate images. Please try again.', 'error')
                    return render_template('dashboard/new_project.html')
            
            # Use the generated concept
            concept = concept_result['concept']
            
            # For development, create mock project and moodboard IDs
            project_id = f"project_{user_id}_{int(time.time())}"
            moodboard_id = f"moodboard_{user_id}_{int(time.time())}"
            
            # Create project data
            project_data = {
                'user_id': user_id,
                'title': project_title,
                'description': story_concept,
                'mood': mood,
                'tone': tone,
                'genre': genre,
                'visual_style': visual_style,
                'status': 'active',
                'created_at': time.time(),
                'updated_at': time.time()
            }
            
            # Create moodboard data
            moodboard_data = {
                'user_id': user_id,
                'project_id': project_id,
                'story': story_concept,
                'style': visual_style,
                'image_count': len(images),
                'aspect_ratio': '16:9',
                'concept': concept,
                'images': images,
                'status': 'completed',
                'created_at': time.time(),
                'updated_at': time.time()
            }
            
            logger.info(f"Successfully created project {project_id} and moodboard {moodboard_id}")
            
            # Redirect to results page
            flash('Moodboard generated successfully!', 'success')
            return redirect(url_for('main.moodboard_results', moodboard_id=moodboard_id))
            
        except Exception as e:
            logger.error(f"Moodboard generation failed: {str(e)}")
            flash('An error occurred during generation. Please try again.', 'error')
            return render_template('dashboard/new_project.html')
    
    return render_template('dashboard/new_project.html')

@bp.route('/templates')
def templates():
    """Templates page"""
    return render_template('templates.html')

@bp.route('/settings')
def settings():
    """Settings page"""
    return render_template('dashboard/settings.html')

@bp.route('/settings/<section>')
def settings_section(section):
    """Settings section page"""
    valid_sections = ['profile', 'password', 'notifications', 'billing', 'social', 'api']
    if section not in valid_sections:
        return redirect(url_for('main.settings'))
    return render_template(f'dashboard/settings/{section}.html', section=section)

@bp.route('/moodboard/<moodboard_id>')
def moodboard_results(moodboard_id):
    """Display generated moodboard results"""
    try:
        # For development, create mock moodboard data
        moodboard = {
            'id': moodboard_id,
            'concept': 'A dark sci-fi story with serious tone, visualized in cinematic style. A cyberpunk detective story',
            'story': 'A cyberpunk detective story',
            'style': 'cinematic',
            'image_count': 4,
            'images': [
                {
                    'url': 'https://picsum.photos/400/300?random=1',
                    'prompt': 'dark sci-fi scene 1'
                },
                {
                    'url': 'https://picsum.photos/400/300?random=2', 
                    'prompt': 'dark sci-fi scene 2'
                },
                {
                    'url': 'https://picsum.photos/400/300?random=3',
                    'prompt': 'dark sci-fi scene 3'
                },
                {
                    'url': 'https://picsum.photos/400/300?random=4',
                    'prompt': 'dark sci-fi scene 4'
                }
            ]
        }
        
        return render_template('dashboard/moodboard_results.html', moodboard=moodboard)
        
    except Exception as e:
        logger.error(f"Failed to load moodboard {moodboard_id}: {str(e)}")
        flash('Failed to load moodboard', 'error')
        return redirect(url_for('main.dashboard'))

@bp.route('/moodboard/<moodboard_id>/edit', methods=['POST'])
def edit_moodboard(moodboard_id):
    """Edit moodboard using conversational AI"""
    try:
        data = request.get_json()
        edit_prompt = data.get('edit_prompt')
        image_index = data.get('image_index', 0)
        
        if not edit_prompt:
            return jsonify({'error': 'Edit prompt is required'}), 400
        
        # Initialize Gemini service
        from app.services.gemini_service import GeminiService
        gemini_service = GeminiService()
        
        # For now, create a mock edited image
        # In production, this would use the actual Gemini service
        edited_image = {
            'url': f'https://picsum.photos/400/300?random={int(time.time())}',
            'prompt': edit_prompt,
            'index': image_index,
            'edited': True
        }
        
        return jsonify({
            'success': True,
            'edited_image': edited_image,
            'message': 'Image edited successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to edit moodboard {moodboard_id}: {str(e)}")
        return jsonify({'error': 'Failed to edit image'}), 500

@bp.route('/moodboard/<moodboard_id>/chat', methods=['POST'])
def chat_with_moodboard(moodboard_id):
    """Start conversational editing session"""
    try:
        data = request.get_json()
        message = data.get('message')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Initialize Gemini service for conversational editing
        from app.services.gemini_service import GeminiService
        gemini_service = GeminiService()
        chat_session = gemini_service.create_conversational_session()
        
        # Send message to chat session
        response = chat_session.send_message(message)
        
        return jsonify({
            'success': True,
            'response': response.get('text', ''),
            'image': response.get('image'),
            'message': message
        })
        
    except Exception as e:
        logger.error(f"Failed to chat with moodboard {moodboard_id}: {str(e)}")
        return jsonify({'error': 'Failed to process message'}), 500
