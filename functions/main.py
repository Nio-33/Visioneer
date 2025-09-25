"""
Firebase Cloud Functions for Visioneer
"""

import functions_framework
from flask import Flask, request, jsonify
import os
from google.cloud import firestore
from google.cloud import storage
import google.generativeai as genai

# Initialize Firebase services
db = firestore.Client()
storage_client = storage.Client()

# Configure Gemini AI
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

app = Flask(__name__)

@functions_framework.http
def visioneer_app(request):
    """Main Cloud Function for Visioneer app"""
    return app(request.environ, lambda *args: None)

@app.route('/api/generate-moodboard', methods=['POST'])
def generate_moodboard():
    """Generate a new moodboard using Gemini AI"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['story', 'style', 'image_count', 'aspect_ratio', 'user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate moodboard using Gemini AI
        model = genai.GenerativeModel('gemini-pro')
        
        # Create prompt for moodboard generation
        prompt = f"""
        Create a visual moodboard concept for the following story:
        
        Story: {data['story']}
        Style: {data['style']}
        Image Count: {data['image_count']}
        Aspect Ratio: {data['aspect_ratio']}
        
        Please provide:
        1. A detailed description of the visual elements
        2. Color palette suggestions
        3. Mood and atmosphere descriptions
        4. Specific visual references for each image
        
        Format the response as a structured JSON with image descriptions.
        """
        
        response = model.generate_content(prompt)
        
        # Save moodboard to Firestore
        moodboard_data = {
            'user_id': data['user_id'],
            'story': data['story'],
            'style': data['style'],
            'image_count': data['image_count'],
            'aspect_ratio': data['aspect_ratio'],
            'ai_response': response.text,
            'status': 'generated',
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = db.collection('moodboards').add(moodboard_data)
        moodboard_id = doc_ref[1].id
        
        return jsonify({
            'status': 'success',
            'moodboard_id': moodboard_id,
            'message': 'Moodboard generated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/moodboard/<moodboard_id>', methods=['GET'])
def get_moodboard(moodboard_id):
    """Get moodboard by ID"""
    try:
        doc_ref = db.collection('moodboards').document(moodboard_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({'error': 'Moodboard not found'}), 404
        
        moodboard_data = doc.to_dict()
        moodboard_data['id'] = doc.id
        
        return jsonify(moodboard_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get user projects"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id parameter required'}), 400
        
        projects_ref = db.collection('projects').where('user_id', '==', user_id)
        projects = projects_ref.stream()
        
        project_list = []
        for project in projects:
            project_data = project.to_dict()
            project_data['id'] = project.id
            project_list.append(project_data)
        
        return jsonify({'projects': project_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create new project"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'title' not in data or 'user_id' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        project_data = {
            'title': data['title'],
            'description': data.get('description', ''),
            'user_id': data['user_id'],
            'status': 'active',
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = db.collection('projects').add(project_data)
        project_id = doc_ref[1].id
        
        return jsonify({
            'status': 'success',
            'project_id': project_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
