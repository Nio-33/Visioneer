# 🚀 Visioneer Production Deployment Guide

## Overview

This guide will help you deploy Visioneer to production with all the advanced AI capabilities from Gemini 2.5 Flash Image (Nano Banana).

## 🎯 Production-Ready Features

### ✅ **Advanced AI Integration**
- **Gemini 2.5 Flash Image (Nano Banana)** for photorealistic image generation
- **Conversational Image Editing** - Chat-based iterative image refinement
- **Photo Restoration & Colorization** - Restore old/damaged images
- **Multi-Image Processing** - Combine multiple input images
- **Real-time Image Generation** - Fast, high-quality results

### ✅ **Production Infrastructure**
- **Scalable Architecture** - Horizontal scaling support
- **Redis Caching** - Performance optimization
- **Usage Tracking** - Billing and monitoring
- **Rate Limiting** - API protection
- **Security Headers** - Production security
- **SSL/TLS** - Encrypted connections
- **Monitoring** - Health checks and metrics

## 🛠️ Prerequisites

### System Requirements
- **Python 3.8+**
- **Redis Server** (for caching and session storage)
- **PostgreSQL/MySQL** (for production database)
- **Nginx** (reverse proxy and SSL termination)
- **SSL Certificate** (Let's Encrypt recommended)

### Environment Variables
```bash
# Core Application
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost/visioneer

# Redis
REDIS_URL=redis://localhost:6379

# Firebase (Backend Services)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-bucket.appspot.com
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_MESSAGING_SENDER_ID=your-sender-id

# AI Services
GEMINI_API_KEY=your-gemini-api-key

# Monitoring
SENTRY_DSN=your-sentry-dsn-here

# Email (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 🚀 Deployment Methods

### Method 1: Automated Deployment Script

```bash
# Make the deployment script executable
chmod +x deploy.py

# Run the deployment script
python deploy.py
```

### Method 2: Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f visioneer
```

### Method 3: Manual Deployment

#### 1. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y nginx redis-server postgresql postgresql-contrib
```

#### 2. Database Setup
```bash
# Create database
sudo -u postgres createdb visioneer

# Create user
sudo -u postgres createuser --interactive visioneer
```

#### 3. Application Setup
```bash
# Set environment variables
export FLASK_ENV=production
export DATABASE_URL=postgresql://visioneer:password@localhost/visioneer

# Run database migrations
flask db upgrade

# Start the application
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 run:app
```

#### 4. Nginx Configuration
```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/visioneer
sudo ln -s /etc/nginx/sites-available/visioneer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 5. SSL Setup (Let's Encrypt)
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 🔧 Configuration

### Production Configuration
The application uses different configurations for different environments:

- **Development**: `app.config.DevelopmentConfig`
- **Production**: `app.config.ProductionConfig`
- **Testing**: `app.config.TestingConfig`

### Key Production Settings

#### Security
```python
# Security headers
SECURITY_HEADERS = {
    'X-Frame-Options': 'DENY',
    'X-Content-Type-Options': 'nosniff',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
}

# Rate limiting
RATELIMIT_DEFAULT = "1000 per hour"
RATELIMIT_STORAGE_URL = "redis://localhost:6379"
```

#### Performance
```python
# Caching
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379'
CACHE_DEFAULT_TIMEOUT = 300

# Compression
COMPRESS_MIMETYPES = ['text/html', 'text/css', 'application/json']
COMPRESS_LEVEL = 6
```

#### AI Service Limits
```python
# Usage limits
MAX_IMAGES_PER_REQUEST = 10
MAX_IMAGE_SIZE = 8 * 1024 * 1024  # 8MB
AI_REQUEST_TIMEOUT = 60  # seconds
```

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Application health
curl http://localhost:8000/api/health

# Database health
curl http://localhost:8000/api/health/database

# Redis health
curl http://localhost:8000/api/health/redis
```

### Log Monitoring
```bash
# Application logs
sudo journalctl -u visioneer.service -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Performance Monitoring
- **Prometheus Metrics**: `http://localhost:8000/metrics`
- **Sentry Error Tracking**: Automatic error reporting
- **Usage Analytics**: Track AI service usage and costs

## 💰 Billing & Usage Tracking

### AI Service Costs
- **Image Generation**: $0.04 per image
- **Image Editing**: $0.04 per edit
- **Conversational Editing**: $0.04 per message
- **Photo Restoration**: $0.04 per restoration

### Usage Monitoring
```python
# Track usage
from app.services.usage_tracking import UsageTracker
tracker = UsageTracker()

# Track an image generation
tracker.track_usage(
    user_id="user123",
    service_type="image_generation",
    model_used="gemini-2.5-flash-image-preview",
    metadata={"image_count": 1, "prompt_length": 150}
)

# Get user usage summary
summary = tracker.get_usage_summary("user123", days=30)
print(f"Total cost: ${summary['total_cost']}")
```

## 🔒 Security Best Practices

### 1. Environment Security
- Use strong, unique secrets
- Rotate API keys regularly
- Enable 2FA on all accounts
- Use environment-specific configurations

### 2. Application Security
- Enable CSRF protection
- Implement rate limiting
- Use HTTPS everywhere
- Validate all inputs
- Sanitize file uploads

### 3. Infrastructure Security
- Keep systems updated
- Use firewall rules
- Monitor for suspicious activity
- Regular security audits

## 🚨 Troubleshooting

### Common Issues

#### 1. AI Service Errors
```bash
# Check Gemini API key
echo $GEMINI_API_KEY

# Test API connection
curl -H "Authorization: Bearer $GEMINI_API_KEY" \
     https://generativelanguage.googleapis.com/v1/models
```

#### 2. Database Connection Issues
```bash
# Check database status
sudo systemctl status postgresql

# Test connection
psql -h localhost -U visioneer -d visioneer
```

#### 3. Redis Connection Issues
```bash
# Check Redis status
sudo systemctl status redis

# Test connection
redis-cli ping
```

#### 4. High Memory Usage
```bash
# Monitor memory usage
htop

# Check for memory leaks
python -m memory_profiler run.py
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_user_id ON projects(user_id);
CREATE INDEX idx_created_at ON projects(created_at);
```

#### 2. Caching Strategy
```python
# Cache frequently accessed data
@cache.memoize(timeout=300)
def get_user_projects(user_id):
    return Project.query.filter_by(user_id=user_id).all()
```

#### 3. Image Optimization
```python
# Compress images before storage
from PIL import Image
import io

def optimize_image(image_data, max_size=(1920, 1080), quality=85):
    img = Image.open(io.BytesIO(image_data))
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    return output.getvalue()
```

## 📈 Scaling

### Horizontal Scaling
```yaml
# docker-compose.yml
services:
  visioneer:
    image: visioneer:latest
    deploy:
      replicas: 3
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://user:pass@db:5432/visioneer
```

### Load Balancing
```nginx
upstream visioneer_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location / {
        proxy_pass http://visioneer_backend;
    }
}
```

## 🎉 Success Metrics

### Key Performance Indicators
- **Response Time**: < 2 seconds for image generation
- **Uptime**: 99.9% availability
- **Error Rate**: < 0.1% of requests
- **User Satisfaction**: High-quality AI-generated images

### Monitoring Dashboard
- Real-time usage statistics
- Cost tracking and billing
- Performance metrics
- Error rates and alerts

## 📞 Support

For production support and issues:
- **Documentation**: Check this guide first
- **Logs**: Review application and system logs
- **Monitoring**: Use built-in health checks
- **Community**: GitHub Issues for bug reports

---

**🎯 Your Visioneer application is now production-ready with advanced AI capabilities!**

The integration of Gemini 2.5 Flash Image (Nano Banana) provides:
- **Photorealistic image generation**
- **Conversational editing interface**
- **Photo restoration capabilities**
- **Production-grade infrastructure**
- **Comprehensive monitoring**

Deploy with confidence and start creating amazing AI-powered moodboards! 🚀✨
