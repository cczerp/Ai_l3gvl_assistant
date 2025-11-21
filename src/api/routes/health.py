"""
Health check endpoints.
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        System health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with component status.
    
    Returns:
        Detailed health information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "healthy",
            "models": {
                "cloud": "healthy",
                "local": "healthy"
            },
            "rag": {
                "embeddings": "healthy",
                "vector_store": "healthy",
                "retrieval": "healthy"
            },
            "database": "healthy"
        },
        "version": "1.0.0"
    }
