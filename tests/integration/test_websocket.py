import json
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
from tests.conftest import TestSessionLocal, test_engine, Base


def test_websocket_streaming_flow():
    # Setup test DB
    async def _override_get_db():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db

    client = TestClient(app)
    conv_id = str(uuid.uuid4())

    try:
        with client.websocket_connect("/api/v1/conversation/stream") as websocket:
            payload = {
                "action": "send_message",
                "conversation_id": conv_id,
                "message": "Yesterday I go to market and I meet my friend.",
                "voice_id": "female_01",
                "speed": 0.95
            }
            websocket.send_text(json.dumps(payload))

            events = []
            while True:
                data = websocket.receive_text()
                event = json.loads(data)
                events.append(event)
                if event.get("type") in ["conversation_complete", "error"]:
                    break

            event_types = [e["type"] for e in events]
            assert "conversation_started" in event_types
            assert "language_detected" in event_types
            assert "text_chunk" in event_types
            assert "audio_chunk" in event_types
            assert "audio_complete" in event_types
            assert "grammar_result" in event_types
            assert "conversation_complete" in event_types

            # Verify sequence numbers for audio chunks
            audio_events = [e for e in events if e["type"] == "audio_chunk"]
            assert len(audio_events) >= 1
            assert audio_events[0]["sequence"] == 1
            assert len(audio_events[0]["data"]) > 0
    finally:
        app.dependency_overrides.clear()
