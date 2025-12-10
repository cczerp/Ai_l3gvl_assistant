"""
Configuration management for the Legal-AI system.
Loads and manages configuration from YAML files.
"""

import os
from pathlib import Path
from typing import Any, Dict
import yaml


class Config:
    """Central configuration manager for the Legal-AI system."""
    
    def __init__(self, config_dir: str = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Path to configuration directory. Defaults to ./config
        """
        if config_dir is None:
            self.config_dir = Path(__file__).parent
        else:
            self.config_dir = Path(config_dir)
        
        self.models_config = self._load_yaml('models.yaml')
        self.rag_config = self._load_yaml('rag.yaml')
        self.api_config = self._load_yaml('api.yaml')
    
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        Load YAML configuration file.
        
        Args:
            filename: Name of the YAML file to load
            
        Returns:
            Dictionary containing configuration
        """
        config_path = self.config_dir / filename
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Configuration file {filename} not found")
            return {}
        except yaml.YAMLError as e:
            print(f"Error parsing {filename}: {e}")
            return {}
    
    def get_model_config(self, model_type: str, model_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific model.
        
        Args:
            model_type: Type of model ('cloud_models' or 'local_models')
            model_name: Name of the specific model
            
        Returns:
            Model configuration dictionary
        """
        return self.models_config.get(model_type, {}).get(model_name, {})
    
    def get_rag_config(self, section: str = None) -> Dict[str, Any]:
        """
        Get RAG configuration.
        
        Args:
            section: Specific section of RAG config, or None for all
            
        Returns:
            RAG configuration dictionary
        """
        if section:
            return self.rag_config.get(section, {})
        return self.rag_config
    
    def get_api_config(self, section: str = None) -> Dict[str, Any]:
        """
        Get API configuration.
        
        Args:
            section: Specific section of API config, or None for all
            
        Returns:
            API configuration dictionary
        """
        if section:
            return self.api_config.get(section, {})
        return self.api_config
    
    def get_env_variable(self, key: str, default: str = None) -> str:
        """
        Get environment variable with optional default.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Environment variable value or default
        """
        return os.environ.get(key, default)


# Global configuration instance
_config = None


def get_config() -> Config:
    """
    Get the global configuration instance.
    
    Returns:
        Global Config instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config
