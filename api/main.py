#!/usr/bin/env python3
"""
Bitcoin Balance Tracker API - Simplified Single-User Version

A clean REST API for the Bitcoin Balance Tracker with essential security features:
- API Key authentication
- Rate limiting
- HTTPS enforcement
- Input validation
- Comprehensive logging
- API versioning
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import bitcoin_tracker
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

from api.core.config import get_settings
from api.middleware.rate_limiting import RateLimitMiddleware
from api.middleware.logging import LoggingMiddleware
from api.middleware.security_headers import SecurityHeadersMiddleware
from api.v1.routes import api_router as api_v1_router
from api.core.exceptions import setup_exception_handlers
from bitcoin_tracker import BitcoinTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
bitcoin_tracker_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global bitcoin_tracker_instance
    
    # Startup
    logger.info("🚀 Starting Bitcoin Balance Tracker API")
    
    # Initialize Bitcoin Tracker
    config_path = get_settings().bitcoin_config_path
    bitcoin_tracker_instance = BitcoinTracker(config_path)
    
    # Store in app state
    app.state.bitcoin_tracker = bitcoin_tracker_instance
    
    logger.info("✅ API initialization complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Bitcoin Balance Tracker API")
    if bitcoin_tracker_instance and hasattr(bitcoin_tracker_instance, 'disconnect'):
        bitcoin_tracker_instance.disconnect()

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title="Bitcoin Balance Tracker API",
        description="""
        A clean REST API for tracking Bitcoin wallet balances.
        
        ## Features
        
        - **🔐 API Key Authentication**: Simple and secure API key authentication
        - **🛡️ Rate Limiting**: Intelligent rate limiting to prevent abuse
        - **📊 Input Validation**: Comprehensive request validation
        - **🔒 HTTPS Only**: Enforced secure connections in production
        - **📝 Comprehensive Logging**: Full audit trail
        - **⚡ High Performance**: Async FastAPI with automatic docs
        - **📚 Auto Documentation**: Interactive API docs
        
        ## Bitcoin Features
        
        - Get address balances (all Bitcoin address types supported)
        - Transaction history
        - Address validation
        - Multiple address queries
        - Server discovery and health monitoring
        """,
        version=settings.api_version,
        openapi_url=f"/v1/openapi.json",
        docs_url="/v1/docs",
        redoc_url="/v1/redoc",
        lifespan=lifespan
    )
    
    # Security Middleware (order matters!)
    if settings.environment == "production":
        app.add_middleware(HTTPSRedirectMiddleware)
    
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    # CORS Middleware - simplified for single website
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Exception handlers
    setup_exception_handlers(app)
    
    # Include API routes
    app.include_router(
        api_v1_router,
        prefix="/v1",
        tags=["v1"]
    )
    
    # Root endpoint
    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "message": "Bitcoin Balance Tracker API",
            "version": settings.api_version,
            "docs": "/v1/docs",
            "status": "healthy"
        }
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint for monitoring"""
        try:
            from datetime import datetime
            health_status = {
                "status": "healthy",
                "version": settings.api_version,
                "timestamp": datetime.utcnow().isoformat(),
                "services": {
                    "api": "healthy",
                    "bitcoin_tracker": "healthy" if bitcoin_tracker_instance else "unhealthy"
                }
            }
            
            # Test Bitcoin tracker connection if available
            if bitcoin_tracker_instance:
                try:
                    server_info = bitcoin_tracker_instance.get_server_info()
                    health_status["services"]["electrum_connection"] = "healthy" if server_info else "degraded"
                except Exception:
                    health_status["services"]["electrum_connection"] = "unhealthy"
                    health_status["status"] = "degraded"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "error": "Service unavailable",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    
    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    
    # SSL configuration for production
    ssl_config = {}
    if settings.environment == "production" and settings.ssl_cert_path and settings.ssl_key_path:
        ssl_config = {
            "ssl_certfile": settings.ssl_cert_path,
            "ssl_keyfile": settings.ssl_key_path
        }
    
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level="info",
        **ssl_config
    ) 