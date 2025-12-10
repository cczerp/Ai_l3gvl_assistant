"""
DeepInfra model integration (10M tokens/month FREE).
Good alternative with generous free tier.
"""

import os
import time
from typing import Optional
from datetime import datetime
import httpx
import logging

from .base_model import BaseModel, ModelResponse

logger = logging.getLogger(__name__)


class DeepInfraModel(BaseModel):
    """DeepInfra model integration with generous free tier."""

    # Pricing after free tier (per 1M tokens)
    # FREE: 10M tokens/month
    PRICING = {
        "meta-llama/Meta-Llama-3-70B-Instruct": {"input": 0.59, "output": 0.79},
        "mistralai/Mixtral-8x7B-Instruct-v0.1": {"input": 0.27, "output": 0.27},
        "meta-llama/Meta-Llama-3-8B-Instruct": {"input": 0.08, "output": 0.08},
    }

    API_BASE = "https://api.deepinfra.com/v1/openai"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "meta-llama/Meta-Llama-3-70B-Instruct"
    ):
        """
        Initialize DeepInfra model.

        Args:
            api_key: DeepInfra API key (defaults to DEEPINFRA_API_KEY env var)
            model_name: Model to use
        """
        api_key = api_key or os.getenv('DEEPINFRA_API_KEY')
        if not api_key:
            raise ValueError("DeepInfra API key required")

        super().__init__(api_key, model_name)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ) -> ModelResponse:
        """Generate response from DeepInfra."""

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
                provider="deepinfra",
                confidence=0.80,
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
                f"DeepInfra HTTP error: {e.response.status_code} - {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"DeepInfra error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ):
        """Generate streaming response from DeepInfra."""

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
            logger.error(f"DeepInfra streaming error: {e}")
            raise

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for DeepInfra request.

        Note: FREE 10M tokens/month!
        """
        pricing = self.PRICING.get(
            self.model_name,
            self.PRICING["meta-llama/Meta-Llama-3-70B-Instruct"]
        )
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost
