# Visioneer Setup Guide

This guide will walk you through setting up the Visioneer AI-powered moodboard creation tool.

## Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.9+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/)
- **Google Cloud Account** - For Gemini AI API access
- **Firebase Account** - For backend services

## Step 1: Project Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd /Users/nio/Visioneer
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Firebase CLI:**
   ```bash
   npm install -g firebase-tools
   ```

## Step 2: Google Cloud Setup

1. **Create a Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Note down your project ID

2. **Enable Gemini AI API:**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Generative Language API"
   - Click "Enable"

3. **Create API Key:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy the API key (you'll need it later)

## Step 3: Firebase Setup

1. **Create Firebase Project:**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Click "Add project"
   - Use the same project ID as your Google Cloud project
   - Enable Google Analytics (optional)

2. **Enable Firebase Services:**
   - **Authentication:** Go to Authentication > Sign-in method, enable Email/Password
   - **Firestore:** Go to Firestore Database, create database in production mode
   - **Storage:** Go to Storage, get started with default rules
   - **Hosting:** Go to Hosting, get started (optional for development)

3. **Generate Service Account Key:**
   - Go to Project Settings > Service accounts
   - Click "Generate new private key"
   - Download the JSON file and save it as `firebase-service-account.json` in the project root

4. **Configure Firebase CLI:**
   ```bash
   firebase login
   firebase use --add
   # Select your project when prompted
   ```

## Step 4: Environment Configuration

1. **Copy environment template:**
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` file with your credentials:**
   ```env
   # Flask Configuration
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   FLASK_APP=run.py

   # Google Gemini API
   GEMINI_API_KEY=your_gemini_api_key_here

   # Firebase Configuration
   FIREBASE_PROJECT_ID=your_firebase_project_id
   FIREBASE_STORAGE_BUCKET=your_storage_bucket_name
   FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
   FIREBASE_API_KEY=your_firebase_api_key

   # Development settings
   DEBUG=True
   TESTING=False
   ```

3. **Generate a secret key:**
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

## Step 5: Firebase Deployment

1. **Deploy Firestore rules:**
   ```bash
   firebase deploy --only firestore:rules
   ```

2. **Deploy Storage rules:**
   ```bash
   firebase deploy --only storage:rules
   ```

3. **Deploy Cloud Functions (if using):**
   ```bash
   firebase deploy --only functions
   ```

## Step 6: Run the Application

1. **Start the development server:**
   ```bash
   python run.py
   ```

2. **Open your browser:**
   - Navigate to `http://localhost:5000`
   - You should see the Visioneer homepage

## Step 7: Testing

1. **Run unit tests:**
   ```bash
   pytest tests/unit/
   ```

2. **Run all tests:**
   ```bash
   pytest
   ```

3. **Test with coverage:**
   ```bash
   pytest --cov=app tests/
   ```

## Step 8: Development Workflow

1. **Code formatting:**
   ```bash
   black app/
   flake8 app/
   ```

2. **Run in development mode:**
   ```bash
   export FLASK_ENV=development
   python run.py
   ```

3. **Debug mode:**
   ```bash
   export FLASK_DEBUG=1
   python run.py
   ```

## Troubleshooting

### Common Issues

1. **Firebase Authentication Error:**
   - Ensure your service account key is in the project root
   - Check that Firebase Authentication is enabled
   - Verify your Firebase project ID is correct

2. **Gemini API Error:**
   - Verify your API key is correct
   - Check that the Generative Language API is enabled
   - Ensure you have billing enabled on your Google Cloud project

3. **Import Errors:**
   - Make sure your virtual environment is activated
   - Run `pip install -r requirements.txt` again
   - Check that you're using Python 3.9+

4. **Port Already in Use:**
   - Change the port in `run.py` or kill the process using port 5000
   - Use `lsof -ti:5000 | xargs kill -9` on macOS/Linux

### Getting Help

- Check the logs in your terminal for error messages
- Review the Firebase Console for authentication and database issues
- Consult the [Flask documentation](https://flask.palletsprojects.com/)
- Review the [Firebase documentation](https://firebase.google.com/docs)

## Next Steps

Once you have the basic application running:

1. **Create your first moodboard** by registering an account
2. **Test the AI integration** with a sample story
3. **Customize the styling** in `app/static/css/style.css`
4. **Add new features** following the existing code patterns
5. **Deploy to production** using Firebase Hosting or your preferred platform

## Production Deployment

For production deployment:

1. **Set environment variables** on your hosting platform
2. **Use a production WSGI server** like Gunicorn
3. **Enable HTTPS** and proper security headers
4. **Set up monitoring** with Firebase Analytics
5. **Configure proper logging** for error tracking

## Support

If you encounter issues:

1. Check this setup guide first
2. Review the error logs
3. Consult the documentation
4. Create an issue in the project repository

Happy coding! 🎬✨
