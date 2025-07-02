"""
Simple rate limiting middleware for Bitcoin Balance Tracker API
"""

import time
from typing import Dict, Tuple
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from api.core.config import get_settings

logger = logging.getLogger(__name__)


class SimpleRateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.settings = get_settings()
    
    def is_allowed(self, key: str) -> Tuple[bool, Dict[str, str]]:
        """Check if request is allowed and return rate limit headers"""
        now = time.time()
        window = 60  # 1 minute window
        
        # Clean old requests
        if key in self.requests:
            self.requests[key] = [req_time for req_time in self.requests[key] if now - req_time < window]
        else:
            self.requests[key] = []
        
        # Check limits
        current_requests = len(self.requests[key])
        limit = self.settings.rate_limit_requests_per_minute
        
        # Rate limit headers
        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(max(0, limit - current_requests)),
            "X-RateLimit-Reset": str(int(now + window))
        }
        
        # Check if allowed
        if current_requests >= limit:
            return False, headers
        
        # Allow and record request
        self.requests[key].append(now)
        headers["X-RateLimit-Remaining"] = str(limit - current_requests - 1)
        
        return True, headers


# Global rate limiter instance
rate_limiter = SimpleRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health check
        if request.url.path in ["/health", "/", "/v1/docs", "/v1/redoc", "/v1/openapi.json"]:
            return await call_next(request)
        
        # Get client identifier
        client_ip = self.get_client_ip(request)
        
        # Check rate limit
        allowed, headers = rate_limiter.is_allowed(client_ip)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return Response(
                content='{"detail": "Rate limit exceeded. Please try again later."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    **headers,
                    "Content-Type": "application/json",
                    "Retry-After": "60"
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        for key, value in headers.items():
            response.headers[key] = value
        
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check X-Forwarded-For header first (for proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection IP
        return request.client.host if request.client else "unknown" 