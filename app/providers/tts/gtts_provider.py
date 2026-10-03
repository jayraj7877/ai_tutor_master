import io
import asyncio
from typing import List, AsyncGenerator
from gtts import gTTS
from app.core.logging import logger
from app.providers.tts.base import TTSProvider, TTSChunk
from app.providers.tts.mock_tts import MockTTSProvider


VOICE_LANG_MAPPING = {
    "female_01": "en",
    "male_01": "en",
    "female_02": "hi",
    "male_02": "hi",
}


def synthesize_gtts_sync(text: str, lang: str) -> bytes:
    fp = io.BytesIO()
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.write_to_fp(fp)
    return fp.getvalue()


class GTTSProvider(TTSProvider):
    """Google Text-to-Speech provider using gTTS with async non-blocking execution."""

    async def generate_chunks(
        self,
        text_chunks: List[str],
        voice_id: str = "female_01",
        language: str = "en",
        speed: float = 0.95,
    ) -> AsyncGenerator[TTSChunk, None]:
        lang_code = VOICE_LANG_MAPPING.get(voice_id, language)
        loop = asyncio.get_running_loop()

        for idx, text in enumerate(text_chunks, start=1):
            try:
                # Offload blocking gTTS HTTP call to executor
                audio_bytes = await loop.run_in_executor(None, synthesize_gtts_sync, text, lang_code)
                yield TTSChunk(
                    sequence=idx,
                    format="mp3",
                    data=audio_bytes,
                    text=text,
                )
            except Exception as e:
                logger.warning("gTTS synthesis failed, using mock audio fallback for chunk", chunk_idx=idx, error=str(e))
                mock_provider = MockTTSProvider()
                async for mock_chunk in mock_provider.generate_chunks([text], voice_id, language, speed):
                    mock_chunk.sequence = idx
                    yield mock_chunk
