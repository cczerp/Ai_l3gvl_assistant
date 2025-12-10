"""
HuggingFace Inference API model integration.
"""

import os
import time
from typing import Optional
from datetime import datetime
import httpx
import logging

from .base_model import BaseModel, ModelResponse

logger = logging.getLogger(__name__)


class HuggingFaceModel(BaseModel):
    """HuggingFace Inference API model integration."""

    # HuggingFace is FREE but has rate limits
    # Free tier: 30,000 requests/month
    PRICING = {
        "mistralai/Mixtral-8x7B-Instruct-v0.1": {"input": 0.0, "output": 0.0},  # FREE
        "meta-llama/Llama-2-70b-chat-hf": {"input": 0.0, "output": 0.0},  # FREE
        "mistralai/Mistral-7B-Instruct-v0.2": {"input": 0.0, "output": 0.0},  # FREE
    }

    API_BASE = "https://api-inference.huggingface.co/models"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    ):
        """
        Initialize HuggingFace model.

        Args:
            api_key: HuggingFace API key (defaults to HUGGINGFACE_API_KEY env var)
            model_name: Model to use
        """
        api_key = api_key or os.getenv('HUGGINGFACE_API_KEY')
        if not api_key:
            raise ValueError("HuggingFace API key required")

        super().__init__(api_key, model_name)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ) -> ModelResponse:
        """Generate response from HuggingFace."""

        start_time = time.time()

        # Format prompt (Mixtral uses specific format)
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"<s>[INST] {system_prompt}\n\n{prompt} [/INST]"
        else:
            full_prompt = f"<s>[INST] {prompt} [/INST]"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.API_BASE}/{self.model_name}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "inputs": full_prompt,
                        "parameters": {
                            "temperature": temperature,
                            "max_new_tokens": max_tokens,
                            "return_full_text": False,
                            **kwargs
                        },
                    },
                    timeout=120.0  # HuggingFace can be slower
                )

                # Handle model loading
                if response.status_code == 503:
                    # Model is loading, wait and retry
                    logger.info(f"Model {self.model_name} is loading, waiting...")
                    import asyncio
                    await asyncio.sleep(20)
                    response = await client.post(
                        f"{self.API_BASE}/{self.model_name}",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "inputs": full_prompt,
                            "parameters": {
                                "temperature": temperature,
                                "max_new_tokens": max_tokens,
                                "return_full_text": False,
                                **kwargs
                            },
                        },
                        timeout=120.0
                    )

                response.raise_for_status()
                data = response.json()

            # Extract response
            if isinstance(data, list) and len(data) > 0:
                content = data[0].get("generated_text", "")
            elif isinstance(data, dict):
                content = data.get("generated_text", "")
            else:
                content = str(data)

            # Estimate tokens
            input_tokens = self.count_tokens(full_prompt)
            output_tokens = self.count_tokens(content)
            tokens_used = input_tokens + output_tokens

            latency = time.time() - start_time

            return ModelResponse(
                content=content,
                model=self.model_name,
                provider="huggingface",
                confidence=0.75,  # Free models are less reliable
                tokens_used=tokens_used,
                cost=0.0,  # FREE!
                latency=latency,
                citations=[],
                metadata={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                },
                timestamp=datetime.now()
            )

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HuggingFace API HTTP error: {e.response.status_code} - {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"HuggingFace API error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ):
        """Generate streaming response from HuggingFace."""

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"<s>[INST] {system_prompt}\n\n{prompt} [/INST]"
        else:
            full_prompt = f"<s>[INST] {prompt} [/INST]"

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.API_BASE}/{self.model_name}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "inputs": full_prompt,
                        "parameters": {
                            "temperature": temperature,
                            "max_new_tokens": max_tokens,
                            "return_full_text": False,
                            **kwargs
                        },
                        "stream": True,
                    },
                    timeout=120.0
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                import json
                                chunk = json.loads(line)
                                if "token" in chunk and "text" in chunk["token"]:
                                    yield chunk["token"]["text"]
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            logger.error(f"HuggingFace streaming error: {e}")
            raise

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """HuggingFace Inference API is FREE!"""
        return 0.0
