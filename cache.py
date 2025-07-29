# cache.py - High-performance caching layer for MEXC API

import asyncio
import time
import hashlib
from typing import Optional, Dict, Any, Union
try:
    import orjson as json_lib
    JSON_LOADS = json_lib.loads
    JSON_DUMPS = json_lib.dumps
except ImportError:
    import ujson as json_lib
    JSON_LOADS = json_lib.loads
    JSON_DUMPS = lambda x: json_lib.dumps(x).encode() if isinstance(x, dict) else json_lib.dumps(x)
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# In-memory cache as fallback when Redis is not available
_memory_cache: Dict[str, Dict[str, Any]] = {}
_cache_lock = asyncio.Lock()

# Redis client (will be initialized if Redis is available)
_redis_client = None

async def init_cache():
    """Initialize caching system (Redis preferred, memory fallback)"""
    global _redis_client

    try:
        # Try to import and use Redis
        import redis.asyncio as redis
        _redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=False,  # We'll handle JSON encoding ourselves
            max_connections=20,
            socket_connect_timeout=5,
            socket_timeout=5
        )

        # Test connection
        await _redis_client.ping()
        logger.info("Redis cache initialized successfully")
        return True

    except Exception as e:
        logger.warning(f"Redis not available, using memory cache: {e}")
        _redis_client = None
        return False

async def close_cache():
    """Close cache connections"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None

def _generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a consistent cache key from arguments"""
    key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
    return hashlib.md5(key_data.encode()).hexdigest()

async def get_cached(key: str) -> Optional[Any]:
    """Get value from cache (Redis or memory)"""
    try:
        if _redis_client:
            # Try Redis first
            cached_data = await _redis_client.get(key)
            if cached_data:
                data = JSON_LOADS(cached_data)
                # Check if expired
                if data.get('expires', 0) > time.time():
                    return data['value']
                else:
                    # Remove expired key
                    await _redis_client.delete(key)
        
        # Fallback to memory cache
        async with _cache_lock:
            if key in _memory_cache:
                data = _memory_cache[key]
                if data.get('expires', 0) > time.time():
                    return data['value']
                else:
                    del _memory_cache[key]
        
        return None
        
    except Exception as e:
        logger.error(f"Cache get error for key {key}: {e}")
        return None

async def set_cached(key: str, value: Any, ttl: int = 300) -> bool:
    """Set value in cache with TTL (Redis or memory)"""
    try:
        expires = time.time() + ttl
        cache_data = {
            'value': value,
            'expires': expires,
            'created': time.time()
        }
        
        if _redis_client:
            # Store in Redis
            await _redis_client.setex(
                key,
                ttl,
                JSON_DUMPS(cache_data)
            )
        
        # Also store in memory cache as backup
        async with _cache_lock:
            _memory_cache[key] = cache_data
            
            # Clean up expired memory cache entries periodically
            if len(_memory_cache) > 1000:
                current_time = time.time()
                expired_keys = [
                    k for k, v in _memory_cache.items() 
                    if v.get('expires', 0) <= current_time
                ]
                for k in expired_keys:
                    del _memory_cache[k]
        
        return True
        
    except Exception as e:
        logger.error(f"Cache set error for key {key}: {e}")
        return False

async def delete_cached(key: str) -> bool:
    """Delete value from cache"""
    try:
        if _redis_client:
            await _redis_client.delete(key)
        
        async with _cache_lock:
            _memory_cache.pop(key, None)
        
        return True
        
    except Exception as e:
        logger.error(f"Cache delete error for key {key}: {e}")
        return False

def cached_api_call(ttl: int = 300, key_prefix: str = "api"):
    """Decorator for caching API calls"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _generate_cache_key(f"{key_prefix}:{func.__name__}", *args, **kwargs)
            
            # Try to get from cache first
            cached_result = await get_cached(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Call the actual function
            logger.debug(f"Cache miss for {func.__name__}, calling API")
            result = await func(*args, **kwargs)
            
            # Cache the result
            await set_cached(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

# Cache statistics
async def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    stats = {
        'memory_cache_size': len(_memory_cache),
        'redis_available': _redis_client is not None,
        'timestamp': time.time()
    }
    
    if _redis_client:
        try:
            info = await _redis_client.info()
            stats.update({
                'redis_used_memory': info.get('used_memory_human', 'unknown'),
                'redis_connected_clients': info.get('connected_clients', 0),
                'redis_total_commands_processed': info.get('total_commands_processed', 0)
            })
        except Exception as e:
            logger.error(f"Error getting Redis stats: {e}")
    
    return stats

async def clear_cache(pattern: str = "*") -> int:
    """Clear cache entries matching pattern"""
    cleared = 0
    
    try:
        if _redis_client:
            keys = await _redis_client.keys(pattern)
            if keys:
                cleared += await _redis_client.delete(*keys)
        
        # Clear memory cache
        async with _cache_lock:
            if pattern == "*":
                cleared += len(_memory_cache)
                _memory_cache.clear()
            else:
                # Simple pattern matching for memory cache
                keys_to_delete = [k for k in _memory_cache.keys() if pattern.replace("*", "") in k]
                for key in keys_to_delete:
                    del _memory_cache[key]
                cleared += len(keys_to_delete)
        
        logger.info(f"Cleared {cleared} cache entries matching pattern: {pattern}")
        return cleared
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return 0
