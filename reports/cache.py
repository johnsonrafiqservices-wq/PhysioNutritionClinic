from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import hashlib
import json

class ReportCache:
    """Cache manager for report data to improve performance"""
    
    CACHE_TIMEOUT = {
        'dashboard': 300,      # 5 minutes
        'patient': 600,        # 10 minutes
        'financial': 900,      # 15 minutes
        'appointment': 300,    # 5 minutes
        'performance': 1800,   # 30 minutes
    }
    
    @staticmethod
    def generate_cache_key(report_type, parameters):
        """Generate a unique cache key based on report type and parameters"""
        # Create a hash of the parameters for consistent key generation
        param_string = json.dumps(parameters, sort_keys=True)
        param_hash = hashlib.md5(param_string.encode()).hexdigest()
        return f"report_cache:{report_type}:{param_hash}"
    
    @staticmethod
    def get_cached_report(report_type, parameters):
        """Retrieve cached report data if available and not expired"""
        cache_key = ReportCache.generate_cache_key(report_type, parameters)
        cached_data = cache.get(cache_key)
        
        if cached_data:
            # Check if cache is still valid
            cache_time = cached_data.get('cached_at')
            if cache_time:
                cache_age = (timezone.now() - cache_time).total_seconds()
                timeout = ReportCache.CACHE_TIMEOUT.get(report_type, 600)
                
                if cache_age < timeout:
                    return cached_data.get('data')
        
        return None
    
    @staticmethod
    def cache_report(report_type, parameters, data):
        """Cache report data with timestamp"""
        cache_key = ReportCache.generate_cache_key(report_type, parameters)
        timeout = ReportCache.CACHE_TIMEOUT.get(report_type, 600)
        
        cached_data = {
            'data': data,
            'cached_at': timezone.now(),
            'report_type': report_type,
            'parameters': parameters
        }
        
        cache.set(cache_key, cached_data, timeout)
        return cache_key
    
    @staticmethod
    def invalidate_report_cache(report_type=None):
        """Invalidate cached reports, optionally by type"""
        if report_type:
            # This is a simplified approach - in production you might want
            # to use cache versioning or maintain a list of cache keys
            cache_pattern = f"report_cache:{report_type}:*"
            # Note: This requires Redis or a cache backend that supports pattern deletion
            try:
                cache.delete_pattern(cache_pattern)
            except AttributeError:
                # Fallback for cache backends that don't support pattern deletion
                pass
        else:
            # Clear all report caches
            try:
                cache.delete_pattern("report_cache:*")
            except AttributeError:
                pass
    
    @staticmethod
    def get_cache_stats():
        """Get cache statistics for monitoring"""
        stats = {
            'total_keys': 0,
            'hit_rate': 0,
            'memory_usage': 0,
            'by_type': {}
        }
        
        try:
            # This would need to be implemented based on your cache backend
            # Redis example:
            if hasattr(cache, '_cache') and hasattr(cache._cache, 'get_client'):
                redis_client = cache._cache.get_client()
                info = redis_client.info()
                stats['memory_usage'] = info.get('used_memory_human', '0')
                
                # Get keys matching our pattern
                keys = redis_client.keys('report_cache:*')
                stats['total_keys'] = len(keys)
                
                # Count by report type
                for key in keys:
                    key_str = key.decode() if isinstance(key, bytes) else key
                    parts = key_str.split(':')
                    if len(parts) >= 3:
                        report_type = parts[2]
                        stats['by_type'][report_type] = stats['by_type'].get(report_type, 0) + 1
                        
        except Exception:
            # Fallback if cache backend doesn't support these operations
            pass
        
        return stats

def cache_report_data(report_type):
    """Decorator to cache report data"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract parameters from function arguments
            parameters = kwargs.copy()
            
            # Try to get from cache first
            cached_data = ReportCache.get_cached_report(report_type, parameters)
            if cached_data:
                return cached_data
            
            # Generate fresh data
            data = func(*args, **kwargs)
            
            # Cache the result
            ReportCache.cache_report(report_type, parameters, data)
            
            return data
        return wrapper
    return decorator

class CacheWarmer:
    """Utility to pre-warm frequently accessed report caches"""
    
    @staticmethod
    def warm_dashboard_cache():
        """Pre-warm dashboard cache with common date ranges"""
        from .views import generate_dashboard_export_data
        from datetime import date
        
        common_ranges = [
            # This month
            {
                'start_date': date.today().replace(day=1).isoformat(),
                'end_date': date.today().isoformat()
            },
            # Last 30 days
            {
                'start_date': (date.today() - timedelta(days=30)).isoformat(),
                'end_date': date.today().isoformat()
            },
            # This year
            {
                'start_date': date.today().replace(month=1, day=1).isoformat(),
                'end_date': date.today().isoformat()
            }
        ]
        
        for params in common_ranges:
            try:
                data = generate_dashboard_export_data(params)
                ReportCache.cache_report('dashboard', params, data)
            except Exception as e:
                print(f"Failed to warm cache for dashboard with params {params}: {e}")
    
    @staticmethod
    def warm_financial_cache():
        """Pre-warm financial report cache"""
        from .views import generate_financial_export_data
        
        common_periods = ['this_month', 'last_month', 'this_quarter', 'this_year']
        
        for period in common_periods:
            params = {'period': period}
            try:
                data = generate_financial_export_data(params)
                ReportCache.cache_report('financial', params, data)
            except Exception as e:
                print(f"Failed to warm cache for financial with period {period}: {e}")
    
    @staticmethod
    def warm_all_caches():
        """Warm all report caches"""
        CacheWarmer.warm_dashboard_cache()
        CacheWarmer.warm_financial_cache()
        print("Cache warming completed")

# Signal handlers to invalidate cache when data changes
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver([post_save, post_delete], sender='patients.Patient')
def invalidate_patient_cache(sender, **kwargs):
    """Invalidate patient report cache when patient data changes"""
    ReportCache.invalidate_report_cache('patient')
    ReportCache.invalidate_report_cache('dashboard')

@receiver([post_save, post_delete], sender='billing.Invoice')
def invalidate_financial_cache(sender, **kwargs):
    """Invalidate financial report cache when billing data changes"""
    ReportCache.invalidate_report_cache('financial')
    ReportCache.invalidate_report_cache('dashboard')

@receiver([post_save, post_delete], sender='billing.Payment')
def invalidate_payment_cache(sender, **kwargs):
    """Invalidate financial report cache when payment data changes"""
    ReportCache.invalidate_report_cache('financial')
    ReportCache.invalidate_report_cache('dashboard')

@receiver([post_save, post_delete], sender='appointments.Appointment')
def invalidate_appointment_cache(sender, **kwargs):
    """Invalidate appointment report cache when appointment data changes"""
    ReportCache.invalidate_report_cache('appointment')
    ReportCache.invalidate_report_cache('dashboard')
