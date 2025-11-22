"""
Citation checking and validation endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from src.citation import CitationChecker

router = APIRouter()


class CitationCheckRequest(BaseModel):
    """Request model for citation checking."""
    text: str


class CitationCheckResponse(BaseModel):
    """Response model for citation checking."""
    total_citations: int
    valid_citations: int
    invalid_citations: int
    citations: List[Dict[str, Any]]


@router.post("/citation/check", response_model=CitationCheckResponse)
async def check_citations(request: CitationCheckRequest):
    """
    Check and validate legal citations in text.
    
    Args:
        request: Text containing citations to check
        
    Returns:
        Citation validation results
    """
    try:
        checker = CitationChecker()
        results = checker.check_text(request.text)
        
        return CitationCheckResponse(**results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/citation/extract")
async def extract_citations(text: str):
    """
    Extract citations from text.
    
    Args:
        text: Input text
        
    Returns:
        List of extracted citations
    """
    try:
        checker = CitationChecker()
        citations = checker.extract_citations(text)
        
        return {
            "citations": [
                {
                    "text": c.raw_text,
                    "type": c.citation_type.value,
                    "volume": c.volume,
                    "reporter": c.reporter,
                    "page": c.page
                }
                for c in citations
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/citation/format")
async def format_citation(
    volume: str,
    reporter: str,
    page: str,
    format_style: str = "bluebook"
):
    """
    Format a citation according to specified style.
    
    Args:
        volume: Volume number
        reporter: Reporter abbreviation
        page: Page number
        format_style: Citation style (bluebook, alwd, etc.)
        
    Returns:
        Formatted citation
    """
    # Stub implementation
    return {
        "formatted": f"{volume} {reporter} {page}",
        "style": format_style
    }
