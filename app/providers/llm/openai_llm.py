import json
import httpx
from typing import List, Dict, Any, Optional, AsyncGenerator
from app.core.config import settings
from app.core.logging import logger
from app.providers.llm.base import LLMProvider, LLMResponse


SYSTEM_PROMPT = """You are a friendly, warm, and natural English tutor speaking with a language learner.
Your goal is to maintain a natural conversation and encourage the student to practice speaking.
RULES:
1. Speak naturally as a friend, not a textbook.
2. Keep responses concise (1-3 sentences) so they are easy to listen to via voice playback.
3. Understand native language / Hinglish input, but respond primarily in English.
4. Do NOT explicitly list grammar mistakes in your spoken response. Focus on continuing the conversation.
5. Ask occasional, natural follow-up questions when appropriate, but do not overwhelm the user with questions.
6. Adapt your vocabulary to the student's difficulty level.
"""


class OpenAILLMProvider(LLMProvider):
    """OpenAI API Provider implementation supporting custom endpoints (Ollama / vLLM / OpenAI)."""

    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL or "https://api.openai.com/v1"
        self.model = settings.LLM_MODEL or "gpt-4o-mini"

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        language: str = "en",
        user_context: Optional[Dict[str, Any]] = None,
        conversation_context: Optional[Dict[str, Any]] = None,
    ) -> LLMResponse:
        prompt_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": prompt_messages,
            "temperature": 0.7,
            "max_tokens": 150,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
                content = data["choices"][0]["message"]["content"].strip()
                return LLMResponse(
                    response_text=content,
                    intent="conversational_reply",
                    tone="friendly",
                    difficulty=conversation_context.get("difficulty", "intermediate") if conversation_context else "intermediate",
                )
        except Exception as e:
            logger.error("OpenAI API call failed, falling back to mock LLM response", error=str(e))
            from app.providers.llm.mock_llm import MockLLMProvider
            return await MockLLMProvider().generate_response(messages, language, user_context, conversation_context)

    async def stream_response_chunks(
        self,
        messages: List[Dict[str, str]],
        language: str = "en",
        user_context: Optional[Dict[str, Any]] = None,
        conversation_context: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        prompt_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": prompt_messages,
            "temperature": 0.7,
            "max_tokens": 150,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                async with client.stream("POST", f"{self.base_url}/chat/completions", headers=headers, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: ") and line != "data: [DONE]":
                            chunk_data = json.loads(line[6:])
                            delta = chunk_data["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
        except Exception as e:
            logger.error("OpenAI stream failed, using mock stream fallback", error=str(e))
            from app.providers.llm.mock_llm import MockLLMProvider
            async for chunk in MockLLMProvider().stream_response_chunks(messages, language, user_context, conversation_context):
                yield chunk
