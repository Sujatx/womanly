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
    async def _get_json(cache_key: str) -> Optional[dict]:
        if not _cache:
            return None

        try:
            cached = await _cache.get(cache_key)
            if cached:
                logger.debug(f"Cache HIT: {cache_key}")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache get error for {cache_key}: {str(e)}")
        return None

    @staticmethod
    async def _set_json(cache_key: str, ttl: int, data) -> None:
        if not _cache:
            return

        try:
            await _cache.setex(cache_key, ttl, json.dumps(data))
            logger.debug(f"Cache SET: {cache_key}")
        except Exception as e:
            logger.warning(f"Cache set error for {cache_key}: {str(e)}")

    @staticmethod
    async def _delete_pattern(pattern: str) -> None:
        if not _cache:
            return

        try:
            async for key in _cache.scan_iter(match=pattern):
                await _cache.delete(key)
            logger.debug(f"Invalidated cache pattern: {pattern}")
        except Exception as e:
            logger.warning(f"Cache invalidation error for {pattern}: {str(e)}")
    
    @staticmethod
    async def get_cached_products(skip: int = 0, limit: int = 20) -> Optional[dict]:
        """Get cached product list."""
        cache_key = f"products:skip={skip}:limit={limit}"
        return await CacheService._get_json(cache_key)
    
    @staticmethod
    async def set_cached_products(skip: int, limit: int, data: List[dict], total: int) -> None:
        """Cache product list."""
        cache_key = f"products:skip={skip}:limit={limit}"
        payload = {"data": data, "total": total}
        await CacheService._set_json(cache_key, CacheService.PRODUCT_CACHE_TTL, payload)
    
    @staticmethod
    async def get_cached_product(product_id: int) -> Optional[dict]:
        """Get cached single product."""
        cache_key = f"product:{product_id}"
        return await CacheService._get_json(cache_key)
    
    @staticmethod
    async def set_cached_product(product_id: int, data: dict) -> None:
        """Cache single product."""
        cache_key = f"product:{product_id}"
        await CacheService._set_json(cache_key, CacheService.PRODUCT_CACHE_TTL, data)
    
    @staticmethod
    async def get_cached_categories() -> Optional[List[dict]]:
        """Get cached categories."""
        return await CacheService._get_json("categories:all")
    
    @staticmethod
    async def set_cached_categories(data: List[dict]) -> None:
        """Cache categories."""
        await CacheService._set_json("categories:all", CacheService.CATEGORY_CACHE_TTL, data)
    
    @staticmethod
    async def invalidate_product_cache(product_id: Optional[int] = None) -> None:
        """Invalidate product cache (called when product is updated)."""
        if not _cache:
            return

        try:
            if product_id is not None:
                await _cache.delete(f"product:{product_id}")
                logger.debug(f"Invalidated product cache: {product_id}")
                return

            await CacheService._delete_pattern("products:*")
            logger.debug("Invalidated all product cache")
        except Exception as e:
            logger.warning(f"Cache invalidation error: {str(e)}")
    
    @staticmethod
    async def invalidate_category_cache() -> None:
        """Invalidate category cache (called when category is updated)."""
        await CacheService._delete_pattern("categories:all")
    
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
