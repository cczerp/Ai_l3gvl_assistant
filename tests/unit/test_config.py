"""Tests for configuration system."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import Config, get_config


def test_config_initialization():
    """Test config can be initialized."""
    config = Config()
    assert config is not None


def test_load_models_config():
    """Test loading models configuration."""
    config = Config()
    assert config.models_config is not None
    assert "cloud_models" in config.models_config
    assert "local_models" in config.models_config


def test_load_rag_config():
    """Test loading RAG configuration."""
    config = Config()
    assert config.rag_config is not None
    assert "embeddings" in config.rag_config
    assert "vector_store" in config.rag_config


def test_load_api_config():
    """Test loading API configuration."""
    config = Config()
    assert config.api_config is not None
    assert "server" in config.api_config


def test_get_config_singleton():
    """Test global config instance."""
    config1 = get_config()
    config2 = get_config()
    assert config1 is config2


def test_get_model_config():
    """Test getting specific model config."""
    config = Config()
    openai_config = config.get_model_config("cloud_models", "openai")
    assert openai_config is not None
    assert "model_name" in openai_config
