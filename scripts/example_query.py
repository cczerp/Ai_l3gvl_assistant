#!/usr/bin/env python3
"""
Example script for querying the Legal-AI system.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.router import ModelRouter, QueryType
from src.rag import RetrievalService
from src.models import OpenAIModel


def main():
    """Run example query."""
    query = "What are the requirements for a valid contract under federal law?"
    
    print(f"Query: {query}\n")
    
    # Initialize router
    router = ModelRouter(strategy="cost_optimized")
    
    # Route query
    model_info = router.route_query(
        query=query,
        query_type=QueryType.LEGAL_ANALYSIS,
        prefer_local=False
    )
    
    print(f"Selected model: {model_info['model_name']}")
    print(f"Model type: {model_info['model_type']}\n")
    
    # Retrieve context (stub)
    retrieval = RetrievalService()
    results = retrieval.retrieve(query, top_k=3)
    
    print(f"Retrieved {len(results)} relevant documents:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Score: {result['score']:.2f}")
        print(f"   Metadata: {result['metadata']}")
    
    print("\n[In production, this would generate an answer using the selected model]")


if __name__ == "__main__":
    main()
