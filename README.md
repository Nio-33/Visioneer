# Visioneer 🎬✨

*AI-Powered Visual Moodboard Creator for Filmmakers*

Transform your story ideas into stunning visual moodboards with just a description. Visioneer uses Google's Gemini AI to analyze your narrative and generate professional-quality image collections that capture the mood, tone, and visual style of your creative projects.

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
   cp env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```env
   FLASK_ENV=development
   SECRET_KEY=your_secret_key_here
   GEMINI_API_KEY=your_gemini_api_key
   FIREBASE_PROJECT_ID=your_firebase_project_id
   FIREBASE_STORAGE_BUCKET=your_storage_bucket
   FIREBASE_AUTH_DOMAIN=your_auth_domain
   FIREBASE_API_KEY=your_firebase_api_key
   FIREBASE_APP_ID=your_firebase_app_id
   ```

6. **Initialize Firebase services**
   ```bash
   firebase deploy --only functions
   firebase deploy --only firestore:rules
   firebase deploy --only storage:rules
   ```

7. **Run the application**
   ```bash
   python run.py
   ```

Visit `http://localhost:5000` to see your application running!

## 🏗️ Project Structure

```
visioneer-web/
├── app/                          # Flask application
│   ├── __init__.py              # App factory
│   ├── auth/                    # Authentication routes
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── main/                    # Main application routes
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── api/                     # API endpoints
│   │   ├── __init__.py
│   │   ├── moodboard.py
│   │   └── projects.py
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── ai_service.py
│   │   └── firebase_service.py
│   └── templates/               # Jinja2 templates
│       ├── base.html
│       ├── index.html
│       ├── auth/
│       └── dashboard/
├── functions/                   # Firebase Cloud Functions
│   ├── main.py
│   └── requirements.txt
├── requirements.txt             # Python dependencies
├── env.example                  # Environment variables template
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
- **Google Gemini API** - AI image generation

### Frontend
- **Jinja2** - Template engine
- **Bootstrap 5** - CSS framework
- **Alpine.js** - Lightweight JavaScript framework
- **Font Awesome** - Icons

### Cloud Services
- **Firebase Authentication** - User management
- **Cloud Firestore** - NoSQL database
- **Cloud Storage** - File storage
- **Cloud Functions** - Serverless API
- **Google Gemini API** - AI image generation

## 📝 Features Implemented

### ✅ Completed
- **Project Structure**: Complete Flask application with proper organization
- **Landing Page**: Hero section, features showcase, examples
- **Authentication Pages**: Login, register, forgot password
- **Dashboard**: Project management, navigation, user interface
- **Project Creation**: Story input form with categorization
- **Settings Pages**: Profile, billing, preferences management
- **Firebase Integration**: Database rules, storage rules, Cloud Functions
- **AI Service**: Gemini AI integration for moodboard generation
- **Responsive Design**: Mobile-friendly dark theme

### 🚧 In Progress
- **AI Integration**: Complete Gemini API implementation
- **Image Generation**: Actual image creation from prompts
- **User Authentication**: Firebase Auth integration
- **Data Persistence**: Firestore integration

### 📋 TODO
- **Export Features**: PDF generation, image downloads
- **Collaboration**: Team features, sharing
- **Advanced Customization**: Style fine-tuning
- **Performance Optimization**: Caching, CDN
- **Testing**: Unit and integration tests

## 🎯 Usage

### Creating Your First Moodboard

1. **Sign up** using the registration form
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

## 🚀 Deployment

### Development
```bash
python run.py
```

### Production
```bash
# Firebase Hosting
firebase use production
firebase deploy

# Or deploy to your preferred platform
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

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

---

**Built with ❤️ for the filmmaking community**

*Ready to bring your stories to life? [Start creating your first moodboard today!](https://visioneer.app)*
