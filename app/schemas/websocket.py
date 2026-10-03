from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class WSIncomingMessage(BaseModel):
    action: str = Field(default="send_message", description="Action name, e.g. send_message")
    conversation_id: str = Field(..., description="UUID of the conversation session")
    message: str = Field(..., min_length=1, description="User message text")
    voice_id: str = Field(default="female_01", description="Voice ID for audio synthesis")
    speed: float = Field(default=0.95, ge=0.5, le=2.0, description="TTS playback speed")


class WSOutgoingEvent(BaseModel):
    type: str = Field(..., description="Event type string")
    conversation_id: Optional[str] = Field(None, description="Conversation ID associated with event")
    sequence: Optional[int] = Field(None, description="Sequence number for chunks")
    format: Optional[str] = Field(None, description="Audio format, e.g., 'mp3'")
    data: Optional[str] = Field(None, description="Base64-encoded audio chunk payload")
    text: Optional[str] = Field(None, description="Text snippet corresponding to chunk or event message")
    payload: Optional[Dict[str, Any]] = Field(None, description="Structured payload for complex events")
    error: Optional[str] = Field(None, description="Error detail string if event is an error")
