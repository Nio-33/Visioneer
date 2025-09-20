#!/usr/bin/env python3
"""
Visioneer Web Application Entry Point
AI-Powered Visual Moodboard Creator for Filmmakers
"""

import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Development server
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    port = int(os.getenv('PORT', 5000))
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )
