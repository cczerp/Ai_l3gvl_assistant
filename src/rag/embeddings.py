"""
Embedding service for converting legal text to vector representations.
Supports both cloud (OpenAI) and local (sentence-transformers) embeddings.
"""

from typing import List, Optional
import numpy as np
from config import get_config


class EmbeddingService:
    """
    Service for generating embeddings from legal text.
    """
    
    def __init__(self, provider: str = "openai"):
        """
        Initialize embedding service.
        
        Args:
            provider: Embedding provider ('openai', 'local', 'huggingface')
        """
        self.config = get_config()
        self.rag_config = self.config.get_rag_config('embeddings')
        self.provider = provider
        self.model = self.rag_config.get('model')
        self.dimension = self.rag_config.get('dimension', 1536)
        self.batch_size = self.rag_config.get('batch_size', 100)
        
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector as numpy array
        """
        # Stub implementation
        # In production: call OpenAI API or load local model
        return np.random.rand(self.dimension)
    
    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            # Stub implementation
            # In production: batch process through embedding model
            batch_embeddings = [self.embed_text(text) for text in batch]
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a search query.
        
        Args:
            query: Search query text
            
        Returns:
            Query embedding vector
        """
        # May use different embedding strategy for queries vs documents
        return self.embed_text(query)
    
    def get_dimension(self) -> int:
        """
        Get the dimension of embeddings.
        
        Returns:
            Embedding dimension
        """
        return self.dimension
