import httpx
from typing import List, AsyncGenerator
from app.core.config import settings
from app.core.logging import logger
from app.providers.tts.base import TTSProvider, TTSChunk
from app.providers.tts.mock_tts import MockTTSProvider


class ElevenLabsTTSProvider(TTSProvider):
    """ElevenLabs API Provider Adapter."""

    def __init__(self):
        self.api_key = settings.TTS_API_KEY
        self.base_url = settings.TTS_BASE_URL or "https://api.elevenlabs.io/v1"

    async def generate_chunks(
        self,
        text_chunks: List[str],
        voice_id: str = "female_01",
        language: str = "en",
        speed: float = 0.95,
    ) -> AsyncGenerator[TTSChunk, None]:
        # Map generic voice_id to ElevenLabs voice ID
        provider_voice = "21m00Tcm4TlvDq8ikWAM"  # Default Rachel voice
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            for idx, text in enumerate(text_chunks, start=1):
                payload = {
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                    }
                }
                url = f"{self.base_url}/text-to-speech/{provider_voice}"
                try:
                    res = await client.post(url, headers=headers, json=payload)
                    res.raise_for_status()
                    yield TTSChunk(
                        sequence=idx,
                        format="mp3",
                        data=res.content,
                        text=text
                    )
                except Exception as e:
                    logger.error("ElevenLabs TTS request failed, falling back to mock TTS", chunk_idx=idx, error=str(e))
                    mock_provider = MockTTSProvider()
                    async for mock_chunk in mock_provider.generate_chunks([text], voice_id, language, speed):
                        mock_chunk.sequence = idx
                        yield mock_chunk
