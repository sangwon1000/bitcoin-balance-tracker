"""
API v1 Routes - Simplified for single-user
"""

from fastapi import APIRouter
from api.v1.routes import bitcoin

# Main API router
api_router = APIRouter()

# Include Bitcoin routes
api_router.include_router(
    bitcoin.router,
    prefix="/bitcoin",
    tags=["Bitcoin"]
)

# Simple status endpoint
@api_router.get("/status", tags=["Status"])
async def api_status():
    """Get API status"""
    return {
        "status": "operational",
        "version": "1.0.0",
        "endpoints": {
            "bitcoin": "/v1/bitcoin/*",
            "docs": "/v1/docs",
            "health": "/health"
        }
    } 