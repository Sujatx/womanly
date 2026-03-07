"""Redis caching service for performance optimization."""

import json
import logging
from typing import Optional, List
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Redis client
try:
    _cache = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Caching disabled.")
    _cache = None


class CacheService:
    """Manage application-level caching for products and categories."""
    
    PRODUCT_CACHE_TTL = 86400  # 1 day in seconds
    CATEGORY_CACHE_TTL = 86400  # 1 day in seconds
    
    @staticmethod
    async def get_cached_products(skip: int = 0, limit: int = 20) -> Optional[dict]:
        """Get cached product list."""
        if not _cache:
            return None
        
        cache_key = f"products:skip={skip}:limit={limit}"
        try:
            cached = await _cache.get(cache_key)
            if cached:
                logger.debug(f"Cache HIT: {cache_key}")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache get error for {cache_key}: {str(e)}")
        return None
    
    @staticmethod
    async def set_cached_products(skip: int, limit: int, data: List[dict], total: int) -> None:
        """Cache product list."""
        if not _cache:
            return
        
        cache_key = f"products:skip={skip}:limit={limit}"
        try:
            payload = {"data": data, "total": total}
            await _cache.setex(cache_key, CacheService.PRODUCT_CACHE_TTL, json.dumps(payload))
            logger.debug(f"Cache SET: {cache_key}")
        except Exception as e:
            logger.warning(f"Cache set error for {cache_key}: {str(e)}")
    
    @staticmethod
    async def get_cached_product(product_id: int) -> Optional[dict]:
        """Get cached single product."""
        if not _cache:
            return None
        
        cache_key = f"product:{product_id}"
        try:
            cached = await _cache.get(cache_key)
            if cached:
                logger.debug(f"Cache HIT: {cache_key}")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache get error for {cache_key}: {str(e)}")
        return None
    
    @staticmethod
    async def set_cached_product(product_id: int, data: dict) -> None:
        """Cache single product."""
        if not _cache:
            return
        
        cache_key = f"product:{product_id}"
        try:
            await _cache.setex(cache_key, CacheService.PRODUCT_CACHE_TTL, json.dumps(data))
            logger.debug(f"Cache SET: {cache_key}")
        except Exception as e:
            logger.warning(f"Cache set error for {cache_key}: {str(e)}")
    
    @staticmethod
    async def get_cached_categories() -> Optional[List[dict]]:
        """Get cached categories."""
        if not _cache:
            return None
        
        cache_key = "categories:all"
        try:
            cached = await _cache.get(cache_key)
            if cached:
                logger.debug(f"Cache HIT: {cache_key}")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache get error for {cache_key}: {str(e)}")
        return None
    
    @staticmethod
    async def set_cached_categories(data: List[dict]) -> None:
        """Cache categories."""
        if not _cache:
            return
        
        cache_key = "categories:all"
        try:
            await _cache.setex(cache_key, CacheService.CATEGORY_CACHE_TTL, json.dumps(data))
            logger.debug(f"Cache SET: {cache_key}")
        except Exception as e:
            logger.warning(f"Cache set error for {cache_key}: {str(e)}")
    
    @staticmethod
    async def invalidate_product_cache(product_id: Optional[int] = None) -> None:
        """Invalidate product cache (called when product is updated)."""
        if not _cache:
            return
        
        try:
            if product_id:
                await _cache.delete(f"product:{product_id}")
                logger.debug(f"Invalidated product cache: {product_id}")
            else:
                pattern = "products:*"
                cursor = b"0"
                while cursor:
                    cursor, keys = await _cache.scan(cursor, match=pattern)
                    if keys:
                        await _cache.delete(*keys)
                logger.debug("Invalidated all product cache")
        except Exception as e:
            logger.warning(f"Cache invalidation error: {str(e)}")
    
    @staticmethod
    async def invalidate_category_cache() -> None:
        """Invalidate category cache (called when category is updated)."""
        if not _cache:
            return
        
        try:
            await _cache.delete("categories:all")
            logger.debug("Invalidated category cache")
        except Exception as e:
            logger.warning(f"Cache invalidation error: {str(e)}")
    
    @staticmethod
    async def get_cache_stats() -> dict:
        """Get cache statistics."""
        if not _cache:
            return {"status": "disabled", "reason": "Redis not connected"}
        
        try:
            info = await _cache.info()
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands": info.get("total_commands_processed", 0)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
