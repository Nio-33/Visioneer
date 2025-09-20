"""
Projects API endpoints
"""

from flask import request, jsonify, session, current_app
from app.api import api_bp
from app.auth.routes import login_required
from app.services.firebase_service import firebase_service
from datetime import datetime

@api_bp.route('/projects', methods=['GET'])
@login_required
def api_get_projects():
    """Get user's projects/moodboards"""
    try:
        user_id = session['user']['uid']
        
        # Get query parameters
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validate parameters
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 20
        
        # Get moodboards from Firestore
        moodboards = firebase_service.db.collection('moodboards')\
            .where('user_id', '==', user_id)\
            .order_by('created_at', direction=firestore.Query.DESCENDING)\
            .limit(limit)\
            .offset(offset)\
            .stream()
        
        projects = []
        for doc in moodboards:
            project_data = doc.to_dict()
            
            # Convert datetime objects to strings
            if 'created_at' in project_data:
                project_data['created_at'] = project_data['created_at'].isoformat()
            if 'updated_at' in project_data:
                project_data['updated_at'] = project_data['updated_at'].isoformat()
            
            projects.append(project_data)
        
        return jsonify({
            'success': True,
            'projects': projects,
            'count': len(projects),
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        current_app.logger.error(f"API get projects error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@api_bp.route('/projects/search', methods=['GET'])
@login_required
def api_search_projects():
    """Search user's projects"""
    try:
        user_id = session['user']['uid']
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        # Get all user's moodboards
        moodboards = firebase_service.db.collection('moodboards')\
            .where('user_id', '==', user_id)\
            .stream()
        
        # Filter by search query (simple text search)
        results = []
        for doc in moodboards:
            moodboard_data = doc.to_dict()
            
            # Search in title and story
            searchable_text = f"{moodboard_data.get('title', '')} {moodboard_data.get('story', '')}".lower()
            
            if query.lower() in searchable_text:
                # Convert datetime objects
                if 'created_at' in moodboard_data:
                    moodboard_data['created_at'] = moodboard_data['created_at'].isoformat()
                if 'updated_at' in moodboard_data:
                    moodboard_data['updated_at'] = moodboard_data['updated_at'].isoformat()
                
                results.append(moodboard_data)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results),
            'query': query
        })
        
    except Exception as e:
        current_app.logger.error(f"API search projects error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@api_bp.route('/projects/stats', methods=['GET'])
@login_required
def api_get_project_stats():
    """Get user's project statistics"""
    try:
        user_id = session['user']['uid']
        
        # Get all user's moodboards
        moodboards = firebase_service.db.collection('moodboards')\
            .where('user_id', '==', user_id)\
            .stream()
        
        stats = {
            'total_projects': 0,
            'completed_projects': 0,
            'in_progress_projects': 0,
            'styles_used': {},
            'created_this_month': 0,
            'created_this_week': 0
        }
        
        current_date = datetime.utcnow()
        
        for doc in moodboards:
            moodboard_data = doc.to_dict()
            stats['total_projects'] += 1
            
            # Count by status
            status = moodboard_data.get('status', 'unknown')
            if status == 'completed':
                stats['completed_projects'] += 1
            elif status in ['prompts_generated', 'generating_images', 'processing']:
                stats['in_progress_projects'] += 1
            
            # Count by style
            style = moodboard_data.get('style', 'unknown')
            stats['styles_used'][style] = stats['styles_used'].get(style, 0) + 1
            
            # Count recent creations
            created_at = moodboard_data.get('created_at')
            if created_at:
                # Calculate time differences
                time_diff = current_date - created_at
                
                if time_diff.days <= 7:
                    stats['created_this_week'] += 1
                if time_diff.days <= 30:
                    stats['created_this_month'] += 1
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"API get project stats error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
