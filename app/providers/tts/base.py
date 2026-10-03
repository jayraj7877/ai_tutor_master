from abc import ABC, abstractmethod
from typing import List, AsyncGenerator
from pydantic import BaseModel


class TTSChunk(BaseModel):
    sequence: int
    format: str = "mp3"
    data: bytes
    text: str


class TTSProvider(ABC):
    """Abstract Base Class for Text-To-Speech Providers."""

    @abstractmethod
    async def generate_chunks(
        self,
        text_chunks: List[str],
        voice_id: str = "female_01",
        language: str = "en",
        speed: float = 0.95,
    ) -> AsyncGenerator[TTSChunk, None]:
        """Synthesize audio bytes for each text chunk asynchronously."""
        pass
