"""
Main application routes
"""

from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app.main import bp
from app.services.ai_service import AIService
from app.services.image_generation_service import ImageGenerationService
from app.services.firebase_service import FirebaseService
from app.utils.validators import APIValidator
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import time

logger = logging.getLogger(__name__)

@bp.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@bp.route('/login')
def login_redirect():
    """Redirect /login to /auth/login"""
    return redirect(url_for('auth.login'))

@bp.route('/register')
def register_redirect():
    """Redirect /register to /auth/register"""
    return redirect(url_for('auth.register'))

@bp.route('/forgot-password')
def forgot_password_redirect():
    """Redirect /forgot-password to /auth/forgot_password"""
    return redirect(url_for('auth.forgot_password'))

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
    from app.auth.firebase_auth import get_current_user
    user = get_current_user()
    return render_template('dashboard/index.html', user=user)

@bp.route('/projects')
def projects():
    """Projects page"""
    from app.auth.firebase_auth import get_current_user
    user = get_current_user()
    return render_template('dashboard/projects.html', user=user)

@bp.route('/new-project', methods=['GET', 'POST'])
def new_project():
    """Create new project page"""
    from app.auth.firebase_auth import get_current_user
    user = get_current_user()

    if request.method == 'POST':
        try:
            # Get form data
            project_title = request.form.get('project-title')
            story_concept = request.form.get('story-description')
            mood = request.form.get('mood')
            tone = request.form.get('tone')
            genre = request.form.get('genre')
            visual_style = request.form.get('visual-style')
            
            # Debug: Log form data
            logger.info(f"Form data received: project_title={project_title}, story_concept={story_concept[:50]}..., mood={mood}, tone={tone}, genre={genre}, visual_style={visual_style}")
            
            # Validate required fields
            if not all([project_title, story_concept, mood, tone, genre, visual_style]):
                flash('All fields are required', 'error')
                return render_template('dashboard/new_project.html', user=user)
            
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
                return render_template('dashboard/new_project.html', user=user)
            
            # Generate image prompts
            prompts = ai_service.generate_image_prompts(
                concept_result['concept'],
                4
            )
            
            if not prompts:
                flash('Failed to generate image prompts. Please try again.', 'error')
                return render_template('dashboard/new_project.html', user=user)
            
            # Generate images using Gemini 2.5 Flash Image (Nano Banana)
            # Use parallel processing for faster generation
            logger.info(f"Generating {len(prompts)} images in parallel with Gemini 2.5 Flash Image")
            images = []

            # Function to generate a single image
            def generate_single_image(index, prompt):
                try:
                    result = ai_service.generate_image_with_nano_banana(
                        prompt,
                        f"Style: {visual_style}, Mood: {mood}, Genre: {genre}"
                    )
                    return (index, prompt, result)
                except Exception as e:
                    logger.error(f"Error generating image {index+1}: {str(e)}")
                    return (index, prompt, {'success': False, 'error': str(e)})

            # Generate all images in parallel
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_index = {
                    executor.submit(generate_single_image, i, prompt): i
                    for i, prompt in enumerate(prompts)
                }

                # Collect results as they complete
                results = []
                for future in as_completed(future_to_index):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Error in parallel image generation: {str(e)}")

                # Sort results by index to maintain order
                results.sort(key=lambda x: x[0])

                # Process results and convert to base64
                import base64
                import io

                for index, prompt, result in results:
                    if result['success'] and result['images']:
                        for j, img in enumerate(result['images']):
                            buffer = io.BytesIO()
                            img.save(buffer, format='PNG')
                            img_b64 = base64.b64encode(buffer.getvalue()).decode()

                            images.append({
                                'url': f"data:image/png;base64,{img_b64}",
                                'prompt': prompt,
                                'enhanced_prompt': result['prompt_used'],
                                'index': len(images),
                                'provider': 'gemini-2.5-flash-image',
                                'style': visual_style,
                                'model_used': result['model_used']
                            })
                    else:
                        logger.warning(f"Failed to generate image {index+1}: {result.get('error', 'Unknown error')}")
            
            if not images:
                # Fall back to demo images if AI generation fails
                flash('AI image generation failed. Using demo images for now. Please check your Gemini API key and billing setup.', 'warning')
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
            return render_template('dashboard/new_project.html', user=user)
    
    return render_template('dashboard/new_project.html', user=user)

