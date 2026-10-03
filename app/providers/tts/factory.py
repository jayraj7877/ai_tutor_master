from app.core.config import settings
from app.providers.tts.base import TTSProvider
from app.providers.tts.mock_tts import MockTTSProvider
from app.providers.tts.gtts_provider import GTTSProvider
from app.providers.tts.elevenlabs_tts import ElevenLabsTTSProvider


def get_tts_provider() -> TTSProvider:
    provider_name = settings.TTS_PROVIDER.lower()
    if provider_name == "gtts":
        return GTTSProvider()
    elif provider_name == "elevenlabs":
        return ElevenLabsTTSProvider()
    elif provider_name == "mock":
        return MockTTSProvider()
    return GTTSProvider()
