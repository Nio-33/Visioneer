"""
Main application routes for Visioneer
"""

from flask import render_template, request, redirect, url_for, flash, session, jsonify, current_app
from app.main import main_bp
from app.auth.routes import login_required
from app.services.firebase_service import firebase_service
from app.services.ai_service import ai_service
import json
from datetime import datetime

@main_bp.route('/')
def index():
    """Home page"""
    return render_template('main/index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user_id = session['user']['uid']
    
    try:
        # Get user's recent moodboards
        if firebase_service.db:
            moodboards = firebase_service.get_user_moodboards(user_id, limit=12)
            user_data = firebase_service.get_user(user_id)
        else:
            # Development mode - mock data
            moodboards = []
            user_data = {
                'display_name': session['user'].get('display_name', 'Developer'),
                'email': session['user'].get('email', 'dev@example.com'),
                'subscription_tier': 'free'
            }
        
        return render_template('dashboard/index.html', 
                             moodboards=moodboards,
                             user=user_data)
    
    except Exception as e:
        current_app.logger.error(f"Dashboard error: {str(e)}")
        flash('Error loading dashboard.', 'error')
        return render_template('dashboard/index.html', moodboards=[], user={})

@main_bp.route('/create')
@login_required
def create_moodboard():
    """Moodboard creation page"""
    return render_template('moodboard/create.html')

@main_bp.route('/generate', methods=['POST'])
@login_required
def generate_moodboard():
    """Generate moodboard via AI"""
    try:
        # Get form data
        story_text = request.form.get('story')
        style = request.form.get('style', 'cinematic')
        image_count = int(request.form.get('image_count', 8))
        aspect_ratio = request.form.get('aspect_ratio', '16:9')
        
        # Validate input
        if not story_text or len(story_text.strip()) < 50:
            return jsonify({
                'success': False,
                'error': 'Story description must be at least 50 characters long.'
            })
        
        # Initialize AI service if not already done
        if not ai_service.initialized:
            ai_service.initialize(current_app.config['GEMINI_API_KEY'])
        
        # Analyze story
        analysis_result = ai_service.analyze_story(story_text, style)
        
        if not analysis_result['success']:
            return jsonify({
                'success': False,
                'error': 'Failed to analyze story: ' + analysis_result.get('error', 'Unknown error')
            })
        
        # Generate image prompts
        image_prompts = ai_service.generate_image_prompts(
            analysis_result['analysis'], 
            image_count
        )
        
        if not image_prompts:
            return jsonify({
                'success': False,
                'error': 'Failed to generate image prompts.'
            })
        
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
            'message': 'Moodboard analysis completed. Ready for image generation.'
        })
        
    except Exception as e:
        current_app.logger.error(f"Generate moodboard error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while generating the moodboard.'
        })

@main_bp.route('/moodboard/<moodboard_id>')
@login_required
def view_moodboard(moodboard_id):
    """View specific moodboard"""
    try:
        # Get moodboard from Firestore
        moodboard_doc = firebase_service.db.collection('moodboards').document(moodboard_id).get()
        
        if not moodboard_doc.exists:
            flash('Moodboard not found.', 'error')
            return redirect(url_for('main.dashboard'))
        
        moodboard_data = moodboard_doc.to_dict()
        
        # Check if user owns this moodboard
        if moodboard_data['user_id'] != session['user']['uid']:
            flash('You do not have permission to view this moodboard.', 'error')
            return redirect(url_for('main.dashboard'))
        
        return render_template('moodboard/view.html', moodboard=moodboard_data)
        
    except Exception as e:
        current_app.logger.error(f"View moodboard error: {str(e)}")
        flash('Error loading moodboard.', 'error')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')

@main_bp.route('/pricing')
def pricing():
    """Pricing page"""
    return render_template('main/pricing.html')
