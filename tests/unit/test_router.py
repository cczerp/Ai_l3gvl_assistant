"""Tests for model router."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.router import ModelRouter, QueryType


def test_router_initialization():
    """Test router can be initialized."""
    router = ModelRouter()
    assert router is not None
    assert router.strategy in ["cost_optimized", "performance", "hybrid"]


def test_route_simple_query():
    """Test routing a simple query."""
    router = ModelRouter(strategy="cost_optimized")
    result = router.route_query(
        query="What is a contract?",
        query_type=QueryType.SIMPLE_QUERY
    )
    
    assert "model_type" in result
    assert "model_name" in result
    assert "config" in result


def test_route_complex_query():
    """Test routing a complex query."""
    router = ModelRouter(strategy="performance")
    result = router.route_query(
        query="Analyze the constitutional implications of...",
        query_type=QueryType.COMPLEX_REASONING
    )
    
    assert result["model_type"] == "cloud"


def test_fallback_model():
    """Test fallback model selection."""
    router = ModelRouter()
    fallback = router.get_fallback_model("gpt-4")
    
    assert fallback is not None
    assert "model_type" in fallback
