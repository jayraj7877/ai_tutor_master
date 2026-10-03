import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoints(async_client: AsyncClient):
    res_health = await async_client.get("/api/v1/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    res_ready = await async_client.get("/api/v1/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] in ["ready", "degraded"]


@pytest.mark.asyncio
async def test_voices_endpoint(async_client: AsyncClient):
    res = await async_client.get("/api/v1/voices")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert data[0]["voice_id"] == "female_01"


@pytest.mark.asyncio
async def test_language_detect_endpoint(async_client: AsyncClient):
    res = await async_client.post("/api/v1/language/detect", json={"text": "Yesterday I go to market"})
    assert res.status_code == 200
    assert res.json()["primary_language"] == "en"


@pytest.mark.asyncio
async def test_grammar_check_endpoint(async_client: AsyncClient):
    res = await async_client.post(
        "/api/v1/grammar/check",
        json={"text": "Yesterday I go to market and I meet my friend.", "language": "en"}
    )
    assert res.status_code == 200
    mistakes = res.json()["mistakes"]
    assert len(mistakes) >= 2


@pytest.mark.asyncio
async def test_conversation_message_flow(async_client: AsyncClient):
    conv_id = str(uuid.uuid4())
    payload = {
        "conversation_id": conv_id,
        "message": "Yesterday I go to market and I meet my friend.",
        "voice_id": "female_01",
        "speed": 0.95
    }
    res = await async_client.post("/api/v1/conversation/message", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["conversation_id"] == conv_id
    assert "nice day" in data["assistant_response"].lower() or "friend" in data["assistant_response"].lower()
    assert len(data["grammar_analysis"]) >= 2
    assert len(data["audio_chunks"]) >= 1
    assert data["audio_chunks"][0]["sequence"] == 1
    assert "metrics" in data
    assert data["metrics"]["total_response_ms"] > 0
