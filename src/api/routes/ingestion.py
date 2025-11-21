"""
Data ingestion endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from src.ingestion import IngestionPipeline, DocumentType

router = APIRouter()


class IngestionRequest(BaseModel):
    """Request model for data ingestion."""
    doc_type: str
    state: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None


class IngestionResponse(BaseModel):
    """Response model for ingestion operations."""
    status: str
    statistics: Dict[str, Any]


@router.post("/ingest", response_model=IngestionResponse)
async def ingest_documents(request: IngestionRequest):
    """
    Ingest legal documents into the system.
    
    Args:
        request: Ingestion parameters
        
    Returns:
        Ingestion statistics
    """
    try:
        pipeline = IngestionPipeline()
        
        if request.doc_type == "state_laws":
            stats = pipeline.ingest_state_laws(state=request.state)
        elif request.doc_type == "federal_laws":
            stats = pipeline.ingest_federal_laws()
        elif request.doc_type == "cases":
            stats = pipeline.ingest_cases(
                start_year=request.start_year,
                end_year=request.end_year
            )
        elif request.doc_type == "legal_dictionaries":
            stats = pipeline.ingest_legal_dictionaries()
        elif request.doc_type == "all":
            stats = pipeline.ingest_all()
        else:
            raise ValueError(f"Unknown document type: {request.doc_type}")
        
        return IngestionResponse(
            status="completed",
            statistics=stats
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ingest/status")
async def get_ingestion_status():
    """
    Get status of ingestion operations.
    
    Returns:
        Current ingestion status
    """
    # Stub implementation
    return {
        "active_jobs": 0,
        "completed_jobs": 0,
        "failed_jobs": 0
    }
