"""
Simple API Key authentication for single-user Bitcoin Balance Tracker API
"""

import secrets
import hashlib
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import APIKeyHeader
import logging
from typing import Optional

from api.core.config import get_settings

logger = logging.getLogger(__name__)


class SimpleAuth:
    """Simple API key authentication"""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key_header = APIKeyHeader(
            name=self.settings.api_key_header_name,
            auto_error=False
        )
    
    def verify_api_key(self, api_key: str) -> bool:
        """Verify API key"""
        if not api_key:
            return False
        
        # Simple constant-time comparison to prevent timing attacks
        return secrets.compare_digest(api_key, self.settings.api_key)
    
    def is_ip_allowed(self, ip: str) -> bool:
        """Check if IP address is in allow list"""
        allowed_ips = self.settings.allowed_ips_list
        if not allowed_ips:
            return True  # No restrictions if list is empty
        
        return ip in allowed_ips
    
    def generate_api_key(self) -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(32)


# Global auth instance
auth = SimpleAuth()


def get_client_ip(request: Request) -> str:
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


async def verify_api_key(
    request: Request,
    api_key: Optional[str] = Depends(auth.api_key_header)
) -> bool:
    """Verify API key and IP address"""
    
    # Check IP allowlist
    client_ip = get_client_ip(request)
    if not auth.is_ip_allowed(client_ip):
        logger.warning(f"Access denied for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied from this IP address"
        )
    
    # Check API key in header first, then in query parameters
    if not api_key:
        # Check for API key in query parameters as fallback
        api_key = request.query_params.get("api_key") or request.query_params.get("key")
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required (use X-API-Key header or ?api_key= query parameter)",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    if not auth.verify_api_key(api_key):
        logger.warning(f"Invalid API key attempt from IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    return True


# Convenience dependency for protecting endpoints
require_api_key = Depends(verify_api_key) 