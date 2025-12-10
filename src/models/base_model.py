"""
Base model interface for all AI providers.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ModelResponse:
    """Standard response format from all models."""
    content: str
    model: str
    provider: str
    confidence: float  # 0.0 to 1.0
    tokens_used: int
    cost: float  # USD
    latency: float  # seconds
    citations: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime


class BaseModel(ABC):
    """Abstract base class for all AI models."""

    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the model.

        Args:
            api_key: API key for the provider
            model_name: Specific model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        self.provider = self.__class__.__name__.replace('Model', '').lower()

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ) -> ModelResponse:
        """
        Generate a response from the model.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters

        Returns:
            ModelResponse object
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ):
        """
        Generate a streaming response from the model.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters

        Yields:
            Chunks of generated text
        """
        pass

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate the cost of a request.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        # Override in subclasses with actual pricing
        return 0.0

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
