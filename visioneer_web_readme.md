# Visioneer 🎬✨

*AI-Powered Visual Moodboard Creator for Filmmakers*

Transform your story ideas into stunning visual moodboards with just a description. Visioneer uses Google's Gemini AI to analyze your narrative and generate professional-quality image collections that capture the mood, tone, and visual style of your creative projects.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-v2.3+-green.svg)](https://flask.palletsprojects.com/)
[![Firebase](https://img.shields.io/badge/firebase-v10+-orange.svg)](https://firebase.google.com/)

## 🎯 Features

- **🤖 AI-Powered Generation**: Convert story descriptions into cohesive visual moodboards
- **🎬 Filmmaker-Focused**: Designed specifically for film pre-production workflows
- **⚡ Real-time Processing**: Generate complete moodboards in under 30 seconds
- **🎨 Style Customization**: Multiple visual styles (Cinematic, Noir, Vintage, Modern)
- **💾 Project Management**: Save, organize, and version your moodboards
- **🤝 Collaboration**: Share projects and gather feedback from team members
- **📤 Professional Exports**: PDF presentations, high-res images, print formats
- **📱 Responsive Design**: Works seamlessly on desktop, tablet, and mobile

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Node.js 16+ (for Firebase CLI)
- Google Cloud Project with billing enabled
- Firebase project set up
- Gemini API access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/visioneer-web.git
   cd visioneer-web
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Firebase**
   ```bash
   npm install -g firebase-tools
   firebase login
   firebase init
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```env
   FLASK_ENV=development
   SECRET_KEY=your_secret_key_here
   GEMINI_API_KEY=your_gemini_api_key
   FIREBASE_PROJECT_ID=your_firebase_project_id
   FIREBASE_STORAGE_BUCKET=your_storage_bucket
   FIREBASE_AUTH_DOMAIN=your_auth_domain
   ```

6. **Initialize Firebase services**
   ```bash
   firebase deploy --only functions
   firebase deploy --only firestore:rules
   firebase deploy --only storage:rules
   ```

7. **Run the application**
   ```bash
   flask run
   ```

Visit `http://localhost:5000` to see your application running!

## 🏗️ Project Structure

```
visioneer-web/
├── app/                          # Flask application
│   ├── __init__.py              # App factory
│   ├── auth/                    # Authentication routes
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── main/                    # Main application routes
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── api/                     # API endpoints
│   │   ├── __init__.py
│   │   ├── moodboard.py
│   │   └── projects.py
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── project.py
│   │   └── moodboard.py
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── ai_service.py
│   │   ├── firebase_service.py
│   │   └── image_service.py
│   ├── static/                  # Static assets
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── dashboard/
│   │   └── moodboard/
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── decorators.py
│       └── validators.py
├── functions/                   # Firebase Cloud Functions
│   ├── main.py
│   ├── gemini_handler.py
│   ├── image_processor.py
│   └── requirements.txt
├── tests/                       # Test suite
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── config/                      # Configuration files
│   ├── __init__.py
│   ├── development.py
│   ├── production.py
│   └── testing.py
├── migrations/                  # Database migrations
├── requirements.txt             # Python dependencies
├── .env.example                # Environment variables template
├── firebase.json               # Firebase configuration
├── firestore.rules            # Firestore security rules
├── storage.rules              # Storage security rules
└── run.py                     # Application entry point
```

## 🛠️ Technology Stack

### Backend
- **Flask 2.3+** - Web framework
- **Python 3.9+** - Programming language
- **Firebase Admin SDK** - Backend services integration
- **Gunicorn** - WSGI HTTP Server

### Frontend
- **Jinja2** - Template engine
- **Bootstrap 5** - CSS framework
- **Alpine.js** - Lightweight JavaScript framework
- **Firebase SDK** - Client-side authentication

### Cloud Services
- **Firebase Authentication** - User management
- **Cloud Firestore** - NoSQL database
- **Cloud Storage** - File storage
- **Cloud Functions** - Serverless API
- **Google Gemini API** - AI image generation

### Development Tools
- **pytest** - Testing framework
- **Black** - Code formatting
- **Flake8** - Code linting
- **Firebase CLI** - Development tools

## 📝 Usage

### Creating Your First Moodboard

1. **Sign up** using Google or email
2. **Click "New Moodboard"** from your dashboard
3. **Enter your story description**:
   ```
   A cyberpunk thriller set in Neo-Tokyo 2087. Neon-lit streets, 
   rain-soaked pavement, towering holographic advertisements. 
   The protagonist is a tech-savvy detective investigating 
   corporate espionage in the digital underground.
   ```
4. **Select your preferences**:
   - Style: Cinematic
   - Images: 8
   - Aspect Ratio: 16:9
5. **Click "Generate Moodboard"**
6. **Review and refine** your results
7. **Export or share** your final moodboard

### API Usage

Generate moodboards programmatically:

```python
import requests

# Authentication required
headers = {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
}

data = {
    'story': 'Your story description here',
    'style': 'cinematic',
    'image_count': 6,
    'aspect_ratio': '16:9'
}

response = requests.post(
    'https://your-app.web.app/api/generate-moodboard',
    headers=headers,
    json=data
)

moodboard = response.json()
```

## 🧪 Testing

Run the complete test suite:

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# All tests with coverage
pytest --cov=app tests/

# Specific test file
pytest tests/unit/test_ai_service.py -v
```

Firebase Emulator testing:
```bash
firebase emulators:start
export USE_FIREBASE_EMULATOR=true
pytest tests/integration/
```

## 🚀 Deployment

### Development
```bash
flask run --debug
```

### Staging
```bash
# Deploy to Firebase Hosting
firebase use staging
firebase deploy

# Or deploy to your preferred platform
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### Production
```bash
# Firebase Hosting
firebase use production
firebase deploy

# Docker deployment
docker build -t visioneer-web .
docker run -p 8000:8000 visioneer-web

# Environment-specific configurations
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FLASK_ENV` | Environment (development/production) | Yes |
| `SECRET_KEY` | Flask secret key | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `FIREBASE_PROJECT_ID` | Firebase project ID | Yes |
| `FIREBASE_STORAGE_BUCKET` | Firebase storage bucket | Yes |
| `FIREBASE_AUTH_DOMAIN` | Firebase auth domain | Yes |
| `REDIS_URL` | Redis connection string (optional) | No |

### Firebase Configuration

Update `firebase.json`:
```json
{
  "hosting": {
    "public": "app/static",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      {
        "source": "**",
        "function": "app"
      }
    ]
  },
  "functions": {
    "source": "functions",
    "runtime": "python39"
  }
}
```

## 📊 Monitoring & Analytics

### Performance Monitoring
- Firebase Performance Monitoring integrated
- Custom metrics for moodboard generation times
- Error tracking with Sentry (optional)

### Analytics Events
- User registration and authentication
- Moodboard creation and completion
- Export and sharing actions
- Feature usage patterns

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Run tests**
   ```bash
   pytest
   black app/
   flake8 app/
   ```
5. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Code Style

- Follow PEP 8 style guidelines
- Use Black for code formatting
- Write comprehensive tests for new features
- Update documentation for API changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini Team** - For powerful AI capabilities
- **Firebase Team** - For robust backend services
- **Flask Community** - For the excellent web framework
- **Open Source Contributors** - For invaluable tools and libraries

## 📞 Support & Community

- **Documentation**: [docs.visioneer.app](https://docs.visioneer.app)
- **Issues**: [GitHub Issues](https://github.com/yourusername/visioneer-web/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/visioneer-web/discussions)
- **Email**: support@visioneer.app
- **Discord**: [Join our community](https://discord.gg/visioneer)

## 🗺️ Roadmap

- [ ] **v1.1** - Advanced style customization and fine-tuning
- [ ] **v1.2** - Team collaboration features and real-time editing
- [ ] **v1.3** - Video moodboard generation
- [ ] **v1.4** - Integration with popular filmmaking tools (Final Cut Pro, Premiere)
- [ ] **v1.5** - Custom AI model training for personalized styles
- [ ] **v2.0** - Mobile companion app with camera integration

---

**Built with ❤️ for the filmmaking community**

*Ready to bring your stories to life? [Start creating your first moodboard today!](https://visioneer.app)*