@bp.route('/templates')
def templates():
    """Templates page"""
    from app.auth.firebase_auth import get_current_user
    user = get_current_user()
    return render_template('dashboard/templates.html', user=user)

@bp.route('/settings')
def settings():
    """Settings page"""
    from app.auth.firebase_auth import get_current_user
    user = get_current_user()
    return render_template('dashboard/settings.html', user=user)

@bp.route('/settings/<section>', methods=['GET', 'POST'])
def settings_section(section):
    """Settings section page"""
    from app.auth.firebase_auth import get_current_user
    user = get_current_user()
    valid_sections = ['profile', 'password', 'notifications', 'billing', 'social', 'api']
    if section not in valid_sections:
        return redirect(url_for('main.settings'))

    # Handle profile update form submission
    if request.method == 'POST' and section == 'profile':
        try:
            from app.auth.firebase_auth import auth_manager

            first_name = request.form.get('firstName', '').strip()
            last_name = request.form.get('lastName', '').strip()
            email = request.form.get('email', '').strip()
            bio = request.form.get('bio', '').strip()

            # Combine first and last name
            full_name = f"{first_name} {last_name}".strip()

            # Update Firebase user profile
            if user and user.get('uid'):
                success = auth_manager.update_user_profile(
                    uid=user['uid'],
                    display_name=full_name if full_name else None,
                    email=email if email else None
                )

                if success:
                    flash('Profile updated successfully!', 'success')
                else:
                    flash('Profile updated in session, but Firebase sync failed.', 'warning')
            else:
                # Fallback: Update session data only
                if full_name:
                    session['user_name'] = full_name
                if email:
                    session['user_email'] = email
                flash('Profile updated successfully!', 'success')

            return redirect(url_for('main.settings_section', section='profile'))
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            flash('Failed to update profile. Please try again.', 'error')

    return render_template(f'dashboard/settings/{section}.html', section=section, user=user)

@bp.route('/conversational-editor')
def conversational_editor():
    """Conversational AI image editor page"""
    from app.auth.firebase_auth import get_current_user
    user = get_current_user()
    return render_template('dashboard/conversational_editor.html', user=user)

@bp.route('/moodboard/<moodboard_id>')
def moodboard_results(moodboard_id):
    """Display generated moodboard results"""
    from app.auth.firebase_auth import get_current_user
    user = get_current_user()
    try:
        # In a real application, this would fetch from database
        # For now, we'll create a mock moodboard with the actual generated data
        # This should be replaced with database lookup in production
        
        # Create mock moodboard data that matches the generation process
        moodboard = {
            'id': moodboard_id,
            'concept': 'A dark sci-fi story with serious tone, visualized in cinematic style. A cyberpunk detective story.',
            'story': 'A cyberpunk detective story',
            'style': 'cinematic',
            'mood': 'dark',
            'tone': 'serious',
            'genre': 'sci-fi',
            'visual_style': 'cinematic',
            'image_count': 4,
            'images': [
                {
                    'url': 'https://picsum.photos/400/300?random=1',
                    'prompt': 'dark sci-fi scene 1',
                    'enhanced_prompt': 'dark sci-fi scene 1',
                    'index': 0,
                    'provider': 'demo',
                    'style': 'cinematic'
                },
                {
                    'url': 'https://picsum.photos/400/300?random=2', 
                    'prompt': 'dark sci-fi scene 2',
                    'enhanced_prompt': 'dark sci-fi scene 2',
                    'index': 1,
                    'provider': 'demo',
                    'style': 'cinematic'
                },
                {
                    'url': 'https://picsum.photos/400/300?random=3',
                    'prompt': 'dark sci-fi scene 3',
                    'enhanced_prompt': 'dark sci-fi scene 3',
                    'index': 2,
                    'provider': 'demo',
                    'style': 'cinematic'
                },
                {
                    'url': 'https://picsum.photos/400/300?random=4',
                    'prompt': 'dark sci-fi scene 4',
                    'enhanced_prompt': 'dark sci-fi scene 4',
                    'index': 3,
                    'provider': 'demo',
                    'style': 'cinematic'
                }
            ]
        }
        
        return render_template('dashboard/moodboard_results.html', moodboard=moodboard, user=user)
        
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

