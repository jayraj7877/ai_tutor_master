import pytest
from app.providers.llm.mock_llm import MockLLMProvider


@pytest.mark.asyncio
async def test_mock_llm_tutor_behavior():
    provider = MockLLMProvider()
    messages = [{"role": "user", "content": "Yesterday I go to market and I meet my friend."}]
    res = await provider.generate_response(messages)

    assert "nice day" in res.response_text.lower() or "market" in res.response_text.lower() or "friend" in res.response_text.lower()
    assert res.intent == "friendly_chat"
    assert res.tone == "warm_encouraging"
