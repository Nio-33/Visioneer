"""
Usage tracking service for AI service billing and monitoring
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import redis
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class UsageRecord:
    """Record of AI service usage"""
    user_id: str
    service_type: str  # 'image_generation', 'image_editing', 'conversational_edit', 'restoration'
    model_used: str
    timestamp: float
    cost: float
    metadata: Dict
    session_id: Optional[str] = None

class UsageTracker:
    """Service for tracking AI usage and billing"""
    
    def __init__(self):
        """Initialize usage tracker with Redis connection"""
        self.redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self.redis_client.ping()  # Test connection
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory storage.")
            self.redis_client = None
            self._memory_store = {}
        
        # Pricing per service (in USD)
        self.pricing = {
            'image_generation': 0.04,  # $0.04 per image
            'image_editing': 0.04,
            'conversational_edit': 0.04,
            'restoration': 0.04,
            'text_generation': 0.001  # $0.001 per request
        }
    
    def track_usage(self, user_id: str, service_type: str, model_used: str, 
                   metadata: Dict = None, session_id: str = None) -> UsageRecord:
        """
        Track a usage event
        
        Args:
            user_id: ID of the user
            service_type: Type of service used
            model_used: AI model used
            metadata: Additional metadata
            session_id: Optional session ID for conversational editing
            
        Returns:
            UsageRecord object
        """
        try:
            cost = self.pricing.get(service_type, 0.04)
            record = UsageRecord(
                user_id=user_id,
                service_type=service_type,
                model_used=model_used,
                timestamp=time.time(),
                cost=cost,
                metadata=metadata or {},
                session_id=session_id
            )
            
            # Store in Redis or memory
            if self.redis_client:
                key = f"usage:{user_id}:{int(record.timestamp)}"
                self.redis_client.setex(key, 86400 * 30, json.dumps(asdict(record)))  # 30 days TTL
            else:
                if user_id not in self._memory_store:
                    self._memory_store[user_id] = []
                self._memory_store[user_id].append(record)
            
            logger.info(f"Tracked usage: {service_type} for user {user_id}, cost: ${cost}")
            return record
            
        except Exception as e:
            logger.error(f"Error tracking usage: {e}")
            return None
    
    def get_user_usage(self, user_id: str, days: int = 30) -> List[Dict]:
        """
        Get usage statistics for a user
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            List of usage records
        """
        try:
            if self.redis_client:
                # Get all usage keys for user
                pattern = f"usage:{user_id}:*"
                keys = self.redis_client.keys(pattern)
                
                usage_records = []
                for key in keys:
                    data = self.redis_client.get(key)
                    if data:
                        record = json.loads(data)
                        # Filter by date range
                        if record['timestamp'] >= time.time() - (days * 86400):
                            usage_records.append(record)
                
                return sorted(usage_records, key=lambda x: x['timestamp'], reverse=True)
            else:
                # Use memory store
                if user_id not in self._memory_store:
                    return []
                
                cutoff_time = time.time() - (days * 86400)
                records = [asdict(r) for r in self._memory_store[user_id] 
                          if r.timestamp >= cutoff_time]
                return sorted(records, key=lambda x: x['timestamp'], reverse=True)
                
        except Exception as e:
            logger.error(f"Error getting user usage: {e}")
            return []
    
    def get_user_total_cost(self, user_id: str, days: int = 30) -> float:
        """
        Get total cost for a user over specified days
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            Total cost in USD
        """
        usage_records = self.get_user_usage(user_id, days)
        return sum(record['cost'] for record in usage_records)
    
    def get_usage_summary(self, user_id: str, days: int = 30) -> Dict:
        """
        Get usage summary for a user
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            Usage summary dictionary
        """
        usage_records = self.get_user_usage(user_id, days)
        
        summary = {
            'total_requests': len(usage_records),
            'total_cost': sum(record['cost'] for record in usage_records),
            'by_service': {},
            'by_model': {},
            'daily_usage': {}
        }
        
        # Group by service type
        for record in usage_records:
            service = record['service_type']
            model = record['model_used']
            
            if service not in summary['by_service']:
                summary['by_service'][service] = {'count': 0, 'cost': 0}
            summary['by_service'][service]['count'] += 1
            summary['by_service'][service]['cost'] += record['cost']
            
            if model not in summary['by_model']:
                summary['by_model'][model] = {'count': 0, 'cost': 0}
            summary['by_model'][model]['count'] += 1
            summary['by_model'][model]['cost'] += record['cost']
        
        # Group by day
        for record in usage_records:
            date = datetime.fromtimestamp(record['timestamp']).strftime('%Y-%m-%d')
            if date not in summary['daily_usage']:
                summary['daily_usage'][date] = {'count': 0, 'cost': 0}
            summary['daily_usage'][date]['count'] += 1
            summary['daily_usage'][date]['cost'] += record['cost']
        
        return summary
    
    def check_usage_limits(self, user_id: str, service_type: str, 
                          daily_limit: int = 100) -> bool:
        """
        Check if user has exceeded usage limits
        
        Args:
            user_id: User ID
            service_type: Service type to check
            daily_limit: Daily limit for the service
            
        Returns:
            True if within limits, False if exceeded
        """
        try:
            # Get today's usage
            today = datetime.now().strftime('%Y-%m-%d')
            usage_records = self.get_user_usage(user_id, 1)
            
            # Count today's usage for this service
            today_usage = [r for r in usage_records 
                          if r['service_type'] == service_type and
                          datetime.fromtimestamp(r['timestamp']).strftime('%Y-%m-%d') == today]
            
            return len(today_usage) < daily_limit
            
        except Exception as e:
            logger.error(f"Error checking usage limits: {e}")
            return True  # Allow if check fails
    
    def cleanup_old_records(self, days: int = 30):
        """Clean up old usage records"""
        try:
            if self.redis_client:
                # Redis TTL handles cleanup automatically
                pass
            else:
                # Clean up memory store
                cutoff_time = time.time() - (days * 86400)
                for user_id in list(self._memory_store.keys()):
                    self._memory_store[user_id] = [
                        r for r in self._memory_store[user_id] 
                        if r.timestamp >= cutoff_time
                    ]
                    if not self._memory_store[user_id]:
                        del self._memory_store[user_id]
                        
        except Exception as e:
            logger.error(f"Error cleaning up old records: {e}")
