"""
Groq model integration (Llama-3, Mixtral on fast inference).
"""

import os
import time
from typing import Optional
from datetime import datetime
import httpx
import logging

from .base_model import BaseModel, ModelResponse

logger = logging.getLogger(__name__)


class GroqModel(BaseModel):
    """Groq fast inference model integration."""

    # Groq is FREE but has rate limits
    # Free tier: 14,400 requests/day, 10 requests/minute
    PRICING = {
        "llama-3-70b-8192": {"input": 0.0, "output": 0.0},  # FREE
        "llama-3-8b-8192": {"input": 0.0, "output": 0.0},   # FREE
        "mixtral-8x7b-32768": {"input": 0.0, "output": 0.0},  # FREE
    }

    API_BASE = "https://api.groq.com/openai/v1"

    def __init__(self, api_key: Optional[str] = None, model_name: str = "llama-3-70b-8192"):
        """
        Initialize Groq model.

        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model_name: Model to use
        """
        api_key = api_key or os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("Groq API key required")

        super().__init__(api_key, model_name)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ) -> ModelResponse:
        """Generate response from Groq."""

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

            latency = time.time() - start_time

            return ModelResponse(
                content=content,
                model=self.model_name,
                provider="groq",
                confidence=0.80,  # Groq is fast but slightly less reliable
                tokens_used=tokens_used,
                cost=0.0,  # FREE!
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
            logger.error(f"Groq API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ):
        """Generate streaming response from Groq."""

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
            logger.error(f"Groq streaming error: {e}")
            raise

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Groq is FREE!"""
        return 0.0
