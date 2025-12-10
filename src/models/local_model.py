"""
Local model inference using transformers and PyTorch.
For running Llama-3, Phi-3, Gemma, etc. on your own server/cloud.
"""

import os
import time
from typing import Optional
from datetime import datetime
import logging

from .base_model import BaseModel, ModelResponse

logger = logging.getLogger(__name__)


class LocalModel(BaseModel):
    """
    Local model inference using HuggingFace transformers.
    Supports: Llama-3, Phi-3, Gemma, Mistral, etc.
    """

    # All local models are FREE!
    PRICING = {}

    def __init__(
        self,
        model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct",
        model_path: Optional[str] = None,
        device: str = "auto",
        quantization: str = "4bit"
    ):
        """
        Initialize local model.

        Args:
            model_name: HuggingFace model name or local path
            model_path: Optional local path to model weights
            device: Device to run on ('auto', 'cuda', 'cpu')
            quantization: Quantization level ('none', '4bit', '8bit')
        """
        super().__init__("local", model_name)

        self.model_path = model_path or model_name
        self.device = device
        self.quantization = quantization
        self.model = None
        self.tokenizer = None

        # Load model on initialization
        self._load_model()

    def _load_model(self):
        """Load the model and tokenizer."""
        try:
            from transformers import (
                AutoModelForCausalLM,
                AutoTokenizer,
                BitsAndBytesConfig
            )
            import torch

            logger.info(f"Loading local model: {self.model_name}")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )

            # Configure quantization
            quantization_config = None
            if self.quantization == "4bit":
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            elif self.quantization == "8bit":
                quantization_config = BitsAndBytesConfig(load_in_8bit=True)

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                quantization_config=quantization_config,
                device_map=self.device,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.quantization == "none" else None
            )

            logger.info(f"✅ Model loaded successfully: {self.model_name}")

        except ImportError as e:
            logger.error(f"Missing dependencies: {e}")
            raise ImportError(
                "Local model inference requires: transformers, torch, accelerate, bitsandbytes"
            )
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ) -> ModelResponse:
        """Generate response from local model."""

        start_time = time.time()

        # Format prompt based on model type
        formatted_prompt = self._format_prompt(prompt, system_prompt)

        try:
            # Tokenize input
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=4096
            )
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

            # Generate
            import torch
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=temperature > 0,
                    top_p=0.9,
                    **kwargs
                )

            # Decode output
            response = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            )

            input_tokens = inputs['input_ids'].shape[1]
            output_tokens = outputs.shape[1] - input_tokens
            tokens_used = input_tokens + output_tokens

            latency = time.time() - start_time

            return ModelResponse(
                content=response.strip(),
                model=self.model_name,
                provider="local",
                confidence=0.75,  # Local models vary in quality
                tokens_used=tokens_used,
                cost=0.0,  # FREE!
                latency=latency,
                citations=[],
                metadata={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "quantization": self.quantization,
                    "device": str(self.model.device),
                },
                timestamp=datetime.now()
            )

        except Exception as e:
            logger.error(f"Local model generation error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ):
        """Generate streaming response from local model."""

        formatted_prompt = self._format_prompt(prompt, system_prompt)

        try:
            from transformers import TextIteratorStreamer
            import torch
            from threading import Thread

            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=4096
            )
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

            streamer = TextIteratorStreamer(
                self.tokenizer,
                skip_special_tokens=True,
                skip_prompt=True
            )

            generation_kwargs = dict(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                top_p=0.9,
                streamer=streamer,
                **kwargs
            )

            # Run generation in thread
            thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
            thread.start()

            # Yield tokens as they come
            for text in streamer:
                yield text

            thread.join()

        except Exception as e:
            logger.error(f"Local model streaming error: {e}")
            raise

    def _format_prompt(self, prompt: str, system_prompt: Optional[str]) -> str:
        """
        Format prompt based on model type.
        Different models have different chat templates.
        """
        # Try to use model's chat template
        if hasattr(self.tokenizer, 'chat_template') and self.tokenizer.chat_template:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            return self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

        # Fallback: Simple format
        if system_prompt:
            return f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]"
        else:
            return f"<s>[INST] {prompt} [/INST]"

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Local models are FREE!"""
        return 0.0
