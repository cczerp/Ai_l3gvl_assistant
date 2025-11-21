"""
Model Router for selecting between cloud and local models.
Implements intelligent routing based on query complexity, cost, and performance requirements.
"""

from enum import Enum
from typing import Optional, Dict, Any
from config import get_config


class QueryType(Enum):
    """Types of legal queries for routing decisions."""
    SIMPLE_QUERY = "simple_query"
    COMPLEX_REASONING = "complex_reasoning"
    LEGAL_ANALYSIS = "legal_analysis"
    CITATION_EXTRACTION = "citation_extraction"
    CASE_SUMMARIZATION = "case_summarization"
    CONTRACT_REVIEW = "contract_review"
    PRECEDENT_SEARCH = "precedent_search"


class ModelRouter:
    """
    Routes queries to appropriate models based on complexity, cost, and performance.
    """
    
    def __init__(self, strategy: str = "cost_optimized"):
        """
        Initialize the model router.
        
        Args:
            strategy: Routing strategy (cost_optimized, performance, hybrid)
        """
        self.config = get_config()
        self.strategy = strategy
        self.models_config = self.config.models_config
        
    def route_query(
        self, 
        query: str, 
        query_type: QueryType,
        prefer_local: bool = False
    ) -> Dict[str, Any]:
        """
        Route a query to the appropriate model.
        
        Args:
            query: The legal query text
            query_type: Type of query for routing
            prefer_local: Whether to prefer local models
            
        Returns:
            Dictionary with selected model information
        """
        # Analyze query complexity
        complexity = self._analyze_complexity(query)
        
        # Select model based on strategy
        if self.strategy == "cost_optimized":
            return self._cost_optimized_routing(query_type, complexity, prefer_local)
        elif self.strategy == "performance":
            return self._performance_routing(query_type, complexity)
        else:  # hybrid
            return self._hybrid_routing(query_type, complexity, prefer_local)
    
    def _analyze_complexity(self, query: str) -> str:
        """
        Analyze query complexity.
        
        Args:
            query: The query text
            
        Returns:
            Complexity level: 'simple', 'medium', 'complex'
        """
        # Stub implementation - analyze based on length, keywords, etc.
        word_count = len(query.split())
        
        if word_count < 20:
            return "simple"
        elif word_count < 100:
            return "medium"
        else:
            return "complex"
    
    def _cost_optimized_routing(
        self, 
        query_type: QueryType, 
        complexity: str,
        prefer_local: bool
    ) -> Dict[str, Any]:
        """
        Route based on cost optimization (prefer local models when possible).
        
        Args:
            query_type: Type of query
            complexity: Query complexity level
            prefer_local: Whether to prefer local models
            
        Returns:
            Selected model configuration
        """
        # For simple queries or when local is preferred, use local models
        if complexity == "simple" or prefer_local:
            if query_type in [QueryType.CITATION_EXTRACTION, QueryType.SIMPLE_QUERY]:
                return {
                    "model_type": "local",
                    "model_name": "llama3",
                    "config": self.config.get_model_config("local_models", "llama3")
                }
            else:
                return {
                    "model_type": "local",
                    "model_name": "mixtral",
                    "config": self.config.get_model_config("local_models", "mixtral")
                }
        
        # For complex queries, use cloud models
        if query_type in [QueryType.COMPLEX_REASONING, QueryType.LEGAL_ANALYSIS]:
            return {
                "model_type": "cloud",
                "model_name": "gpt-4",
                "config": self.config.get_model_config("cloud_models", "openai")
            }
        else:
            return {
                "model_type": "cloud",
                "model_name": "claude",
                "config": self.config.get_model_config("cloud_models", "anthropic")
            }
    
    def _performance_routing(
        self, 
        query_type: QueryType, 
        complexity: str
    ) -> Dict[str, Any]:
        """
        Route based on performance (always use best available model).
        
        Args:
            query_type: Type of query
            complexity: Query complexity level
            
        Returns:
            Selected model configuration
        """
        # Always use cloud models for best performance
        return {
            "model_type": "cloud",
            "model_name": "gpt-4",
            "config": self.config.get_model_config("cloud_models", "openai")
        }
    
    def _hybrid_routing(
        self, 
        query_type: QueryType, 
        complexity: str,
        prefer_local: bool
    ) -> Dict[str, Any]:
        """
        Route using hybrid approach (balance cost and performance).
        
        Args:
            query_type: Type of query
            complexity: Query complexity level
            prefer_local: Whether to prefer local models
            
        Returns:
            Selected model configuration
        """
        # Use local for simple, cloud for complex
        if complexity == "simple":
            return self._cost_optimized_routing(query_type, complexity, True)
        else:
            return self._performance_routing(query_type, complexity)
    
    def get_fallback_model(self, failed_model: str) -> Dict[str, Any]:
        """
        Get fallback model if primary model fails.
        
        Args:
            failed_model: Name of the model that failed
            
        Returns:
            Fallback model configuration
        """
        # Stub implementation - return alternative model
        if failed_model in ["gpt-4", "claude"]:
            return {
                "model_type": "local",
                "model_name": "mixtral",
                "config": self.config.get_model_config("local_models", "mixtral")
            }
        else:
            return {
                "model_type": "cloud",
                "model_name": "gpt-4",
                "config": self.config.get_model_config("cloud_models", "openai")
            }
