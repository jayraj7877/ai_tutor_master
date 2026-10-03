import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from app.providers.llm.base import LLMProvider, LLMResponse


class MockLLMProvider(LLMProvider):
    """Local mock provider for instant response generation without external API dependencies."""

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        language: str = "en",
        user_context: Optional[Dict[str, Any]] = None,
        conversation_context: Optional[Dict[str, Any]] = None,
    ) -> LLMResponse:
        last_message = messages[-1]["content"] if messages else ""
        text_lower = last_message.lower()

        # Handle specific test case from requirement prompt:
        # User: "Yesterday I go to market and I meet my friend."
        # AI: "That sounds like a nice day! What did you and your friend do?"
        if "market" in text_lower or "friend" in text_lower:
            resp_text = "That sounds like a nice day! What did you and your friend do?"
            follow_up = "What did you buy at the market?"
        elif "hello" in text_lower or "hi" in text_lower or "namaste" in text_lower:
            resp_text = "Hello! It is great to chat with you today. How is your day going so far?"
            follow_up = "How is your day going so far?"
        elif "office" in text_lower or "work" in text_lower:
            resp_text = "Oh, what did you do at the office yesterday?"
            follow_up = "Did you have many meetings?"
        else:
            resp_text = f"That is really interesting! Could you tell me a little more about that?"
            follow_up = "Could you elaborate?"

        return LLMResponse(
            response_text=resp_text,
            intent="friendly_chat",
            tone="warm_encouraging",
            follow_up=follow_up,
            difficulty=conversation_context.get("difficulty", "intermediate") if conversation_context else "intermediate",
        )

    async def stream_response_chunks(
        self,
        messages: List[Dict[str, str]],
        language: str = "en",
        user_context: Optional[Dict[str, Any]] = None,
        conversation_context: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        full_resp = await self.generate_response(messages, language, user_context, conversation_context)
        # Simulate word/chunk token streaming
        words = full_resp.response_text.split()
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i+3]) + " "
            yield chunk
            await asyncio.sleep(0.02)
