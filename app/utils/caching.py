"""
Caching utilities for Visioneer application
"""

import json
import hashlib
import time
from typing import Any, Optional, Callable
from functools import wraps
from flask import current_app, request
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Cache management utility"""
    
    def __init__(self):
        self.cache = {}
        self.ttl = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            return None
        
        # Check TTL
        if key in self.ttl and time.time() > self.ttl[key]:
            self.delete(key)
            return None
        
        return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set value in cache with TTL"""
        self.cache[key] = value
        self.ttl[key] = time.time() + ttl
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        self.cache.pop(key, None)
        self.ttl.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        self.ttl.clear()
    
    def cleanup_expired(self) -> None:
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [key for key, expiry in self.ttl.items() if current_time > expiry]
        for key in expired_keys:
            self.delete(key)

# Global cache manager
cache_manager = CacheManager()

def cache_key_generator(*args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    # Create a hash of the function arguments
    key_data = {
        'args': args,
        'kwargs': kwargs,
        'endpoint': request.endpoint if request else None
    }
    
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()

def cached(ttl: int = 3600, key_func: Optional[Callable] = None):
    """
    Caching decorator
    
    Args:
        ttl: Time to live in seconds
        key_func: Custom key generation function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{f.__name__}:{cache_key_generator(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {cache_key}")
            
            return result
        return decorated_function
    return decorator

def invalidate_cache(pattern: str) -> None:
    """Invalidate cache entries matching pattern"""
    keys_to_delete = [key for key in cache_manager.cache.keys() if pattern in key]
    for key in keys_to_delete:
        cache_manager.delete(key)
    logger.info(f"Invalidated {len(keys_to_delete)} cache entries matching '{pattern}'")

def cache_user_data(user_id: str, data: Any, ttl: int = 1800) -> None:
    """Cache user-specific data"""
    key = f"user:{user_id}:{hashlib.md5(str(data).encode()).hexdigest()}"
    cache_manager.set(key, data, ttl)

def get_cached_user_data(user_id: str, data_hash: str) -> Optional[Any]:
    """Get cached user-specific data"""
    key = f"user:{user_id}:{data_hash}"
    return cache_manager.get(key)

def cache_moodboard_result(moodboard_id: str, result: Any, ttl: int = 3600) -> None:
    """Cache moodboard generation result"""
    key = f"moodboard:{moodboard_id}"
    cache_manager.set(key, result, ttl)

def get_cached_moodboard_result(moodboard_id: str) -> Optional[Any]:
    """Get cached moodboard result"""
    key = f"moodboard:{moodboard_id}"
    return cache_manager.get(key)

def cache_ai_response(prompt_hash: str, response: Any, ttl: int = 7200) -> None:
    """Cache AI service responses"""
    key = f"ai:{prompt_hash}"
    cache_manager.set(key, response, ttl)

def get_cached_ai_response(prompt_hash: str) -> Optional[Any]:
    """Get cached AI response"""
    key = f"ai:{prompt_hash}"
    return cache_manager.get(key)

class RedisCache:
    """Redis-based cache implementation"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in Redis cache"""
        try:
            self.redis.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from Redis cache"""
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear cache entries matching pattern"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis clear pattern error: {str(e)}")
            return 0

def get_cache_stats() -> dict:
    """Get cache statistics"""
    return {
        'total_entries': len(cache_manager.cache),
        'expired_entries': len([k for k, v in cache_manager.ttl.items() if time.time() > v]),
        'memory_usage': sum(len(str(v)) for v in cache_manager.cache.values())
    }
