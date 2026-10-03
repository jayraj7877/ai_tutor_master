import io
import wave
import struct
from typing import List, AsyncGenerator
from app.providers.tts.base import TTSProvider, TTSChunk


def generate_synthetic_wav_bytes(duration_sec: float = 0.5) -> bytes:
    """Generates a minimal valid 16-bit PCM WAV audio byte string."""
    sample_rate = 16000
    num_samples = int(sample_rate * duration_sec)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        # Generate silence / subtle tone samples
        raw_samples = bytearray()
        for i in range(num_samples):
            # Gentle 440 Hz tone
            val = int(1000 * (i % 36 / 36.0))
            raw_samples.extend(struct.pack('<h', val))
        wav_file.writeframes(raw_samples)
    return buf.getvalue()


class MockTTSProvider(TTSProvider):
    """Local mock provider producing valid synthetic audio frames with zero latency."""

    async def generate_chunks(
        self,
        text_chunks: List[str],
        voice_id: str = "female_01",
        language: str = "en",
        speed: float = 0.95,
    ) -> AsyncGenerator[TTSChunk, None]:
        wav_data = generate_synthetic_wav_bytes(duration_sec=0.5)
        for idx, text in enumerate(text_chunks, start=1):
            yield TTSChunk(
                sequence=idx,
                format="wav",
                data=wav_data,
                text=text
            )
