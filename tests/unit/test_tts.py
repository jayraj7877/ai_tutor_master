import pytest
from app.providers.tts.mock_tts import MockTTSProvider


@pytest.mark.asyncio
async def test_tts_mock_provider_chunks():
    provider = MockTTSProvider()
    chunks_text = ["Hello there!", "How are you doing today?"]
    generated = []
    async for chunk in provider.generate_chunks(chunks_text, voice_id="female_01", speed=0.95):
        generated.append(chunk)

    assert len(generated) == 2
    assert generated[0].sequence == 1
    assert generated[0].text == "Hello there!"
    assert len(generated[0].data) > 0
    assert generated[1].sequence == 2
    assert generated[1].text == "How are you doing today?"
