"""
Anthropic Claude model integration.
"""

import os
import time
from typing import Optional
from datetime import datetime
from anthropic import AsyncAnthropic
import logging

from .base_model import BaseModel, ModelResponse

logger = logging.getLogger(__name__)


class AnthropicModel(BaseModel):
    """Anthropic Claude model integration."""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
        "claude-3-sonnet-20240229": {"input": 3.0, "output": 15.0},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    }

    def __init__(self, api_key: Optional[str] = None, model_name: str = "claude-3-opus-20240229"):
        """
        Initialize Anthropic model.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model_name: Model to use
        """
        api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("Anthropic API key required")

        super().__init__(api_key, model_name)
        self.client = AsyncAnthropic(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ) -> ModelResponse:
        """Generate response from Claude."""

        start_time = time.time()

        try:
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )

            content = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            tokens_used = input_tokens + output_tokens

            cost = self.estimate_cost(input_tokens, output_tokens)
            latency = time.time() - start_time

            return ModelResponse(
                content=content,
                model=self.model_name,
                provider="anthropic",
                confidence=0.90,  # Claude is highly reliable
                tokens_used=tokens_used,
                cost=cost,
                latency=latency,
                citations=[],
                metadata={
                    "stop_reason": response.stop_reason,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                },
                timestamp=datetime.now()
            )

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ):
        """Generate streaming response from Claude."""

        try:
            async with self.client.messages.stream(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for Anthropic request."""
        pricing = self.PRICING.get(self.model_name, self.PRICING["claude-3-opus-20240229"])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost
