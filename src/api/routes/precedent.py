"""
Precedent graph search endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from src.precedent import PrecedentGraph

router = APIRouter()


class PrecedentSearchRequest(BaseModel):
    """Request model for precedent search."""
    case_id: Optional[str] = None
    citation: Optional[str] = None
    topic: Optional[str] = None
    jurisdiction: Optional[str] = None
    max_depth: int = 2
    limit: int = 10


class PrecedentSearchResponse(BaseModel):
    """Response model for precedent search."""
    related_cases: List[Dict[str, Any]]
    total_found: int


@router.post("/precedent/search", response_model=PrecedentSearchResponse)
async def search_precedent(request: PrecedentSearchRequest):
    """
    Search precedent graph for related cases.
    
    Args:
        request: Precedent search parameters
        
    Returns:
        Related cases and citation information
    """
    try:
        graph = PrecedentGraph()
        
        # Stub implementation - would query actual graph
        related_cases = []
        
        if request.case_id:
            cases = graph.find_related_cases(
                case_id=request.case_id,
                max_depth=request.max_depth,
                limit=request.limit
            )
            related_cases = [
                {
                    "case_id": case.case_id,
                    "case_name": case.case_name,
                    "citation": case.citation,
                    "court": case.court,
                    "jurisdiction": case.jurisdiction
                }
                for case in cases
            ]
        
        elif request.topic:
            cases = graph.search_by_topic(
                topic=request.topic,
                jurisdiction=request.jurisdiction
            )
            related_cases = [
                {
                    "case_id": case.case_id,
                    "case_name": case.case_name,
                    "citation": case.citation
                }
                for case in cases[:request.limit]
            ]
        
        return PrecedentSearchResponse(
            related_cases=related_cases,
            total_found=len(related_cases)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/precedent/citation-count/{case_id}")
async def get_citation_count(case_id: str):
    """
    Get citation statistics for a case.
    
    Args:
        case_id: Case identifier
        
    Returns:
        Citation counts
    """
    try:
        graph = PrecedentGraph()
        counts = graph.get_citation_count(case_id)
        
        return counts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/precedent/most-cited")
async def get_most_cited_cases(limit: int = 10):
    """
    Get most frequently cited cases.
    
    Args:
        limit: Number of cases to return
        
    Returns:
        List of most cited cases
    """
    try:
        graph = PrecedentGraph()
        cases = graph.get_most_cited_cases(limit=limit)
        
        return {
            "cases": [
                {
                    "case_id": case.case_id,
                    "case_name": case.case_name,
                    "citation": case.citation,
                    "citation_count": len(case.cited_by)
                }
                for case in cases
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
