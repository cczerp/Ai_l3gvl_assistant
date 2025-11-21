"""Data ingestion pipeline for legal documents."""

from .ingestion_pipeline import IngestionPipeline, DocumentProcessor, DocumentType

__all__ = ['IngestionPipeline', 'DocumentProcessor', 'DocumentType']
