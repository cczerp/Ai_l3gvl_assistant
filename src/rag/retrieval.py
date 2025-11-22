"""
Retrieval service for RAG pipeline.
Combines embedding, vector search, and reranking.
"""

from typing import List, Dict, Any, Optional
from config import get_config
from .embeddings import EmbeddingService
from .vector_store import VectorStore


class RetrievalService:
    """
    Service for retrieving relevant legal documents for queries.
    """
    
    def __init__(self):
        """Initialize retrieval service."""
        self.config = get_config()
        self.retrieval_config = self.config.get_rag_config('retrieval')
        
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        
        self.top_k = self.retrieval_config.get('top_k', 5)
        self.similarity_threshold = self.retrieval_config.get('similarity_threshold', 0.7)
        self.reranking_enabled = self.retrieval_config.get('reranking_enabled', True)
    
    def retrieve(
        self, 
        query: str,
        top_k: Optional[int] = None,
        filter_criteria: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            top_k: Number of results to return (overrides config)
            filter_criteria: Optional metadata filters
            
        Returns:
            List of retrieved documents with scores and metadata
        """
        k = top_k if top_k is not None else self.top_k
        
        # Generate query embedding
        query_embedding = self.embedding_service.embed_query(query)
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding, 
            top_k=k * 2 if self.reranking_enabled else k,
            filter_criteria=filter_criteria
        )
        
        # Filter by similarity threshold
        filtered_results = [
            (doc_id, score, metadata) 
            for doc_id, score, metadata in results 
            if score >= self.similarity_threshold
        ]
        
        # Rerank if enabled
        if self.reranking_enabled:
            filtered_results = self._rerank(query, filtered_results)
        
        # Format results
        return [
            {
                "doc_id": doc_id,
                "score": score,
                "metadata": metadata,
                "content": metadata.get("content", "")
            }
            for doc_id, score, metadata in filtered_results[:k]
        ]
    
    def _rerank(
        self, 
        query: str, 
        results: List[tuple]
    ) -> List[tuple]:
        """
        Rerank results using cross-encoder model.
        
        Args:
            query: Original query
            results: Initial results to rerank
            
        Returns:
            Reranked results
        """
        # Stub implementation
        # In production: use cross-encoder model for reranking
        # For now, just return the same results
        return results
    
    def retrieve_by_citation(self, citation: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve document by legal citation.
        
        Args:
            citation: Legal citation (e.g., "Brown v. Board of Education, 347 U.S. 483")
            
        Returns:
            Document if found, None otherwise
        """
        # Stub implementation
        # In production: search by citation metadata
        filter_criteria = {"citation": citation}
        results = self.retrieve(citation, top_k=1, filter_criteria=filter_criteria)
        return results[0] if results else None
    
    def retrieve_by_jurisdiction(
        self, 
        query: str, 
        jurisdiction: str,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents filtered by jurisdiction.
        
        Args:
            query: Search query
            jurisdiction: Jurisdiction to filter by (state or federal)
            top_k: Number of results to return
            
        Returns:
            List of retrieved documents
        """
        filter_criteria = {"jurisdiction": jurisdiction}
        return self.retrieve(query, top_k=top_k, filter_criteria=filter_criteria)
    
    def get_context_window(
        self, 
        query: str, 
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Get formatted context window for LLM prompt.
        
        Args:
            query: Search query
            max_tokens: Maximum tokens for context (overrides config)
            
        Returns:
            Formatted context string
        """
        max_tokens = max_tokens or self.retrieval_config.get('max_context_tokens', 8000)
        
        results = self.retrieve(query)
        
        # Format context with metadata
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[Document {i}]")
            
            # Add metadata
            metadata = result['metadata']
            if 'citation' in metadata:
                context_parts.append(f"Citation: {metadata['citation']}")
            if 'jurisdiction' in metadata:
                context_parts.append(f"Jurisdiction: {metadata['jurisdiction']}")
            
            # Add content
            context_parts.append(f"Content: {result['content']}\n")
        
        context = "\n".join(context_parts)
        
        # Stub: truncate to max_tokens
        # In production: use proper tokenizer
        return context[:max_tokens * 4]  # Rough approximation
