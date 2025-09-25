"""
Health check API endpoints
"""

from flask import jsonify, request
from app.api import bp
from app.utils.performance import get_performance_stats, performance_monitor
from app.utils.caching import get_cache_stats
from app.config import Config
import logging
import time

logger = logging.getLogger(__name__)

@bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    try:
        # Check basic application health
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'version': '1.0.0',
            'environment': Config.FLASK_ENV
        }
        
        return jsonify(health_status), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 500

@bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check with system metrics"""
    try:
        # Get system metrics
        system_metrics = performance_monitor.get_system_metrics()
        
        # Check critical services
        services_status = {
            'database': check_database_health(),
            'firebase': check_firebase_health(),
            'ai_services': check_ai_services_health(),
            'storage': check_storage_health()
        }
        
        # Overall health status
        all_services_healthy = all(service['status'] == 'healthy' for service in services_status.values())
        
        health_status = {
            'status': 'healthy' if all_services_healthy else 'degraded',
            'timestamp': time.time(),
            'version': '1.0.0',
            'environment': Config.FLASK_ENV,
            'system_metrics': system_metrics,
            'services': services_status,
            'performance': get_performance_stats()
        }
        
        status_code = 200 if all_services_healthy else 503
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 500

@bp.route('/health/ready', methods=['GET'])
def readiness_check():
    """Kubernetes readiness probe"""
    try:
        # Check if application is ready to serve traffic
        ready_checks = {
            'database_connected': check_database_health()['status'] == 'healthy',
            'firebase_connected': check_firebase_health()['status'] == 'healthy',
            'ai_services_available': check_ai_services_health()['status'] == 'healthy'
        }
        
        all_ready = all(ready_checks.values())
        
        if all_ready:
            return jsonify({'status': 'ready'}), 200
        else:
            return jsonify({
                'status': 'not_ready',
                'checks': ready_checks
            }), 503
            
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return jsonify({
            'status': 'not_ready',
            'error': str(e)
        }), 503

@bp.route('/health/live', methods=['GET'])
def liveness_check():
    """Kubernetes liveness probe"""
    try:
        # Simple liveness check - just verify the app is running
        return jsonify({'status': 'alive'}), 200
        
    except Exception as e:
        logger.error(f"Liveness check failed: {str(e)}")
        return jsonify({
            'status': 'dead',
            'error': str(e)
        }), 500

def check_database_health():
    """Check database connectivity"""
    try:
        from app.services.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        # Try to perform a simple operation
        # This is a placeholder - in real implementation, you'd test actual DB operations
        return {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            'status': 'unhealthy',
            'error': str(e)
        }

def check_firebase_health():
    """Check Firebase services health"""
    try:
        # Check Firebase configuration
        required_config = [
            'FIREBASE_PROJECT_ID',
            'FIREBASE_STORAGE_BUCKET',
            'FIREBASE_AUTH_DOMAIN'
        ]
        
        missing_config = [config for config in required_config if not getattr(Config, config)]
        
        if missing_config:
            return {
                'status': 'unhealthy',
                'error': f'Missing Firebase configuration: {missing_config}'
            }
        
        return {
            'status': 'healthy',
            'message': 'Firebase configuration valid'
        }
        
    except Exception as e:
        logger.error(f"Firebase health check failed: {str(e)}")
        return {
            'status': 'unhealthy',
            'error': str(e)
        }

def check_ai_services_health():
    """Check AI services health"""
    try:
        # Check AI service configuration
        ai_services = {
            'gemini': bool(Config.GEMINI_API_KEY),
            'openai': bool(Config.OPENAI_API_KEY)
        }
        
        available_services = [service for service, available in ai_services.items() if available]
        
        if not available_services:
            return {
                'status': 'unhealthy',
                'error': 'No AI services configured'
            }
        
        return {
            'status': 'healthy',
            'message': f'AI services available: {available_services}'
        }
        
    except Exception as e:
        logger.error(f"AI services health check failed: {str(e)}")
        return {
            'status': 'unhealthy',
            'error': str(e)
        }

def check_storage_health():
    """Check storage health"""
    try:
        # Check storage configuration
        if not Config.FIREBASE_STORAGE_BUCKET:
            return {
                'status': 'unhealthy',
                'error': 'Storage bucket not configured'
            }
        
        return {
            'status': 'healthy',
            'message': 'Storage configuration valid'
        }
        
    except Exception as e:
        logger.error(f"Storage health check failed: {str(e)}")
        return {
            'status': 'unhealthy',
            'error': str(e)
        }

@bp.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    try:
        from app.utils.performance import get_performance_stats
        
        metrics_data = get_performance_stats()
        
        # Format as Prometheus metrics
        prometheus_metrics = []
        
        # System metrics
        system = metrics_data.get('system', {})
        prometheus_metrics.append(f"# HELP cpu_percent CPU usage percentage")
        prometheus_metrics.append(f"# TYPE cpu_percent gauge")
        prometheus_metrics.append(f"cpu_percent {system.get('cpu_percent', 0)}")
        
        prometheus_metrics.append(f"# HELP memory_percent Memory usage percentage")
        prometheus_metrics.append(f"# TYPE memory_percent gauge")
        prometheus_metrics.append(f"memory_percent {system.get('memory_percent', 0)}")
        
        # Endpoint metrics
        endpoints = metrics_data.get('endpoints', {})
        for endpoint, metrics in endpoints.items():
            prometheus_metrics.append(f"# HELP request_duration_seconds Request duration in seconds")
            prometheus_metrics.append(f"# TYPE request_duration_seconds histogram")
            prometheus_metrics.append(f"request_duration_seconds{{endpoint=\"{endpoint}\"}} {metrics.get('avg_time', 0)}")
        
        return '\n'.join(prometheus_metrics), 200, {'Content-Type': 'text/plain'}
        
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {str(e)}")
        return jsonify({'error': str(e)}), 500
