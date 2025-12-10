"""
Google Gemini model integration.
"""

import os
import time
from typing import Optional
from datetime import datetime
import logging

from .base_model import BaseModel, ModelResponse

logger = logging.getLogger(__name__)


class GeminiModel(BaseModel):
    """Google Gemini model integration."""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "gemini-pro": {"input": 0.5, "output": 1.5},
        "gemini-1.5-pro": {"input": 3.5, "output": 10.5},
        "gemini-1.5-flash": {"input": 0.35, "output": 1.05},
    }

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-pro"):
        """
        Initialize Gemini model.

        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            model_name: Model to use
        """
        api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google API key required")

        super().__init__(api_key, model_name)

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.genai = genai
            self.model = genai.GenerativeModel(model_name)
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. "
                "Install with: pip install google-generativeai"
            )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ) -> ModelResponse:
        """Generate response from Gemini."""

        start_time = time.time()

        # Combine system prompt and user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        try:
            # Configure generation
            generation_config = self.genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                **kwargs
            )

            # Generate response (Gemini doesn't have native async, use sync)
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )

            content = response.text

            # Estimate tokens (Gemini doesn't always provide token counts)
            input_tokens = self.count_tokens(full_prompt)
            output_tokens = self.count_tokens(content)
            tokens_used = input_tokens + output_tokens

            cost = self.estimate_cost(input_tokens, output_tokens)
            latency = time.time() - start_time

            return ModelResponse(
                content=content,
                model=self.model_name,
                provider="google",
                confidence=0.85,  # Gemini is generally reliable
                tokens_used=tokens_used,
                cost=cost,
                latency=latency,
                citations=[],
                metadata={
                    "finish_reason": getattr(response, 'finish_reason', None),
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                },
                timestamp=datetime.now()
            )

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ):
        """Generate streaming response from Gemini."""

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        try:
            generation_config = self.genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                **kwargs
            )

            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config,
                stream=True
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Gemini streaming error: {e}")
            raise

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for Gemini request."""
        pricing = self.PRICING.get(self.model_name, self.PRICING["gemini-pro"])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost
