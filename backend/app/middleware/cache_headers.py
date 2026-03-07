"""Cache-Control headers middleware for optimal browser/CDN caching."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp
import hashlib


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Add Cache-Control headers based on content type and path."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        path = request.url.path
        
        # Skip cache headers for error responses
        if response.status_code >= 400:
            response.headers['Cache-Control'] = 'no-store'
            return response
        
        # API endpoints
        if path.startswith('/api/v1/products') and request.method == 'GET':
            # Product catalog: 1 hour cache
            response.headers['Cache-Control'] = 'public, max-age=3600, stale-while-revalidate=7200'
            
        elif path.startswith('/api/v1/categories') and request.method == 'GET':
            # Categories: 1 day cache
            response.headers['Cache-Control'] = 'public, max-age=86400, stale-while-revalidate=172800'
            
        elif path.startswith('/health') or path.startswith('/api/v1/health'):
            # Health checks: 30 seconds
            response.headers['Cache-Control'] = 'public, max-age=30'
            
        elif path.startswith('/api/v1/') and request.method == 'GET':
            # Other GET APIs: 5 minutes, but check for freshness
            if 'user' in path or 'cart' in path or 'order' in path or 'wishlist' in path:
                # Private user data: no cache
                response.headers['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'
            else:
                # Public data: short cache
                response.headers['Cache-Control'] = 'public, max-age=300'
                
        elif path.startswith('/api/'):
            # All other API calls (POST/PUT/DELETE): no cache
            response.headers['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        
        else:
            # Static files, HTML: no cache (served by frontend server in production)
            response.headers['Cache-Control'] = 'no-cache, must-revalidate'
        
        # Add weak ETag for cacheable GET responses and support conditional requests.
        if request.method == 'GET' and response.status_code < 400:
            cache_control = response.headers.get('Cache-Control', '')
            is_cacheable = 'no-store' not in cache_control and 'private' not in cache_control
            if is_cacheable:
                body = b''
                async for chunk in response.body_iterator:
                    body += chunk

                etag = f'W/"{hashlib.md5(body).hexdigest()}"'
                incoming_etag = request.headers.get('If-None-Match')

                if incoming_etag == etag:
                    return Response(status_code=304, headers={'ETag': etag})

                headers = dict(response.headers)
                headers['ETag'] = etag
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=headers,
                    media_type=response.media_type,
                    background=response.background,
                )

        return response
