"""
Fireworks AI model integration (FREE credit, ultra-fast).
Alternative to Together AI, similar speed to Groq.
"""

import os
import time
from typing import Optional
from datetime import datetime
import httpx
import logging

from .base_model import BaseModel, ModelResponse

logger = logging.getLogger(__name__)


class FireworksModel(BaseModel):
    """Fireworks AI fast inference model integration."""

    # Pricing after free credit (per 1M tokens)
    PRICING = {
        "accounts/fireworks/models/llama-v3-70b-instruct": {"input": 0.90, "output": 0.90},
        "accounts/fireworks/models/mixtral-8x7b-instruct": {"input": 0.50, "output": 0.50},
        "accounts/fireworks/models/llama-v3-8b-instruct": {"input": 0.20, "output": 0.20},
    }

    API_BASE = "https://api.fireworks.ai/inference/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "accounts/fireworks/models/llama-v3-70b-instruct"
    ):
        """
        Initialize Fireworks AI model.

        Args:
            api_key: Fireworks AI API key (defaults to FIREWORKS_API_KEY env var)
            model_name: Model to use
        """
        api_key = api_key or os.getenv('FIREWORKS_API_KEY')
        if not api_key:
            raise ValueError("Fireworks AI API key required")

        super().__init__(api_key, model_name)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ) -> ModelResponse:
        """Generate response from Fireworks AI."""

        start_time = time.time()

        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.API_BASE}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        **kwargs
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()

            content = data["choices"][0]["message"]["content"]
            tokens_used = data["usage"]["total_tokens"]
            input_tokens = data["usage"]["prompt_tokens"]
            output_tokens = data["usage"]["completion_tokens"]

            cost = self.estimate_cost(input_tokens, output_tokens)
            latency = time.time() - start_time

            return ModelResponse(
                content=content,
                model=self.model_name,
                provider="fireworks",
                confidence=0.85,
                tokens_used=tokens_used,
                cost=cost,
                latency=latency,
                citations=[],
                metadata={
                    "finish_reason": data["choices"][0].get("finish_reason"),
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                },
                timestamp=datetime.now()
            )

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Fireworks AI HTTP error: {e.response.status_code} - {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"Fireworks AI error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ):
        """Generate streaming response from Fireworks AI."""

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.API_BASE}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": True,
                        **kwargs
                    },
                    timeout=60.0
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                import json
                                chunk = json.loads(data)
                                if chunk["choices"][0]["delta"].get("content"):
                                    yield chunk["choices"][0]["delta"]["content"]
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            logger.error(f"Fireworks AI streaming error: {e}")
            raise

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for Fireworks AI request."""
        pricing = self.PRICING.get(
            self.model_name,
            self.PRICING["accounts/fireworks/models/llama-v3-70b-instruct"]
        )
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost
