"""
AI Model integrations for Legal-AI Assistant.

Supports multiple providers:
- OpenAI (GPT-4)
- Anthropic (Claude)
- Google (Gemini)
- Groq (Llama-3)
- HuggingFace (Mixtral)
"""

from .base_model import BaseModel, ModelResponse
from .openai_model import OpenAIModel
from .anthropic_model import AnthropicModel
from .gemini_model import GeminiModel
from .groq_model import GroqModel
from .huggingface_model import HuggingFaceModel

__all__ = [
    'BaseModel',
    'ModelResponse',
    'OpenAIModel',
    'AnthropicModel',
    'GeminiModel',
    'GroqModel',
    'HuggingFaceModel',
]
