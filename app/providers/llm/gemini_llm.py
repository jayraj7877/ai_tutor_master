import httpx
from typing import List, Dict, Any, Optional, AsyncGenerator
from app.core.config import settings
from app.core.logging import logger
from app.providers.llm.base import LLMProvider, LLMResponse


class GeminiLLMProvider(LLMProvider):
    """Google Gemini API implementation."""

    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL or "gemini-1.5-flash"

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        language: str = "en",
        user_context: Optional[Dict[str, Any]] = None,
        conversation_context: Optional[Dict[str, Any]] = None,
    ) -> LLMResponse:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        payload = {
            "contents": contents,
            "generationConfig": {"maxOutputTokens": 150, "temperature": 0.7}
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                res.raise_for_status()
                data = res.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return LLMResponse(
                    response_text=text,
                    intent="conversational_reply",
                    tone="friendly",
                )
        except Exception as e:
            logger.error("Gemini API error, using mock fallback", error=str(e))
            from app.providers.llm.mock_llm import MockLLMProvider
            return await MockLLMProvider().generate_response(messages, language, user_context, conversation_context)

    async def stream_response_chunks(
        self,
        messages: List[Dict[str, str]],
        language: str = "en",
        user_context: Optional[Dict[str, Any]] = None,
        conversation_context: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        # Fallback to generate_response if streaming endpoint is omitted
        resp = await self.generate_response(messages, language, user_context, conversation_context)
        words = resp.response_text.split()
        for i in range(0, len(words), 3):
            yield " ".join(words[i:i+3]) + " "
