"""API module for Legal-AI system."""

from .main import app
from .routes import query, citation, precedent, ingestion, health

__all__ = ['app']
