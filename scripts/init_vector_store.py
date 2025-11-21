#!/usr/bin/env python3
"""
Initialize vector store for Legal-AI system.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag import EmbeddingService, VectorStore
from config import get_config


def main():
    """Initialize vector store."""
    print("Initializing vector store...")
    
    # Load configuration
    config = get_config()
    
    # Initialize embedding service
    embedding_service = EmbeddingService()
    dimension = embedding_service.get_dimension()
    
    # Initialize vector store
    vector_store = VectorStore()
    vector_store.initialize_index(dimension)
    
    # Save index
    vector_store.save_index()
    
    print(f"Vector store initialized with dimension {dimension}")
    print(f"Storage path: {vector_store.storage_path}")
    print("Done!")


if __name__ == "__main__":
    main()
