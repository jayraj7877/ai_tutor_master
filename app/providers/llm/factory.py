from app.core.config import settings
from app.providers.llm.base import LLMProvider
from app.providers.llm.mock_llm import MockLLMProvider
from app.providers.llm.openai_llm import OpenAILLMProvider
from app.providers.llm.gemini_llm import GeminiLLMProvider


def get_llm_provider() -> LLMProvider:
    provider_name = settings.LLM_PROVIDER.lower()
    if provider_name == "openai":
        return OpenAILLMProvider()
    elif provider_name == "gemini":
        return GeminiLLMProvider()
    elif provider_name == "mock":
        return MockLLMProvider()
    return MockLLMProvider()
