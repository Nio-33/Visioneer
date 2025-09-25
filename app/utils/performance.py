"""
Performance monitoring utilities for Visioneer application
"""

import time
import psutil
import logging
from functools import wraps
from flask import request, g, current_app
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Performance monitoring utility"""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = time.time()
    
    def record_request_time(self, endpoint: str, duration: float):
        """Record request processing time"""
        if endpoint not in self.metrics:
            self.metrics[endpoint] = {
                'total_requests': 0,
                'total_time': 0,
                'avg_time': 0,
                'max_time': 0,
                'min_time': float('inf')
            }
        
        metrics = self.metrics[endpoint]
        metrics['total_requests'] += 1
        metrics['total_time'] += duration
        metrics['avg_time'] = metrics['total_time'] / metrics['total_requests']
        metrics['max_time'] = max(metrics['max_time'], duration)
        metrics['min_time'] = min(metrics['min_time'], duration)
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'uptime': time.time() - self.start_time
        }
    
    def get_endpoint_metrics(self) -> Dict[str, Any]:
        """Get endpoint performance metrics"""
        return self.metrics
    
    def get_slow_queries(self, threshold: float = 1.0) -> Dict[str, Any]:
        """Get slow queries above threshold"""
        return {
            endpoint: metrics for endpoint, metrics in self.metrics.items()
            if metrics['avg_time'] > threshold
        }

# Global performance monitor
performance_monitor = PerformanceMonitor()

def monitor_performance(f):
    """Decorator to monitor function performance"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            endpoint = request.endpoint or f.__name__
            performance_monitor.record_request_time(endpoint, duration)
            
            # Log slow requests
            if duration > 2.0:  # Log requests taking more than 2 seconds
                logger.warning(f"Slow request: {endpoint} took {duration:.2f}s")
    
    return decorated_function

def monitor_memory_usage(f):
    """Decorator to monitor memory usage"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        process = psutil.Process()
        start_memory = process.memory_info().rss
        
        try:
            result = f(*args, **kwargs)
            return result
        finally:
            end_memory = process.memory_info().rss
            memory_used = end_memory - start_memory
            
            if memory_used > 50 * 1024 * 1024:  # Log if more than 50MB used
                logger.warning(f"High memory usage: {f.__name__} used {memory_used / 1024 / 1024:.2f}MB")
    
    return decorated_function

def get_performance_stats() -> Dict[str, Any]:
    """Get comprehensive performance statistics"""
    return {
        'system': performance_monitor.get_system_metrics(),
        'endpoints': performance_monitor.get_endpoint_metrics(),
        'slow_queries': performance_monitor.get_slow_queries(),
        'cache_stats': get_cache_stats() if 'get_cache_stats' in globals() else {}
    }

class DatabasePerformanceMonitor:
    """Database performance monitoring"""
    
    def __init__(self):
        self.query_times = []
        self.slow_queries = []
    
    def record_query(self, query: str, duration: float):
        """Record database query performance"""
        self.query_times.append(duration)
        
        if duration > 1.0:  # Queries taking more than 1 second
            self.slow_queries.append({
                'query': query[:100] + '...' if len(query) > 100 else query,
                'duration': duration,
                'timestamp': time.time()
            })
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get database query statistics"""
        if not self.query_times:
            return {}
        
        return {
            'total_queries': len(self.query_times),
            'avg_time': sum(self.query_times) / len(self.query_times),
            'max_time': max(self.query_times),
            'min_time': min(self.query_times),
            'slow_queries_count': len(self.slow_queries)
        }

# Global database performance monitor
db_performance_monitor = DatabasePerformanceMonitor()

def optimize_image_processing(image_data: bytes, max_size: tuple = (1024, 1024)) -> bytes:
    """Optimize image for web delivery"""
    from PIL import Image
    import io
    
    try:
        # Open image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        # Resize if too large
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Optimize and save
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=85, optimize=True)
        
        return output.getvalue()
    
    except Exception as e:
        logger.error(f"Image optimization failed: {str(e)}")
        return image_data

def compress_response_data(data: Any) -> bytes:
    """Compress response data"""
    import gzip
    import json
    
    try:
        json_data = json.dumps(data).encode('utf-8')
        compressed = gzip.compress(json_data)
        
        # Only use compression if it actually reduces size
        if len(compressed) < len(json_data):
            return compressed
        else:
            return json_data
    
    except Exception as e:
        logger.error(f"Response compression failed: {str(e)}")
        return json.dumps(data).encode('utf-8')

def batch_process_items(items: list, batch_size: int = 10, 
                       process_func: callable = None) -> list:
    """Process items in batches for better performance"""
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        
        if process_func:
            batch_results = process_func(batch)
            results.extend(batch_results)
        else:
            results.extend(batch)
    
    return results

def async_task_wrapper(func):
    """Wrapper for async tasks to prevent blocking"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # In a real implementation, you would use Celery or similar
        # For now, we'll just execute synchronously
        return func(*args, **kwargs)
    
    return decorated_function

def get_performance_recommendations() -> list:
    """Get performance optimization recommendations"""
    recommendations = []
    
    # Check system metrics
    system_metrics = performance_monitor.get_system_metrics()
    
    if system_metrics['cpu_percent'] > 80:
        recommendations.append("High CPU usage detected. Consider scaling horizontally.")
    
    if system_metrics['memory_percent'] > 80:
        recommendations.append("High memory usage detected. Consider optimizing memory usage.")
    
    if system_metrics['disk_percent'] > 90:
        recommendations.append("High disk usage detected. Consider cleaning up old files.")
    
    # Check endpoint metrics
    endpoint_metrics = performance_monitor.get_endpoint_metrics()
    slow_endpoints = performance_monitor.get_slow_queries(threshold=2.0)
    
    if slow_endpoints:
        recommendations.append(f"Slow endpoints detected: {list(slow_endpoints.keys())}")
    
    return recommendations
