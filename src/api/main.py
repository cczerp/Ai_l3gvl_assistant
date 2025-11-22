"""
Main FastAPI application for Legal-AI system.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_config

# Import routers
from .routes import query, citation, precedent, ingestion, health

# Initialize FastAPI app
app = FastAPI(
    title="Legal-AI Assistant API",
    description="Hybrid legal-AI system with cloud and local models, RAG, and comprehensive legal data",
    version="1.0.0"
)

# Load configuration
config = get_config()
api_config = config.get_api_config()

# Configure CORS
cors_config = api_config.get('cors', {})
if cors_config.get('enabled', True):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.get('allow_origins', ["*"]),
        allow_credentials=True,
        allow_methods=cors_config.get('allow_methods', ["*"]),
        allow_headers=cors_config.get('allow_headers', ["*"]),
    )

# Include routers
app.include_router(query.router, prefix="/api/v1", tags=["query"])
app.include_router(citation.router, prefix="/api/v1", tags=["citation"])
app.include_router(precedent.router, prefix="/api/v1", tags=["precedent"])
app.include_router(ingestion.router, prefix="/api/v1", tags=["ingestion"])
app.include_router(health.router, tags=["health"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("Starting Legal-AI API server...")
    print("Configuration loaded successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("Shutting down Legal-AI API server...")


if __name__ == "__main__":
    import uvicorn
    server_config = api_config.get('server', {})
    uvicorn.run(
        app,
        host=server_config.get('host', '0.0.0.0'),
        port=server_config.get('port', 8000),
        workers=server_config.get('workers', 1),
        reload=server_config.get('reload', False)
    )
