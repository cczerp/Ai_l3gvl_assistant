"""
AI Model integrations for Legal-AI Assistant.

Supports multiple providers:
- OpenAI (GPT-4) - Paid
- Anthropic (Claude) - Paid
- Google (Gemini) - FREE
- Groq (Llama-3) - FREE
- HuggingFace (Mixtral) - FREE
- Together AI (Llama-3/Mixtral) - FREE with $25 credit
- Local Models (Llama-3, Phi-3, Gemma) - FREE
"""

from .base_model import BaseModel, ModelResponse
from .openai_model import OpenAIModel
from .anthropic_model import AnthropicModel
from .gemini_model import GeminiModel
from .groq_model import GroqModel
from .huggingface_model import HuggingFaceModel
from .together_model import TogetherModel
from .local_model import LocalModel

__all__ = [
    'BaseModel',
    'ModelResponse',
    'OpenAIModel',
    'AnthropicModel',
    'GeminiModel',
    'GroqModel',
    'HuggingFaceModel',
    'TogetherModel',
    'LocalModel',
]
