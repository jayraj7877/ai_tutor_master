from typing import List, Dict, Any


class ConversationContextManager:
    """Manages context window size, message history formatting, and historical context summarization."""

    def __init__(self, max_history_messages: int = 10):
        self.max_history_messages = max_history_messages

    def format_history_for_llm(
        self,
        past_messages: List[Dict[str, Any]],
        learning_language: str = "en",
        native_language: str = "hi",
        difficulty: str = "intermediate"
    ) -> List[Dict[str, str]]:
        """Formats database message records into LLM message array."""
        # Truncate to most recent messages to prevent token overflow
        recent_messages = past_messages[-self.max_history_messages:]
        
        formatted = []
        for msg in recent_messages:
            role = "user" if msg.get("role") == "user" else "assistant"
            formatted.append({"role": role, "content": msg.get("text", "")})

        return formatted