@bp.route('/moodboard/<moodboard_id>/refine', methods=['POST'])
def refine_moodboard(moodboard_id):
    """Refine moodboard using AI"""
    try:
        data = request.get_json()
        refine_prompt = data.get('refine_prompt')
        
        if not refine_prompt:
            return jsonify({'error': 'Refine prompt is required'}), 400
        
        # Initialize AI service for refinement
        from app.services.ai_service import AIService
        ai_service = AIService()
        
        # Generate refined images using the refine prompt
        # For now, we'll create mock refined images
        # In production, this would use the actual AI service
        refined_images = []
        for i in range(4):
            refined_images.append({
                'url': f'https://picsum.photos/400/300?random={int(time.time()) + i}',
                'prompt': f'{refine_prompt} - refined scene {i+1}',
                'enhanced_prompt': f'{refine_prompt} - refined scene {i+1}',
                'index': i,
                'provider': 'refined',
                'style': 'cinematic',
                'refined': True
            })
        
        return jsonify({
            'success': True,
            'refined_images': refined_images,
            'message': 'Moodboard refined successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to refine moodboard {moodboard_id}: {str(e)}")
        return jsonify({'error': 'Failed to refine moodboard'}), 500

@bp.route('/moodboard/<moodboard_id>/save', methods=['POST'])
def save_moodboard_to_project(moodboard_id):
    """Save moodboard to user's projects"""
    try:
        data = request.get_json()
        project_name = data.get('project_name', f'Project {moodboard_id}')
        
        # Get current user (for development, use mock user)
        user_id = session.get('user_id', 'dev-user-123')
        
        # In a real application, this would save to database
        # For now, we'll create a mock project entry
        project_data = {
            'id': f'project_{user_id}_{int(time.time())}',
            'user_id': user_id,
            'name': project_name,
            'moodboard_id': moodboard_id,
            'created_at': time.time(),
            'status': 'active'
        }
        
        # In production, this would be saved to database
        logger.info(f"Saved moodboard {moodboard_id} to project {project_data['id']}")
        
        return jsonify({
            'success': True,
            'project_id': project_data['id'],
            'message': f'Moodboard saved to project "{project_name}"'
        })
        
    except Exception as e:
        logger.error(f"Failed to save moodboard {moodboard_id}: {str(e)}")
        return jsonify({'error': 'Failed to save moodboard'}), 500

@bp.route('/api/auto-generate-story', methods=['POST'])
def auto_generate_story():
    """Auto-generate story/concept using AI"""
    try:
        data = request.get_json()
        project_title = data.get('project_title', 'Untitled Project')
        mood = data.get('mood', 'Not specified')
        tone = data.get('tone', 'Not specified')
        genre = data.get('genre', 'Not specified')
        visual_style = data.get('visual_style', 'Not specified')
        
        # Initialize AI service
        from app.services.ai_service import AIService
        ai_service = AIService()
        
        # Create a ultra-concise prompt for story generation
        prompt = f"""Generate a brief {genre} story concept in 2-3 sentences (max 100 words).
The mood is {mood}, tone is {tone}, visual style is {visual_style}.
Project title: "{project_title}"

Write only the core story/scene description. No sections, no character analysis, no bullet points - just a simple narrative description."""
        
        # Generate story using AI
        response = ai_service.text_model.generate_content(prompt)
        generated_story = response.text.strip()
        
        return jsonify({
            'success': True,
            'story': generated_story,
            'message': 'Story generated successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to auto-generate story: {str(e)}")
        return jsonify({'error': 'Failed to generate story'}), 500
