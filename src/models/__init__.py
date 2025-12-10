"""
AI Model integrations for Legal-AI Assistant.

Supports multiple providers:
- OpenAI (GPT-4) - Paid
- Anthropic (Claude) - Paid
- Google (Gemini) - FREE (60 req/min)
- Groq (Llama-3) - FREE (14,400 req/day)
- HuggingFace (Mixtral) - FREE (30k req/month)
- Fireworks AI - FREE credit, ultra-fast
- DeepInfra - FREE (10M tokens/month)
- Local Models (Llama-3, Phi-3, Gemma) - FREE unlimited
"""

from .base_model import BaseModel, ModelResponse
from .openai_model import OpenAIModel
from .anthropic_model import AnthropicModel
from .gemini_model import GeminiModel
from .groq_model import GroqModel
from .huggingface_model import HuggingFaceModel
from .fireworks_model import FireworksModel
from .deepinfra_model import DeepInfraModel
from .local_model import LocalModel

__all__ = [
    'BaseModel',
    'ModelResponse',
    'OpenAIModel',
    'AnthropicModel',
    'GeminiModel',
    'GroqModel',
    'HuggingFaceModel',
    'FireworksModel',
    'DeepInfraModel',
    'LocalModel',
]
